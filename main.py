from xiaomi_ndef import *

BYTES_DATA = bytes.fromhex(
    "0a4b0801100d2201032a094d492d4e4643544147380f4a3127" +
    "1700000003000e5441475f444953434f564552454465064d49" +
    "52524f52011130303a30303a30303a30303a30303a30306a02" +
    "fa7f"
)
NEW_DATA = tag.NfcTagAppData(
    major_version=1,
    minor_version=0,
    write_time=0000000000,
    flags=0,
    records=(
        tag.NfcTagDeviceRecord(
            device_type=tag.DeviceType.MI_SOUND_BOX,
            flags=0,
            device_number=0,
            attributes_map=tag.NfcTagDeviceRecord.new_attributes_map(
                [
                    tag.DeviceAttribute.BLUETOOTH_MAC_ADDRESS.new_pair(b"\x00\x00\x00\x00\x00\x01")
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


def main() -> None:
    mi_connect_data = MiConnectData.parse(BYTES_DATA)
    print(mi_connect_data)
    nfc_protocol = mi_connect_data.get_nfc_protocol()
    print(nfc_protocol)
    nfc_payload = mi_connect_data.to_xiaomi_nfc_payload(nfc_protocol)
    print(nfc_payload)
    print(NEW_DATA)
    print(NEW_DATA.encode().hex())
    print(
        MiConnectData.from_nfc_payload(
            XiaomiNfcPayload(
                major_version=1,
                minor_version=0,
                id_hash=None,
                protocol=V1NfcProtocol,
                appData=NEW_DATA
            )
        ).to_bytes().hex()
    )


if __name__ == "__main__":
    main()
