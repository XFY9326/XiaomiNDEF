import dataclasses
import enum
from collections import OrderedDict
from io import BytesIO
from typing import Mapping, Iterable

from ._utils import UINT8_BYTES_SIZE, UINT32_BYTES_SIZE
from ._utils import read_uint8, read_uint32, read_bytes, write_uint8, write_uint32
from .base import AppData, UInt8BytesMap


@enum.unique
class DeviceType(enum.IntEnum):
    UNKNOWN = 0
    TV = 2
    PC = 3
    CAR = 5
    PAD = 8

    @staticmethod
    def parse(value: int) -> 'DeviceType':
        try:
            return DeviceType(value)
        except ValueError:
            return DeviceType.UNKNOWN


@dataclasses.dataclass(frozen=True)
class _KeyValue:
    value: int
    is_text: bool | None = None


@enum.unique
class PayloadKey(enum.Enum):
    UNKNOWN = _KeyValue(0)
    ACTION_SUFFIX = _KeyValue(101, True)
    BLUETOOTH_MAC = _KeyValue(1, True)
    WIFI_MAC = _KeyValue(2, True)
    WIRED_MAC = _KeyValue(3, True)
    EXT_ABILITY = _KeyValue(121, False)

    @property
    def key_value(self) -> int:
        return self.value.value

    @property
    def is_text(self) -> bool | None:
        return self.value.is_text

    def new_pair(self, value: str | bytes) -> tuple['PayloadKey', bytes]:
        if isinstance(value, str):
            return self, value.encode("utf-8")
        elif isinstance(value, bytes):
            return self, value
        else:
            raise ValueError("value must be str or bytes")

    def repr_data(self, data: bytes) -> str:
        if self.is_text:
            return data.decode("utf-8")
        else:
            return repr(data)

    @staticmethod
    def parse(value: int) -> 'PayloadKey':
        for e in PayloadKey:
            if e.value == value:
                return e
        return PayloadKey.UNKNOWN


@dataclasses.dataclass(frozen=True)
class HandoffAppData(AppData):
    major_version: int
    minor_version: int
    device_type: int
    attributes_map: UInt8BytesMap
    action: str
    payloads_map: UInt8BytesMap

    @property
    def enum_device_type(self) -> DeviceType:
        return DeviceType.parse(self.device_type)

    @property
    def enum_payloads_map(self) -> OrderedDict[PayloadKey, bytes]:
        return OrderedDict((PayloadKey.parse(k), v) for k, v in self.payloads_map.items())

    @staticmethod
    def new_payloads_map(data: Mapping[PayloadKey, bytes] | Iterable[tuple[PayloadKey, bytes]]) -> UInt8BytesMap:
        if isinstance(data, Mapping):
            items = data.items()
        elif isinstance(data, Iterable):
            items = data
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        items: Iterable[tuple[PayloadKey, bytes]]
        return UInt8BytesMap((k.key_value, v) for k, v in items)

    @staticmethod
    def encode_payloads_map(data: OrderedDict[PayloadKey, bytes]) -> bytes:
        return HandoffAppData.new_payloads_map(data).encode()

    @staticmethod
    def decode_payloads_map(buffer: bytes) -> OrderedDict[PayloadKey, bytes]:
        bytes_map = UInt8BytesMap.read_from(BytesIO(buffer))
        return OrderedDict((PayloadKey.parse(k), v) for k, v in bytes_map.items())

    def size(self) -> int:
        return (
                UINT8_BYTES_SIZE +  # major_version
                UINT8_BYTES_SIZE +  # minor_version
                UINT32_BYTES_SIZE +  # device_type
                UINT8_BYTES_SIZE +  # attributes_map size
                self.attributes_map.size() +  # attributes_map
                UINT8_BYTES_SIZE +  # action size
                len(self.action.encode("utf-8")) +  # action
                self.payloads_map.size()  # payloads_map
        )

    def encode_into(self, buffer: BytesIO) -> None:
        action_bytes = self.action.encode("utf-8")
        write_uint8(buffer, self.major_version)
        write_uint8(buffer, self.minor_version)
        write_uint32(buffer, self.device_type)
        write_uint8(buffer, len(self.attributes_map))
        self.attributes_map.encode_into(buffer)
        write_uint8(buffer, len(action_bytes))
        buffer.write(action_bytes)
        self.payloads_map.encode_into(buffer)

    @staticmethod
    def decode(buffer: BytesIO) -> 'HandoffAppData':
        return HandoffAppData(
            major_version=read_uint8(buffer),
            minor_version=read_uint8(buffer),
            device_type=read_uint32(buffer),
            attributes_map=UInt8BytesMap.read_from(buffer, read_uint8(buffer)),
            action=read_bytes(buffer, read_uint8(buffer)).decode("utf-8"),
            payloads_map=UInt8BytesMap.read_from(buffer)
        )
