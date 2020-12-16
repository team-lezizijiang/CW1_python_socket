import threading
import os
import socket
from time import sleep
from message import message
from tcpMessage import tcpMessage


class FileDownloader:
    fileNameList = list()

    def __init__(self, queue, fileList, peers, port):
        self.queue = queue
        self.port = port
        self.socket = socket.socket()
        self.peers = peers
        self.ticketList = list()
        with open("ticketStorage.txt", 'a+') as f:
            oldTicketList = f.readlines()
        oldTicketList = [i[:-2] for i in oldTicketList]
        self.ticketList.extend(oldTicketList)
        self.download_file_list = fileList
        for i in fileList.keys():
            self.fileNameList.append(fileList[i].filename)
        self.file_process = threading.Thread(target=self.update)
        self.file_process.setDaemon(True)
        self.file_process.start()

    def update(self):
        while True:
            if self.queue.qsize() == 0:
                continue
            temp_message = self.queue.get()
            if temp_message.message_type == message.NEW_TICKET:
                new_ticket = temp_message.message
                if new_ticket.sharedFile not in self.download_file_list.keys():
                    self.download_file(new_ticket)
                    self.ticketList.append(new_ticket)
                    with open("ticketStorage.txt", 'a') as f:
                        f.writelines(new_ticket.sharedFile.filename+'\n')
            else:
                self.queue.put(temp_message)
            sleep(0.1)

    def download_file(self, ticket):
        self.socket.connect(ticket.peer)
        filename = ticket.sharedFile.filename
        if filename in self.fileNameList:
            os.remove(filename)
        with open(filename + ".lefting", "ab+") as f:
            i = ticket.find_first_untraverse_block()
            while i != -1:
                self.socket.send((tcpMessage(tcpMessage.DOWNLOAD, ticket.sharedFile.filename, i).toJson()))
                flag = 0
                while flag != 1:
                    file_message = self.queue.get()
                    if file_message.message_type == message.FILE_BLOCK:
                        file_block = file_message.message
                        self.check_block(file_block)
                        f.seek(i * ticket.blockSize)
                        f.write(file_block)
                        flag = 1
                    sleep(0.1)
                ticket.update(i)
                i = ticket.find_first_untraverse_block()
            with open("ticketStorage.txt", 'a') as f2:
                file_list = f2.readlines()
                file_list.remove(+'\n')
        os.rename(ticket.sharedFile.filename+".lefting", filename)

