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
from .typechecker import TypeCheckerError, get_constant_type, get_constant_ordinal_value

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

    def p_program(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program : PROGRAM ID program-arguments ';' block
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
        block : stack-new-scope constant-block type-block variable-block
        '''
        self.symbols.unstack_top_scope()
        p[0] = Block(p[2], p[3], p[4])

    def p_stack_new_scope(self, _: ply.yacc.YaccProduction) -> None:
        '''
        stack-new-scope :
        '''
        self.symbols.stack_new_scope()

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

    # 6.3 - Constant definitions

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
        unsigned-constant : FLOAT
                          | INTEGER
                          | STRING
        '''
        p[0] = p[1].value

    def p_signed_constant_sign(self, p: ply.yacc.YaccProduction) -> None:
        '''
        signed-constant : '+' unsigned-constant
                        | '-' unsigned-constant
        '''

        if isinstance(p[2], str):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Type error: unary \'{p[1]}\' operator cannot be applied to a string',
                        self.lexer.lineno,
                        p.lexspan(0)[0],
                        1)
            self.has_errors = True
        else:
            multiplier = 1 if p[1] == '+' else -1
            p[0] = multiplier * p[2]

    # TODO - add error rules telling the user they can't assign an expression to a constant

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
             | range-type
             | structured-type
        '''
        p[0] = p[1]

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
        p[0] = PointerType(p[2])

    def p_enumerated_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        enumerated-type : '(' identifier-list ')'
        '''

        ret: list[ConstantDefinition] = []
        for i, (identifier, start) in enumerate(p[2]):
            try:
                value = EnumeratedTypeConstantValue(identifier, i, None) # type is set later
                constant = ConstantDefinition(identifier, value)
                self.symbols.add(constant, (start, start + len(identifier)))

                ret.append(constant)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_range_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        range-type : constant RANGE constant
        '''

        type1 = get_constant_type(p[1])
        type2 = get_constant_type(p[3])
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
            value1 = get_constant_ordinal_value(p[1])
            value2 = get_constant_ordinal_value(p[3])
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

        p[0] = RangeType(p[1], p[3])

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

    # TODO - implement records later
    def p_record_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        record-type :
        '''

    def p_set_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        set-type : SET OF type
        '''

        print_error(self.file_path,
                    self.lexer.lexdata,
                    'Set types are not supported',
                    self.lexer.lineno,
                    p.lexspan(0)[0],
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
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
                    p.lexspan(0)[1] - p.lexspan(0)[0] + 1)
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
                self.symbols.add(variable, (start, start + len(identifier)))
                ret.append(variable)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

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
