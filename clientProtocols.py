from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from socket import socket

class InsertRecord(Protocol):
    def __init__(self, message):
        print("Protocol initialized")
        self.msg = message
    def connectionMade(self):
        self.transport.write(self.msg)
    def sendMessage(self, msg):
        self.transport.write("MESSAGE %s\n" % msg)
    
    def dataReceived(self, data):
        print("data")
        reactor.stop()

class ClientInsertFactory(ClientFactory):
    def __init__(self, dataRecord):
        self.dataRecord = dataRecord
    def buildProtocol(self, addr):
        return InsertRecord(self.dataRecord)
    def startedConnecting(self, connector):
        print("Started to connect to IS Server")

def establishSession(action, data):
    if action == "insert":
        self.sock.sendall(data)
    elif action == "update":
        pass #tbd
    else:
        print("Unable to establish session")
    return
