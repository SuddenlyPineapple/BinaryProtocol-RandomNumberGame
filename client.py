import struct
import socket
import sys
import time
import binascii
from functions import *
from operation import OPERATION

class Client():
    def __init__(self):
        pass
        print("Initialize Client Protocol!")

    def dec2bin(self, d):
        # dec -> bin
        b = bin(d)
        return b

    def intTObool(self, num):
        bin_string = format(num, '04b')
        return [x == '1' for x in bin_string[::-1]]

    # Packing Frame data to Binary
    def pack_message(self,OP,AN,ID):
        operation = OPERATION(OP)

        packer = struct.Struct('5? 4? 3?')
        message = intTOboolArr(operation.value, '05b') + intTOboolArr(AN, '04b') + intTOboolArr(ID, '03b')
        packed_data = packer.pack(*message)

        return packed_data

    #For unpacking massages from Binary to Frame structure
    def unpack_message(self, data):
        unpacker = struct.Struct('5? 4? 3?')
        unpacked_data = unpacker.unpack(data)
        OP = OPERATION(boolArrTOint(unpacked_data[:5]))
        AN = boolArrTOint(unpacked_data[5:9])
        ID = boolArrTOint(unpacked_data[9:])
        return [OP,AN,ID]


    def start(self):
        print "Client is starting!"

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 10000)
        print >> sys.stderr, 'connecting to %s port %s' % server_address
        sock.connect(server_address)
        #print(struct.Struct('5? 4? 3?').size)

        #Zmienne Clienta
        ID=0
        TRIES=0

        try:
            #Packing Data to Binary
            error = False
            number = 16
            while number < 0 or number > 15:
                if error:
                    number = input("Wrong number! Chose form 0 to 15: ")
                else:
                    number = input('Pick one number from 0 to 15 as the number of tries:')
                    if number < 0 or number > 15:
                        error = True

            message = self.pack_message(OPERATION.GET_ID_TRIES, number, ID)
            #print >> sys.stderr, 'sending "%s"' % binascii.hexlify(message)
            sock.sendall(message)

            while True:
                #Receive response with ID OR ID&TRIES
                data = sock.recv(12)
                received = self.unpack_message(data)
                #print(received)

                action = received[0]
                answer = received[1]
                token = received[2]

                if action == OPERATION.SEND_ID:
                    ID = token
                    TRIES = answer
                    print('send' + str(received))
                    print "Waiting for second player to join and input number of tries!"

                    # time.sleep(10)
                    # message = self.pack_message(OPERATION.TRIES, 0, ID)
                    # sock.sendall(message)
                    # data  = sock.recv(12)
                    # if len(data) == 12:
                    #     received = self.unpack_message(data)
                        #if received[0] == OPERATION.TRIES: #and received[1] !=0:
                        #print "Tries: " + str(received)

                    while True:
                        time.sleep(2)
                        message = self.pack_message(OPERATION.TRIES, 1, ID) #TRIES z AN ustawionym na 1 pyta o to czy drugi gracz wpisal juz swoja liczbe do wylosowania
                        sock.sendall(message)
                        data  = sock.recv(12)
                        received = self.unpack_message(data)
                        print "Tries log: " + str(received)
                        if received[0] == OPERATION.TRIES and received[1] !=0:
                            break

                game = True
                while game:

                    #Winning
                    if received[0] == OPERATION.RESULT:
                        print "Congratulations! You have won!"
                        game = False

                    #Losing
                    elif received[0] == OPERATION.TRIES and received[1] == 0:
                        print "Game over! You used all of your tries!"
                        game = False

                    #Game in progress
                    else:
                        error = False
                        number = 16
                        while number <0 or number > 15:
                            if error:
                                number = input ("Wrong number! Chose from 0 to 15: ")
                            else:
                                number = input('Try to guess the number. Pick one from 0 to 15:')
                                if number <0 or number > 15 :
                                    error = True

                        #Sending pick
                        message = self.pack_message(OPERATION.GUESS, number, ID)
                        sock.sendall(message)

                    #Receiving picking result
                    data = sock.recv(12)
                    received = self.unpack_message(data)
                    #print "Tries left: " + str(received)
                    print "Tries left: " + str(received[2])

                break

            #Look for the response
            # amount_received = 0
            # amount_expected = len(message)
            #
            # while amount_received < amount_expected:
            #     data = sock.recv(12)
            #     amount_received += len(data)
            #     print >> sys.stderr, 'received "%s"' % binascii.hexlify(data)

        finally:
            print >> sys.stderr, 'closing socket'
            sock.close()