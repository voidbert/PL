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

from __future__ import annotations

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *

class Label:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def callable(call: str) -> Label:
        return Label(f'FN{call}')

    @staticmethod
    def user(call: None | CallableDefinition, name: int) -> Label:
        if call is None:
            return Label(f'USER{name}')
        else:
            return Label(f'USER{name}{call.name.lower()}')

    def __str__(self) -> str:
        return f'{self.name}:'

EWVMArgument = int | str | Label

class EWVMStatement:
    def __init__(self, instruction: str, *args: EWVMArgument) -> None:
        self.instruction = instruction
        self.arguments = args

    def __str__(self) -> str:
        def stringize_argument(argument: EWVMArgument) -> str:
            if isinstance(argument, Label):
                return argument.name
            else:
                return str(argument)

        indent = '  ' * (self.instruction != 'START')
        arguments_str = ' '.join(stringize_argument(argument) for argument in self.arguments)
        return f'{indent}{self.instruction} {arguments_str}'

EWVMProgram = list[Label | EWVMStatement]

def export_assembly(program: EWVMProgram) -> str:
    return '\n'.join(str(e) for e in program)

def __generate_statement_assembly(statement: Statement,
                                  call: None | CallableDefinition = None) -> EWVMProgram:

    # Statement label
    ret: EWVMProgram = []
    if statement[1] is not None:
        ret.append(Label.user(call, statement[1].name))

    # Statement content
    if isinstance(statement[0], list): # BeginEndStatement
        for s in statement[0]:
            ret.extend(__generate_statement_assembly(s, call))
    elif isinstance(statement[0], GotoStatement):
        ret.append(EWVMStatement('JUMP', Label.user(call, statement[0].label.name)))

    return ret

def __generate_block_assembly(block: Block,
                              call: None | CallableDefinition = None) -> EWVMProgram:
    ret: EWVMProgram = []

    # Block start
    if call is None:
        ret.append(EWVMStatement('START'))
    else:
        ret.append(Label.callable(call.name))

    # Statements
    ret.extend(__generate_statement_assembly((block.body, None), call))

    # Block end
    ret.append(EWVMStatement('STOP' if call is None else 'RETURN'))
    return ret

def generate_program_assembly(program: Program) -> EWVMProgram:
    ret = __generate_block_assembly(program.block)

    # Callables can only occur at the top level
    for call in program.block.callables:
        ret.extend(__generate_block_assembly(call.body, call))

    return ret
