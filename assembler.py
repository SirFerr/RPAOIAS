from typing import List, Dict
from isa import OPCODES, to_signed_byte

class Assembler:
    def __init__(self):
        self.labels: Dict[str, int] = {}   # Словарь для хранения меток и их адресов
        self.code: List[int] = []          # Список байт с результирующим машинным кодом

    @staticmethod
    def _clean(line: str) -> str:
        for c in (';', '#'):
            if c in line:
                line = line[:line.index(c)]
        return line.strip()

    def assemble(self, src: str) -> List[int]:
        lines = [self._clean(x) for x in src.splitlines()]
        # Проход 1: собираем метки
        pc = 0
        for line in lines:
            if not line:
                continue
            if line.endswith(':'):
                label = line[:-1].strip()
                if not label:
                    raise ValueError("Пустая метка")
                if label in self.labels:
                    raise ValueError(f"Дублирование метки: {label}")
                self.labels[label] = pc
                continue

            parts = line.split()
            mnem = parts[0].upper()
            if mnem == "PUSH":
                pc += 2
            if mnem in ("JZ", "JMP"):
                pc += 2  # команда + 1 байт смещения
            else:
                if mnem not in OPCODES:
                    raise ValueError(f"Неизвестная мнемоника {mnem}")
                pc += 1

        # Проход 2: формируем машинный код
        self.code = []
        pc = 0
        for line in lines:
            if not line or line.endswith(':'):
                continue
            parts = line.split()
            mnem = parts[0].upper()

            if mnem in ("JZ", "JMP"):
                if len(parts) != 2:
                    raise ValueError(f"{mnem} требует указания метки")
                target = parts[1]
                if target not in self.labels:
                    raise ValueError(f"Неизвестная метка: {target}")
                # относительное смещение от следующего байта после текущей команды
                next_pc = pc + 2
                off = self.labels[target] - next_pc
                self.code.append(OPCODES[mnem])
                self.code.append(to_signed_byte(off))
                pc += 2
            elif mnem == "PUSH":
                if len(parts) != 2:
                    raise ValueError("PUSH требует аргумент")
                imm = int(parts[1])
                if not -128 <= imm <= 127:
                    raise ValueError("Число вне диапазона байта")
                self.code.append(OPCODES["PUSH"])
                self.code.append(imm & 0xFF)
                pc += 2

            else:
                self.code.append(OPCODES[mnem])
                pc += 1

        return self.code
