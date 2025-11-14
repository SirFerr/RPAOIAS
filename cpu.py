from dataclasses import dataclass, field
from typing import List
from isa import OPCODES

@dataclass
class CPUState:
    pc: int = 0      # счётчик команд
    ip: int = 0      # указатель данных
    acc: int = 0     # аккумулятор, только для OUT
    stack: List[int] = field(default_factory=list)  # стек

class MiniCPU:
    def __init__(self, code: List[int], data: List[int], trace: bool = True):
        self.code = code[:]          # память инструкций (байты)
        self.data = data[:]          # память данных (целые числа)
        self.state = CPUState()
        self.trace = trace
        self.cycles = 0              # счётчик тактов (для учёта изменений за шаг)

    def push(self, v: int):
        # положить значение в стек
        self.state.stack.append(int(v))

    def pop(self) -> int:
        # снять значение с вершины стека
        if not self.state.stack:
            raise RuntimeError("Переполнение стека (stack underflow)")
        return self.state.stack.pop()

    def fetch(self) -> int:
        # Получение следующей инструкции
        if self.state.pc < 0 or self.state.pc >= len(self.code):
            raise RuntimeError(f"PC вышел за границы кода: {self.state.pc}")
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
        if opcode == OPCODES["NOPE"]:
            dbg("NOPE")

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
                raise RuntimeError(f"IP вне диапазона данных: {self.state.ip}")
            v = self.data[self.state.ip]
            self.state.ip += 1
            self.push(v); dbg(f"NEXT -> push {v}")

        elif opcode == OPCODES["SETIP"]:
            v = self.pop()
            if not (0 <= v <= len(self.data)):
                raise RuntimeError(f"SETIP в неверный индекс {v}")
            self.state.ip = v; dbg(f"SETIP {v}")

        elif opcode == OPCODES["JZ"]:
            off = self.fetch()
            if off >= 128: off -= 256
            cond = self.pop()
            if cond == 0:
                self.state.pc += off
                dbg(f"JZ выполнен, смещение={off}")
            else:
                dbg(f"JZ не выполнен, смещение={off}")

        elif opcode == OPCODES["JMP"]:
            off = self.fetch()
            if off >= 128: off -= 256
            self.state.pc += off
            dbg(f"JMP смещение={off}")

        elif opcode == OPCODES["LT"]:
            b,a = self.pop(), self.pop()
            self.push(1 if a < b else 0); dbg(f"LT -> {1 if a<b else 0}")

        elif opcode == OPCODES["OUT"]:
            v = self.pop()
            self.state.acc = v
            dbg(f"OUT {v}")
            print(f"[IO] OUT = {v}")

        elif opcode == OPCODES["LOAD"]:
            # Получить по произвольному адресу
            addr = self.pop()
            if not (0 <= addr < len(self.data)):
                raise RuntimeError(f"LOAD: wrong address({addr})")
            v = self.data[addr]
            self.push(v)
            dbg(f"LOAD addr={addr} -> {v}")

        elif opcode == OPCODES["PUSH"]:
            # Положить произовльное число в стек
            imm = self.fetch()
            if imm >= 128:
                imm -= 256
            self.push(imm)
            dbg(f"PUSH {imm}")


        elif opcode == OPCODES["STORE"]:
            val = self.pop()
            addr = self.pop()
            if not (0 <= addr < len(self.data)):
                raise RuntimeError(f"STORE: wrong address({addr})")
            self.data[addr] = val
            dbg(f"STORE addr={addr} <- {val}")

        else:
            raise RuntimeError(f"Неизвестный код операции {opcode:#x} по адресу PC {pc_before}")

        self.cycles += 1
        return True

    def run(self):
        while self.step():
            pass
        return self.state
