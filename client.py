#from clientProtocols import *
import random
import socket
from os import urandom
import thread
from Crypto.Cipher import AES
from bloomFilter import *
import hashlib

class IDXServer():

    def __init__(self, ip, key, port):
        self.port = port
        self.ip = ip
        self.key = key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

    def sendMsg(self, data):
        self.sock.sendall(data)

def genSecretShares(record):
    #creates 3 8 bit shares
    rand = int(urandom(1).encode('hex'), 16)
    rand2 = int(urandom(1).encode('hex'),16)
    s1 = record ^ rand
    s2 = rand ^ rand2
    s3 = rand2

    return [s1,s2,s3]

    
data = "hello"
# establishSession("insert", "Hello!", 123)
records = [132, 56, 9, 100, 80, 32, 42, 42, 3, 10]

servers = [IDXServer('localhost', 1, 2222), IDXServer('localhost', 1, 2223) , IDXServer('localhost', 1, 2224)]

if __name__ == "__main__":
 
    idx = 0 #keep record idx
    secretShares0 = []
    secretShares1 = []
    secretShares2 = []
    bloomFilters = []
    indices = []
    HMACK = "1234123412341234"
    SK = "1010" * 4
    for record in records:
        #gen secret shares
        shares =genSecretShares(record)
        secretShares0.append(shares[0])
        secretShares1.append(shares[1])
        secretShares2.append(shares[2])
        bloomfilter = BloomFilter()
        bloomfilter.create(record)
        bloomFilters.append(bloomfilter)

        indices.append(idx)
        idx += 1

    #gen bloomfilters, each leaf is just a idx into a table, send over ss tables also
    BFTree = BloomFilterTree(bloomFilters,indices)
    JSONTree = BFTree.getJSON()
    BFTree.encrypt("1010101010101010")
    servers[0].sendMsg(json.dumps({"action": "init", "shares": secretShares0, "BFTree": JSONTree}))
    servers[1].sendMsg(json.dumps({"action": "init", "shares": secretShares1, "BFTree": JSONTree}))
    servers[2].sendMsg(json.dumps({"action": "init", "shares": secretShares2, "BFTree": JSONTree}))
    
    while(1):
        action = raw_input("What would you like to do (query, insert, exit): ")
        
        if action == 'insert':
            #for testing datarecords are just "IDX numval"
            print("todo")
            '''
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
            '''                
 
        elif action == 'query':
            print("Only query supported is SELECT * where VAL == inputValue")
            inputVal = int(raw_input("Enter an input value: "))
            server = int(raw_input("Pick a server (0,1,2): "))

            bloomfilter = BloomFilter()
            bloomfilter.create(inputVal)
            #build input bloomfilter
            
            #build json GC
            #circuit is just for each bit of the bloom filter, xor with wirelabelings of secret key and server bloomfilter, AND with query bloomfilter, XNOR with query bloomfilter, AND all together
            #first build this component for each of the 16 bits
            
            while(True):
                '''
                while True:
                    data = servers[server].sock.recv(2048)
                    if data != "ready":
                        break
                        '''
                wirelabelings = {}
                gates = []
                for x in range(16): #gen bloomfilter for input doing this with JSON
                    #first compute xor garbled table
                    wirelabelings[str(0) + "BFK" + str(x)] = urandom(16) #CLIENT QUERY LABELLINGS
                    wirelabelings[str(1) + "BFK" + str(x)] = urandom(16)
                    wirelabelings[str(0) + "SBFK" + str(x)] = urandom(16) #SERVER BLOOMFILTER
                    wirelabelings[str(1) + "SBFK" + str(x)] = urandom(16)
                    wirelabelings[str(0) + "SK" + str(x)] = urandom(16) # SECRET KEY
                    wirelabelings[str(1) + "SK" + str(x)] = urandom(16)

                    #xor gate
                    o0 = urandom(16) #output = 0
                    o1 = urandom(16) #output = 1
                    garbledTable = []
                    for k1 in range(2):
                        for k2 in range(2):
                            cipher1 = AES.new(wirelabelings[str(k1) + "SK" + str(x)], AES.MODE_ECB)
                            cipher2 = AES.new(wirelabelings[str(k2) + "SBFK" + str(x)], AES.MODE_ECB)
                            h = hashlib.md5()
                            h.update(HMACK)
                            MAC = h.digest()
                            if k1 == k2: #output 0
                                garbledGate = cipher1.encrypt(o0)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o0) 
                                MAC = h.digest()
                            else:
                                garbledGate = cipher1.encrypt(o1)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o1) 
                                MAC = h.digest()

                            #input 1 is always the key to the HMAC
                            garbledTable.append((garbledGate.encode('base64'), MAC.encode('base64')))
                    #shuffle gates
                    random.shuffle(garbledTable)
                    gate = {"GATE": garbledTable, "input1": "SK" + str(x), "input2": "SBFK" + str(x)}
                    
                    #AND GATE
                    o10 = urandom(16)
                    o11 = urandom(16)
                    garbledTable = []
                    for k1 in range(2):
                        for k2 in range(2):
                            h = hashlib.md5()
                            cipher1 = AES.new(wirelabelings[str(k1) + "BFK" + str(x)], AES.MODE_ECB)
                            if k2 == 0:
                                cipher2 = AES.new(o0, AES.MODE_ECB)
                            else:
                                cipher2 = AES.new(o1, AES.MODE_ECB)
                            h.update(HMACK)
                            MAC = h.digest()
                            if k1 == k2 and k1 == 1 and k2 == 1: #1 output
                                garbledGate = cipher1.encrypt(o11)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o11)
                                MAC = h.digest()
                            else:
                                garbledGate = cipher1.encrypt(o10)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o10)
                                MAC = h.digest()
                            garbledTable.append((garbledGate.encode('base64'), MAC.encode('base64')))
                    random.shuffle(garbledTable)
                    gate = {"GATE": garbledTable,  "input1": "BFK" + str(x), "input2": gate}

                    #XNOR
                    garbledTable = []
                    o20 = urandom(16)
                    o21 = urandom(16)
                    for k1 in range(2):
                        for k2 in range(2):
                            h = hashlib.md5()
                            cipher1 = AES.new(wirelabelings[str(k1) + "BFK" + str(x)], AES.MODE_ECB)
                            if k2 == 0:
                                cipher2 = AES.new(o10, AES.MODE_ECB)
                            else:
                                cipher2 = AES.new(o11, AES.MODE_ECB)
                            h.update(HMACK)
                            MAC = h.digest()
                            if k1 == k2: #1 output
                                garbledGate = cipher1.encrypt(o21)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o21)
                                MAC = h.digest()
                            else:
                                garbledGate = cipher1.encrypt(o20)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o20)
                                MAC = h.digest()
                            garbledTable.append((garbledGate.encode('base64'), MAC.encode('base64')))
                    random.shuffle(garbledTable)
                    gate = {"GATE": garbledTable,  "input1": "BFK" + str(x), "input2": gate}
                    gates.append([o20, o21, gate])
                #keep anding these gates together
                while len(gates) != 1:
                    o0 = urandom(16)
                    o1 = urandom(16)
                    gate1 = gates.pop(0)
                    gate2 = gates.pop(0)
                    garbledTable = []
                    for k1 in range(2):
                        for k2 in range(2):
                            h = hashlib.md5()
                            cipher1 = AES.new(gate1[k1], AES.MODE_ECB)
                            cipher2 = AES.new(gate2[k2], AES.MODE_ECB)
                            h.update(HMACK)
                            MAC = h.digest()
                            if k1 == 1 and k2 == 1: #output 1
                                garbledGate = cipher1.encrypt(o1)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o1)
                                MAC = h.digest()
                            else: #output 0
                                garbledGate = cipher1.encrypt(o0)
                                garbledGate = cipher2.encrypt(garbledGate)
                                h.update(HMACK + MAC + o0)
                                MAC = h.digest()
                            garbledTable.append((garbledGate.encode('base64'), MAC.encode('base64')))

                    random.shuffle(garbledTable)
                    #print(garbledTable)
                    assert(len(garbledTable) == 4)
                    gate = {"GATE": garbledTable, "input1": gate1[2], "input2": gate2[2]}
                    gates.append([o0, o1, gate])
                    #print(gate)
                    #print(gates[-1])
                GC = gates[0]
                message = {"action": "query", "GC": GC[-1]}
                o0 = GC[0]
                o1 = GC[1]
                #print(o0,o1)
                servers[server].sendMsg(json.dumps(message))
                #print(len(json.dumps(message)))
                failed = False
                done = False
                while(True):
                    data = servers[server].sock.recv(2048)
                    if data != "":
                        #print("got data: " + data)
                        if "SBFK" in data:
                            key = wirelabelings[data]
                            #print("sending key: " + key)
                            servers[server].sendMsg(key)
                        elif "SK" in data:
                            idx = int(data[2:])
                            key = wirelabelings[str(SK[idx]) + data]
                            #print("sending key: " + key)
                            servers[server].sendMsg(key)
                        elif "BFK" in data: 
                            idx = int(data[3:])
                            key = wirelabelings[str(bloomfilter.bitarray[idx]) + data]
                            #print("sending key: " + key)
                            servers[server].sendMsg(key)
                        else: #get sent some key, send the output corresponding to it
                            if data == o0:
                                servers[server].sendMsg("0")
                            elif data == o1:
                                servers[server].sendMsg("1")
                    if data == "next":
                        break
                    if data == "failed":
                        failed = True
                        break
                    if data == "done":
                        done = True
                        servers[server].sendMsg("get result")
                        while(True):
                            data = servers[server].sock.recv(2048)
                            if data != "":
                                if data == "failed":
                                    failed = True 
                                else:
                                    print("Returned indices: " + data)
                                    print("server 0 shares: ", secretShares0)
                                    print("server 1 shares: ", secretShares1)
                                    print("server 2 shares: ", secretShares2)
                                break
                        break

                if failed:
                    print("record not found")
                    break
                elif done:
                    break
                

                        
            '''
            for x in range(16):
                gate = {"XOR":[             \
            '''
        elif action == 'exit':
            break
        else:
            print(action + ": not recognized")
