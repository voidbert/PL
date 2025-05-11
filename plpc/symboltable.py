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

from .ast import ConstantDefinition
from .error import print_error

class SymbolTableError(ValueError):
    pass


SymbolValue = ConstantDefinition

QueryConstantResult = None | ConstantDefinition
QueryResult = None | ConstantDefinition

class SymbolTable:
    def __init__(self, file_path: str, lexer: ply.lex.Lexer) -> None:
        self.file_path = file_path
        self.lexer = lexer

        self.scopes: list[dict[str, SymbolValue]] = []

    def stack_new_scope(self) -> None:
        self.scopes.append({})

    def unstack_top_scope(self) -> None:
        self.scopes.pop()

    def query(self,
              identifier: str,
              lexspan: tuple[int, int] = (0, 0),
              error: bool = False,
              target_object_name: str = 'Object') -> tuple[QueryResult, bool]:

        identifier_lower = identifier.lower()

        for i, scope in enumerate(reversed(self.scopes)):
            scope_result = scope.get(identifier_lower)
            if scope_result is not None:
                return scope_result, i == 0

        if error:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'{target_object_name} {identifier} not found',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return None, False

    def query_constant(self,
                       identifier: str,
                       lexspan: tuple[int, int] = (0, 0),
                       error: bool = False) -> tuple[QueryConstantResult, bool]:

        query_result, top_scope = self.query(identifier, lexspan, error, 'Constant')

        if not isinstance(query_result, ConstantDefinition):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Object with name {identifier} is not a constant',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return query_result, top_scope

    def add_constant(self, constant: ConstantDefinition, lexspan: tuple[int, int]) -> None:
        query_result, top_scope = self.query(constant.name)

        if query_result is not None:
            if top_scope:
                print_error(self.file_path,
                            self.lexer.lexdata,
                            f'Object with name {constant.name} already exists at this level',
                            self.lexer.lineno,
                            lexspan[0],
                            lexspan[1] - lexspan[0] + 1)

                raise SymbolTableError()
            else:
                # TODO - test this when procedures and functions are implemented
                print_error(self.file_path,
                            self.lexer.lexdata,
                            f'Shadowing object with name {constant.name}',
                            self.lexer.lineno,
                            lexspan[0],
                            lexspan[1] - lexspan[0] + 1,
                            True)
        else:
            self.scopes[-1][constant.name] = constant
