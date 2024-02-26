import abc
import dataclasses
import enum
from collections import OrderedDict
from io import BytesIO
from typing import Mapping, Iterable

from ._utils import UINT8_BYTES_SIZE, UINT16_BYTES_SIZE, UINT32_BYTES_SIZE
from ._utils import read_uint8, read_uint16, read_uint32, read_bytes, write_uint8, write_uint16, write_uint32
from .base import BinaryData, AppData, UInt16BytesMap
from .tnf import XiaomiNdefTNF

_TYPE_DEVICE = 0x01
_TYPE_ACTION = 0x02
_PREFIX_APP_DATA_MAP = b"mxD"


@enum.unique
class AppDataValueType(enum.IntEnum):
    UNKNOWN = enum.auto()
    ATTRIBUTES_MAP = enum.auto()
    IOT_ACTION = enum.auto()


@enum.unique
class Action(enum.IntEnum):
    UNKNOWN = 0
    IOT = 1
    MUSIC_RELAY = 2
    TEL_RELAY = 3
    FILE_TRANSFER = 4
    SCREEN_CASTING = 5
    CORP_OPERATION = 6
    VIDEO_RELAY = 7
    VOIP_RELAY = 8
    IOT_ENV = 9
    REMOTE_CONTROLLER = 10
    GUEST_NETWORK = 11
    EMPTY = 12
    CUSTOM = 13
    AUTO = 0xffff >> 1

    @staticmethod
    def parse(value: int) -> 'Action':
        try:
            return Action(value)
        except ValueError:
            return Action.UNKNOWN


@enum.unique
class Condition(enum.IntEnum):
    UNKNOWN = 0
    APP_FOREGROUND = 1
    SCREEN_LOCKED = 2
    AUTO = 0xff >> 1

    @staticmethod
    def parse(value: int) -> 'Condition':
        try:
            return Condition(value)
        except ValueError:
            return Condition.UNKNOWN


@enum.unique
class DeviceType(enum.IntEnum):
    UNKNOWN = 0
    IOT = 1
    MI_ROUTER = 2
    MI_SOUND_BOX = 3
    MI_LAPTOP = 4
    MI_TV = 5
    MI_PHONE = 6
    IOT_USER_ENV = 7

    @staticmethod
    def parse(value: int) -> 'DeviceType':
        try:
            return DeviceType(value)
        except ValueError:
            return DeviceType.UNKNOWN


@dataclasses.dataclass(frozen=True)
class _AttrValue:
    value: int
    is_text: bool | None = None


class DeviceAttribute(enum.Enum):
    UNKNOWN = _AttrValue(0)
    WIFI_MAC_ADDRESS = _AttrValue(1, False)
    BLUETOOTH_MAC_ADDRESS = _AttrValue(2, False)
    NIC_MAC_ADDRESS = _AttrValue(3, False)
    IP_ADDRESS = _AttrValue(4)
    PORT_1 = _AttrValue(5)
    PORT_2 = _AttrValue(6)
    PORT_3 = _AttrValue(7)
    ID_HASH = _AttrValue(8, False)
    DEVICE_TOKEN = _AttrValue(9)
    AUTH_TOKEN = _AttrValue(10)
    DEVICE_NAME = _AttrValue(11)
    DEVICE_TYPE = _AttrValue(12)
    APP_DATA = _AttrValue(13, False)
    USER_ENV_TOKEN = _AttrValue(14)
    SSID = _AttrValue(15, True)
    PASSWORD = _AttrValue(17, True)
    MODEL = _AttrValue(18, True)

    # IOT
    IOT_DEVICE_ID = _AttrValue(6, True)
    IOT_USER_MODEL = _AttrValue(7, True)
    IOT_NFC_EXTRA_DATA = _AttrValue(8, True)
    IOT_DEVICE_MAC = _AttrValue(2, True)
    IOT_APP_DATA = _AttrValue(13, True)

    # IOT_ENV
    IOT_ENV_USER_ID = _AttrValue(1, True)
    IOT_ENV_OWNER_UID = _AttrValue(2, True)
    IOT_ENV_REGION = _AttrValue(3, True)
    IOT_ENV_SCENE_NAME = _AttrValue(4, True)

    @property
    def attribute_value(self) -> int:
        return self.value.value

    @property
    def is_text(self) -> bool | None:
        return self.value.is_text

    def new_pair(self, value: str | bytes) -> tuple['DeviceAttribute', bytes]:
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

    @property
    def is_iot(self) -> bool:
        return self.name.startswith("IOT_") and not self.name.endswith("IOT_ENV_")

    @property
    def is_iot_env(self) -> bool:
        return self.name.startswith("IOT_ENV_")

    @property
    def attribute_name(self) -> str:
        if self.is_iot:
            return self.name[len("IOT_"):]
        elif self.is_iot_env:
            return self.name[len("IOT_ENV_"):]
        else:
            return self.name

    @staticmethod
    def parse(value: int) -> 'DeviceAttribute':
        for e in DeviceAttribute:
            if not e.is_iot and not e.is_iot_env and e.value == value:
                return e
        return DeviceAttribute.UNKNOWN

    @staticmethod
    def parse_iot(value: int) -> 'DeviceAttribute':
        for e in DeviceAttribute:
            if e.is_iot and e.value == value:
                return e
        return DeviceAttribute.UNKNOWN

    @staticmethod
    def parse_iot_env(value: int) -> 'DeviceAttribute':
        for e in DeviceAttribute:
            if e.is_iot_env and e.value == value:
                return e
        return DeviceAttribute.UNKNOWN


@dataclasses.dataclass(frozen=True)
class NfcTagRecord(BinaryData, abc.ABC):
    tag_type: int

    @abc.abstractmethod
    def _content_size(self) -> int:
        raise NotImplemented

    @abc.abstractmethod
    def _encode_content_into(self, buffer: BytesIO) -> None:
        raise NotImplemented

    def size(self) -> int:
        return (
                UINT8_BYTES_SIZE +  # type
                UINT16_BYTES_SIZE +  # content size
                self._content_size()  # content
        )

    def encode_into(self, buffer: BytesIO) -> None:
        write_uint8(buffer, self.tag_type)
        write_uint16(buffer, self.size())
        self._encode_content_into(buffer)

    @staticmethod
    def decode(buffer: BytesIO) -> 'NfcTagRecord':
        record_type = read_uint8(buffer)
        record_size = read_uint16(buffer) - UINT8_BYTES_SIZE - UINT16_BYTES_SIZE
        content = BytesIO(read_bytes(buffer, record_size))
        if record_type == _TYPE_DEVICE:
            return NfcTagDeviceRecord(
                device_type=read_uint16(content),
                flags=read_uint8(content),
                device_number=read_uint8(content),
                attributes_map=UInt16BytesMap.read_from(BytesIO(content.read()))
            )
        elif record_type == _TYPE_ACTION:
            return NfcTagActionRecord(
                action=read_uint16(content),
                condition=read_uint8(content),
                device_number=read_uint8(content),
                flags=read_uint8(content),
                condition_parameters=content.read()
            )
        else:
            raise ValueError(f"Unknown NfcTagRecord type {record_type}")


@dataclasses.dataclass(frozen=True)
class NfcTagActionRecord(NfcTagRecord):
    action: int
    condition: int
    device_number: int
    flags: int
    condition_parameters: bytes | None = dataclasses.field(default=None)
    tag_type: int = dataclasses.field(default=_TYPE_ACTION, init=False)

    @property
    def enum_action(self) -> Action:
        return Action.parse(self.action)

    @property
    def enum_condition(self) -> Condition:
        return Condition.parse(self.condition)

    def _content_size(self) -> int:
        return (
                UINT16_BYTES_SIZE +  # action
                UINT8_BYTES_SIZE +  # condition
                UINT8_BYTES_SIZE +  # device_number
                UINT8_BYTES_SIZE +  # flags
                (len(self.condition_parameters) if self.condition_parameters else 0)  # condition_parameters
        )

    def _encode_content_into(self, buffer: BytesIO) -> None:
        write_uint16(buffer, self.action)
        write_uint8(buffer, self.condition)
        write_uint8(buffer, self.device_number)
        write_uint8(buffer, self.flags)
        if self.condition_parameters:
            buffer.write(self.condition_parameters)


@dataclasses.dataclass(frozen=True)
class NfcTagDeviceRecord(NfcTagRecord):
    device_type: int
    flags: int
    device_number: int
    attributes_map: UInt16BytesMap
    tag_type: int = dataclasses.field(default=_TYPE_DEVICE, init=False)

    @property
    def enum_device_type(self) -> DeviceType:
        return DeviceType.parse(self.device_type)

    @property
    def enum_attributes_map(self) -> OrderedDict[DeviceAttribute, bytes]:
        return OrderedDict((DeviceAttribute.parse(k), v) for k, v in self.attributes_map.items())

    def get_all_attributes_map(self, action: Action, ndef_type: XiaomiNdefTNF) -> OrderedDict[DeviceAttribute, bytes]:
        def _map_key(key: int) -> DeviceAttribute:
            match ndef_type:
                case XiaomiNdefTNF.SMART_HOME:
                    match action:
                        case Action.IOT:
                            return DeviceAttribute.parse_iot(key)
                        case Action.IOT_ENV:
                            return DeviceAttribute.parse_iot_env(key)
                        case _:
                            return DeviceAttribute.parse(key)
                case XiaomiNdefTNF.MI_CONNECT_SERVICE | _:
                    return DeviceAttribute.parse(key)

        result_map = OrderedDict((_map_key(k), v) for k, v in self.attributes_map.items())
        if DeviceAttribute.APP_DATA in result_map:
            app_data_bytes = result_map[DeviceAttribute.APP_DATA]
            value_type = self.get_app_data_value_type(app_data_bytes, action, ndef_type)
            if value_type == AppDataValueType.ATTRIBUTES_MAP:
                result_map.update(self.decode_app_data_value_map(app_data_bytes))
        return result_map

    @staticmethod
    def get_app_data_value_type(app_data: bytes, action: Action, ndef_type: XiaomiNdefTNF) -> AppDataValueType:
        if ndef_type == XiaomiNdefTNF.SMART_HOME and (action == Action.IOT or action == Action.IOT_ENV):
            return AppDataValueType.IOT_ACTION
        elif ndef_type == XiaomiNdefTNF.MI_CONNECT_SERVICE and app_data.startswith(_PREFIX_APP_DATA_MAP):
            return AppDataValueType.ATTRIBUTES_MAP
        else:
            return AppDataValueType.UNKNOWN

    @staticmethod
    def new_attributes_map(data: Mapping[DeviceAttribute, bytes] | Iterable[tuple[DeviceAttribute, bytes]]) -> UInt16BytesMap:
        if isinstance(data, Mapping):
            items = data.items()
        elif isinstance(data, Iterable):
            items = data
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        items: Iterable[tuple[DeviceAttribute, bytes]]
        return UInt16BytesMap((k.attribute_value, v) for k, v in items)

    @staticmethod
    def decode_attributes_map(buffer: bytes) -> OrderedDict[DeviceAttribute, bytes]:
        bytes_map = UInt16BytesMap.read_from(BytesIO(buffer))
        return OrderedDict((DeviceAttribute.parse(k), v) for k, v in bytes_map.items())

    @staticmethod
    def decode_app_data_value_map(buffer: bytes) -> OrderedDict[DeviceAttribute, bytes]:
        if not buffer.startswith(_PREFIX_APP_DATA_MAP):
            raise ValueError("Not an valid DeviceAttribute.APP_DATA map byte array")
        return NfcTagDeviceRecord.decode_attributes_map(buffer)

    @staticmethod
    def encode_app_data_value_map(data: OrderedDict[DeviceAttribute, bytes]) -> bytes:
        return _PREFIX_APP_DATA_MAP + NfcTagDeviceRecord.new_attributes_map(data).encode()

    def _content_size(self) -> int:
        return (
                UINT16_BYTES_SIZE +  # device_type
                UINT8_BYTES_SIZE +  # flags
                UINT8_BYTES_SIZE +  # device_number
                self.attributes_map.size()  # attributes_map
        )

    def _encode_content_into(self, buffer: BytesIO) -> None:
        write_uint16(buffer, self.device_type)
        write_uint8(buffer, self.flags)
        write_uint8(buffer, self.device_number)
        self.attributes_map.encode_into(buffer)


@dataclasses.dataclass(frozen=True)
class NfcTagAppData(AppData):
    major_version: int
    minor_version: int
    write_time: int
    flags: int
    records: tuple[NfcTagRecord, ...]

    def first_device_record(self) -> NfcTagDeviceRecord | None:
        for record in self.records:
            if isinstance(record, NfcTagDeviceRecord):
                return record
        return None

    def first_action_record(self) -> NfcTagActionRecord | None:
        for record in self.records:
            if isinstance(record, NfcTagActionRecord):
                return record
        return None

    def first_enum_action(self) -> Action:
        record = self.first_action_record()
        return Action.parse(record.action) if record is not None else Action.UNKNOWN

    def first_action_value(self) -> int | None:
        record = self.first_action_record()
        return record.action if record is not None else None

    def first_device_enum_attributes_map(self) -> OrderedDict[DeviceAttribute, bytes]:
        record = self.first_device_record()
        return record.enum_attributes_map if record is not None else OrderedDict()

    def size(self) -> int:
        return (
                UINT8_BYTES_SIZE +  # majorVersion
                UINT8_BYTES_SIZE +  # minor_version
                UINT32_BYTES_SIZE +  # write_time
                UINT8_BYTES_SIZE +  # flags
                UINT8_BYTES_SIZE +  # records size
                sum(record.size() for record in self.records)  # records
        )

    def encode_into(self, buffer: BytesIO) -> None:
        write_uint8(buffer, self.major_version)
        write_uint8(buffer, self.minor_version)
        write_uint32(buffer, self.write_time)
        write_uint8(buffer, self.flags)
        write_uint8(buffer, len(self.records))
        for record in self.records:
            record.encode_into(buffer)

    @staticmethod
    def decode(buffer: BytesIO) -> 'NfcTagAppData':
        return NfcTagAppData(
            major_version=read_uint8(buffer),
            minor_version=read_uint8(buffer),
            write_time=read_uint32(buffer),
            flags=read_uint8(buffer),
            records=tuple(NfcTagRecord.decode(buffer) for _ in range(read_uint8(buffer)))
        )
