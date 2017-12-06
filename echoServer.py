from twisted.internet import protocol, reactor, endpoints
from twisted.conch.telnet import TelnetProtocol
from twisted.conch.telnet import StatefulTelnetProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint

class Echo(protocol.Protocol):
    def connectionMade(self):
        print(self.transport.client[0])

    def dataReceived(self, data):
        if data[:-2] == "close":
            self.transport.loseConnection()
        #self.transport.write("Hello from the honeypot, you said: " + data)
        print("Received: " + data, len(data))
    def connectionLost(self, reason):
        print(reason)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

#endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
endpoint = TCP4ServerEndpoint(reactor, 2222)
endpoint.listen(EchoFactory())
print("HI")
reactor.run()
