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
        print("Client factor init")
    def buildProtocol(self, addr):
        return InsertRecord(self.dataRecord)
    def startedConnecting(self, connector):
        print("Started to connect to IS Server")

def session():
    reactor.run()

sock = socket()
sock.connect(('localhost', 2222))
sock.sendall("Hello! \n")
print("----round2----")
sock.sendall("Hello again!\n")
sock.close()
