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

@successful_test('MyVar123')
def test_alphanumeric_id() -> list[SimpleToken]:
    return [('ID', 'MyVar123')]

# This test is supposed to fail -> 6.1.3 Identifiers
@failing_test('123var')
def test_id_prefixed_by_digit() -> None:
    pass

@failing_test('_start')
def test_underscore_id() -> None:
    pass

@failing_test('hello_world')
def test_underscore_id_2() -> None:
    pass

# Numbers

@successful_test('42')
def test_integer() -> list[SimpleToken]:
    return [('INTEGER', int('42'))]

@successful_test('3.14')
def test_float() -> list[SimpleToken]:
    return [('FLOAT', 3.14)]

@successful_test('1e-5')
def test_scientific_float() -> list[SimpleToken]:
    return [('FLOAT', 1e-5)]

@successful_test('87.35E+8')
def test_scientific_float_2() -> list[SimpleToken]:
    return [('FLOAT', 87.35E+8)]

# Full Strings

@successful_test('\'hello\'')
def test_string() -> list[SimpleToken]:
    return [('STRING', 'hello')]

@successful_test('\'"A string " with " quotation "marks"\'')
def test_quoted_string() -> list[SimpleToken]:
    return [('STRING', '"A string " with " quotation "marks"')]

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

@successful_test('12.3.4')
def test_combined_tokens_2() -> None:
    return [('FLOAT', 12.3), ('.', '.'), ('INTEGER', 4)]

@successful_test('@hello-world')
def test_combined_tokens_3() -> None:
    return [('^', '@'), ('ID', 'hello'), ('-', '-'), ('ID', 'world')]

# Program and blocks

@successful_test('PROGRAM Test; BEGIN END.')
def test_program_structure() -> list[SimpleToken]:
    return [
        ('PROGRAM', 'PROGRAM'),
        ('ID', 'Test'),
        (';', ';'),
        ('BEGIN', 'BEGIN'),
        ('END', 'END'),
        ('.', '.')
    ]

@successful_test('LABEL 123; CONST PI=3.14; TYPE Int=INTEGER; VAR x:Real;')
def test_declaration_keywords() -> list[SimpleToken]:
    return [
        ('LABEL', 'LABEL'), ('INTEGER', 123), (';', ';'),
        ('CONST', 'CONST'), ('ID', 'PI'), ('=', '='), ('FLOAT', 3.14), (';', ';'),
        ('TYPE', 'TYPE'), ('ID', 'Int'), ('=', '='), ('ID', 'INTEGER'), (';', ';'),
        ('VAR', 'VAR'), ('ID', 'x'), (':', ':'), ('ID', 'Real'), (';', ';')
    ]

# Type declarations

@successful_test('ARRAY [1..10] OF INTEGER; PACKED SET OF CHAR; FILE OF RECORD;')
def test_type_keywords() -> list[SimpleToken]:
    return [
        ('ARRAY', 'ARRAY'), ('[', '['), ('INTEGER', 1),
        ('RANGE', '..'), ('INTEGER', 10), (']', ']'),
        ('OF', 'OF'), ('ID', 'INTEGER'), (';', ';'),
        ('PACKED', 'PACKED'), ('SET', 'SET'), ('OF', 'OF'), ('ID', 'CHAR'), (';', ';'),
        ('FILE', 'FILE'), ('OF', 'OF'), ('RECORD', 'RECORD'), (';', ';')
    ]

# Subprograms

@successful_test('FUNCTION Foo():Integer; PROCEDURE Bar();')
def test_subprogram_keywords() -> list[SimpleToken]:
    return [
        ('FUNCTION', 'FUNCTION'), ('ID', 'Foo'), ('(', '('), (')', ')'),
        (':', ':'), ('ID', 'Integer'), (';', ';'),
        ('PROCEDURE', 'PROCEDURE'), ('ID', 'Bar'), ('(', '('), (')', ')'), (';', ';')
    ]

# Control flow

@successful_test('''
IF x THEN y ELSE z;
FOR i:=1 TO 10 DO;
WHILE b DO;
REPEAT UNTIL c;
CASE x OF 1: END;
GOTO 99;
WITH r DO;
''')
def test_control_flow() -> list[SimpleToken]:
    return [
        ('IF', 'IF'), ('ID', 'x'), ('THEN', 'THEN'), ('ID', 'y'),
        ('ELSE', 'ELSE'), ('ID', 'z'), (';', ';'),
        ('FOR', 'FOR'), ('ID', 'i'), ('ASSIGN', ':='), ('INTEGER', 1),
        ('TO', 'TO'), ('INTEGER', 10), ('DO', 'DO'), (';', ';'),
        ('WHILE', 'WHILE'), ('ID', 'b'), ('DO', 'DO'), (';', ';'),
        ('REPEAT', 'REPEAT'), ('UNTIL', 'UNTIL'), ('ID', 'c'), (';', ';'),
        ('CASE', 'CASE'), ('ID', 'x'), ('OF', 'OF'), ('INTEGER', 1),
        (':', ':'), ('END', 'END'), (';', ';'),
        ('GOTO', 'GOTO'), ('INTEGER', 99), (';', ';'),
        ('WITH', 'WITH'), ('ID', 'r'), ('DO', 'DO'), (';', ';')
    ]

# Operators

@successful_test('IF (x AND y) OR NOT z THEN a DIV b MOD c IN d')
def test_operator_keywords() -> list[SimpleToken]:
    return [
        ('IF', 'IF'), ('(', '('), ('ID', 'x'), ('AND', 'AND'),
        ('ID', 'y'), (')', ')'), ('OR', 'OR'), ('NOT', 'NOT'),
        ('ID', 'z'), ('THEN', 'THEN'), ('ID', 'a'), ('DIV', 'DIV'),
        ('ID', 'b'), ('MOD', 'MOD'), ('ID', 'c'), ('IN', 'IN'), ('ID', 'd')
    ]

# Values

@successful_test('ptr := NIL')
def test_nil_keyword() -> list[SimpleToken]:
    return [
        ('ID', 'ptr'), ('ASSIGN', ':='), ('NIL', 'NIL')
    ]

# Edge Cases

@successful_test('begin end if then')
def test_case_insensitivity() -> list[SimpleToken]:
    return [
        ('BEGIN', 'begin'), ('END', 'end'),
        ('IF', 'if'), ('THEN', 'then')
    ]

@successful_test('PROGRAMTest')
def test_keyword_adjacent_to_id() -> list[SimpleToken]:
    return [
        ('ID', 'PROGRAMTest')
    ]
