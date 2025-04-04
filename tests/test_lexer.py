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

# Special Symbols

@successful_test('<>')
def test_different() -> list[SimpleToken]:
    return [('DIFFERENT', '<>')]

@successful_test('<=')
def test_le() -> list[SimpleToken]:
    return [('LE', '<=')]

@successful_test('>=')
def test_ge() -> list[SimpleToken]:
    return [('GE', '>=')]

@successful_test(':=')
def test_assign() -> list[SimpleToken]:
    return [('ASSIGN', ':=')]

@successful_test('..')
def test_range() -> list[SimpleToken]:
    return [('RANGE', '..')]

# Identifiers

@successful_test('x')
def test_simple_id() -> list[SimpleToken]:
    return [('ID', 'x')]

@successful_test('myVar123')
def test_alphanumeric_id() -> list[SimpleToken]:
    return [('ID', 'myVar123')]

# TODO -> Verify if this is supposed to fail
#@failing_test('123var')
#def test_invalid_id() -> None:
#    pass

@failing_test('_start')
def test_underscore_id() -> None:
    pass

# Numbers

@successful_test('42')
def test_integer() -> list[SimpleToken]:
    return [('INTEGER', 42)]

@successful_test('3.14')
def test_float() -> list[SimpleToken]:
    return [('FLOAT', 3.14)]

@successful_test('1e-5')
def test_scientific_float() -> list[SimpleToken]:
    return [('FLOAT', 1e-5)]

# TODO -> Verify if this is supposed to fail
#@failing_test('12.3.4')
#def test_invalid_float() -> None:
#    pass

# Full Strings

@successful_test('\'hello\'')
def test_string() -> list[SimpleToken]:
    return [('STRING', 'hello')]

# TODO -> Check if this is supposed to work
#@successful_test('''"a quote " that quotes"''')
#def test_escaped_string() -> list[SimpleToken]:
#    return [('STRING', '"a quote " that quotes"')]

@failing_test('\'unterminated')
def test_unterminated_string() -> None:
    pass

# Lexical Alternatives

@successful_test('^')
def test_alt_caret() -> list[SimpleToken]:
    return [('^', '^')]

@successful_test('(.')
def test_alt_lbracket() -> list[SimpleToken]:
    return [('[', '(.')]

@successful_test('.)')
def test_alt_rbracket() -> list[SimpleToken]:
    return [(']', '.)')]

# ------------------------------------- COMBINATION OF TOKENS -------------------------------------

@successful_test('x := 42 + y; { Compute something }')
def test_combined_tokens() -> list[SimpleToken]:
    return [
        ('ID', 'x'),
        ('ASSIGN', ':='),
        ('INTEGER', 42),
        ('+', '+'),
        ('ID', 'y'),
        (';', ';'),
    ]

# TODO -> Check if this is supposed to fail
#@failing_test('@invalid-char')
#def test_invalid_char() -> None:
#    pass

# Token separation tests here
