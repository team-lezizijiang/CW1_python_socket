import hashlib
import threading
import os
import socket
import base64
from ticket import Ticket
from time import sleep
from SharedFile import SharedFile
from message import message
from tcpMessage import tcpMessage


class FileDownloader:

    def __init__(self, ticketQueue, blockQueue, messageQueue, fileList, peers, port):
        self.ticketQueue = ticketQueue
        self.peers = peers
        self.existFileList = fileList
        self.ticketList = list()
        self.port = port
        self.downloadTicketState = dict()
        self.blockQueue = blockQueue
        self.messageQueue = messageQueue
        if os.path.exists("ticketStorage.txt") and os.path.getsize("ticketStorage.txt") != 0:
            with open("ticketStorage.txt", 'r') as f:
                oldTicketList = f.readlines()
            for i in oldTicketList:
                try:
                    string = i.rstrip('\n')
                    lst1 = string.split()
                    blockStateInfoList = eval(lst1[3])
                    new_ticket = Ticket(SharedFile(lst1[0], eval(lst1[1]), eval(lst1[2])).__dict__, 4096, lst1[4])
                    new_ticket.blockStateList = blockStateInfoList
                    self.ticketList.append(new_ticket)
                except:
                    pass
        elif not os.path.exists("ticketStorage.txt"):
            open("ticketStorage.txt", 'w').close()
        self.file_process = threading.Thread(target=self.update)
        self.file_process.setDaemon(True)
        self.file_process.start()

    def update(self):
        while True:
            if self.ticketQueue.qsize() == 0:
                continue
            temp_message = self.ticketQueue.get()
            temp_message.message['sharedFile']["filename"] = os.path.sep.join(temp_message.message['sharedFile']["filename"].split('\\'))
            new_ticket = Ticket(temp_message.message['sharedFile'], temp_message.message['blockSize'],
                                       temp_message.message['peer'])
            print('new new_ticket received')
            self.ticketList.append(new_ticket)
            with open ("ticketStorage.txt", 'w') as f:
                f.write(str(new_ticket) + '\n')
            for i in self.ticketList:
                self.download_file(i)
            sleep(1)

    def download_file(self, new_ticket):
        filename = new_ticket.sharedFile['filename']
        if os.path.isfile(filename):
            os.remove(filename)
        if not os.path.exists(filename + ".lefting"):
            file = open(filename + ".lefting", mode='w')
            file.close()
        if new_ticket.blockNumber != 0:
            with open(filename + ".lefting", "ab+") as f:
                i = new_ticket.find_first_untraverse_block()
                while i != -1:
                    conn = socket.socket()
                    conn.connect((new_ticket.peer, self.port), )
                    conn.send((tcpMessage(tcpMessage.DOWNLOAD, filename, i).toJson()))
                    flag = 0
                    while flag != 1:
                        if self.blockQueue.empty():
                            continue
                        file_message = self.blockQueue.get()
                        print('start downloading ' + filename + 'block ' + str(i))
                        file_block = file_message.message[0]
                        index = file_message.message[1]
                        f.seek(index * new_ticket.blockSize)
                        f.write(file_block)
                        flag = 1
                        sleep(0.1)
                    new_ticket.update(i)
                    i = new_ticket.find_first_untraverse_block()
                    conn.close()
        os.rename(filename + ".lefting", filename)
        self.ticketList.remove(new_ticket)
        self.existFileList[filename] = SharedFile(filename, os.path.getmtime(filename), os.path.getsize(filename))
        conn = socket.socket()
        conn.connect((new_ticket.peer, self.port), )
        conn.send(tcpMessage(tcpMessage.SUCCESS_ACCEPT, new_ticket.toJson(), 0).toJson())
        print('start complete ' + filename)
        with open("ticketStorage.txt", 'w') as f:
            for ticket in self.ticketList:
                f.write(str(ticket) + '\n')
        # correct_md5 = self.messageQueue.get().message
        # print("md5 check success and md5 is" + str(correct_md5))

