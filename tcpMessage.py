import struct
import json
import base64


class tcpMessage:
    message_type = 0
    index = 0
    BLOCK_MESSAGE = 1
    WAKE = 2
    DOWNLOAD = 5
    NEW_TICKET = 3
    SUCCESS_ACCEPT = 4
    MD5 = 6

    def __init__(self, message_type, message, index=0):
        self.message_type = message_type
        self.index = index
        self.message = message

    def toJson(self):
        jsons = json.dumps({"message_type": self.message_type,
                            "index": self.index,
                            "message": self.message
                            }, default=lambda x: base64.b64encode(x).decode('utf-8') if isinstance(x, (
        bytes, bytearray)) else x.__dict__, indent=4)
        # File Bytes to Base64 Bytes then to String
        return struct.pack("I", len(jsons)) + jsons.encode('utf-8')


if __name__ == "__main__":
    print(tcpMessage(0, {}, 0).toJson())
