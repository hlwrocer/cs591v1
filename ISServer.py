import hashlib

test = True

class dataRecord():
    def __init__(self, idx, ss):
        self.id = idx
        self.ss = ss
        self.share1 = (None,None) #share of another servers share
        self.share2 = (None,None)

#Client, when sending SS'd record, also sends Bloomfilter of the record itself,

#For demo purposes, I'll have the clients send the SS, and the record itself, and have each server create the original bloom filter I'd need to convert each object into
#JSON objects, or something that is parsable
class BloomFilter():
    def __init__(self, size=20, hashcount=10):
        self.size = size #size of bitarray
        self.hashcount = hashcount # hashes
        self.bitarray = size*[0]

    def create(self, record): #bloomfilter for specific record
        for i in range(self.hashcount):
            h = hashlib.md5() #for demo purposes just using md5
            h.update(str(i)) #seed with i
            h.update(record) #record only contains one column, otherwise hash every column
            self.bitarray[int(int(h.hexdigest(),16)) % self.size] = 1

    def join(self, bloomfilter): #combines a bloomfilter, useful for reconstruction assumed to be same size
        for i in range(self.size):
            if bloomfilter.bitarray[i] == 1:
                self.bitarray[i] = 1

class BloomFilterTree(): #probably a better way to construct this
    def __init__(self, bloomfilters, dataRecords):
        self.root = BloomFilter()
        self.BFHashCount = 10
        self.BFSize = 20
        for bloomfilter in bloomfilters:
            self.root.join(bloomfilter)
        if len(bloomfilters) >= 2:
            self.isLeaf = False
            self.childLeft = BloomFilterTree(bloomfilters[0:len(bloomfilters)/2], dataRecords[0:len(bloomfilters)/2])
            self.childRight = BloomFilterTree(bloomfilters[len(bloomfilters)/2:], dataRecords[len(bloomfilters)/2:])
        else:
            self.isLeaf = True
            self.child = dataRecords[0]
    def retrieveRecord(self, query):
        #for now i'll just support a basic select query, e.g just SELECT INTVAL, can't query directly by index
        params = query.split(" ")
        if params[0].upper() == "SELECT":
            #check if in root, then check children
            for i in range(self.BFHashCount):
                h = hashlib.md5() #for demo purposes just using md5
                h.update(str(i)) #seed with i
                h.update(params[1]) #record only contains one column, otherwise hash every column
                if self.root.bitarray[int(int(h.hexdigest(),16)) % self.BFSize] != 1:
                    return []

            #if in root
            if self.isLeaf:
                return [self.child] #return datarecord
            else:
                recordsLeft = self.childLeft.retrieveRecord(query)
                recordsRight = self.childRight.retrieveRecord(query)
                return recordsLeft + recordsRight


if test:
    a = BloomFilter()
    a.create("13")
    b = BloomFilter()
    b.create("50")
    c = BloomFilter()
    c.create("43")
    print a.bitarray, 'a'
    print b.bitarray, 'b'
    print c.bitarray, 'c'
    
    BFTree = BloomFilterTree([a,b,c],["13","50","43"])
    print BFTree.root.bitarray, 'should be a + b + c'  #should be a,b,c joined
    print BFTree.childLeft.root.bitarray, 'should be a' #should just be a
    print BFTree.childLeft.isLeaf, 'should be true'
    print BFTree.childLeft.child, 'should be 13'

    print BFTree.childRight.root.bitarray, 'should be b+c'
    print BFTree.childRight.isLeaf, 'should be false'
    print BFTree.childRight.childLeft.root.bitarray, 'should be b'
    print BFTree.childRight.childRight.root.bitarray, 'should be c'

    print BFTree.retrieveRecord("SELECT 13")
    print BFTree.retrieveRecord("SELECT 32")
    print BFTree.retrieveRecord("SELECT 50")


