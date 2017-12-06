#from clientProtocols import *
from socket import socket
import thread

class IDXServer():

    def __init__(ip='localhost', key, port):
        self.port = port
        self.ip = ip
        self.key = key
        self.sock = socket()
        self.sock.connect(ip, port)

    def sendMsg(data):
        self.sock.sendall(data)


data = "hello"
# establishSession("insert", "Hello!", 123)

if __name__ == "__main__":
    idx = 0 #keep record idx
    while(1):
        action = raw_input("What would you like to do (query, insert, exit): ")
        if action == 'insert':
            #for testing datarecords are just "IDX numval"
            try:
                data = int(raw_input("Enter the data: "))
                availableServers = (0,1,2)
                idxserver1 = int(raw_input("Pick a server to talk to " + str(availableServers) + ": "))
                print(str(idxserver1))
                print(idxserver1 in availableServers)
                assert(idxserver1 in availableServers)
                availableServers = tuple(s for s in availableServers if s != idxserver1)
                idxserver2= int(raw_input("Pick another server to talk to " + str(availableServers) + ": "))
                assert(idxserver2 in availableServers)
                establishSession(action, "insert " + str(idx) + " " + str(data), idxserver1)
                establishSession(action, "insert " + str(idx) + " " + str(data), idxserver2)
                idx += 1
            except Exception as err:
                print("Malformed input")
                print(err)
                


            
        elif action == 'query':
            #
            print("NYI")
        elif action == 'exit':
            break
        else:
            print(action + ": not recognized")
