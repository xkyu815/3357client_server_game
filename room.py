import socket
import argparse

localIP     = "127.0.0.1"
##localPort   = 7777
bufferSize  = 1024

parser = argparse.ArgumentParser("server parameters passed")
parser.add_argument('port',type=int,help = "port to listen")
parser.add_argument('name',help = "the name of the room running on the server")
parser.add_argument('description',help = "description of the room")
parser.add_argument('items',help = "items to be found in the room initially",nargs="*")

options = parser.parse_args()

description = options.description  # player name from server
name = options.name     # description from server
items = options.items 
localPort = options.port   
# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 # Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

 # Listen for incoming datagrams

def dosomthing(port=options.port, name=options.name, 
				description=options.description, items=options.items):
				return 0

while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    mesg_description = "Room Starting Description:\n{}\n\n{}\n\nIn this room, there are:\n{}".format(name,description,"\n".join(items))
    bytesToSend = str.encode(mesg_description)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Room Starting Description:\n\n{}\n\n{}".format(name,description)
    print(clientMsg)
   # msgFromClient = UDPServerSocket.recvfrom(bufferSize)
   # pw_bytes = msgFromClient[0].decode("utf-8")
   # print(pw_bytes)

    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend,address)