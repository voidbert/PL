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
import re
import ply.lex

class LexerError(ValueError):
    pass

class _Lexer:
    has_errors: bool = False                  # If errors have been detected by the lexer
    last_error: tuple[int, int] | None = None # Start position and length of error
    line_start: int = 0                       # Start position of the current line

    literals = '.;:(,)<>=+-*/[]^'

    keywords = {
        # Program and blocks
        'PROGRAM', 'BEGIN', 'END',
        'LABEL', 'CONST', 'TYPE', 'VAR',

        # Type declarations
        'ARRAY', 'PACKED', 'SET', 'FILE', 'OF', 'RECORD',

        # Subprograms
        'FUNCTION', 'PROCEDURE',

        # Control flow
        'IF', 'THEN', 'ELSE',
        'FOR', 'TO', 'DOWNTO', 'DO',
        'WHILE',                     # 'DO' as well
        'REPEAT', 'UNTIL',
        'CASE',                      # 'OF' as well
        'GOTO',
        'WITH',

        # Operators
        'AND', 'OR', 'NOT',
        'IN',
        'DIV', 'MOD',

        # Values
        # Must be supported here not to collide with identifiers
        'NIL'
    }

    tokens = list(keywords.union({
        # 6.1.2 - Special-symbols
        'DIFFERENT',
        'LE',
        'GE',
        'ASSIGN',
        'RANGE',

        # 6.1.3 - Identifiers
        'ID',

        # 6.1.4 - Directives
        # Not supported by the lexer (see ID)

        # 6.1.5 - Numbers
        'FLOAT',
        'INTEGER',

        # 6.1.6 - Labels
        # Not supported by the lexer (see INTEGER)

        # 6.1.7 - Character-strings
        'STRING',

        # 6.1.8 - Token separators
        'COMMENT',

        # 6.1.9 - Lexical alternatives
        'ALT_CARET'
        'ALT_LBRACKET'
        'ALT_RBRACKET'
    }))

    t_DIFFERENT = r'<>'
    t_LE = r'<='
    t_GE = r'>='
    t_ASSIGN = r':='
    t_RANGE = r'\.\.'

    @classmethod
    def t_ID(cls, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[a-z][a-z0-9]*'
        upper = t.value.upper()
        if upper in cls.keywords:
            t.type = upper
        return t

    @staticmethod
    def t_FLOAT(t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+(\.[0-9]+e(\+|\-)?[0-9]+|\.[0-9]+|e(\+|\-)?[0-9]+)'
        t.value = float(t.value)
        return t

    @staticmethod
    def t_INTEGER(t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+'
        t.value = int(t.value)
        return t

    @staticmethod
    def t_STRING(t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\'((?:\'\'|[^\'])*)\''
        t.value = t.value[1:-1].replace('\'\'', '\'')
        return t

    @staticmethod
    def t_ALT_CARET(t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'@'
        t.type = '^'
        return t

    @staticmethod
    def t_ALT_LBRACKET(t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\(\.'
        t.type = '['
        return t

    @staticmethod
    def t_ALT_RBRACKET(t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\.\)'
        t.type = ']'
        return t

    t_ignore = ' \t\r'
    t_ignore_COMMENT = r'({|\(\*)(.|\n)*?(}|\*\))'

    @classmethod
    def t_newline(cls, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\n+'

        cls.commit_error()
        lexer.lineno += len(t.value)
        cls.line_start = lexer.lexpos

    @classmethod
    def t_eof(cls, t: ply.lex.LexToken) -> ply.lex.LexToken:
        cls.t_newline(t) # Commit error if need be
        if cls.has_errors:
            raise LexerError()

    @classmethod
    def t_error(cls, _: ply.lex.LexToken) -> None:
        if cls.last_error is not None:
            start, length = cls.last_error

            if start + length == lexer.lexpos:
                # Error continuation
                cls.last_error = start, length + 1
            else:
                cls.commit_error()
                cls.last_error = lexer.lexpos, 1
        else:
            # First error in the line
            cls.last_error = lexer.lexpos, 1

        lexer.skip(1)

    @classmethod
    def commit_error(cls) -> None:
        if cls.last_error is not None:
            # Determine important positions in the text
            line_end = lexer.lexdata.find('\n', cls.line_start)
            if line_end == -1:
                line_end = lexer.lexlen

            start, length = cls.last_error
            relative_start = start - cls.line_start
            length = min(length, line_end - start)

            # Pretty print error
            line = lexer.lexdata[cls.line_start:line_end]

            error_location = f'{SOURCE_FILE}:{lexer.lineno}:{relative_start + 1}'
            error_description = 'Lexer failed to reconize the following characters here'
            error_underline = ' ' * relative_start + '\033[91m^' + '~' * (length - 1) + '\033[0m'

            print(f'{error_location}: \033[91merror\033[0m: {error_description}', file=sys.stderr)
            print(f'{lexer.lineno: 6d} | {line}', file=sys.stderr)
            print(f'         {error_underline}\n', file=sys.stderr)

            cls.has_errors = True
            cls.last_error = None

SOURCE_FILE = '<stdin>'
lexer = ply.lex.lex(module=_Lexer, reflags=re.IGNORECASE)
