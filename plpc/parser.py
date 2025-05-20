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

from typing import Any, Callable

import ply.lex
import ply.yacc

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_error
from .lexer import create_lexer
from .symboltable import SymbolTable, SymbolTableError
from .typechecker import TypeChecker, TypeCheckerError

class ParserError(ValueError):
    pass

class _Parser:
    def __init__(self, file_path: str, start_production: str):
        self.file_path = file_path
        self.has_errors = False

        self.lexer = create_lexer(file_path)
        self.tokens = list(self.lexer.lextokens)
        self.parser = ply.yacc.yacc(module=self,
                                    start=start_production,
                                    debug=False,
                                    write_tables=False)

        self.symbols = SymbolTable(file_path, self.lexer)
        self.type_checker = TypeChecker(file_path, self.lexer)

    # 6.2 - Blocks, scopes and activations

    def p_program(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program : PROGRAM ID program-arguments ';' block '.'
        '''
        p[0] = Program(p[2], p[5])

    def p_program_arguments_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program-arguments :
        '''

    def p_program_arguments_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program-arguments : '(' ')'
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Invalid program arguments: at least one argument required',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1)

    def p_program_arguments_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program-arguments : '(' identifier-list ')'
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Program arguments are not supported. Ignoring them...',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1,
                    True)

    def p_identitifier_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        identifier-list : ID
        '''
        p[0] = [(p[1], p.lexspan(1)[0])]

    def p_identitifier_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        identifier-list : identifier-list ',' ID
        '''
        p[1].append((p[3], p.lexspan(3)[0]))
        p[0] = p[1]

    def p_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        block : label-block \
                constant-block \
                type-block \
                variable-block \
                callable-block \
                begin-end-statement \
        '''
        p[0] = Block(p[1], p[2], p[3], p[4], p[5], p[6])

        for label in p[2]:
            if label.used and label.statement is None:
                print_error(self.file_path,
                            self.lexer.lexdata,
                            f'Label \'{label.name}\' was used but not assigned to any statement',
                            self.lexer.lineno,
                            p.lexspan(2)[0],
                            p.lexspan(2)[1] - p.lexspan(2)[0] + 1)

    def p_label_block_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-block :
        '''
        p[0] = []

    def p_label_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-block : LABEL
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'At least one constant definition is required in a label block',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('LABEL'))

        self.has_errors = True
        p[0] = []

    def p_label_block_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-block : LABEL label-list ';'
        '''
        p[0] = p[2]

    def p_label_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-list : INTEGER
        '''

        try:
            label = LabelDefinition(p[1].value, None)
            self.symbols.add(label,
                             (p.lexspan(1)[0], p.lexspan(1)[0] + len(str(p[1].value)) - 1))

            p[0] = [label]
        except SymbolTableError:
            self.has_errors = True

    def p_label_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-list : label-list ',' INTEGER
        '''

        try:
            label = LabelDefinition(p[3].value, None)
            self.symbols.add(label,
                             (p.lexspan(3)[0], p.lexspan(3)[0] + len(str(p[3].value)) - 1))

            p[1].append(label)
            p[0] = p[1]
        except SymbolTableError:
            self.has_errors = True

    # 6.3 - Constant definitions

    def p_constant_block_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-block :
        '''
        p[0] = []

    def p_constant_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-block : CONST
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'At least one constant definition is required in a constant block',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('CONST'))

        self.has_errors = True
        p[0] = []

    def p_constant_block_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-block : CONST constant-definition-list
        '''
        p[0] = p[2]

    def p_constant_definition_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-definition-list : constant-definition
        '''
        p[0] = [p[1]]

    def p_constant_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-definition-list : constant-definition-list constant-definition
        '''
        p[1].append(p[2])
        p[0] = p[1]

    def p_constant_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-definition : ID '=' constant ';'
        '''
        p[0] = ConstantDefinition(p[1], p[3])

        try:
            self.symbols.add(p[0], (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1))
        except SymbolTableError:
            self.has_errors = True

    def p_constant(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant : unsigned-constant
                 | signed-constant
        '''
        p[0] = p[1]

    def p_constant_expression(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant : expression
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Full expressions are not allowed in constants',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
        self.has_errors = True

    def p_unsigned_constant_id(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unsigned-constant : ID
        '''

        try:
            query_result, _ = \
                self.symbols.query_constant(p[1],
                                            (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                                            True)

            assert query_result is not None
            p[0] = query_result.value
        except SymbolTableError:
            self.has_errors = True

    def p_unsigned_constant_literal(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unsigned-constant : unsigned-constant-literal
        '''
        p[0] = p[1]

    def p_unsigned_constant_literal_literal(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unsigned-constant-literal : FLOAT
                                  | INTEGER
                                  | STRING
        '''
        p[0] = p[1].value

    def p_signed_constant_sign(self, p: ply.yacc.YaccProduction) -> None:
        '''
        signed-constant : '+' unsigned-constant
                        | '-' unsigned-constant
        '''

        try:
            constant_type = self.type_checker.get_constant_type(p[2])
            _ = self.type_checker.get_unary_operation_type(
                UnaryOperation(p[1], (p[2], constant_type)),
                (p.lexspan(0)[0], p.lexspan(0)[0])
            )

            multiplier = 1 if p[1] == '+' else -1
            p[0] = multiplier * p[2]
        except TypeCheckerError:
            self.has_errors = True

    # 6.4 - Type definitions

    def p_type_block_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-block :
        '''
        p[0] = []

    def p_type_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-block : TYPE
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'At least one type definition is required in a type block',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('TYPE'))

        self.has_errors = True
        p[0] = []

    def p_type_block_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-block : TYPE type-definition-list
        '''
        p[0] = p[2]

    def p_type_definition_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-definition-list : type-definition
        '''
        p[0] = [p[1]]

    def p_type_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-definition-list : type-definition-list type-definition
        '''
        p[1].append(p[2])
        p[0] = p[1]

    def p_type_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-definition : ID '=' type ';'
        '''

        type_definition = TypeDefinition(p[1], p[3])
        p[0] = type_definition

        if isinstance(p[3], list):
            # Enumerated type
            for constant in p[3]:
                constant.value.constant_type = type_definition

        try:
            self.symbols.add(p[0], (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1))
        except SymbolTableError:
            self.has_errors = True

    def p_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type : type-id
             | pointer-type
             | enumerated-type
             | structured-type
        '''
        p[0] = p[1]

    def p_type_range(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type : range-type
        '''

        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Range type being interpreted as the type of its components',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1,
                    True)
        p[0] = p[1].subtype

    def p_type_id(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-id : ID
        '''

        try:
            query_result, _ = \
                self.symbols.query_type(p[1],
                                        (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                                        True)

            assert query_result is not None
            p[0] = query_result.value
        except SymbolTableError:
            self.has_errors = True

    def p_pointer_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        pointer-type : '^' type-id
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Pointer types are not supported',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('^'))
        self.has_errors = True

    def p_enumerated_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        enumerated-type : '(' identifier-list ')'
        '''

        ret: list[ConstantDefinition] = []
        for i, (identifier, start) in enumerate(p[2]):
            try:
                value = EnumeratedTypeConstantValue(identifier, i, None) # type is set later
                constant = ConstantDefinition(identifier, value)
                self.symbols.add(constant, (start, start + len(identifier) - 1))

                ret.append(constant)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_range_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        range-type : constant RANGE constant
        '''

        # NOTE: error spans are somewhat off, but it seems to be a yacc bug

        try:
            type1 = self.type_checker.get_constant_type(p[1])
            type2 = self.type_checker.get_constant_type(p[3])
        except TypeCheckerError:
            self.has_errors = True
            return

        if type1 != type2:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Types of elements in range type are different',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
            self.has_errors = True
            return

        try:
            value1 = self.type_checker.get_constant_ordinal_value(p[1])
            value2 = self.type_checker.get_constant_ordinal_value(p[3])
        except TypeCheckerError:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Type of elements in range type is not ordinal',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
            self.has_errors = True
            return

        if value1 > value2:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Range\'s upper bound is lower than its lower bound',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
            self.has_errors = True
            return

        p[0] = RangeType(p[1], p[3], self.type_checker.get_constant_type(p[1]))

    def p_structured_type_unpacked(self, p: ply.yacc.YaccProduction) -> None:
        '''
        structured-type : unpacked-structured-type
        '''
        p[0] = p[1]

    def p_structured_type_packed(self, p: ply.yacc.YaccProduction) -> None:
        '''
        structured-type : PACKED unpacked-structured-type
        '''

        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Packed structured types are not supported. Ignoring this keyword ...',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('PACKED'),
                    True)

        p[0] = p[2]

    def p_unpacked_structured_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unpacked-structured-type : array-type
                                 | record-type
                                 | set-type
                                 | file-type
        '''
        p[0] = p[1]

    def p_array_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-type : ARRAY '[' array-dimensions ']' OF type
        '''
        if isinstance(p[6], ArrayType):
            p[3].extend(p[6].dimensions)
            p[0] = ArrayType(p[6].subtype, p[3])
        else:
            p[0] = ArrayType(p[6], p[3])

    def p_array_dimensions_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-dimensions : range-type
        '''
        p[0] = [p[1]]

    def p_array_dimensions_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-dimensions : array-dimensions ',' range-type
        '''
        p[1].append(p[3])
        p[0] = p[1]

    def p_record_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        record-type : RECORD
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Record types are not supported',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('RECORD'))
        self.has_errors = True
        raise SyntaxError()

    def p_set_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        set-type : SET OF type
        '''

        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Set types are not supported',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('SET'))
        self.has_errors = True

    def p_file_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        file-type : FILE OF type
        '''

        print_error(self.file_path,
                    self.lexer.lexdata,
                    'File types are not supported',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('FILE'))
        self.has_errors = True

    # 6.5 - Declarations and denotations of variables

    def p_variable_block_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-block :
        '''
        p[0] = []

    def p_variable_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-block : VAR
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'At least one variable definition is required in a variable block',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('VAR'))

        self.has_errors = True
        p[0] = []

    def p_variable_block_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-block : VAR variable-definition-list
        '''
        p[0] = p[2]

    def p_variable_definition_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-definition-list : variable-definition
        '''
        p[0] = [p[1]]

    def p_variable_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-definition-list : variable-definition-list variable-definition
        '''
        p[1].append(p[2])
        p[0] = p[1]

    def p_variable_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-definition : identifier-list ':' type ';'
        '''

        ret: list[VariableDefinition] = []
        for identifier, start in p[1]:
            try:
                variable = VariableDefinition(identifier, p[3])
                self.symbols.add(variable, (start, start + len(identifier) - 1))
                ret.append(variable)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_variable_usage(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-usage : ID variable-index-list
        '''
        try:
            definition, _ = self.symbols.query_variable(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1])),
                True
            )
            assert definition is not None

            current_type = definition.variable_type
            for _, index_type in p[2]:
                try:
                    current_type = self.type_checker.type_after_indexation(
                        current_type,
                        index_type,
                        p.lexspan(0)
                    )
                except TypeCheckerError:
                    self.has_errors = True
                    break

            p[0] = VariableUsage(definition, current_type, p[2])
        except SymbolTableError:
            self.has_errors = True

    def p_variable_index_list_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-index-list :
        '''
        p[0] = []

    def p_variable_index_list_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-index-list : variable-indices
        '''
        p[0] = p[1]

    def p_variable_indices_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-indices : variable-index
        '''
        p[0] = p[1]

    def p_variable_indices_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-indices : variable-indices variable-index
        '''
        p[1].extend(p[2])
        p[0] = p[1]

    def p_variable_index(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-index : '[' expression-list ']'
        '''
        p[0] = p[2]

    # 6.6. Procedure and function delarations

    def p_callable_block_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-block :
        '''
        p[0] = []

    def p_callable_block_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-block : callable-list
        '''

        if len(self.symbols.scopes) > 1:
            first_token_length = \
                len('PROCEDURE') if p[1][0].return_type == BuiltInType.VOID else len('FUNCTION')

            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Nested procedures / functions are not supported',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        first_token_length)
            self.has_errors = True

        p[0] = p[1]

    def p_callable_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-list : callable-definition
        '''
        p[0] = [p[1]]

    def p_callable_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-list : callable-block ';' callable-definition
        '''
        p[1].append(p[3])
        p[0] = p[1]

    def p_callable_definition_procedure(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-definition : procedure-heading ';' block
        '''

        call = CallableDefinition(
            p[1][0],
            p[1][1],
            BuiltInType.VOID,
            p[3]
        )
        self.symbols.unstack_top_scope()

        try:
            self.symbols.add(call, (p[1][2], p[1][2] + len(p[1][0]) - 1))
            p[0] = call
        except SymbolTableError:
            self.has_errors = True

    def p_callable_definition_function(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-definition : function-heading ';' block
        '''

        call = CallableDefinition(
            p[1][0],
            p[1][1],
            p[1][2],
            p[3]
        )
        self.symbols.unstack_top_scope()

        try:
            self.symbols.add(call, (p[1][3], p[1][3] + len(p[1][0]) - 1))
            p[0] = call
        except SymbolTableError:
            self.has_errors = True

    def p_new_scope_procedure(self, p: ply.yacc.YaccProduction) -> None:
        '''
        procedure-heading : PROCEDURE ID new-scope parameter-list
        '''
        p[0] = (p[2], p[4], p.lexspan(2)[0])

    def p_function_heading(self, p: ply.yacc.YaccProduction) -> None:
        '''
        function-heading : FUNCTION ID new-scope parameter-list ':' type-id
        '''
        self.symbols.add(VariableDefinition(p[2], p[6]), p.lexspan(2))
        p[0] = (p[2], p[4], p[6], p.lexspan(2)[0])

    def p_new_scope(self, _: ply.yacc.YaccProduction) -> None:
        '''
        new-scope :
        '''
        self.symbols.new_scope()

    def p_parameter_list_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list :
        '''
        p[0] = []

    def p_parameter_list_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list : '(' parameter-list-non-empty ')'
        '''
        p[0] = p[2]

    def p_parameter_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list-non-empty : parameter
        '''
        p[0] = p[1]

    def p_parameter_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list-non-empty : parameter-list-non-empty ';' parameter
        '''
        p[1].extend(p[3])
        p[0] = p[1]

    def p_parameter(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter : identifier-list ':' type-id
        '''

        ret: list[VariableDefinition] = []
        for identifier, start in p[1]:
            try:
                variable = VariableDefinition(identifier, p[3])
                self.symbols.add(variable, (start, start + len(identifier) - 1))
                ret.append(variable)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_callable_call(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-call : ID callable-arguments
        '''
        try:
            definition, _ = self.symbols.query_callable(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                True
            )
            assert definition is not None

            if definition.parameters is not None:
                if len(definition.parameters) != len(p[2]):
                    print_error(self.file_path,
                                self.lexer.lexdata,
                                'Wrong number of arguments',
                                self.lexer.lineno,
                                p.lexspan(2)[0],
                                p.lexspan(2)[0] - p.lexspan(2)[1] + 1)
                    self.has_errors = True
                    return

                for i, (left, right) in enumerate(zip(definition.parameters, p[2])):
                    if right and not self.type_checker.can_assign(left.variable_type, right[1]):
                        ordinal = {
                            '1': 'st',
                            '2': 'nd'
                        }.get(str(i + 1)[-1], 'th')

                        print_error(self.file_path,
                                    self.lexer.lexdata,
                                    f'Type mismatch in {i + 1}{ordinal} argument',
                                    self.lexer.lineno,
                                    p.lexspan(1)[0],
                                    len(p[1]))
                        self.has_errors = True

            p[0] = CallableCall(definition, p[2])
        except SymbolTableError:
            self.has_errors = True

    def p_callable_arguments_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-arguments :
        '''
        p[0] = []

    def p_callable_arguments_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-arguments : '(' expression-list ')'
        '''
        p[0] = p[2]

    def p_callable_arguments_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-arguments : '(' ')'
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'To pass no arguments, remove the parentheses',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(1)[1])

    # 6.7 - Expressions

    def p_expression_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression : non-relational-expression
        '''
        p[0] = p[1]

    def p_expression_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression : non-relational-expression relational-operator non-relational-expression
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_relational_operator(self, p: ply.yacc.YaccProduction) -> None:
        '''
        relational-operator : '='
                            | DIFFERENT
                            | '<'
                            | '>'
                            | LE
                            | GE
                            | IN
        '''
        p[0] = p[1].lower()

    def p_non_relational_expression_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        non-relational-expression : first-term
        '''
        p[0] = p[1]

    def p_non_relational_expression_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        non-relational-expression : non-relational-expression adding-operator term
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_adding_operator(self, p: ply.yacc.YaccProduction) -> None:
        '''
        adding-operator : '+'
                        | '-'
                        | OR
        '''
        p[0] = p[1].lower()

    def p_first_term_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-term : first-factor
        '''
        p[0] = p[1]

    def p_first_term_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-term : first-term multiplying-operator factor
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_first_factor_signed(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-factor : '+' factor
                     | '-' factor
        '''

        try:
            operation = UnaryOperation(p[1].lower(), p[2])
            expression_type = self.type_checker.get_unary_operation_type(operation, p.lexspan(1))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_first_factor_unsigned(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-factor : factor
        '''
        p[0] = p[1]

    def p_term_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        term : factor
        '''
        p[0] = p[1]

    def p_term_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        term : term multiplying-operator factor
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_multiplying_operator(self, p: ply.yacc.YaccProduction) -> None:
        '''
        multiplying-operator : '*'
                             | '/'
                             | DIV
                             | MOD
                             | AND
        '''
        p[0] = p[1].lower()

    def p_factor_parentheses(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : '(' expression ')'
        '''
        p[0] = p[2]

    def p_factor_nil(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : NIL
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Pointer types are not supported',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    len('NIL'))
        self.has_errors = True

    def p_factor_not(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : NOT factor
        '''
        try:
            operation = UnaryOperation(p[1].lower(), p[2])
            expression_type = self.type_checker.get_unary_operation_type(operation, p.lexspan(0))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_factor_constant_literal(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : unsigned-constant-literal
        '''
        p[0] = (p[1], self.type_checker.get_constant_type(p[1]))

    def p_factor_as_id_indexed(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : factor-id variable-index-list
               | factor-id callable-arguments empty
        '''

        if not isinstance(p[1], tuple):
            return

        if isinstance(p[1][0], VariableUsage) and len(p) == 3:
            if len(p[2]) > 0:
                p[1] = p[1][0].variable.name
                self.p_variable_usage(p)
                p[0] = (p[0], p[0].type)
            else:
                p[0] = p[1]
        elif isinstance(p[1][0], CallableCall):
            p[1] = p[1][0].callable.name
            self.p_callable_call(p)

            if p[0] is not None:
                p[0] = (p[0], p[0].callable.return_type)
        else:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Indexing / calling object that\'s not a variable / function',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
            self.has_errors = True

    def p_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        empty :
        '''
        # A simple trick not to rework the whole grammar

    def p_factor_id(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor-id : ID
        '''
        try:
            obj, _ = self.symbols.query(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1])),
                True
            )
            assert obj is not None

            if isinstance(obj, ConstantDefinition):
                p[0] = (obj, self.type_checker.get_constant_type(obj.value))
            elif isinstance(obj, VariableDefinition):
                p[0] = (VariableUsage(obj, obj.variable_type, []), obj.variable_type)
            elif isinstance(obj, CallableDefinition):
                if obj.return_type == BuiltInType.VOID:
                    print_error(self.file_path,
                                self.lexer.lexdata,
                                'This is a procedure and not a function',
                                self.lexer.lineno,
                                p.lexspan(0)[0],
                                p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
                    self.has_errors = True
                    return

                p[0] = (CallableCall(obj, []), obj.return_type)

        except SymbolTableError:
            self.has_errors = True

    def p_expression_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression-list : expression
        '''
        p[0] = [p[1]]

    def p_expression_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression-list : expression-list ',' expression
        '''
        p[1].append(p[3])
        p[0] = p[1]

    # 6.8 - Statements

    def p_begin_end_statement(self, p: ply.yacc.YaccProduction) -> None:
        '''
        begin-end-statement : BEGIN statement-list END
        '''
        p[0] = p[2]

    def p_begin_end_statement_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        begin-end-statement : BEGIN END
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Empty compound statements are not allowed in standard Pascal',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
        self.has_errors = True

        p[0] = []

    def p_statement_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement-list : statement
        '''
        if p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_statement_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement-list : statement-list ';' statement
        '''
        if p[3] is not None:
            p[1].append(p[3])
        p[0] = p[1]

    def p_statement_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement : unlabeled-statement
        '''
        p[0] = p[1]

    def p_statement_labeled(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement : INTEGER ':' unlabeled-statement
        '''
        try:
            label = self.symbols.query_label(
                p[1].value,
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1].string_value) - 1),
                True
            )

            if label.statement is None:
                label.statement = p[3]
            else:
                print_error(self.file_path,
                            self.lexer.lexdata,
                            'Label already assigned to a statement',
                            self.lexer.lineno,
                            p.lexspan(1)[0],
                            len(p[1].string_value))
                self.has_errors = True
        except SymbolTableError:
            self.has_errors = True

        p[0] = p[3]

    def p_unlabeled_statement_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement :
        '''

    def p_unlabeled_statement_assign(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : variable-usage ASSIGN expression
        '''

        if p[1] is not None and \
            p[3] is not None and \
            not self.type_checker.can_assign(p[1].type, p[3][1]):

            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Assignment is impossible due to type mismatch',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
            self.has_errors = True

        p[0] = AssignStatement(p[1], p[3])

    def p_unlabeled_statement_goto(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : GOTO INTEGER
        '''
        try:
            label = self.symbols.query_label(
                p[2].value,
                (p.lexspan(2)[0], p.lexspan(2)[0] + len(p[2].string_value) - 1),
                True
            )
            label.used = True
            p[0] = GotoStatement(label)
        except SymbolTableError:
            self.has_errors = True

    def p_unlabeled_statement_call(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : callable-call
        '''
        if p[1] is not None and p[1].callable.return_type != BuiltInType.VOID:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Calling a function, and not a procedure',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        len(p[1].callable.name))
            self.has_errors = True
        else:
            p[0] = p[1]

    def p_unlabeled_statement_begin_end(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : begin-end-statement
        '''
        p[0] = p[1]

    def p_unlabeled_statement_if(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : IF expression THEN statement if-statement-else
        '''

        if p[2] is not None and p[2][1] != BuiltInType.BOOLEAN:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Expression in if-statement is not boolean',
                        self.lexer.lineno,
                        p.lexspan(2)[0],
                        p.lexspan(2)[1] - p.lexspan(2)[0] + 1)
            self.has_errors = True

        p[0] = IfStatement(p[2], p[4], p[5])

    def p_if_statement_else_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        if-statement-else :
        '''
        p[0] = []

    def p_if_statement_else_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        if-statement-else : ELSE statement
        '''
        p[0] = p[2]

    def p_if_statement_else_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        if-statement-else : ';' ELSE statement
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Invalid syntax. Maybe you have an extra semicolon?',
                    self.lexer.lineno,
                    p.lexspan(1)[0],
                    len(';'))
        self.has_errors = True

    # TODO - implement case statement

    def p_unlabeled_statement_repeat(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : REPEAT statement-list UNTIL expression
        '''

        if p[4] is not None and p[4][1] != BuiltInType.BOOLEAN:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Expression in repeat-until loop is not boolean',
                        self.lexer.lineno,
                        p.lexspan(4)[0],
                        p.lexspan(4)[1] - p.lexspan(4)[0] + 1)
            self.has_errors = True

        p[0] = RepeatStatement(p[4], p[2])

    def p_unlabeled_statement_while(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : WHILE expression DO statement
        '''

        if p[2] is not None and p[2][1] != BuiltInType.BOOLEAN:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Expression in while loop is not boolean',
                        self.lexer.lineno,
                        p.lexspan(2)[0],
                        p.lexspan(2)[1] - p.lexspan(2)[0] + 1)
            self.has_errors = True

        p[0] = WhileStatement(p[2], p[4])

    def p_unlabeled_statement_for(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : FOR ID ASSIGN expression TO     expression DO statement
                            | FOR ID ASSIGN expression DOWNTO expression DO statement
        '''

        try:
            definition, top_scope = self.symbols.query_variable(
                p[2],
                (p.lexspan(2)[0], p.lexspan(2)[0] + len(p[2]) - 1),
                True
            )
            assert definition is not None

            if not top_scope:
                print_error(self.file_path,
                            self.lexer.lexdata,
                            'For-loop control variable is not in the top-most scope',
                            self.lexer.lineno,
                            p.lexspan(2)[0],
                            p.lexspan(2)[1] - p.lexspan(2)[0] + 1)
                self.has_errors = True

            if definition.variable_type not in \
                [BuiltInType.BOOLEAN, BuiltInType.INTEGER, BuiltInType.CHAR] and \
                not isinstance(definition.variable_type, list):

                print_error(self.file_path,
                            self.lexer.lexdata,
                            'For loop control variable is not ordinal',
                            self.lexer.lineno,
                            p.lexspan(2)[0],
                            p.lexspan(2)[1] - p.lexspan(2)[0] + 1)
                self.has_errors = True

            if p[4] is not None and \
                not self.type_checker.can_assign(definition.variable_type, p[4][1]):

                print_error(self.file_path,
                            self.lexer.lexdata,
                            'Type mismatch between expression and loop control variable',
                            self.lexer.lineno,
                            p.lexspan(4)[0],
                            p.lexspan(4)[1] - p.lexspan(4)[0] + 1)
                self.has_errors = True

            if p[6] is not None and \
                not self.type_checker.can_assign(definition.variable_type, p[6][1]):

                print_error(self.file_path,
                            self.lexer.lexdata,
                            'Type mismatch between expression and loop control variable',
                            self.lexer.lineno,
                            p.lexspan(6)[0],
                            p.lexspan(6)[1] - p.lexspan(6)[0] + 1)
                self.has_errors = True

            p[0] = ForStatement(definition, p[4], p[6], p[5].lower(), p[8])
        except SymbolTableError:
            self.has_errors = True

    def p_unlabeled_statement_with(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : WITH variable-list DO statement
        '''
        print_error(self.file_path,
                    self.lexer.lexdata,
                    'WITH statements are not supported',
                    self.lexer.lineno,
                    p.lexspan(1)[0],
                    len('WITH'))
        self.has_errors = True

    def p_variable_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-list : variable-usage
        '''

    def p_variable_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-list : variable-list ',' variable-usage
        '''

    def p_error(self, t: ply.lex.LexToken) -> None:
        if t is None:
            if self.lexer.lexdata.endswith('\n'):
                eof_position = len(self.lexer.lexdata) - 1
                line_number = self.lexer.lineno - 1
            else:
                eof_position = len(self.lexer.lexdata)
                line_number = self.lexer.lineno

            print_error(self.file_path,
                        self.lexer.lexdata,
                        'Expecting input before end-of-file',
                        line_number,
                        eof_position,
                        1)
            string_value = ''
        else:
            string_value = t.value if isinstance(t.value, str) else t.value.string_value
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Unexpected token: {string_value}',
                        self.lexer.lineno,
                        t.lexpos,
                        len(string_value))

            # Read ahead looking for a closing 'END'
            while True:
                tok = self.parser.token()
                if not tok or tok.type == 'END':
                    self.parser.errok()
                    break

        self.has_errors = True

def create_parser(file_path: str,
                  start_production: str = 'program') -> ply.yacc.LRParser:

    def parse_wrapper(*args: str, **kwargs: Any) -> Callable[..., ply.yacc.LRParser]:
        ast = old_parse_fn(*args, tracking=True, **kwargs)
        if parser.has_errors:
            raise ParserError()

        return ast

    parser = _Parser(file_path, start_production)
    old_parse_fn = parser.parser.parse
    parser.parser.parse = parse_wrapper
    return parser.parser
