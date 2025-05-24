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

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_unlocalized_error
from .typechecker import TypeChecker

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
    elif isinstance(constant, str):
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
        return [__generate_constant_assembly('0')]
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

        return ret
    else:
        raise EWVMError()

def __generate_statement_assembly(statement: Statement,
                                  call: None | CallableDefinition = None) -> EWVMProgram:
    # Statement label
    ret: EWVMProgram = []
    if statement[1] is not None:
        ret.append(Label.user(call, statement[1].name))

    # Statement content
    if isinstance(statement[0], list): # BeginEndStatement
        for s in statement[0]:
            ret.extend(__generate_statement_assembly(s, call))
    elif isinstance(statement[0], GotoStatement):
        ret.append(Comment(f'GOTO {statement[0].label.name}'))
        ret.append(EWVMStatement('JUMP', Label.user(call, statement[0].label.name)))

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
    ret.extend(__generate_statement_assembly((block.body, None), call))

    # Block end
    if call is None:
        ret.append(EWVMStatement('STOP'))
    else:
        assert call.parameters is not None

        total_pops = len(block.variables) + len(call.parameters)
        if call.return_variable is not None:
            total_pops -= 1

        if total_pops > 0:
            ret.append(EWVMStatement('POP', total_pops))
        ret.append(EWVMStatement('RETURN'))

    return ret

def generate_program_assembly(program: Program) -> EWVMProgram:
    ret = __generate_block_assembly(program.block)

    # Callables can only occur at the top level
    for call in program.block.callables:
        ret.extend(__generate_block_assembly(call.body, call))

    return ret
