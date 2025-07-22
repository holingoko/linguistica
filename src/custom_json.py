import json

from src.qt import *


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QByteArray):
            return {
                "_type": "QByteArray",
                "value": bytes(obj.toHex()).decode("utf-8"),
            }
        return super().default(obj)


class Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self,
            object_hook=self.object_hook,
            *args,
            **kwargs,
        )

    @staticmethod
    def object_hook(obj):
        if not "_type" in obj:
            return obj
        _type = obj["_type"]
        value = obj["value"]
        if _type == "QByteArray":
            return QByteArray.fromHex(bytes(value, encoding="utf-8"))
        return obj
