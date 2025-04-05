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

    def p_program_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''program-definition : INTEGER'''
        p[0] = p[1].value

    def p_error(self, t: ply.lex.LexToken) -> None:
        string_value = t.value if isinstance(t.value, str) else t.value.string_value

        print_error(self.file_path,
                    self.lexer.lexdata,
                    f'Unexpected token: {string_value}',
                    t.lexer.lineno,
                    t.lexpos,
                    len(string_value))

        self.has_errors = True

def create_parser(file_path: str,
                  start_production: str = 'program-definition') -> ply.yacc.LRParser:

    def parse_wrapper(*args: str, **kwargs: Any) -> Callable[..., ply.yacc.LRParser]:
        ast = old_parse_fn(*args, **kwargs)
        if parser.has_errors:
            raise ParserError()

        return ast

    parser = _Parser(file_path, start_production)
    old_parse_fn = parser.parser.parse
    parser.parser.parse = parse_wrapper
    return parser.parser
