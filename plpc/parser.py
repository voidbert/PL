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

import ply.yacc
from .lexer import create_lexer, get_tokens

class ParserError(ValueError):
    pass

class _Parser:
    def __init__(self, file_path: str):
        self.lexer = create_lexer(file_path)
        self.tokens = get_tokens()

    def p_num(self, p: ply.yacc.YaccProduction) -> None:
        '''program-definition : INTEGER'''
        p[0] = p[1]

def create_parser(file_path: str) -> ply.yacc.LRParser:
    return ply.yacc.yacc(module=_Parser(file_path), debug=False, write_tables=False)
