import json


class Ticket:
    blockStateList = list()
    peer = 0
    blockNumber = 0
    blockSize = 0
    lastBlockSize = 0

    def __init__(self, file, size, peer):
        self.sharedFile = file
        self.blockSize = size
        self.peer = peer
        file_size = file.size
        while file_size > 0:
            file_size -= size
            self.blockNumber += 1
        self.lastBlockSize = file_size + size
        self.blockStateList = [0 for i in range(self.blockNumber)]

    def update(self, index):
        self.blockStateList[index] = 1  # 1表示传输成功

    def find_first_untraverse_block(self):
        for i in range(len(self.blockStateList)):
            if self.blockStateList[i] == 0:
                return i
        return -1

    def __eq__(self, other):
        return self.sharedFile.mtime == other.sharedFile.mtime and self.sharedFile.size == other.sharedFile.size

    def __dict__(self):
        return {
            "sharedFile": self.sharedFile,
            "blockSize": self.blockSize,
            "blockNumber": self.blockNumber,
            "lastBlockSize": self.lastBlockSize,
            "blockStateList": self.blockStateList,
            "peer": self.peer
        }

    def toJson(self):
        return json.dumps(self.__dict__())
