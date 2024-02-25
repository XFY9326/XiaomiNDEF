import abc
from collections import OrderedDict
from io import BytesIO

from ._utils import UINT8_BYTES_SIZE, UINT16_BYTES_SIZE
from ._utils import read_uint8, read_uint16, read_bytes, write_uint8, write_uint16


class BinaryData(abc.ABC):
    @abc.abstractmethod
    def size(self) -> int:
        raise NotImplemented

    @abc.abstractmethod
    def encode_into(self, buffer: BytesIO) -> None:
        raise NotImplemented

    def encode(self) -> bytes:
        buffer = BytesIO(bytearray(self.size()))
        self.encode_into(buffer)
        return bytes(buffer.getvalue())


class AppData(BinaryData, abc.ABC):
    pass


class UInt8BytesMap(OrderedDict[int, bytes], BinaryData):

    def __setitem__(self, __key: int, __value: bytes) -> None:
        if not isinstance(__key, int):
            raise TypeError("Key must be an integer")
        if not isinstance(__value, bytes):
            raise TypeError("Value must be a bytes")
        if __key > 0xff or __key < 0:
            raise ValueError("key must be in [0, 0xff]")
        if len(__value) > 0xff:
            raise ValueError("value length must be in (0, 0xff]")
        super().__setitem__(__key, __value)

    def size(self) -> int:
        return sum(2 * UINT8_BYTES_SIZE + len(b) for b in self.values())

    def encode_into(self, buffer: BytesIO) -> None:
        for key, value in self.items():
            write_uint8(buffer, key)
            write_uint8(buffer, len(value))
            buffer.write(value)

    @staticmethod
    def read_from(buffer: BytesIO, length: int | None = None) -> 'UInt8BytesMap':
        bytes_map = UInt8BytesMap()
        i = 0
        while (length is None or i < length) and (key := read_uint8(buffer, False)):
            bytes_map[key] = read_bytes(buffer, read_uint8(buffer))
            i += 1
        return bytes_map


class UInt16BytesMap(OrderedDict[int, bytes], BinaryData):
    def __setitem__(self, __key: int, __value: bytes) -> None:
        if not isinstance(__key, int):
            raise TypeError("Key must be an integer")
        if not isinstance(__value, bytes):
            raise TypeError("Value must be a bytes")
        if __key > 0xffff or __key < 0:
            raise ValueError("key must be in [0, 0xffff]")
        if len(__value) > 0xffff:
            raise ValueError("value length must be in (0, 0xffff]")
        super().__setitem__(__key, __value)

    def size(self) -> int:
        return sum(2 * UINT16_BYTES_SIZE + len(b) for b in self.values())

    def encode_into(self, buffer: BytesIO) -> None:
        for key, value in self.items():
            write_uint16(buffer, key)
            write_uint16(buffer, len(value))
            buffer.write(value)

    @staticmethod
    def read_from(buffer: BytesIO, length: int | None = None) -> 'UInt16BytesMap':
        bytes_map = UInt16BytesMap()
        i = 0
        while (length is None or i < length) and (key := read_uint16(buffer, False)):
            bytes_map[key] = read_bytes(buffer, read_uint16(buffer))
            i += 1
        return bytes_map
