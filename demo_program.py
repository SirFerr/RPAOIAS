from typing import List, Tuple
from assembler import Assembler
from cpu import MiniCPU, CPUState


DEMO_ASM = """
PUSH0
SETIP

NEXT       ; получить N — количество элементов
PUSH0      ; sum = 0
SWAP       ; привести стек к виду [sum, N]

loop:
DUP
JZ end     ; если N == 0 → переход к метке end

; sum += NEXT
SWAP        ; [N, sum]
NEXT        ; взять следующий элемент массива -> [N, sum, x]
SWAP        ; переставить -> [N, x, sum]
ADD         ; сложить sum + x -> [N, sum+x]

; N = N - 1
SWAP        ; переставить -> [sum+x, N]
PUSH1
SUB         ; уменьшить N на 1 -> [sum+x, N-1]  (инвариант [sum, N])
JMP loop    ; перейти к началу цикла

end:
POP         ; удалить N из стека
OUT         ; вывести сумму
HALT        ; остановка программы
"""
LOAD_TEST = """
PUSH 5
PUSH 10
STORE

PUSH 5     
LOAD       
OUT
HALT
"""


def assemble_and_run_demo(array: List[int], trace: bool = True, program = "") -> Tuple[List[int], CPUState]:
    data = array[:]
    asm = Assembler()
    code = asm.assemble(program)
    cpu = MiniCPU(code, data, trace=trace)
    final_state = cpu.run()
    return code, final_state
