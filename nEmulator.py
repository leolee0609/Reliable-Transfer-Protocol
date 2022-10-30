import sys
import time
import copy
import pickle
import random
from fractions import Fraction
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
forward_port = int(sys.argv[1])  # set the port number of forward direction
receiver_address = sys.argv[2]  # get the receiver's address
receiver_port = int(sys.argv[3])  # get the receiver's port number
backward_port = int(sys.argv[4])  # set the port number of backward direction
sender_address = sys.argv[5]  # get the sender's address
sender_port = int(sys.argv[6])  # get the sender's receiving UDP port number
discard_pro = float(sys.argv[7])  # get the discard probability
ifVerbose = bool(sys.argv[8])  # set if execute the verbose mode

def discard_decider():
    '''
    returns True or False based on discard_pro to decide whether a packet
    should be discarded.
    
    discard_decider: None -> Bool
    '''
    if discard_pro == 0.0:
        return False

    # get the weight of the possibility of discarding and not discarding
    R = Fraction(* discard_pro.as_integer_ratio())
    true_weight = R.numerator
    false_weight = R.denominator - R.numerator

    return random.choices([True, False], weights = [true_weight, false_weight], k = 1)[0]

# build a socket to communicate with sender
commuSender_socket = socket(AF_INET, SOCK_DGRAM)
commuSender_socket.bind(('', forward_port))

# build a socket to communicate with receiver
commuReceiver_socket = socket(AF_INET, SOCK_DGRAM)
commuReceiver_socket.bind(('', backward_port))


# start emulating internet
while True:
    # get packet from sender
    sender_packet, senderAddr = commuSender_socket.recvfrom(40960)


    sender_packet = pickle.loads(sender_packet)  # decode the packet

    # report the receiving
    if ifVerbose:
            print('Receiving Packet ' + str(sender_packet.getSeqnum()))

    if (sender_packet.getType() == 2) or (not discard_decider()):  
        # if the packet is a EOT or we don't want to discard it
        commuReceiver_socket.sendto(pickle.dumps(sender_packet), \
            (receiver_address, receiver_port))  # send the packet to receiver

        # report the forwarding
        if ifVerbose:
            print('Forwarding Packet ' + str(sender_packet.getSeqnum()))

        # get packet from receiver
        receiver_packet, receiverAddr = commuReceiver_socket.recvfrom(40960)


        receiver_packet = pickle.loads(receiver_packet)  # decode the packet

        # report the receiving
        if ifVerbose:
                print('Receiving ACK ' + str(receiver_packet.getSeqnum()))

        if (receiver_packet.getType() == 2) or (not discard_decider()):
            # if the packet is a EOT or we don't want to discard it
            commuSender_socket.sendto(pickle.dumps(receiver_packet), \
                (sender_address, sender_port))  # send the packet to sender

            # report the forwarding
            if ifVerbose:
                print('Forwarding ACK ' + str(receiver_packet.getSeqnum()))

        else:
            # report the discarding
            if ifVerbose:
                print('Discarding ACK ' + str(receiver_packet.getSeqnum()))

    else:
        # report the discarding
        if ifVerbose:
            print('Discarding Packet ' + str(sender_packet.getSeqnum()))

    
    
        