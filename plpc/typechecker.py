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

import ply.lex

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_error

class TypeCheckerError(ValueError):
    pass

class TypeChecker:
    def __init__(self, file_path: str, lexer: ply.lex.Lexer) -> None:
        self.file_path = file_path
        self.lexer = lexer

    def get_constant_type(self, constant: ConstantValue) -> TypeValue:
        if isinstance(constant, bool):
            return BuiltInType.BOOLEAN
        elif isinstance(constant, int):
            return BuiltInType.INTEGER
        elif isinstance(constant, float):
            return BuiltInType.REAL
        elif isinstance(constant, str):
            return BuiltInType.CHAR if len(constant) == 1 else BuiltInType.STRING
        elif isinstance(constant, EnumeratedTypeConstantValue):
            assert constant.constant_type is not None
            return constant.constant_type.value
        else:
            # Should be unreachable
            raise TypeCheckerError()

    def get_constant_ordinal_value(self, constant: ConstantValue) -> int:
        if isinstance(constant, bool):
            return int(constant)
        elif isinstance(constant, int):
            return constant
        elif isinstance(constant, str) and len(constant) == 1:
            return ord(constant)
        elif isinstance(constant, EnumeratedTypeConstantValue):
            return constant.value
        else:
            raise TypeCheckerError()

    # 6.7.2.2. Arithmetic operators
    # 6.7.2.3. Boolean operators
    def get_unary_operation_type(self,
                                 operation: UnaryOperation,
                                 lexspan: tuple[int, int]) -> None | TypeValue:
        try:
            subtype = operation.sub[1]
        except TypeError:
            # AST has errors
            return None

        if operation.operator in ['+', '-'] and subtype in [BuiltInType.INTEGER, BuiltInType.REAL]:
            return subtype
        elif operation.operator == 'not' and subtype == BuiltInType.BOOLEAN:
            return subtype
        else:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Invalid type for unary operator \'{operation.operator}\'',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise TypeCheckerError()

    # 6.7.2.2. Arithmetic operators
    # 6.7.2.3. Boolean operators
    # 6.7.2.5. Relational operators
    def get_binary_operation_type(self,
                                  operation: BinaryOperation,
                                  lexspan: tuple[int, int]) -> None | TypeValue:
        try:
            left_type = operation.left[1]
            right_type = operation.right[1]
        except TypeError:
            # AST has errors
            return None

        if operation.operator in ['+', '-', '*'] and \
            left_type in [BuiltInType.INTEGER, BuiltInType.REAL] and \
            right_type in [BuiltInType.INTEGER, BuiltInType.REAL]:

            assert isinstance(left_type, BuiltInType)
            assert isinstance(right_type, BuiltInType)
            return max(left_type, right_type)

        elif operation.operator == '/' and \
            left_type in [BuiltInType.INTEGER, BuiltInType.REAL] and \
            right_type in [BuiltInType.INTEGER, BuiltInType.REAL]:

            return BuiltInType.REAL

        elif operation.operator in ['div', 'mod'] and \
            left_type == BuiltInType.INTEGER and \
            right_type == BuiltInType.INTEGER:

            return BuiltInType.INTEGER

        elif operation.operator in ['and', 'or'] and \
            left_type == BuiltInType.BOOLEAN and \
            right_type == BuiltInType.BOOLEAN:

            return BuiltInType.BOOLEAN

        elif operation.operator in ['=', '<>', '<', '>', '<=', '=>'] and \
            left_type in [BuiltInType.BOOLEAN, BuiltInType.INTEGER, BuiltInType.REAL] and \
            right_type in [BuiltInType.BOOLEAN, BuiltInType.INTEGER, BuiltInType.REAL]:

            return BuiltInType.BOOLEAN

        else:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Invalid types for binary operator \'{operation.operator}\'',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise TypeCheckerError()
