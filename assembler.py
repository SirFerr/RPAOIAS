from typing import List, Dict
from isa import OPCODES, to_signed_byte

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
