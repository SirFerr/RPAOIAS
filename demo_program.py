from typing import List, Tuple
from assembler import Assembler
from cpu import MiniCPU, CPUState

# -----------------------------------------
# Demo program (sum of array) in assembly
# -----------------------------------------

DEMO_ASM = """
; Invariant: [sum, N]
; Init: IP=0; N=NEXT; sum=0; then SWAP -> [sum, N]

PUSH0
SETIP

NEXT       ; N
PUSH0      ; sum
SWAP       ; [sum, N]

loop:
DUP
JZ end

; sum += NEXT
SWAP        ; [N, sum]
NEXT        ; [N, sum, x]
SWAP        ; [N, x, sum]
ADD         ; [N, sum+x]

; N = N - 1
SWAP        ; [sum+x, N]
PUSH1
SUB         ; [sum+x, N-1]  (invariant [sum, N])
JMP loop

end:
POP
OUT
HALT
"""

def assemble_and_run_demo(array: List[int], trace: bool = True) -> Tuple[List[int], CPUState]:
    """
    array: list of ints to sum. We'll place length at data[0], then elements.
    """
    data = [len(array)] + array[:]
    asm = Assembler()
    code = asm.assemble(DEMO_ASM)
    cpu = MiniCPU(code, data, trace=trace)
    final_state = cpu.run()
    return code, final_state
