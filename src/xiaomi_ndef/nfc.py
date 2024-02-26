import abc
import dataclasses
from io import BytesIO
from typing import TypeVar, Generic

from .base import AppData
from .handoff import HandoffAppData
from .tag import NfcTagAppData

_T = TypeVar("_T", bound=AppData)

_FLAG_V1 = 0
_FLAG_V2 = 1
_FLAG_HANDOFF = 3


@dataclasses.dataclass(frozen=True)
@abc.abstractmethod
class XiaomiNfcProtocol(Generic[_T]):
    flags: int

    @abc.abstractmethod
    def decode(self, data: bytes) -> _T:
        raise NotImplemented

    @staticmethod
    def parse(value: int) -> 'XiaomiNfcProtocol':
        if value == _FLAG_V1:
            return V1NfcProtocol
        elif value == _FLAG_V2:
            return V2NfcProtocol
        elif value == _FLAG_HANDOFF:
            return HandoffNfcProtocol
        else:
            raise ValueError(f"Unknown protocol flag {value}")


@dataclasses.dataclass(frozen=True)
class _V1NfcProtocol(XiaomiNfcProtocol[NfcTagAppData]):
    flags: int = dataclasses.field(default=_FLAG_V1, init=False)

    def decode(self, data: bytes) -> NfcTagAppData:
        return NfcTagAppData.decode(BytesIO(data))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "V1"


@dataclasses.dataclass(frozen=True)
class _V2NfcProtocol(XiaomiNfcProtocol[NfcTagAppData]):
    flags: int = dataclasses.field(default=_FLAG_V2, init=False)

    def decode(self, data: bytes) -> NfcTagAppData:
        return NfcTagAppData.decode(BytesIO(data))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "V2"


@dataclasses.dataclass(frozen=True)
class _HandoffNfcProtocol(XiaomiNfcProtocol[HandoffAppData]):
    flags: int = dataclasses.field(default=_FLAG_HANDOFF, init=False)

    def decode(self, data: bytes) -> HandoffAppData:
        return HandoffAppData.decode(BytesIO(data))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "Handoff"


V1NfcProtocol: XiaomiNfcProtocol[NfcTagAppData] = _V1NfcProtocol()
V2NfcProtocol: XiaomiNfcProtocol[NfcTagAppData] = _V2NfcProtocol()
HandoffNfcProtocol: XiaomiNfcProtocol[HandoffAppData] = _HandoffNfcProtocol()


@dataclasses.dataclass(frozen=True)
class XiaomiNfcPayload(Generic[_T]):
    major_version: int
    minor_version: int
    id_hash: int | None
    protocol: XiaomiNfcProtocol[_T]
    appData: _T
