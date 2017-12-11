import hashlib
import random
import json
from Crypto.Cipher import AES 
import socket
import time
import sys

test = False

records = ["132", "56", "9", "100", "80", "32", "42", "42", "3", "10"]
class ISS():
    def __init__(self):
        self.firstMessage = True
        self.bloomFilter = {}
        self.shares = []

    def dataReceived(self, data):
        #self.transport.write("Hello from the honeypot, you said: " + data)
        try:
            data = json.loads(data)
        except:
            print("failed to parse json data")
            #self.transport.loseConnection()
        print('---------------------------')
        self.transport.write("Hi")
        if data["action"] == "query":
            garbledCircuit = data["GC"]
            keys = ""
            self.transport.write("requestKeys ") 
            #self.evalGC(garbledCircuit, self.bloomFilter["root"])

        if data["action"] == "provideKeys":
            pass
        
        print("Received: ",  data, len(data))
        return data



#endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
server1 = 0
server2 = 0
port = int(sys.argv[1])
'''
if port == 2222:
    server1 = 2223
    server2 = 2224
elif port == 2223:
    server1 = 2222
    server2 = 2224
elif port == 2224:
    server1 = 2222
    server2 = 2223
    '''
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', port))
sock.listen(5)

'''
print(server1, server2)
#attempt to establish connections with other IS servres
sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while(True):
    try:
        sock1.connect(("localhost", server1))
        break
    except Exception as e:
        print(e)
        continue
while(True):
    try:
        sock2.connect(("localhost", server2))
        break
    except Exception as e:
        print(e)
        continue

'''
#server = ISS()
bloomFilter = {}
shares = []

def evalGC(GC, BF, connection):
    garbledTable = GC["GATE"]
    HMACK = "1234123412341234"
    if type(GC["input1"]) is dict:
        wire1 = evalGC(GC["input1"], BF, connection)
    else:
        #getkey
        if "SBFK" in GC["input1"]:
            print("SBFK")
            idx = int(GC["input1"][-2:])
            connection.sendall(str(BF[idx]) + GC["input1"])
            while True:
                wire1 = connection.recv(2048)
                if wire1 != "":
                    break
        else:
            #print(GC["input1"])
            #print(GC["input1"])
            connection.sendall(GC["input1"])
            while True:
                wire1 = connection.recv(2048)
                if wire1 != "":
                    break

    if type(GC["input2"]) is dict:
        wire2 = evalGC(GC["input2"], BF, connection)
    else:
        print("2", GC["input2"])
        if "SBFK" in GC["input2"]:
            idx = int(GC["input2"][4:])
            print(BF)
            connection.sendall(str(BF[idx]) + GC["input2"])
            while True:
                wire2 = connection.recv(2048)
                if wire2 != "":
                    break
        else:
            connection.sendall(GC["input2"])
            while True:
                wire2 = connection.recv(2048)
                if wire2 != "":
                    break
        #getkey
    print(wire1,wire2)
    cipher1 = AES.new(wire1, AES.MODE_ECB)
    cipher2 = AES.new(wire2, AES.MODE_ECB)
    for row in garbledTable: 
        encrypted = row[0].decode("base64")
        MAC = row[1].decode("base64")
        encrypted = cipher2.decrypt(encrypted)
        key = cipher1.decrypt(encrypted)
        h = hashlib.md5()
        h.update(HMACK)
        check = h.digest()
        h.update(HMACK + check + key)
        checksum = h.digest()
        print(checksum, MAC)
        if checksum == MAC:
            return key

    return

print("hi")
while 1:
    curConnection, address= sock.accept()
    print(curConnection, address)
    databuf = ""
    while 1:#probably should thread this eventually, networkign ish ard
        data = curConnection.recv(2048)
        if not data:
            break
        databuf += data
        evaluate = 0
        print(len(databuf))
        try:
            data = json.loads(databuf)
            if data["action"] == "init":
                print("init")
                bloomFilter = data["BFTree"]
                shares = data["shares"]
                databuf = ""
            if data["action"] == "query":
                print("query")
                evaluate = True
                databuf = ""
            if data["action"] == "getShares":
                shares = ""
                for index in data["indices"]:
                    shares += "index: " + shares[int(index)] + " "
                curConnection.sendall(shares)



        except Exception as err:
            print(err)
            #print("failed to parse json data")
        if evaluate:
            matches = []
            output = evalGC(data["GC"], bloomFilter["root"], curConnection)
            checkChildren = False
            curConnection.sendall(output)
            while True:
                data = curConnection.recv(2048)
                if data != "":
                    if data == "1":
                        curConnection.sendall("next")
                        checkChildren = True
                    elif data == "0":
                        curConnection.sendall("failed")
                    break
            if checkChildren:
                count = 0
                for child in bloomFilter["children"]:
                    databuf = ""
                    while True:
                        data = curConnection.recv(2048)
                        databuf += data
                        if len(data) != 2048:
                            break
                    data = json.loads(databuf)
                    output = evalGC(data["GC"], child["root"], curConnection)
                    curConnection.sendall(output)
                    while True:
                        data = curConnection.recv(2048)
                        if data != "":
                            if data == "1":
                                curConnection.sendall("next")
                                matches.append(str(count))
                                break
                            elif data == "0":
                                curConnection.sendall("next")
                                break

                    count += 1
                while True:
                    uselessCircuit = curConnection.recv(2048)
                    if uselessCircuit != "":
                        break

                curConnection.send("done")
                while True:
                    msg = curConnection.recv(2048)
                    if msg == "get result":
                        break
                if len(matches) > 0:
                    print(matches)
                    print(shares)
                    #figure out networking, contact other servers here, probably need to thread
                    response = ""
                    for match in matches:
                        response += match + ": " + str(shares[int(match)]) + "\n"

                    curConnection.sendall(response)
                else:
                    curConnection.sendall("failed")
                databuf = ""

            print('finished eval')

