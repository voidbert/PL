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

from pprint import pprint
import sys

from .lexer import LexerError
from .parser import ParserError, create_parser

def main() -> None:
    source = sys.stdin.read()

    try:
        parser = create_parser('<stdin>')
        ast = parser.parse(source)

        pprint(ast)
    except LexerError:
        print('Lexer failed. Aborting ...', file=sys.stderr)
    except ParserError:
        print('Parser failed. Aborting ...', file=sys.stderr)

if __name__ == '__main__':
    main()
