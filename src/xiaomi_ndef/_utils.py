from io import BytesIO
from typing import Literal

UINT8_BYTES_SIZE = 1
UINT16_BYTES_SIZE = 2
UINT32_BYTES_SIZE = 4


def write_uint8(buffer: BytesIO, value: int, byteorder: Literal['big', 'little'] = "big") -> int:
    if value > 0xff or value < 0:
        raise ValueError("value out of range")
    return buffer.write(value.to_bytes(length=UINT8_BYTES_SIZE, byteorder=byteorder, signed=False))


def write_uint16(buffer: BytesIO, value: int, byteorder: Literal['big', 'little'] = "big") -> int:
    if value > 0xffff or value < 0:
        raise ValueError("value out of range")
    return buffer.write(value.to_bytes(length=UINT16_BYTES_SIZE, byteorder=byteorder, signed=False))


def write_uint32(buffer: BytesIO, value: int, byteorder: Literal['big', 'little'] = "big") -> int:
    if value > 0xffffffff or value < 0:
        raise ValueError("value out of range")
    return buffer.write(value.to_bytes(length=UINT32_BYTES_SIZE, byteorder=byteorder, signed=False))


def read_uint8(buffer: BytesIO, strict: bool = True, byteorder: Literal['big', 'little'] = "big") -> int:
    value = buffer.read(UINT8_BYTES_SIZE)
    if len(value) != UINT8_BYTES_SIZE and strict:
        raise ValueError(f"read uint8 failed, read {len(value)} bytes, expected {UINT8_BYTES_SIZE} bytes")
    else:
        return int.from_bytes(value, byteorder=byteorder, signed=False)


def read_uint16(buffer: BytesIO, strict: bool = True, byteorder: Literal['big', 'little'] = "big") -> int:
    value = buffer.read(UINT16_BYTES_SIZE)
    if len(value) != UINT16_BYTES_SIZE and strict:
        raise ValueError(f"read uint16 failed, read {len(value)} bytes, expected {UINT16_BYTES_SIZE} bytes")
    else:
        return int.from_bytes(value, byteorder=byteorder, signed=False)


def read_uint32(buffer: BytesIO, strict: bool = True, byteorder: Literal['big', 'little'] = "big") -> int:
    value = buffer.read(UINT32_BYTES_SIZE)
    if len(value) != UINT32_BYTES_SIZE and strict:
        raise ValueError(f"read uint32 failed, read {len(value)} bytes, expected {UINT32_BYTES_SIZE} bytes")
    else:
        return int.from_bytes(value, byteorder=byteorder, signed=False)


def read_bytes(buffer: BytesIO, size: int, strict: bool = True) -> bytes:
    value = buffer.read(size)
    if len(value) != size and strict:
        raise ValueError(f"read bytes failed, read {len(value)} bytes, expected {size} bytes")
    else:
        return value
