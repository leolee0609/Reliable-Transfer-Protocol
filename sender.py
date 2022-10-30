import sys
import time
import copy
import pickle
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


# get the network emulator address, the emulator port number, the port number used to
#   receive ACKs from the emulator and the timeout interval in ms from command line input
Emu_address = sys.argv[1]
e_port = int(sys.argv[2])
ACK_port = int(sys.argv[3])
TOI = int(sys.argv[4]) / 1000  # from millisecond to second
TfileName = sys.argv[5]

# build empty log files
seqlogFile = open('seqnum.log', 'w')
acklogFile = open('ack.log', 'w')

# get the content of the file that will be transmitted
Tfile = open(TfileName, 'r')
TfileContent = Tfile.read()
content = copy.deepcopy(TfileContent)  # get a copy of the content to manipulate
Tfile.close()

N = 30  # set the window size to be 30 packets

# devide the data into packets
P = {}  # stores all the packets
seq = 0  # let the order of a packet be the sequence number of the packet
dataLength = len(content) // 30 + 1
seq = 0
while seq < N:  # check if content is all pipelined
    dataPiece = copy.deepcopy(content[: dataLength])  # get the data of the packet
    P[seq] = Packet(1, seq, dataPiece)  # append the new packet to P
    content = copy.deepcopy(content[dataLength: ])  # cut the packed part of content

    seq += 1  # increment the sequence number



# implement RDT

senderSocket = socket(AF_INET, SOCK_DGRAM)  # create a socket
senderSocket.bind(('', ACK_port))

# send data until every packets are sent and ACKed
while P != {}:
    # transmit every packet in P
    for sqnb in P:
        senderSocket.sendto(pickle.dumps(P[sqnb]), (Emu_address, e_port))  # send the packet
        seqlogFile.write(str(P[sqnb].getSeqnum()) + '\n')  # record the sent packet's sequence number

    # receive the ACKs before timeout
    try:
        senderSocket.settimeout(TOI)
        while True:
            ACK_packet, emulator_addr = senderSocket.recvfrom(40960)
            ACK_packet = pickle.loads(ACK_packet)  # decode the pickled class received

            # record the ACKed sequence number
            acklogFile.write(str(ACK_packet.getSeqnum()) + '\n')

            # get the sequence number of the packet
            ACK_seqnum = ACK_packet.getSeqnum()

            if ACK_seqnum in P:
                P.pop(ACK_seqnum)  # pop out the ACKed element in P since it has already been received

    except Exception:
        if P == {}:
            break
        else:
            continue

# every packet has been received by the receiver, send EOT
EOT = Packet(2, 9999, '')
senderSocket.sendto(pickle.dumps(EOT), (Emu_address, e_port))

# record the sending
seqlogFile.write(str(EOT.getSeqnum()) + '\n')

# get the ACKed EOT
senderSocket.settimeout(1000)
ACK_packet, emulator_addr = senderSocket.recvfrom(40960)
ACK_packet = pickle.loads(ACK_packet)

# record the ACKed sequence number
acklogFile.write(str(ACK_packet.getSeqnum()) + '\n')

if ACK_packet.getType() == 2:
# close everything and quit
    senderSocket.close()
    seqlogFile.close()
    acklogFile.close()
    exit(0)
