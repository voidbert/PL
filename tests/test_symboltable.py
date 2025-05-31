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

import sys
import functools
import pytest
import ply.lex
from typing import Callable, Any, Dict, Tuple

from plpc.symboltable import (
    SymbolTable,
    SymbolTableError,
    SymbolValue,
    TypeDefinition,
    VariableDefinition,
    ConstantDefinition,
    CallableDefinition,
    LabelDefinition,
    BuiltInType,
    Block,
)

class DummyLexer:
    def __init__(self):
        self.lexdata = ""

    def input(self, text: str) -> None:
        pass

    def token(self):
        return None

    @property
    def lineno(self) -> int:
        return 0

    @property
    def lexpos(self) -> int:
        return 0

def successful_test() -> \
                    Callable[[Callable[[], Dict[str, Tuple[SymbolValue, int]]]], Callable[[], None]]:

    def decorator(test_fn: Callable[[], Dict[str, Tuple[SymbolValue, int]]]) -> Callable[[], None]:
        @functools.wraps(test_fn)
        def wrapper() -> None:
            st = SymbolTable("<test-input>", DummyLexer())

            module_of_test = sys.modules[test_fn.__module__]
            setattr(module_of_test, 'SYMTAB', st)

            try:
                expected_map = test_fn()
            finally:
                delattr(module_of_test, 'SYMTAB')

            got_map: Dict[str, Tuple[SymbolValue, int]] = {}
            for depth, scope_dict in enumerate(st.scopes):
                for name, symval in scope_dict.items():
                    got_map[name] = (symval, depth)

            assert got_map == expected_map

        return wrapper

    return decorator

# Built-in types, constants, callables must be present at depth = 0
@successful_test()
def test_builtin_symbols_present():
    return {
        "integer": (TypeDefinition("integer", BuiltInType.INTEGER), 0),
        "real":    (TypeDefinition("real",    BuiltInType.REAL),    0),
        "boolean": (TypeDefinition("boolean", BuiltInType.BOOLEAN), 0),
        "char":    (TypeDefinition("char",    BuiltInType.CHAR),    0),
        "string":  (TypeDefinition("char",    BuiltInType.STRING),  0),
        "true":   (ConstantDefinition("true",  True),  0),
        "false":  (ConstantDefinition("false", False), 0),
        "maxint": (ConstantDefinition("maxint", 1 << 16 - 1), 0),
        "write":   (CallableDefinition("write",   None, None, Block([], [], [], [], [], [])), 0),
        "writeln": (CallableDefinition("writeln", None, None, Block([], [], [], [], [], [])), 0),
        "read":    (CallableDefinition("read",    None, None, Block([], [], [], [], [], [])), 0),
        "readln":  (CallableDefinition("readln",  None, None, Block([], [], [], [], [], [])), 0),
        "length":  (
            CallableDefinition(
                "length",
                None,
                VariableDefinition("length", BuiltInType.INTEGER, True),
                Block([], [], [], [], [], [])
            ),
            0
        ),
    }

# Redeclaring in the same scope raises SymbolTableError
@successful_test()
def test_redeclare_same_scope_raises():
    SYMTAB.add(TypeDefinition("MyType", BuiltInType.INTEGER), (1,1))
    with pytest.raises(SymbolTableError):
        SYMTAB.add(TypeDefinition("MyType", BuiltInType.REAL), (2,2))

    base = test_builtin_symbols_present.__wrapped__().copy()
    base["mytype"] = (TypeDefinition("MyType", BuiltInType.INTEGER), 0)
    return base

# Querying undefined with error=True raises SymbolTableError
@successful_test()
def test_query_undefined_raises():
    with pytest.raises(SymbolTableError):
        SYMTAB.query_type("DoesNotExist", (0,0), error=True)

    return test_builtin_symbols_present.__wrapped__().copy()
