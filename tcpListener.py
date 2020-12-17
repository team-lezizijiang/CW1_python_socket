import json
import socket
import hashlib
import struct
import time
from multiprocessing import queues
from threading import Thread

from message import message
from tcpMessage import tcpMessage
from ticket import Ticket


class TcpListener:
    peers = dict()
    host = ""
    port = ""
    filelist = {}
    listener = None

    def __init__(self, host, port, peers, fileQueue, ticketQueue, blockQueue, filelist):
        self.socket = socket.socket()
        self.filelist = filelist
        self.socket.bind(('0.0.0.0', port,))
        self.host = host
        self.port = port
        self.peers = peers
        self.fileQueue = fileQueue
        self.ticketQueue = ticketQueue
        self.blockQueue = blockQueue
        self.listener = Thread(target=self.listen)
        self.updater = Thread(target=self.update)
        self.listener.setDaemon(True)
        self.listener.start()
        self.hello(self.peers)

    def push(self, message_type, message1):
        self.queue.push(message(message_type, message1))

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
            message = self.fileQueue.get()
            if message != None:
                if message.message_type == message.NEW_FILE:
                    new_file_list = message.message
                    for file in new_file_list.keys():
                        for peer in self.peers:
                            conn = socket.socket
                            conn.connect((peer, self.port,))
                            conn.send(
                                (tcpMessage(tcpMessage.NEW_TICKET, Ticket(new_file_list[file], 4096, 0), 0)).toJson())

    def listen(self):
        self.socket.listen(5)
        while True:
            conn, addr = self.socket.accept()  # accept connection from other clients, also blocking
            print(f"[SERVER] connected from [{addr[0]} | {addr[1]}]")
            handleThread = Thread(target=self.handle, args=(conn,))
            handleThread.start()

    def sendFile(self, ticket, peer):
        conn = socket.socket()
        conn.connect((peer, self.port), )
        for i in range(0, len(ticket['blockStateList'])):
            if ticket['blockStateList'][i] == 0:
                with open(ticket['filename'], 'br') as fp:
                    fp.seek(i * ticket['blockSize'])
                    conn.send(tcpMessage(tcpMessage.BLOCK_MESSAGE, fp.read(
                        ticket['blockSize'] if i != (len(ticket['blockStateList']) - 1) else ticket['lastBlockSize'],
                        ), i).toJson())
        conn.close()

    def handle(self, conn):
        conn.setblocking(True)
        headerlength = conn.recv(4)
        # print("4 bytes received ...")
        headerlength = struct.unpack("I", headerlength)
        print(f"[SERVER] received a header with length [{headerlength}]")
        jsonfile = conn.recv(headerlength[0])
        header = json.loads(jsonfile)  # load json file to dict
        print(header)
        if header["message_type"] == tcpMessage.NEW_TICKET:  # new ticket with new file to be sync
            header['message']['peer'] = conn.getperrnamne()[0]
            self.ticketQueue.push(message(message_type=message.NEW_TICKET, message=header['message']))
        elif header["message_type"] == tcpMessage.WAKE:  # peers update the fileList
            self.peers[str(conn.getpeername()[0])] = header['message']
        elif header["message_type"] == tcpMessage.DOWNLOAD:  # accept request and send block back
            self.sendFile(header["message"], conn.getpeername()[0])
        elif header["message_type"] == tcpMessage.BLOCK_MESSAGE:  # accept the block data and send it to downloader
            self.blockQueue.push(message(message_type=message.FILE_BLOCK, message=(header["message"], header["index"])))
        elif header["message_type"] == tcpMessage.SUCCESS_ACCEPT:  # peer received file, send back md5 to check it
            self.sendMD5(header["message"]['filename'], conn.getpeername()[0])
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

