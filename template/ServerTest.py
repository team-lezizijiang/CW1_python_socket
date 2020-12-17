import client
import server
import threading

testserver = server.Server("",9999)



def serverThre(server):
    server.listen()
    server.handleCon()

def clientThre(client):
    client.connectServer()



sTher = threading.Thread(target=serverThre,args=(testserver,))


sTher.start()