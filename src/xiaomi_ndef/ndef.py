from pyndef import NdefMessage, NdefTNF, NdefRecord

from .mi_connect import MiConnectData
from .nfc import XiaomiNfcPayload
from .tnf import XiaomiNdefTNF

_URI_MI_HOME = "https://g.home.mi.com"
_PKG_MI_CONNECT_SERVICE = "com.xiaomi.mi_connect_service"
_PKG_SMART_HOME = "com.xiaomi.smarthome"


def get_xiami_ndef_payload_type(msg: NdefMessage) -> XiaomiNdefTNF:
    for record in msg.records:
        if record.tnf == NdefTNF.EXTERNAL_TYPE:
            payload_type = XiaomiNdefTNF.parse(record.record_type)
            if payload_type != XiaomiNdefTNF.UNKNOWN:
                return payload_type
    return XiaomiNdefTNF.UNKNOWN


def get_xiami_ndef_payload_bytes(msg: NdefMessage, payload_type: XiaomiNdefTNF) -> bytes | None:
    if payload_type == XiaomiNdefTNF.UNKNOWN:
        raise ValueError("Unknown payload type")
    for record in msg.records:
        if record.tnf == NdefTNF.EXTERNAL_TYPE:
            if XiaomiNdefTNF.parse(record.record_type) == payload_type:
                return record.payload
    return None


def new_xiaomi_ndef_record(payload_type: XiaomiNdefTNF, payload: XiaomiNfcPayload) -> NdefRecord:
    if payload_type == XiaomiNdefTNF.UNKNOWN:
        raise ValueError("Unknown payload type")
    return NdefRecord(
        tnf=NdefTNF.EXTERNAL_TYPE,
        record_type=payload_type.to_bytes(),
        record_id=None,
        payload=MiConnectData.from_nfc_payload(payload).to_bytes()
    )


def new_mi_tap_ndef_message(record: NdefRecord) -> NdefMessage:
    return NdefMessage(
        record,
        NdefRecord.create_application_record(_PKG_SMART_HOME),
        NdefRecord.create_application_record(_PKG_MI_CONNECT_SERVICE),
        NdefRecord.create_uri(_URI_MI_HOME),
    )
