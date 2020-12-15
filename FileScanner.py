import threading
import os.path
import time
import multiprocessing as mp

from SharedFile import SharedFile
from message import message


class FileScanner:
    dir = "" # directory to be watched
    fileList = {} # current file list
    file_process = None # thread
    queue = None # message queue


    def __init__(self, fileList, queue, dir="./"):
        """

        :param fileList: current file list
        :param queue: message queue
        :param dir: directory to be watched
        """
        self.queue = queue
        self.fileList = fileList
        self.fileList.update(self.scan(dir))
        self.dir = dir
        self.file_process = threading.Thread(target=self.update, args=(queue,))
        self.file_process.setDaemon(True)
        self.file_process.start()


    def update(self, queue):
        """
        main method. Compare the file list with new on and generate the updated file list
        :type queue: message queue
        """
        while True:
            newFileList = {}
            fileList = self.fileList
            temp = self.scan(self.dir)
            for i in temp.keys():
                if i not in fileList.keys():
                    newFileList[i] = temp[i]
                elif fileList[i].mtime != temp[i].mtime or fileList[i].size != temp[i].size:
                    newFileList[i] = temp[i]
            if len(newFileList) != 0:
                self.push(newFileList, queue)
                fileList.clear()
                self.fileList.update(temp)
            time.sleep(1)



    def scan(self, dir):
        '''

        :param dir: directory to be watched
        :return: current files exists in file system
        '''
        tempList = {}
        g = os.walk(dir)
        for path, dir_list, file_list in g:
            for file_name in file_list:
                abs_name = os.path.join(path, file_name)
                tempList[abs_name]  = SharedFile(abs_name, os.path.getmtime(abs_name), os.path.getsize(abs_name))

        return tempList

    def push(self, new_file_list, queue):
        """
        inform the main thread with new files
        :param new_file_list: list contains new files
        :param queue: message queue
        """
        queue.put(message(message.NEW_FILE, new_file_list))

if __name__ == "__main__":
    s = {}
    dir = r"./"
    filescanner = FileScanner(s, dir=dir, queue=mp.Queue())
    while True:
        time.sleep(20)