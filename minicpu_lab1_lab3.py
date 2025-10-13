
"""
MiniCPU + Assembler (Labs #1 and #3)

Student tail digits: 32 -> binary 0b100000
- 2 LSB bits: 00 => zero-address (stack) instruction format
- 3rd bit: 0 => Harvard architecture (separate code/data memory)
- 4th bit: 0 => task = sum of array

This file provides:
  1) A zero-address stack CPU emulator (Harvard).
  2) A simple assembler for it.
  3) A demo program that sums an array and prints the result.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# -----------------------------
# ISA (Zero-address / stack)
# -----------------------------
# Each instruction is 1 byte opcode; no operands.
# Memory is separate for code and data (Harvard).
# Registers:
#   PC  - program counter
#   SP  - stack pointer (index into stack list; top is the end)
#   IP  - data index pointer used by NEXT/STORE_NEXT (implicit address)
#   ACC - accumulator (only used by OUT for pretty demo; others operate on stack)
#
# Stack behavior: push/pop Python list.
#
# Opcodes:
#   0x00 NOP              - do nothing
#   0x01 HALT             - stop
#   0x02 PUSH0            - push constant 0
#   0x03 PUSH1            - push constant 1
#   0x04 ADD              - (a,b) -> push(a+b)
#   0x05 SUB              - (a,b) -> push(a-b)
#   0x06 MUL              - (a,b) -> push(a*b)
#   0x07 DUP              - duplicate TOS
#   0x08 SWAP             - swap TOS and NOS
#   0x09 POP              - pop and discard
#   0x0A NEXT             - push data[IP]; IP++
#   0x0B SETIP            - pop -> IP
#   0x0C JZ               - pop cond; if cond==0: PC += signed offset in next byte
#   0x0D JMP              - PC += signed offset in next byte
#   0x0E LT               - (a,b) -> push(1 if a<b else 0)
#   0x0F OUT              - pop -> ACC and print (demo IO)
#
# To keep it still zero-address, the only way to read sequential array is NEXT.
# We will preload IP with array base, and preload data memory with array items.
#
# The assembler supports textual mnemonics and a simple label system.
# Jumps accept byte offsets computed by the assembler (relative, signed).
#

OPCODES = {
    "NOP":  0x00,
    "HALT": 0x01,
    "PUSH0":0x02,
    "PUSH1":0x03,
    "ADD":  0x04,
    "SUB":  0x05,
    "MUL":  0x06,
    "DUP":  0x07,
    "SWAP": 0x08,
    "POP":  0x09,
    "NEXT": 0x0A,
    "SETIP":0x0B,
    "JZ":   0x0C,  # + signed byte
    "JMP":  0x0D,  # + signed byte
    "LT":   0x0E,
    "OUT":  0x0F,
}

def to_signed_byte(n: int) -> int:
    """Clamp to signed 8-bit (-128..127) represented as 0..255."""
    if not -128 <= n <= 127:
        raise ValueError(f"Relative jump offset out of range (-128..127): {n}")
    return n & 0xFF

@dataclass
class CPUState:
    pc: int = 0
    ip: int = 0
    acc: int = 0
    stack: List[int] = field(default_factory=list)

class MiniCPU:
    def __init__(self, code: List[int], data: List[int], trace: bool = True):
        self.code = code[:]          # instruction memory (bytes)
        self.data = data[:]          # data memory (ints)
        self.state = CPUState()
        self.trace = trace
        self.cycles = 0              # for "one change per cycle" accounting

    # Helpers
    def push(self, v: int):
        self.state.stack.append(int(v))

    def pop(self) -> int:
        if not self.state.stack:
            raise RuntimeError("Stack underflow")
        return self.state.stack.pop()

    def fetch(self) -> int:
        if self.state.pc < 0 or self.state.pc >= len(self.code):
            raise RuntimeError(f"PC out of code range: {self.state.pc}")
        opcode = self.code[self.state.pc]
        self.state.pc += 1
        return opcode

    def step(self) -> bool:
        pc_before = self.state.pc
        opcode = self.fetch()

        def dbg(extra=""):
            if self.trace:
                print(f"PC={pc_before:02X} OP={opcode:02X} {extra} | "
                      f"IP={self.state.ip} ACC={self.state.acc} STACK={self.state.stack}")

        # Execute
        if opcode == OPCODES["NOP"]:
            dbg("NOP")

        elif opcode == OPCODES["HALT"]:
            dbg("HALT")
            return False

        elif opcode == OPCODES["PUSH0"]:
            self.push(0); dbg("PUSH0")

        elif opcode == OPCODES["PUSH1"]:
            self.push(1); dbg("PUSH1")

        elif opcode == OPCODES["ADD"]:
            b,a = self.pop(), self.pop()
            self.push(a+b); dbg(f"ADD -> {a+b}")

        elif opcode == OPCODES["SUB"]:
            b,a = self.pop(), self.pop()
            self.push(a-b); dbg(f"SUB -> {a-b}")

        elif opcode == OPCODES["MUL"]:
            b,a = self.pop(), self.pop()
            self.push(a*b); dbg(f"MUL -> {a*b}")

        elif opcode == OPCODES["DUP"]:
            v = self.pop(); self.push(v); self.push(v); dbg(f"DUP {v}")

        elif opcode == OPCODES["SWAP"]:
            b,a = self.pop(), self.pop(); self.push(b); self.push(a); dbg("SWAP")

        elif opcode == OPCODES["POP"]:
            _ = self.pop(); dbg("POP")

        elif opcode == OPCODES["NEXT"]:
            if not (0 <= self.state.ip < len(self.data)):
                raise RuntimeError(f"IP out of data range: {self.state.ip}")
            v = self.data[self.state.ip]
            self.state.ip += 1
            self.push(v); dbg(f"NEXT -> push {v}")

        elif opcode == OPCODES["SETIP"]:
            v = self.pop()
            if not (0 <= v <= len(self.data)):
                raise RuntimeError(f"SETIP to invalid index {v}")
            self.state.ip = v; dbg(f"SETIP {v}")

        elif opcode == OPCODES["JZ"]:
            # Next byte is signed offset
            off = self.fetch()
            if off >= 128: off -= 256
            cond = self.pop()
            if cond == 0:
                self.state.pc += off
                dbg(f"JZ taken, off={off}")
            else:
                dbg(f"JZ not-taken, off={off}")

        elif opcode == OPCODES["JMP"]:
            off = self.fetch()
            if off >= 128: off -= 256
            self.state.pc += off
            dbg(f"JMP off={off}")

        elif opcode == OPCODES["LT"]:
            b,a = self.pop(), self.pop()
            self.push(1 if a < b else 0); dbg(f"LT -> {1 if a<b else 0}")

        elif opcode == OPCODES["OUT"]:
            v = self.pop()
            self.state.acc = v
            dbg(f"OUT {v}")
            print(f"[IO] OUT = {v}")

        else:
            raise RuntimeError(f"Unknown opcode {opcode:#x} at PC {pc_before}")

        self.cycles += 1
        return True

    def run(self):
        while self.step():
            pass
        return self.state

# -----------------------------
# Assembler (two-pass, labels, relative jumps)
# -----------------------------
class Assembler:
    def __init__(self):
        self.labels: Dict[str, int] = {}
        self.code: List[int] = []

    @staticmethod
    def _clean(line: str) -> str:
        # strip comments (start with ';' or '#')
        for c in (';', '#'):
            if c in line:
                line = line[:line.index(c)]
        return line.strip()

    def assemble(self, src: str) -> List[int]:
        lines = [self._clean(x) for x in src.splitlines()]
        # Pass 1: collect labels
        pc = 0
        for line in lines:
            if not line:
                continue
            if line.endswith(':'):
                label = line[:-1].strip()
                if not label:
                    raise ValueError("Empty label")
                if label in self.labels:
                    raise ValueError(f"Duplicate label: {label}")
                self.labels[label] = pc
                continue

            parts = line.split()
            mnem = parts[0].upper()
            if mnem in ("JZ", "JMP"):
                pc += 2  # opcode + 1-byte offset
            else:
                if mnem not in OPCODES:
                    raise ValueError(f"Unknown mnemonic {mnem}")
                pc += 1

        # Pass 2: emit code
        self.code = []
        pc = 0
        for line in lines:
            if not line or line.endswith(':'):
                continue
            parts = line.split()
            mnem = parts[0].upper()
            if mnem in ("JZ", "JMP"):
                if len(parts) != 2:
                    raise ValueError(f"{mnem} needs a label")
                target = parts[1]
                if target not in self.labels:
                    raise ValueError(f"Unknown label: {target}")
                # relative offset from next byte after offset
                next_pc = pc + 2
                off = self.labels[target] - next_pc
                self.code.append(OPCODES[mnem])
                self.code.append(to_signed_byte(off))
                pc += 2
            else:
                self.code.append(OPCODES[mnem])
                pc += 1

        return self.code

# -----------------------------------------
# Demo program (sum of array) in assembly
# -----------------------------------------
DEMO_ASM = """
; Invariant: [sum, N] (N on top for easy check)
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

if __name__ == "__main__":
    # Example: sum of [5, -2, 10, 7] = 20
    program, state = assemble_and_run_demo([5, -2, 112, 7], trace=True)
    print("\n--- Machine code (hex) ---")
    print(" ".join(f"{b:02X}" for b in program))
    print("\n--- Final CPU state ---")
    print(state)
