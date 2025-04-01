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

from typing import Callable
from plpc.lexer import LexerError, create_lexer

# ------------------------------------------ EASE OF USE ------------------------------------------

SimpleToken = tuple[str, str]

def successful_test(source: str) -> Callable[[Callable[[], list[SimpleToken]]], Callable[[], None]]:
    def decorator(test: Callable[[], list[SimpleToken]]) -> Callable[[], None]:
        def wrapper() -> None:
            lexer = create_lexer('<test-input>')
            lexer.input(source)

            got = [ (t.type, t.value) for t in lexer ]
            expected = test()

            assert got == expected

        return wrapper

    return decorator

def failing_test(source: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def decorator(_: Callable[[], None]) -> Callable[[], None]:
        def wrapper() -> None:
            try:
                lexer = create_lexer('<test-input>')
                lexer.input(source)
                _ = list(lexer)
            except LexerError:
                return

            assert False

        return wrapper

    return decorator

# ------------------------------------ SINGLE TOKEN TYPE TESTS ------------------------------------

# Empty strings

@successful_test('')
def test_empty_1() -> list[SimpleToken]:
    return []

@successful_test('\n\n\r\r\t\n\r')
def test_empty_2() -> list[SimpleToken]:
    return []

# Comments

@successful_test('{}')
def test_empty_comment_1() -> list[SimpleToken]:
    return []

@successful_test('(**)')
def test_empty_comment_2() -> list[SimpleToken]:
    return []

@successful_test('(*}')
def test_empty_comment_3() -> list[SimpleToken]:
    return []

@successful_test('{*)')
def test_empty_comment_4() -> list[SimpleToken]:
    return []

@successful_test('{Hello! こんにちは}')
def test_non_empty_comment_1() -> list[SimpleToken]:
    return []

@successful_test('(*Hello! こんにちは*)')
def test_non_empty_comment_2() -> list[SimpleToken]:
    return []

@successful_test('(*Hello! こんにちは}')
def test_non_empty_comment_3() -> list[SimpleToken]:
    return []

@failing_test('{')
def test_unterminated_comment_1() -> None:
    pass

@failing_test('{{{{{')
def test_unterminated_comment_2() -> None:
    pass

@failing_test('{ Hello! こんにちは')
def test_unterminated_comment_3() -> None:
    pass

@successful_test('(*')
def test_fake_unterminated_comment_1() -> list[SimpleToken]:
    return [('(', '('), ('*', '*')]

@successful_test('(*)')
def test_fake_unterminated_comment_2() -> list[SimpleToken]:
    return [('(', '('), ('*', '*'), (')', ')')]

@failing_test('{{}')
def test_nested_comment_1() -> None:
    pass

@failing_test('{a{}')
def test_nested_comment_2() -> None:
    pass

@failing_test('{{a}')
def test_nested_comment_3() -> None:
    pass

@failing_test('{a{b}')
def test_nested_comment_4() -> None:
    pass

@failing_test('{(*}')
def test_nested_comment_5() -> None:
    pass

@failing_test('{a(*}')
def test_nested_comment_6() -> None:
    pass

@failing_test('{(*a}')
def test_nested_comment_7() -> None:
    pass

@failing_test('{a(*b}')
def test_nested_comment_8() -> None:
    pass

@failing_test('{(*{}')
def test_nested_comment_9() -> None:
    pass

@failing_test('{{(*}')
def test_nested_comment_10() -> None:
    pass

# Other tokens types here

# ------------------------------------- COMBINATION OF TOKENS -------------------------------------

# Token separation tests here
