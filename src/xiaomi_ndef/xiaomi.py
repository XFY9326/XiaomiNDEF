from . import handoff
from . import tag
from .base import UInt8BytesMap, UInt16BytesMap
from .nfc import XiaomiNfcPayload, V1NfcProtocol, V2NfcProtocol, HandoffNfcProtocol
from .tnf import XiaomiNdefTNF


def new_empty_mi_tap(
        write_time: int
) -> tuple[XiaomiNdefTNF, XiaomiNfcPayload[tag.NfcTagAppData]]:
    return XiaomiNdefTNF.SMART_HOME, XiaomiNfcPayload(
        major_version=1,
        minor_version=2,
        id_hash=0,
        protocol=V1NfcProtocol,
        appData=tag.NfcTagAppData(
            major_version=1,
            minor_version=0,
            write_time=write_time,
            flags=0,
            records=(
                tag.NfcTagDeviceRecord(
                    device_type=tag.DeviceType.IOT,
                    flags=0,
                    device_number=0,
                    attributes_map=UInt16BytesMap()
                ),
                tag.NfcTagActionRecord(
                    action=tag.Action.EMPTY,
                    condition=tag.Condition.AUTO,
                    device_number=0,
                    flags=0
                )
            )
        )
    )


def new_mi_tap_sound_box(
        write_time: int,
        wifi_mac: bytes | None,
        bluetooth_mac: bytes,
        model: str | None
) -> tuple[XiaomiNdefTNF, XiaomiNfcPayload[tag.NfcTagAppData]]:
    attr_map = [
        tag.DeviceAttribute.BLUETOOTH_MAC_ADDRESS.new_pair(bluetooth_mac)
    ]
    if wifi_mac is not None:
        attr_map.append(tag.DeviceAttribute.WIFI_MAC_ADDRESS.new_pair(wifi_mac))
    if model is not None:
        attr_map.append(tag.DeviceAttribute.MODEL.new_pair(model))
    return XiaomiNdefTNF.MI_CONNECT_SERVICE, XiaomiNfcPayload(
        major_version=1,
        minor_version=2,
        id_hash=0,
        protocol=V1NfcProtocol,
        appData=tag.NfcTagAppData(
            major_version=1,
            minor_version=0,
            write_time=write_time,
            flags=0,
            records=(
                tag.NfcTagDeviceRecord(
                    device_type=tag.DeviceType.MI_SOUND_BOX,
                    flags=0,
                    device_number=0,
                    attributes_map=tag.NfcTagDeviceRecord.new_attributes_map(attr_map)
                ),
                tag.NfcTagActionRecord(
                    action=tag.Action.AUTO,
                    condition=tag.Condition.AUTO,
                    device_number=0,
                    flags=0
                )
            )
        )
    )


def new_circulate(
        write_time: int,
        device_type: tag.DeviceType,
        wifi_mac: bytes,
        bluetooth_mac: bytes
) -> tuple[XiaomiNdefTNF, XiaomiNfcPayload[tag.NfcTagAppData]]:
    return XiaomiNdefTNF.MI_CONNECT_SERVICE, XiaomiNfcPayload(
        major_version=1,
        minor_version=11,
        id_hash=0,
        protocol=V2NfcProtocol,
        appData=tag.NfcTagAppData(
            major_version=1,
            minor_version=0,
            write_time=write_time,
            flags=0,
            records=(
                tag.NfcTagDeviceRecord(
                    device_type=device_type,
                    flags=0,
                    device_number=0,
                    attributes_map=tag.NfcTagDeviceRecord.new_attributes_map([
                        tag.DeviceAttribute.WIFI_MAC_ADDRESS.new_pair(wifi_mac),
                        tag.DeviceAttribute.BLUETOOTH_MAC_ADDRESS.new_pair(bluetooth_mac)
                    ])
                ),
                tag.NfcTagActionRecord(
                    action=tag.Action.CUSTOM,
                    condition=tag.Condition.AUTO,
                    device_number=0,
                    flags=0
                )
            )
        )
    )


def new_handoff(
        device_type: handoff.DeviceType,
        payloads_map: UInt8BytesMap
) -> tuple[XiaomiNdefTNF, XiaomiNfcPayload[handoff.HandoffAppData]]:
    return XiaomiNdefTNF.MI_CONNECT_SERVICE, XiaomiNfcPayload(
        major_version=1,
        minor_version=13,
        id_hash=None,
        protocol=HandoffNfcProtocol,
        appData=handoff.HandoffAppData(
            major_version=0x27,
            minor_version=0x17,
            device_type=device_type,
            attributes_map=UInt8BytesMap(),
            action="TAG_DISCOVERED",
            payloads_map=payloads_map
        )
    )


def new_handoff_screen_mirror(
        device_type: handoff.DeviceType,
        bluetooth_mac: str,
        enable_lyra: bool
) -> tuple[XiaomiNdefTNF, XiaomiNfcPayload[handoff.HandoffAppData]]:
    payloads = [
        handoff.PayloadKey.ACTION_SUFFIX.new_pair("MIRROR"),
        handoff.PayloadKey.BLUETOOTH_MAC.new_pair(bluetooth_mac)
    ]
    if enable_lyra:
        payloads.append(handoff.PayloadKey.EXT_ABILITY.new_pair(b"\x00\x00\x00\x01"))
    return new_handoff(
        device_type=device_type,
        payloads_map=handoff.HandoffAppData.new_payloads_map(payloads)
    )


def new_handoff_tv_cast(
        device_type: handoff.DeviceType,
        wifi_mac: str,
        bluetooth_mac: str
) -> tuple[XiaomiNdefTNF, XiaomiNfcPayload[handoff.HandoffAppData]]:
    return new_handoff(
        device_type=device_type,
        payloads_map=handoff.HandoffAppData.new_payloads_map([
            handoff.PayloadKey.ACTION_SUFFIX.new_pair("TVCAST"),
            handoff.PayloadKey.BLUETOOTH_MAC.new_pair(wifi_mac),
            handoff.PayloadKey.BLUETOOTH_MAC.new_pair(bluetooth_mac)
        ])
    )
