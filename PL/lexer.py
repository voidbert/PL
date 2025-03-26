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
import ply.lex

class LexerError(ValueError):
    pass

class _Lexer:
    has_errors: bool = False                  # If errors have been detected by the lexer
    last_error: tuple[int, int] | None = None # Start position and length of error
    line_start: int = 0                       # Start position of the current line

    tokens = ['NUMBER']

    t_ignore = ' \t\r'

    @staticmethod
    def t_NUMBER(t : ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+'

        t.value = int(t.value)
        return t

    @classmethod
    def t_newline(cls, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\n+'

        line_end = lexer.lexpos - len(t.value)
        cls.commit_error(line_end)

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
                # New error in the same line
                line_end = lexer.lexdata.find('\n', lexer.lexpos)
                if line_end == -1:
                    line_end = lexer.lexlen

                cls.commit_error(line_end)
                cls.last_error = lexer.lexpos, 1
        else:
            # First error in the line
            cls.last_error = lexer.lexpos, 1
            cls.has_errors = True

        lexer.skip(1)

    @classmethod
    def commit_error(cls, line_end: int) -> None:
        if cls.last_error is not None:
            start, length = cls.last_error
            line = lexer.lexdata[cls.line_start:line_end]

            relative_start = start - cls.line_start
            error_location = f'{SOURCE_FILE}:{lexer.lineno}:{relative_start + 1}'
            error_description = 'Lexer failed to reconize the following characters here'
            error_underline = ' ' * relative_start + '\033[91m^' + '~' * (length - 1) + '\033[0m'

            print(f'{error_location}: \033[91merror\033[0m: {error_description}', file=sys.stderr)
            print(f'\t{line}', file=sys.stderr)
            print(f'\t{error_underline}\n', file=sys.stderr)

            cls.last_error = None

SOURCE_FILE = '<stdin>'
lexer = ply.lex.lex(module=_Lexer)
