# -------------------------------------------- LICENSE --------------------------------------------
#
# Copyright 2025 Humberto Gomes, José Lopes, José Matos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -------------------------------------------------------------------------------------------------

from __future__ import annotations
from itertools import chain
from typing import cast, get_args

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_unlocalized_error
from .typechecker import TypeChecker
from .symboltable import SymbolTable

class EWVMError(Exception):
    pass

class Label:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def callable(call: str) -> Label:
        return Label(f'FN{call}')

    @staticmethod
    def user(call: None | CallableDefinition, name: int) -> Label:
        if call is None:
            return Label(f'USER{name}')
        else:
            return Label(f'USER{name}{call.name.lower()}')

    @staticmethod
    def system(call: None | CallableDefinition, name: int) -> Label:
        if call is None:
            return Label(f'SYS{name}')
        else:
            return Label(f'SYS{name}{call.name.lower()}')

    def __str__(self) -> str:
        return f'{self.name}:'

EWVMArgument = int | float | str | Label

class EWVMStatement:
    def __init__(self, instruction: str, *args: EWVMArgument) -> None:
        self.instruction = instruction
        self.arguments = args

    def __str__(self) -> str:
        def stringize_argument(argument: EWVMArgument) -> str:
            if isinstance(argument, int):
                return str(argument)
            elif isinstance(argument, float):
                return f'{argument:.10f}'
            elif isinstance(argument, str):
                if '"' in argument:
                    pascal_escaped = argument.replace('\'', '\'\'')
                    print_unlocalized_error(
                        f'Double quotes in string \'{pascal_escaped}\' '
                        'will be removed in EWVM output',
                        True
                    )

                ewvm_escaped = argument.replace('\n', '\\n').replace('"', '')
                return f'"{ewvm_escaped}"'
            elif isinstance(argument, Label):
                return argument.name
            else:
                raise EWVMError()

        indent = '  ' * (self.instruction != 'START')
        arguments_str = ' '.join(stringize_argument(argument) for argument in self.arguments)
        return f'{indent}{self.instruction} {arguments_str}'

class Comment:
    content: str

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return f'  // {self.content}'

EWVMProgram = list[Label | EWVMStatement | Comment]

def export_assembly(program: EWVMProgram, comments: bool = True) -> str:
    return '\n'.join(str(e) for e in program if (not isinstance(e, Comment) or comments))

class LabelGenerator:
    def __init__(self, call: None | CallableDefinition) -> None:
        self.call = call
        self.__count = 0

    def new(self) -> Label:
        self.__count += 1
        return Label.system(self.call, self.__count)

def __generate_constant_assembly(constant: ConstantValue) -> EWVMStatement:
    if isinstance(constant, (bool, int)):
        return EWVMStatement('PUSHI', int(constant))
    if isinstance(constant, float):
        return EWVMStatement('PUSHF', constant)
    elif isinstance(constant, str) and len(constant) == 1:
        return EWVMStatement('PUSHI', ord(constant))
    elif isinstance(constant, str) and len(constant) != 1:
        return EWVMStatement('PUSHS', constant)
    elif isinstance(constant, EnumeratedTypeConstantValue):
        return EWVMStatement('PUSHI', constant.value)
    else:
        raise EWVMError()

def __generate_variable_creation_assembly(variable_type: TypeValue,
                                          label_generator: LabelGenerator,
                                          scope_offset: int) -> EWVMProgram:

    if variable_type in [BuiltInType.BOOLEAN, BuiltInType.INTEGER] or \
        isinstance(variable_type, RangeType):

        return [__generate_constant_assembly(0)]
    elif variable_type == BuiltInType.REAL:
        return [__generate_constant_assembly(0.0)]
    elif variable_type == BuiltInType.CHAR:
        return [__generate_constant_assembly(0)]
    elif variable_type == BuiltInType.STRING:
        return [__generate_constant_assembly('')]
    elif isinstance(variable_type, list): # EnumeratedType
        first_constant = variable_type[0].value
        assert isinstance(first_constant, EnumeratedTypeConstantValue)
        return [__generate_constant_assembly(first_constant.value)]
    elif isinstance(variable_type, ArrayType):
        # Determine size of array
        array_size = 1
        for index_type in variable_type.dimensions:
            type_checker = TypeChecker('', None)
            start = type_checker.get_constant_ordinal_value(index_type.start)
            end = type_checker.get_constant_ordinal_value(index_type.end)
            array_size *= end - start + 1

        # Create array in heap
        ret: EWVMProgram = [EWVMStatement('ALLOC', array_size)]

        # Initialize values in array with a loop
        label = label_generator.new()
        value_init_statement = __generate_variable_creation_assembly(
            variable_type.subtype,
            label_generator,
            scope_offset
        )

        ret.append(EWVMStatement('PUSHI', 0))
        ret.append(label)
        ret.append(EWVMStatement('PUSHL', scope_offset))
        ret.append(EWVMStatement('PUSHL', scope_offset + 1))
        ret.extend(value_init_statement)
        ret.append(EWVMStatement('STOREN'))
        ret.append(EWVMStatement('PUSHI', 1))
        ret.append(EWVMStatement('ADD'))
        ret.append(EWVMStatement('DUP', 1))
        ret.append(EWVMStatement('PUSHI', array_size))
        ret.append(EWVMStatement('SUPEQ'))
        ret.append(EWVMStatement('JZ', label))
        ret.append(EWVMStatement('POP', 1))

        return ret
    else:
        raise EWVMError()

def __generate_variable_usage_assembly(variable: VariableUsage,
                                       label_generator: LabelGenerator,
                                       read_write: bool) -> EWVMProgram:
    ret: EWVMProgram = []

    if read_write and len(variable.indices) == 0:
        instruction = 'STOREL' if variable.variable.callable_scope else 'STOREG'
    else:
        instruction = 'PUSHL' if variable.variable.callable_scope else 'PUSHG'

    ret.append(EWVMStatement(instruction, variable.variable.scope_offset))

    current_type = variable.variable.variable_type
    type_checker = TypeChecker('', None)

    array_end_i = 0
    for index, index_type in variable.indices:
        if isinstance(current_type, ArrayType):
            ret.extend(__generate_expression_assembly((index, index_type), label_generator))
            ret.append(EWVMStatement(
                'PUSHI',
                type_checker.get_constant_ordinal_value(current_type.dimensions[0].start))
            )
            ret.append(EWVMStatement('SUB'))

            element_size = 1
            for range_type in current_type.dimensions[1:]:
                start = type_checker.get_constant_ordinal_value(range_type.start)
                end = type_checker.get_constant_ordinal_value(range_type.end)
                element_size *= end - start + 1

            ret.append(EWVMStatement('PUSHI', element_size))
            ret.append(EWVMStatement('MUL'))
            ret.append(EWVMStatement('PADD'))

            current_type = type_checker.type_after_indexation(current_type, index_type, (0, 0))
            array_end_i += 1
        else:
            break

    if array_end_i != 0:
        if read_write:
            ret.append(EWVMStatement('SWAP')) # TODO - possible optimization
            ret.append(EWVMStatement('STORE', 0))
        else:
            ret.append(EWVMStatement('LOAD', 0))

    if current_type == BuiltInType.STRING and array_end_i != len(variable.indices):
        # pylint: disable-next=undefined-loop-variable
        ret.extend(__generate_expression_assembly((index, index_type), label_generator))
        ret.append(EWVMStatement('PUSHI', 1))
        ret.append(EWVMStatement('SUB'))
        ret.append(EWVMStatement('CHARAT'))

    return ret

def __generate_builtin_callable_assembly(call: CallableCall,
                                         label_generator: LabelGenerator) -> EWVMProgram:
    ret: EWVMProgram = []
    name = call.callable.name.lower()

    if name in ['write', 'writeln']:
        for argument in call.arguments:
            if argument[1] == BuiltInType.BOOLEAN:
                ret.append(__generate_constant_assembly('True'))
                ret.append(__generate_constant_assembly('False'))
                ret.append(EWVMStatement('PUSHSP'))
                ret.append(EWVMStatement('PUSHI', 0))
                ret.extend(__generate_expression_assembly(argument, label_generator))
                ret.append(EWVMStatement('SUB'))
                ret.append(EWVMStatement('LOADN'))
                ret.append(EWVMStatement('WRITES'))
            elif argument[1] == BuiltInType.INTEGER:
                ret.extend(__generate_expression_assembly(argument, label_generator))
                ret.append(EWVMStatement('WRITEI'))

            if argument[1] == BuiltInType.REAL:
                ret.extend(__generate_expression_assembly(argument, label_generator))
                ret.append(EWVMStatement('WRITEF'))

            elif argument[1] in [BuiltInType.CHAR]:
                ret.extend(__generate_expression_assembly(argument, label_generator))
                ret.append(EWVMStatement('WRITECHR'))

            elif argument[1] in [BuiltInType.STRING]:
                ret.extend(__generate_expression_assembly(argument, label_generator))
                ret.append(EWVMStatement('WRITES'))

            elif isinstance(argument[1], list): # EnumeratedType
                for value in reversed(argument[1]):
                    ret.append(__generate_constant_assembly(value.name))

                ret.append(EWVMStatement('PUSHSP'))
                ret.append(EWVMStatement('PUSHI', 0))
                ret.extend(__generate_expression_assembly(argument, label_generator))
                ret.append(EWVMStatement('SUB'))
                ret.append(EWVMStatement('LOADN'))
                ret.append(EWVMStatement('WRITES'))

        if name == 'writeln':
            ret.append(EWVMStatement('WRITELN'))

    elif name in ['readln', 'read']:
        if len(call.arguments) > 1:
            print_unlocalized_error(
                f'{name} with multiple argunments will be split into multiple {name} calls',
                True
            )

        for argument in call.arguments:
            ret.append(EWVMStatement('READ'))

            if argument[1] in [BuiltInType.INTEGER, BuiltInType.BOOLEAN] or \
                isinstance(argument[1], list): # EnumeratedType

                ret.append(EWVMStatement('ATOI'))
            elif argument[1] == BuiltInType.REAL:
                ret.append(EWVMStatement('ATOF'))
            elif argument[1] == BuiltInType.CHAR:
                end_label = label_generator.new()
                ret.append(EWVMStatement('DUP', 2))
                ret.append(EWVMStatement('STRLEN'))
                ret.append(EWVMStatement('PUSHI', 1))
                ret.append(EWVMStatement('EQUAL'))
                ret.append(EWVMStatement('NOT'))
                ret.append(EWVMStatement('JZ', end_label))
                ret.append(EWVMStatement('ERR', 'More than one character written'))
                ret.append(end_label)
                ret.append(EWVMStatement('PUSHI', 0))
                ret.append(EWVMStatement('CHARAT'))

            assert isinstance(argument[0], VariableUsage)
            ret.extend(__generate_variable_usage_assembly(argument[0], label_generator, True))

    elif name == 'length':
        ret.extend(__generate_expression_assembly(call.arguments[0], label_generator))
        ret.append(EWVMStatement('STRLEN'))

    return ret

def __generate_callable_call_assembly(call: CallableCall,
                                      label_generator: LabelGenerator) -> EWVMProgram:

    if call.callable.name.lower() in SymbolTable('', None).scopes[0]:
        return __generate_builtin_callable_assembly(call, label_generator)
    else:
        ret = []

        if call.callable.return_variable is not None:
            ret.extend(__generate_variable_creation_assembly(
                call.callable.return_variable.variable_type,
                cast(LabelGenerator, None), # This should not be used
                0
            ))

        for argument in call.arguments:
            ret.extend(__generate_expression_assembly(argument, label_generator))

        ret.append(EWVMStatement('PUSHA', Label.callable(call.callable.name)))
        ret.append(EWVMStatement('CALL'))

        total_pops = len(call.callable.body.variables) + len(call.arguments)
        if total_pops > 0:
            ret.append(EWVMStatement('POP', total_pops))

        return ret

def __generate_expression_assembly(expression: Expression,
                                   label_generator: LabelGenerator) -> EWVMProgram:

    ret: EWVMProgram = []

    if isinstance(expression[0], get_args(ConstantValue)):
        return [__generate_constant_assembly(expression[0])]
    elif isinstance(expression[0], VariableUsage):
        return __generate_variable_usage_assembly(expression[0], label_generator, False)
    elif isinstance(expression[0], CallableCall):
        return __generate_callable_call_assembly(expression[0], label_generator)
    elif isinstance(expression[0], UnaryOperation):
        if expression[0].operator == '-':
            if expression[0].sub[1] == BuiltInType.REAL:
                ret.append(EWVMStatement('PUSHF', 0.0))
            else:
                ret.append(EWVMStatement('PUSHI', 0))

            ret.extend(__generate_expression_assembly(expression[0].sub, label_generator))

            instruction = 'FSUB' if expression[0].sub[1] == BuiltInType.REAL else 'SUB'
            ret.append(EWVMStatement(instruction))
        elif expression[0].operator == 'not':
            ret.extend(__generate_expression_assembly(expression[0].sub, label_generator))
            ret.append(EWVMStatement('NOT'))

        return ret
    elif isinstance(expression[0], BinaryOperation):
        ret.extend(__generate_expression_assembly(expression[0].left, label_generator))
        if expression[0].left[1] == BuiltInType.INTEGER and expression[1] == BuiltInType.REAL:
            ret.append(EWVMStatement('ITOF'))

        ret.extend(__generate_expression_assembly(expression[0].right, label_generator))
        if expression[0].right[1] == BuiltInType.INTEGER and expression[1] == BuiltInType.REAL:
            ret.append(EWVMStatement('ITOF'))

        instruction = {
            '+': 'FADD' if expression[1] == BuiltInType.REAL else 'ADD',
            '-': 'FSUB' if expression[1] == BuiltInType.REAL else 'SUB',
            '*': 'FMUL' if expression[1] == BuiltInType.REAL else 'MUL',
            '/': 'FDIV',
            'div': 'DIV',
            'mod': 'MOD',
            'AND': 'AND',
            'OR': 'OR',
            '=': 'EQUAL',
            '<>': 'EQUAL',
            '<': 'FINF' if expression[1] == BuiltInType.REAL else 'INF',
            '>': 'FSUP' if expression[1] == BuiltInType.REAL else 'SUP',
            '<=': 'FINFEQ' if expression[1] == BuiltInType.REAL else 'INFEQ',
            '>=': 'FSUPEQ' if expression[1] == BuiltInType.REAL else 'SUPEQ'
        }[expression[0].operator]

        ret.append(EWVMStatement(instruction))
        if expression[0].operator == '<>':
            ret.append(EWVMStatement('NOT'))

        return ret
    else:
        raise EWVMError()

def __generate_statement_assembly(statement: Statement,
                                  label_generator: LabelGenerator,
                                  call: None | CallableDefinition = None) -> EWVMProgram:
    # Statement label
    ret: EWVMProgram = []
    if statement[1] is not None:
        ret.append(Label.user(call, statement[1].name))

    # Assignment
    if isinstance(statement[0], AssignStatement):
        ret.append(Comment(f'{statement[0].left.variable.name} := ...'))
        ret.extend(__generate_expression_assembly(statement[0].right, label_generator))
        ret.extend(__generate_variable_usage_assembly(statement[0].left, label_generator, True))

    # GOTO
    elif isinstance(statement[0], GotoStatement):
        ret.append(Comment(f'GOTO {statement[0].label.name}'))
        ret.append(EWVMStatement('JUMP', Label.user(call, statement[0].label.name)))

    # Procedure call
    elif isinstance(statement[0], CallableCall):
        ret.append(Comment(f'{statement[0].callable.name}()'))
        ret.extend(__generate_callable_call_assembly(statement[0], label_generator))

    # BeginEndStatement
    elif isinstance(statement[0], list):
        for s in statement[0]:
            ret.extend(__generate_statement_assembly(s, label_generator, call))

    return ret

def __generate_block_assembly(block: Block,
                              call: None | CallableDefinition = None) -> EWVMProgram:
    ret: EWVMProgram = []

    # Block start
    if call is None:
        ret.append(EWVMStatement('START'))
    else:
        ret.append(Label.callable(call.name))

    label_generator = LabelGenerator(call)

    # Variables
    if call is not None:
        assert call.parameters is not None

        return_variables = [call.return_variable] if call.return_variable else []
        pre_variables = list(chain(return_variables, call.parameters))
        for i, variable in enumerate(pre_variables):
            variable.scope_offset = i - len(pre_variables)

    for i, variable in enumerate(block.variables):
        variable.scope_offset = i

        ret.append(Comment(f'{variable.name} initialization'))
        ret.extend(__generate_variable_creation_assembly(
            variable.variable_type,
            label_generator,
            variable.scope_offset
        ))

    # Statements
    ret.extend(__generate_statement_assembly((block.body, None), label_generator, call))

    # Block end
    if call is None:
        ret.append(EWVMStatement('STOP'))
    else:
        assert call.parameters is not None
        ret.append(EWVMStatement('RETURN'))

    return ret

def generate_program_assembly(program: Program) -> EWVMProgram:
    ret = __generate_block_assembly(program.block)

    # Callables can only occur at the top level
    for call in program.block.callables:
        ret.extend(__generate_block_assembly(call.body, call))

    return ret
