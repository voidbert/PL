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

from .ewvm import EWVMProgram, EWVMStatement

def __optimization_pass(program: EWVMProgram) -> EWVMProgram:
    ret: EWVMProgram = []

    i = 0
    while i < len(program):
        old_i = i

        if isinstance(program[i], EWVMStatement) and \
            i + 1 < len(program) and \
            isinstance(program[i + 1], EWVMStatement):

            current_statement = program[i]
            next_statement = program[i + 1]
            assert isinstance(current_statement, EWVMStatement)
            assert isinstance(next_statement, EWVMStatement)

            # (PUSHI 0){N} -> PUSHN N
            if current_statement == EWVMStatement('PUSHI', 0):
                count = 0
                while i + count < len(program):
                    if program[i + count] != EWVMStatement('PUSHI', 0):
                        break
                    count += 1

                if count == 1:
                    ret.append(EWVMStatement('PUSHI', 0))
                else:
                    ret.append(EWVMStatement('PUSHN', count))

                i += count

            # STOREL N ; PUSHL N -> DUP 1 ; STOREL N
            # STOREG N ; PUSHG N -> DUP 1 ; STOREG N
            if current_statement.instruction in ['STOREL', 'STOREG']:
                if i + 1 < len(program) and \
                    next_statement.instruction == 'PUSH' + current_statement.instruction[-1] and \
                    current_statement.arguments == next_statement.arguments:

                    ret.append(EWVMStatement('DUP', 1))
                    ret.append(program[i])
                    i += 2

            # PUSHI 2 ; MUL -> DUP 1 ; ADD
            elif current_statement == EWVMStatement('PUSHI', 2) and \
                next_statement == EWVMStatement('MUL'):

                ret.append(EWVMStatement('DUP', 1))
                ret.append(EWVMStatement('ADD'))
                i += 2

        if i == old_i:
            ret.append(program[i])
            i += 1

    return ret

def apply_ewvm_peephole_optimizations(program: EWVMProgram) -> EWVMProgram:
    next_program = program
    while True:
        previous_program = next_program
        next_program = __optimization_pass(previous_program)
        if previous_program == next_program:
            break

    return previous_program
