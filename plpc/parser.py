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
        p[0] = [p[1]]

    def p_identitifier_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        identifier-list : identifier-list ',' ID
        '''
        p[1].append(p[3])
        p[0] = p[1]

    # pylint: disable=line-too-long
    def p_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        block :
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
