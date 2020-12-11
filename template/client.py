import socket
import threading
import sys
import os
from clientMessage import Message
from os.path import isfile, join, getmtime, getsize


class Client:
    def __init__(self, host, port):
        self.host = host  # server ip
        self.port = port  # server port
        self.sockeClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # client socket
        self.filesTobeReq = []


    def connectServer(self):
        # try to connect to server until server response
        while True:
            try:
                self.sockeClient.connect((self.host, self.port))
                message = self.sockeClient.recv(1024).decode("utf-8")
                if message == "Successfuly Connected to Server":
                    print(f"[CLIENT] {message}")
                    self.filelistRec()
            except:  # server is not running currently
                # print("trying to connect to server")
                continue

    def filelistRec(self):
        while True:
            try:
                filelist = self.sockeClient.recv(1024).decode("utf-8")
                filelist = filelist.split(',')
                print(f"[ClIENT] recvie [FILE-LIST] from host {self.host} --------- ")
                self.filecheck(filelist)
            except:
                self.sockeClient.close()
                break
        self.reconnect()


    def filecheck(self,filelist):
        # check whether has the file or not, wether this file has been changed or not
        for file in filelist:
            if isfile(file): # if file already exits in own sharefolder
                # check file information from server, check wether needs to be updated
                requestFileInfromationThred = threading.Thread(target=self.requestFileInformation, args=(file,))
                requestFileInfromationThred.start()
            elif isfile(file) == False: # if the file not exit in own sharefolder
                # direct request to download the whole file
                #break
                requestFileDownloadThred = threading.Thread(target=self.requestFileDownload,args=(file,))
                requestFileDownloadThred.start()


    def requestFileInformation(self,file):
        print(f"[CLIENT-REQUEST]:exits in current share folder, looking for more information from sever ...")
        headerBuilder = Message(operationCode=0, filename=file)
        headerRequestFileInformation = headerBuilder.constructClientHeader()
        print(headerRequestFileInformation)
        self.sockeClient.send(headerRequestFileInformation)


    def requestFileDownload(self,file):
        print(f"[CLIENT-REQUEST]: request [TRANSFER] from sever")
        headerBuilder = Message(operationCode=1,filename=file,blockIndex=0)
        headerRequestFileDownload = headerBuilder.constructClientHeader()
        self.sockeClient.send(headerRequestFileDownload)



    def reconnect(self):
        print("[ClIENT] lost connection with server")
        print("[ClIENT] trying to reconnect to server...")
        self.sockeClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connectServer()

