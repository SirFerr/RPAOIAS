
# Each instruction is 1 byte opcode; no operands.

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