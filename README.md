# Xiaomi NDEF

![!python-versions](https://img.shields.io/badge/Python-3.10-blue)
[![Pypi](https://img.shields.io/pypi/v/xiaomi_ndef?color=orange)](https://pypi.org/project/xiaomi_ndef/)

[![Test](https://github.com/XFY9326/XiaomiNDEF/actions/workflows/test.yml/badge.svg)](https://github.com/XFY9326/XiaomiNDEF/actions/workflows/test.yml)
[![Release](https://github.com/XFY9326/XiaomiNDEF/actions/workflows/release.yml/badge.svg)](https://github.com/XFY9326/XiaomiNDEF/actions/workflows/release.yml)

Encode and decode NDEF message using Xiaomi NFC protocol.

## Usage

```python
from pyndef import NdefMessage

from xiaomi_ndef import MiConnectData, XiaomiNfcPayload, V2NfcProtocol
from xiaomi_ndef import ndef, xiaomi, handoff, tag

# Example
NDEF_MSG_BYTES = b"..."

# Parse ndef
ndef_msg = NdefMessage.parse(NDEF_MSG_BYTES)

ndef_type = ndef.get_xiami_ndef_payload_type(ndef_msg)
ndef_bytes = ndef.get_xiami_ndef_payload_bytes(ndef_msg, ndef_type)

# Parse ndef payload
mi_connect_data = MiConnectData.parse(ndef_bytes)
nfc_protocol = mi_connect_data.get_nfc_protocol()
nfc_payload = mi_connect_data.to_xiaomi_nfc_payload(nfc_protocol)

# Build new screen mirror record
handoff_ndef_type, handoff_payload = xiaomi.new_handoff_screen_mirror(
    device_type=handoff.DeviceType.PC,
    bluetooth_mac="00:00:00:00:00:00",
    enable_lyra=True
)
handoff_record = ndef.new_xiaomi_ndef_record(handoff_ndef_type, handoff_payload)

# Build new ndef msg
handoff_msg = NdefMessage(handoff_record)
print(handoff_msg.to_bytes().hex())

# Customize xiaomi ndef
XiaomiNfcPayload(
    major_version=1,
    minor_version=11,
    id_hash=0,
    protocol=V2NfcProtocol,
    appData=tag.NfcTagAppData(
        major_version=1,
        minor_version=0,
        write_time=1666666666,
        flags=0,
        records=(
            tag.NfcTagDeviceRecord(
                device_type=tag.DeviceType.MI_SOUND_BOX,
                flags=0,
                device_number=0,
                attributes_map=tag.NfcTagDeviceRecord.new_attributes_map([
                    tag.DeviceAttribute.WIFI_MAC_ADDRESS.new_pair("00:00:00:00:00:00"),
                    tag.DeviceAttribute.BLUETOOTH_MAC_ADDRESS.new_pair("00:00:00:00:00:01")
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
```

## License

```text
MIT License

Copyright (c) 2024 XFY9326

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
