import sys
import time
import copy
import pickle
from operator import itemgetter
from socket import *


# define the format of the packet
class Packet:
    '''
    type should be either 0, 1, or 2
    seqnum is an integer
    length is the length of data, which is between 0 and 500
    data's length should not exceed 500
    '''
    def __init__(self, Type, Seqnum, Data):
        self.type = Type
        self.seqnum = Seqnum
        self.data = Data
        self.length = len(Data)
        

    def getType(self):
        '''
        get the type of the packet
        '''
        return self.type

    def getSeqnum(self):
        '''
        get the sequence number of the packet
        '''
        return self.seqnum

    def getLength(self):
        '''
        get the length of the data in the packet
        '''
        return self.length

    def getData(self):
        '''
        get the data content of the packet
        '''
        return self.data

# get the command line arguments
Emu_address = sys.argv[1]
e_port = int(sys.argv[2])
data_port = int(sys.argv[3])
WfileName = sys.argv[4]

# create the log file
alogFile = open('arrival.log', 'w')

# create a disctionary to store the data content
CD = {}

# create a socket for receiver
receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind(('', data_port))


while True:
    dataPacket, senderAddr = receiverSocket.recvfrom(40960)  # receive data
    dataPacket = pickle.loads(dataPacket)  # decode the packet

    dataType = dataPacket.getType()  # get the type of the packet
    dataSeq = dataPacket.getSeqnum()  # get the sequence number of the packet
    dataContent = dataPacket.getData()  # get the content of packet
    dataLength = dataPacket.getLength()  # get the length of the data

    # record the arrived data's sequence number
    alogFile.write(str(dataSeq) + '\n')
    
    # acknowledge the packet to sender
    if dataType != 2:
        ACK_Packet = Packet(0, dataSeq, dataContent)
        receiverSocket.sendto(pickle.dumps(ACK_Packet), (Emu_address, e_port))
    else:
        ACK_Packet = Packet(2, dataSeq, dataContent)
        receiverSocket.sendto(pickle.dumps(ACK_Packet), (Emu_address, e_port))

    if dataType == 2:  # the transmission is over
        # close everything
        receiverSocket.close()
        alogFile.close()
        break

    # check if the packet is duplicated
    if dataSeq in CD:
        continue


    # store the received data
    CD[dataSeq] = dataContent


# reassemble the content
CD = sorted(CD.items())  # reorder the data
lenCD = len(CD)
i = 0
dataStr = ''  # stores the reordered data
while i < lenCD:
    dataStr = dataStr + CD[i][1]

    i += 1 

# create a file to save the data
dataFile = open(WfileName, 'w')
dataFile.writelines(dataStr)
dataFile.close()

exit(0)
