import socket
import threading
import sys
import os
import struct
import json
import hashlib
from clientMessage import Message
from serverMessage import ServerMessage
from os import listdir
from os.path import isfile, join, getmtime, getsize

updateOccurs = False


# server will be listening for connection
class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.severSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.currentfiles = []
        self.request_queue = []

    def listen(self):
        self.severSock.bind((self.host, self.port))  # bind the server socket
        self.severSock.listen(10)  # listen for connection
        print(f"[SERVER] listening on {self.host} | {self.port}")

    def handleCon(self):
        while True:
            conn, addr = self.severSock.accept()  # accept connerction from other clients, also blocking
            print(f"[SERVER] connected from [{addr[0]} | {addr[1]}]")
            conn.send(b"Successfuly Connected to Server")  # send welcome message to client
            handleThread = threading.Thread(target=self.handle, args=(conn,))
            handleThread.start()

    def handle(self, conn):
        self.sendFileList(conn)  # when a client connected to server, server should send the current server file lists
        listenUpdateThre = threading.Thread(target=self.updateFileList)
        listenUpdateThre.start()  # thread for updating the file list in current share folder
        while True:
            global updateOccurs
            if updateOccurs == True:
                self.sendFileList(conn)
                print(f"[SERVER] sent the newest file list to [CLIENT]")
            try:  # try to recevie a request header from client
                self.recvRequest(conn)
            except:
                continue
            # communication with client should go from here

    def recvRequest(self, conn):
        conn.setblocking(False)
        headerlength = conn.recv(4)
        # print("4 bytes recived ...")
        headerlength = struct.unpack("I", headerlength)
        print(f"[SERVER] recived a header with length [{headerlength}]")
        jsonfile = conn.recv(headerlength[0])
        header = json.loads(jsonfile)  # load json file to dict
        print(header)
        # self.responseHeader(header,conn)

        # generater a response header back to client

    def responseHeader(self, requestHeader, conn):
        opreationCode = requestHeader['operationCode']
        filename = requestHeader['filename']
        blockIndex = requestHeader['filename']
        if opreationCode == 0:  # request file information
            header = self.getfile_info(filename)
            conn.send(header)
            print("[SERVER] file information sent to the client")
        elif opreationCode == 1:  # request file block
            pass
        else:  # error code
            pass

    def md5(self, file):
        hash_md5 = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.digest()

    def getfile_info(self, file):

        operationcode = 0
        modifytime = getmtime(file)
        file_size = getsize(file)
        md5_bytes = self.md5(file)
        blocksize = 512
        blocknumber = os.stat(file).st_blocks
        infoheader = ServerMessage()
        header = infoheader.infromationHeader(operationcode, blocksize, blocknumber, md5_bytes, file_size)
        return header

    def updateFileList(self):  # keep listening on share folder
        while True:
            try:
                filelist = self.traverse("share")
            except:
                continue
            # print(filelist)
            if filelist != self.currentfiles:
                self.currentfiles = filelist[:]
                global updateOccurs
                updateOccurs = True
                print("[SERVER-UPDATE] Share Folder modified ..")

    def sendFileList(self, client_conn):  # send the file list to client
        global updateOccurs
        if len(self.currentfiles) != 0:
            files = ",".join(self.currentfiles)
            message = files.encode("utf-8")  # may need to construct a message factory class
            client_conn.send(message)
            updateOccurs = False
        return

    def traverse(self, dir_path):
        file_list = []
        file_folder_list = listdir(dir_path)
        for file_folder_name in file_folder_list:
            if isfile(join(dir_path, file_folder_name)):
                file_list.append(join(dir_path, file_folder_name))
            else:
                file_list.extend(self.traverse(join(dir_path, file_folder_name)))
        return file_list
