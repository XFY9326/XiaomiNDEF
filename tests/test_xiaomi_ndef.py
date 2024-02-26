import unittest
from typing import TypeVar

from xiaomi_ndef import handoff
from xiaomi_ndef import nfc
from xiaomi_ndef import tag
from xiaomi_ndef.base import UInt8BytesMap, AppData
from xiaomi_ndef.mi_connect import MiConnectData

_T = TypeVar("_T", bound=AppData)


class XiaomiNfcTestCase(unittest.TestCase):
    _TEST_PAYLOAD_V1_BYTES = bytes.fromhex(
        "0a63080110022201002a094d492d4e4643544147320100380f" +
        "4a460100646e0c840002010036000300000001000600000000" +
        "000000020006000000000000001200177869616f6d692e7769" +
        "6669737065616b65722e783038630200087fff7f00006a02fa" +
        "7f"
    )
    _TEST_PAYLOAD_V2_BYTES = bytes.fromhex(
        "0a480801100b2201012a094d492d4e4643544147320100380f" +
        "4a2b010063034f6b000201001b000300000001000611111111" +
        "111000020006111111111111020008000d7f00006a02fa7f"
    )
    _TEST_PAYLOAD_HANDOFF_BYTES = bytes.fromhex(
        "0a4b0801100d2201032a094d492d4e4643544147380f4a3127" +
        "1700000003000e5441475f444953434f564552454465064d49" +
        "52524f52011130303a30303a30303a30303a30303a30306a02" +
        "fa7f"
    )

    _TEST_PAYLOAD_V1 = tag.NfcTagAppData(
        major_version=1,
        minor_version=0,
        write_time=1684933764,
        flags=0,
        records=(
            tag.NfcTagDeviceRecord(
                device_type=tag.DeviceType.MI_SOUND_BOX,
                flags=0,
                device_number=0,
                attributes_map=tag.NfcTagDeviceRecord.new_attributes_map(
                    [
                        tag.DeviceAttribute.WIFI_MAC_ADDRESS.new_pair(b"\x00\x00\x00\x00\x00\x00"),
                        tag.DeviceAttribute.BLUETOOTH_MAC_ADDRESS.new_pair(b"\x00\x00\x00\x00\x00\x00"),
                        tag.DeviceAttribute.MODEL.new_pair("xiaomi.wifispeaker.x08c")
                    ]
                )
            ),
            tag.NfcTagActionRecord(
                action=tag.Action.AUTO,
                condition=tag.Condition.AUTO,
                device_number=0,
                flags=0,
                condition_parameters=None,
            )
        )
    )
    _TEST_PAYLOAD_V2 = tag.NfcTagAppData(
        major_version=1,
        minor_version=0,
        write_time=1661161323,
        flags=0,
        records=(
            tag.NfcTagDeviceRecord(
                device_type=tag.DeviceType.MI_SOUND_BOX,
                flags=0,
                device_number=0,
                attributes_map=tag.NfcTagDeviceRecord.new_attributes_map(
                    [
                        tag.DeviceAttribute.WIFI_MAC_ADDRESS.new_pair(b"\x11\x11\x11\x11\x11\x10"),
                        tag.DeviceAttribute.BLUETOOTH_MAC_ADDRESS.new_pair(b"\x11\x11\x11\x11\x11\x11")
                    ]
                )
            ),
            tag.NfcTagActionRecord(
                action=tag.Action.CUSTOM,
                condition=tag.Condition.AUTO,
                device_number=0,
                flags=0,
                condition_parameters=None,
            )
        )
    )
    _TEST_PAYLOAD_HANDOFF = handoff.HandoffAppData(
        major_version=0x27,
        minor_version=0x17,
        device_type=handoff.DeviceType.PC,
        attributes_map=UInt8BytesMap(),
        action="TAG_DISCOVERED",
        payloads_map=handoff.HandoffAppData.new_payloads_map(
            [
                handoff.PayloadKey.ACTION_SUFFIX.new_pair("MIRROR"),
                handoff.PayloadKey.BLUETOOTH_MAC.new_pair("00:00:00:00:00:00")
            ]
        )
    )

    def _test_protocol(self, protocol: nfc.XiaomiNfcProtocol[_T], data: bytes) -> nfc.XiaomiNfcPayload[_T]:
        mi_connect_data = MiConnectData.parse(data)
        self.assertTrue(mi_connect_data.is_valid_nfc_payload)

        nfc_protocol = mi_connect_data.get_nfc_protocol()
        self.assertEqual(protocol, nfc_protocol)

        return mi_connect_data.to_xiaomi_nfc_payload(nfc_protocol)

    def test_v1_protocol(self) -> None:
        payload = self._test_protocol(nfc.V1NfcProtocol, self._TEST_PAYLOAD_V1_BYTES)
        self.assertEqual(self._TEST_PAYLOAD_V1_BYTES, MiConnectData.from_nfc_payload(payload).to_bytes())
        self.assertEqual(self._TEST_PAYLOAD_V1.encode(), payload.appData.encode())
        self.assertEqual(len(self._TEST_PAYLOAD_V1.encode()), payload.appData.size())

    def test_v2_protocol(self) -> None:
        payload = self._test_protocol(nfc.V2NfcProtocol, self._TEST_PAYLOAD_V2_BYTES)
        self.assertEqual(self._TEST_PAYLOAD_V2_BYTES, MiConnectData.from_nfc_payload(payload).to_bytes())
        self.assertEqual(self._TEST_PAYLOAD_V2.encode(), payload.appData.encode())
        self.assertEqual(len(self._TEST_PAYLOAD_V2.encode()), payload.appData.size())

    def test_handoff_protocol(self) -> None:
        payload = self._test_protocol(nfc.HandoffNfcProtocol, self._TEST_PAYLOAD_HANDOFF_BYTES)
        self.assertEqual(self._TEST_PAYLOAD_HANDOFF_BYTES, MiConnectData.from_nfc_payload(payload).to_bytes())
        self.assertEqual(self._TEST_PAYLOAD_HANDOFF.encode(), payload.appData.encode())
        self.assertEqual(len(self._TEST_PAYLOAD_HANDOFF.encode()), payload.appData.size())


if __name__ == "__main__":
    unittest.main()
