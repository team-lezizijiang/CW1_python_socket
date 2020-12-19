# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import multiprocessing as mp
import fileDownloader
import FileScanner
import tcpListener
import time
import os.path
import sys

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press te green button in the gutter to run the script.
if __name__ == '__main__':
    filelist = mp.Manager().dict()
    peers = mp.Manager().dict()
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == '--ip':
            for peer in sys.argv[i+1].split(','):
                peers[peer] = {}
    ticketQueue = mp.Manager().Queue()
    fileQueue = mp.Manager().Queue()
    blockQueue = mp.Manager().Queue()
    messageQueue = mp.Manager().Queue()
    file_scanner = FileScanner.FileScanner(filelist, fileQueue, os.path.normpath("share"))
    time.sleep(1)
    file_downloader = fileDownloader.FileDownloader(ticketQueue, blockQueue, messageQueue, filelist, peers, 24475)
    tcp_listener = tcpListener.TcpListener("127.0.0.1", 24475, peers, fileQueue, ticketQueue, blockQueue, messageQueue, filelist)
    while True:
        time.sleep(1)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
