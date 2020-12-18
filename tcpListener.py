import json
import socket
import hashlib
import struct
import os.path
import base64
import time
from multiprocessing import queues
from threading import Thread

from SharedFile import SharedFile
from message import message
from tcpMessage import tcpMessage
from ticket import Ticket


class TcpListener:
    peers = dict()
    host = ""
    port = ""
    filelist = {}
    listener = None

    def __init__(self, host, port, peers, fileQueue, ticketQueue, blockQueue, messageQueue, filelist):
        self.socket = socket.socket()
        self.filelist = filelist
        self.socket.bind(('0.0.0.0', port,))
        self.host = host
        self.port = port
        self.peers = peers
        self.fileQueue = fileQueue
        self.ticketQueue = ticketQueue
        self.blockQueue = blockQueue
        self.messageQueue = messageQueue
        self.listener = Thread(target=self.listen)
        self.updater = Thread(target=self.update)
        self.listener.setDaemon(True)
        self.updater.setDaemon(True)
        self.updater.start()
        self.listener.start()
        self.hello(self.peers)


    def hello(self, peers):
        for peer in peers.keys():
            conn = socket.socket()
            try:
                conn.connect((peer, self.port), )
                conn.send(tcpMessage(tcpMessage.WAKE, dict(self.filelist), 0).toJson())
                conn.close()
            except Exception as e:
                print(e)
                pass

    def update(self):
        while True:
            if self.fileQueue.qsize() == 0:
                continue
            message = self.fileQueue.get()
            if message != None:
                if message.message_type == message.NEW_FILE:
                    new_file_list = message.message
                    for file in new_file_list.keys():
                        for peer in self.peers.keys():
                            conn = socket.socket()
                            conn.connect((peer, self.port,))
                            conn.send(
                                (tcpMessage(tcpMessage.NEW_TICKET, Ticket(new_file_list[file].__dict__, 409600, peer).__dict__(), 0)).toJson())
                            conn.close()
                            print('new ticket send to' + str(peer))

    def listen(self):
        self.socket.listen(5)
        while True:
            conn, addr = self.socket.accept()  # accept connection from other clients, also blocking
            print(f"[SERVER] connected from [{addr[0]} | {addr[1]}]")
            handleThread = Thread(target=self.handle, args=(conn,))
            handleThread.start()

    def sendFile(self, filename, peer, i):
        conn = socket.socket()
        conn.connect((peer, self.port), )
        with open(filename, 'br') as fp:
            fp.seek(i * 409600)
            conn.send(tcpMessage(tcpMessage.BLOCK_MESSAGE, fp.read(min(409600, os.path.getsize(filename) - i * 409600)), i).toJson())
        conn.close()
        print(str(filename) + " block" + str(i) + "send to " + str(peer))

    def handle(self, conn):
        conn.setblocking(True)
        headerlength = conn.recv(4)
        # print("4 bytes received ...")
        headerlength = struct.unpack("I", headerlength)
        print(f"[SERVER] received a header with length [{headerlength}]")
        jsonfile = conn.recv(headerlength[0])
        header = json.loads(jsonfile.decode('utf-8'))  # load json file to dict
        print(header)
        if header["message_type"] == tcpMessage.NEW_TICKET:  # new new_ticket with new file to be sync
            header['message']['peer'] = conn.getpeername()[0]
            self.ticketQueue.put(message(message_type=message.NEW_TICKET, message=header['message']))
        elif header["message_type"] == tcpMessage.WAKE:  # peers update the fileList
            if self.peers[str(conn.getpeername()[0])] != header['message']:
                self.hello(self.peers)
                self.peers[str(conn.getpeername()[0])] = header['message']
                for i in header["message"].keys():
                    if i not in self.filelist.keys():
                        self.ticketQueue.put(message(message_type=message.NEW_TICKET, message=Ticket(
                            SharedFile(i, header['message'][i]['mtime'], header['message'][i]['size']).__dict__, 409600, conn.getpeername()[0]).__dict__()))

        elif header["message_type"] == tcpMessage.DOWNLOAD:  # accept request and send block back
            self.sendFile(header["message"], conn.getpeername()[0], header['index'])
        elif header["message_type"] == tcpMessage.BLOCK_MESSAGE:  # accept the block data and send it to downloader
            header["message"] = conn.recv(409600)
            self.blockQueue.put(message(message_type=message.FILE_BLOCK, message=(header["message"], header["index"])))
        elif header["message_type"] == tcpMessage.SUCCESS_ACCEPT:  # peer received file, send back md5 to check it
            self.sendMD5(header["message"]['filename'], conn.getpeername()[0])
        elif header["message_type"] == tcpMessage.MD5:
            self.messageQueue.put(message(message_type=message.MD5, message=header['message']))
        conn.close()

    def sendMD5(self, filename, peer):
        conn = socket.socket()
        conn.connect((peer, self.port,))
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        conn.send(tcpMessage(tcpMessage.MD5, hash_md5, 0).toJson())
        conn.close()

