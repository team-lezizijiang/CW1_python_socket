import threading
import os
import socket
from time import sleep
from message import message
from tcpMessage import tcpMessage


class FileDownloader:

    def __init__(self, ticketQueue, blockQueue, fileList, peers, port):
        self.ticketQueue = ticketQueue
        self.peers = peers
        self.existFileList = fileList
        self.ticketList = list()
        self.port = port
        self.blockQueue = blockQueue
        with open("ticketStorage.txt", 'a+') as f:
            oldTicketList = f.readlines()
        oldTicketList = [i[:-2] for i in oldTicketList]
        self.ticketList.extend(oldTicketList)
        self.file_process = threading.Thread(target=self.update)
        self.file_process.setDaemon(True)
        self.file_process.start()

    def update(self):
        while True:
            if self.ticketQueue.qsize() == 0:
                continue
            temp_message = self.ticketQueue.get()
            new_ticket = temp_message.message
            if new_ticket["sharedFile"]['filename'] not in self.existFileList.keys():
                self.download_file(new_ticket)
                self.ticketList.append(new_ticket["sharedFile"]["filename"])
                if not os.path.isfile("ticketStorage.txt"):
                    os.mknod('ticketStorage.txt')
                with open("ticketStorage.txt", 'a+') as f:
                    f.write(new_ticket["sharedFile"]["filename"] + '\n')
            sleep(1)

    def download_file(self, ticket):
        conn = socket.socket()
        conn.connect((ticket['peer'], self.port),)
        filename = ticket["sharedFile"]["filename"]
        if os.path.isfile(filename):
            os.remove(filename)
        os.mknod(filename+".lefting")
        if ticket['blockNumber'] != 0:
            with open(filename + ".lefting", "ab+") as f:
                i = ticket.find_first_untraverse_block()
                while i != -1:
                    conn.send((tcpMessage(tcpMessage.DOWNLOAD, filename, i).toJson()))
                    flag = 0
                    while flag != 1:
                        if self.blockQueue.empty():
                            continue
                        file_message = self.blockQueue.get()
                        file_block = file_message.message[0]
                        index = file_message.message[1]
                        f.seek(index * ticket["blockSize"])
                        f.write(file_block)
                        flag = 1
                        sleep(0.1)
                    ticket.update(i)
                    i = ticket.find_first_untraverse_block()
                with open("ticketStorage.txt", 'rw') as f2:
                    file_list = f2.readlines()
                    file_list.remove(filename+'\n')
                    f2.writelines(file_list)
        os.rename(filename+".lefting", filename)
        conn.send(tcpMessage(tcpMessage.SUCCESS_ACCEPT, filename, 0).toJson())

