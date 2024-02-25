from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Payload(_message.Message):
    __slots__ = ("versionMajor", "versionMinor", "apps", "flags", "name", "idHash", "deviceType", "securityMode", "appsData", "supportSetting", "currentSetting", "wifiMac", "appIds", "commData", "ziped", "wiredMac", "btMac")
    VERSIONMAJOR_FIELD_NUMBER: _ClassVar[int]
    VERSIONMINOR_FIELD_NUMBER: _ClassVar[int]
    APPS_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IDHASH_FIELD_NUMBER: _ClassVar[int]
    DEVICETYPE_FIELD_NUMBER: _ClassVar[int]
    SECURITYMODE_FIELD_NUMBER: _ClassVar[int]
    APPSDATA_FIELD_NUMBER: _ClassVar[int]
    SUPPORTSETTING_FIELD_NUMBER: _ClassVar[int]
    CURRENTSETTING_FIELD_NUMBER: _ClassVar[int]
    WIFIMAC_FIELD_NUMBER: _ClassVar[int]
    APPIDS_FIELD_NUMBER: _ClassVar[int]
    COMMDATA_FIELD_NUMBER: _ClassVar[int]
    ZIPED_FIELD_NUMBER: _ClassVar[int]
    WIREDMAC_FIELD_NUMBER: _ClassVar[int]
    BTMAC_FIELD_NUMBER: _ClassVar[int]
    versionMajor: int
    versionMinor: int
    apps: bytes
    flags: bytes
    name: str
    idHash: bytes
    deviceType: int
    securityMode: int
    appsData: _containers.RepeatedScalarFieldContainer[bytes]
    supportSetting: _containers.RepeatedScalarFieldContainer[bytes]
    currentSetting: _containers.RepeatedScalarFieldContainer[bytes]
    wifiMac: str
    appIds: _containers.RepeatedScalarFieldContainer[int]
    commData: int
    ziped: bool
    wiredMac: str
    btMac: str
    def __init__(self, versionMajor: _Optional[int] = ..., versionMinor: _Optional[int] = ..., apps: _Optional[bytes] = ..., flags: _Optional[bytes] = ..., name: _Optional[str] = ..., idHash: _Optional[bytes] = ..., deviceType: _Optional[int] = ..., securityMode: _Optional[int] = ..., appsData: _Optional[_Iterable[bytes]] = ..., supportSetting: _Optional[_Iterable[bytes]] = ..., currentSetting: _Optional[_Iterable[bytes]] = ..., wifiMac: _Optional[str] = ..., appIds: _Optional[_Iterable[int]] = ..., commData: _Optional[int] = ..., ziped: bool = ..., wiredMac: _Optional[str] = ..., btMac: _Optional[str] = ...) -> None: ...

class Container(_message.Message):
    __slots__ = ("data", "sequenceId")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SEQUENCEID_FIELD_NUMBER: _ClassVar[int]
    data: Payload
    sequenceId: int
    def __init__(self, data: _Optional[_Union[Payload, _Mapping]] = ..., sequenceId: _Optional[int] = ...) -> None: ...
