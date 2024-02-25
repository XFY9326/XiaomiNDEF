import enum


@enum.unique
class XiaomiNdefTNF(str, enum.Enum):
    UNKNOWN = ""
    SMART_HOME = "com.xiaomi.smarthome:externaltype"
    MI_CONNECT_SERVICE = "com.xiaomi.mi_connect_service:externaltype"

    def to_bytes(self) -> bytes:
        return self.value().encode("ascii")

    @staticmethod
    def parse(value: str | bytes) -> 'XiaomiNdefTNF':
        try:
            if isinstance(value, bytes):
                return XiaomiNdefTNF(value.decode("ascii"))
            elif isinstance(value, str):
                return XiaomiNdefTNF(value)
        except ValueError | UnicodeDecodeError:
            pass
        return XiaomiNdefTNF.UNKNOWN
