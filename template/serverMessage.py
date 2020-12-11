import struct
import json

class ServerMessage:

    def __init__(self):
        self.operationcode = 99
        self.filesize = None
        self.blocksize = None
        self.totalBlockNumber = None
        self.md5 = None
        self.blockindex = None
        self.blockLength = None

    def infromationHeader(self,operationCode,blocksize,blockNumber,md5,filesize):
        jsonheader = {
            "operationCode": operationCode,
            "blocksize": blocksize,
            "blockNumber": blockNumber,
            "md5": md5,
            "filesize":filesize
        }
        informationheader = self.json_encode(jsonheader)
        headerlength = struct.pack("I",len(informationheader))
        header = headerlength + informationheader
        return header

    def nofileHeader(self,operationCode):
        jsonheader = {
            "operationCode": operationCode
        }
        nofileheader = self.json_encode(jsonheader)
        headerlength = struct.pack("I",len(nofileheader))
        header = headerlength + nofileheader


    def json_encode(self,jsonheader):
        return json.dumps(jsonheader,ensure_ascii=False).encode("utf-8")
