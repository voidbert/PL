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
    def __init__(self, file_path: str):
        self.has_errors = False                        # If errors have been detected by the lexer
        self.file_path = file_path                     # Path to the source for error printing
        self.last_error: tuple[int, int] | None = None # Start position and length of error
        self.line_start = 0                            # Start position of the current line

        self.literals = '.;:(,)<>=+-*/[]^'
        self.keywords = {
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

        self.tokens = list(self.keywords.union({
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
            'ALT_CARET',
            'ALT_LBRACKET',
            'ALT_RBRACKET'
        }))

        self.t_DIFFERENT = r'<>'
        self.t_LE = r'<='
        self.t_GE = r'>='
        self.t_ASSIGN = r':='
        self.t_RANGE = r'\.\.'

        self.t_ignore = ' \t\r'
        self.t_ignore_COMMENT = r'({|\(\*)((?!{|\(\*)(.|\n))*?(}|\*\))'

    def t_ID(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[a-z][a-z0-9]*'
        upper = t.value.upper()
        if upper in self.keywords:
            t.type = upper
        return t

    def t_FLOAT(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+(\.[0-9]+e(\+|\-)?[0-9]+|\.[0-9]+|e(\+|\-)?[0-9]+)'
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+'
        t.value = int(t.value)
        return t

    def t_STRING(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\'((?:\'\'|[^\'])*)\''
        t.value = t.value[1:-1].replace('\'\'', '\'')
        return t

    def t_ALT_CARET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'@'
        t.type = '^'
        return t

    def t_ALT_LBRACKET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\(\.'
        t.type = '['
        return t

    def t_ALT_RBRACKET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\.\)'
        t.type = ']'
        return t

    def t_newline(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\n+'

        self.commit_error(t.lexer)
        t.lexer.lineno += len(t.value)
        self.line_start = t.lexer.lexpos

    def t_eof(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        self.t_newline(t) # Commit error if need be
        if self.has_errors:
            raise LexerError()

    def t_error(self, t: ply.lex.LexToken) -> None:
        if self.last_error is not None:
            start, length = self.last_error

            if start + length == t.lexer.lexpos:
                # Error continuation
                self.last_error = start, length + 1
            else:
                self.commit_error(t.lexer)
                self.last_error = t.lexer.lexpos, 1
        else:
            # First error in the line
            self.last_error = t.lexer.lexpos, 1

        t.lexer.skip(1)

    def commit_error(self, lexer: ply.lex.Lexer) -> None:
        if self.last_error is not None:
            # Determine important positions in the text
            line_end = lexer.lexdata.find('\n', self.line_start)
            if line_end == -1:
                line_end = lexer.lexlen

            start, length = self.last_error
            relative_start = start - self.line_start
            length = min(length, line_end - start)

            # Pretty print error
            line = lexer.lexdata[self.line_start:line_end]

            error_location = f'{self.file_path}:{lexer.lineno}:{relative_start + 1}'
            error_description = 'Lexer failed to reconize the following characters here'
            error_underline = ' ' * relative_start + '\033[91m^' + '~' * (length - 1) + '\033[0m'

            print(f'{error_location}: \033[91merror\033[0m: {error_description}', file=sys.stderr)
            print(f'{lexer.lineno: 6d} | {line}', file=sys.stderr)
            print(f'         {error_underline}\n', file=sys.stderr)

            self.has_errors = True
            self.last_error = None

def create_lexer(file_path: str) -> ply.lex.Lexer:
    return ply.lex.lex(module=_Lexer(file_path), reflags=re.IGNORECASE)
