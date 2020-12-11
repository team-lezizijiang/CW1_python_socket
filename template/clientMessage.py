import struct
import json


class Message: # a message class for client and server to communicate

    def __init__(self, operationCode, filename, blockIndex = None):
        self.operationCode = operationCode # operation code sent by client
        self.filename = filename # filename
        self.blockIndex = blockIndex # requested block requested by client, should be None if client only wants the file information



    def constructClientHeader(self):

        jsonHeader = {
            "operationCode": self.operationCode,
            "filename": self.filename,
            "blockIndex": self.blockIndex
        }

        jsonHeaderBytes = self.json_enocde(jsonHeader)
        headerlength = struct.pack("I", len(jsonHeaderBytes)) # this int is the length of jsonheader in bytes
        header = headerlength + jsonHeaderBytes
        return header


    def json_enocde(self,jsonheader):
        return json.dumps(jsonheader, ensure_ascii=False).encode("utf-8")
