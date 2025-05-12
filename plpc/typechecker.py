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

from .ast import BuiltInType, ConstantValue, EnumeratedTypeConstantValue, TypeValue

class TypeCheckerError(ValueError):
    pass

def get_constant_type(constant: ConstantValue) -> TypeValue:
    if isinstance(constant, int):
        return BuiltInType.INTEGER
    if isinstance(constant, float):
        return BuiltInType.REAL
    elif isinstance(constant, bool):
        return BuiltInType.BOOLEAN
    elif isinstance(constant, str):
        return BuiltInType.CHAR if len(constant) == 1 else BuiltInType.STRING
    elif isinstance(constant, EnumeratedTypeConstantValue):
        assert constant.constant_type is not None
        return constant.constant_type.value
    else:
        raise TypeCheckerError()

def get_constant_ordinal_value(constant: ConstantValue) -> int:
    if isinstance(constant, int):
        return constant
    elif isinstance(constant, bool):
        return int(constant)
    elif isinstance(constant, str) and len(constant) == 1:
        return ord(constant)
    elif isinstance(constant, EnumeratedTypeConstantValue):
        return constant.value
    else:
        raise TypeCheckerError()
