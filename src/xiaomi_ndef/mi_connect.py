from typing import TypeVar

# noinspection PyPackageRequirements
from google.protobuf import json_format

from .base import AppData
from .nfc import XiaomiNfcPayload, XiaomiNfcProtocol
from .proto.MiConnectProtocol_pb2 import Container, Payload

_T = TypeVar("_T", bound=AppData)

_PAYLOAD_NAME = "MI-NFCTAG"
_PAYLOAD_APP_ID = 16378
_PAYLOAD_DEVICE_TYPE = 15


class MiConnectData:

    def __init__(self, container: Container) -> None:
        self._container: Container = container

    @property
    def is_valid_nfc_payload(self) -> bool:
        return _PAYLOAD_APP_ID in self._container.data.appIds and \
            _PAYLOAD_DEVICE_TYPE == self._container.data.deviceType and \
            _PAYLOAD_NAME == self._container.data.name and \
            len(self._container.data.flags) > 0 and \
            len(self._container.data.appsData) > 0

    def get_nfc_protocol(self) -> XiaomiNfcProtocol:
        if not self.is_valid_nfc_payload:
            raise ValueError("Invalid MiConnectProtocol.Payload for NFC")
        return XiaomiNfcProtocol.parse(self._container.data.flags[0])

    def to_xiaomi_nfc_payload(self, protocol: XiaomiNfcProtocol[_T]) -> XiaomiNfcPayload[_T]:
        if not self.is_valid_nfc_payload:
            raise ValueError("Invalid MiConnectProtocol.Payload for NFC")
        nfc_protocol = self.get_nfc_protocol()
        if nfc_protocol != protocol:
            raise ValueError(f"Wrong protocol {protocol}, excepted {nfc_protocol}")
        id_hash = self._container.data.idHash
        return XiaomiNfcPayload(
            major_version=self._container.data.versionMajor,
            minor_version=self._container.data.versionMinor,
            id_hash=int.from_bytes(id_hash, byteorder="big", signed=False) if id_hash else None,
            protocol=nfc_protocol,
            appData=nfc_protocol.decode(self._container.data.appsData[0]),
        )

    def to_bytes(self) -> bytes:
        return self._container.SerializeToString()

    @staticmethod
    def parse(data: bytes) -> 'MiConnectData':
        return MiConnectData(Container.FromString(data))

    @staticmethod
    def from_nfc_payload(payload: XiaomiNfcPayload) -> 'MiConnectData':
        mi_connect_payload = Payload(
            versionMajor=payload.major_version,
            versionMinor=payload.minor_version,
            flags=payload.protocol.flags.to_bytes(length=1, byteorder="big", signed=False),
            name=_PAYLOAD_NAME,
            deviceType=_PAYLOAD_DEVICE_TYPE,
            appIds=[_PAYLOAD_APP_ID],
            appsData=[payload.appData.encode()],
            idHash=payload.id_hash.to_bytes(length=1, byteorder="big", signed=False) if payload.id_hash is not None else None,
        )
        mi_connect_container = Container(data=mi_connect_payload)
        return MiConnectData(mi_connect_container)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "MiConnectData" + json_format.MessageToJson(self._container, indent=None, ensure_ascii=False)
