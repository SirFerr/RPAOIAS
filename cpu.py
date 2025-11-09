from dataclasses import dataclass, field
from typing import List
from isa import OPCODES

# -----------------------------
# ISA (Zero-address / stack)
# -----------------------------
# Memory is separate for code and data (Harvard).
# Registers:
#   PC  - program counter
#   SP  - stack pointer (index into stack list; top is the end)
#   IP  - data index pointer used by NEXT/STORE_NEXT (implicit address)
#   ACC - accumulator (only used by OUT for pretty demo; others operate on stack)

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
