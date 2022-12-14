import socket
import argparse
import signal
import sys

localIP     = "127.0.0.1"
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

# initialize inventory
user_inventory = []

# Items in the room initially
itemInRoom = items

def look():
	if items is not None:
		mesg = "\n{}\n\n{}\n\nIn this room, there are:\n{}".format(name,description,"\n".join(itemInRoom))
	else:
		mesg = "\n{}\n\n{}\n\nThe room is empty.".format(name,description)
	return mesg

def take(item):
	if item not in itemInRoom:
		mesg = "Item cannot be taken.The item must exist in the room to be taken"
	else:
		mesg = "{} taken".format(item)
		user_inventory.append(item)
		itemInRoom.remove(item)
	return mesg

def inventory():
	if user_inventory == []:
		mesg = "Holding nothing"
	else:
		mesg = "You are holding: \n{}".format("\n".join(user_inventory))
	return mesg

def drop(item):
	if item not in user_inventory:
		mesg = "You are not holding {}".format(item)
	else:
		user_inventory.remove(item)
		itemInRoom.append(item)
		mesg = "You are dropping {}".format(item)
	return mesg

def exit(sig, frame):
	while user_inventory != []:
		drop(user_inventory[0])
	sys.exit(0)

def join():
	mesg_description = "Room Starting Description:\n{}\n\n{}\n\nIn this room, there are:\n{}".format(name,description,"\n".join(items))
	print(mesg_description)
	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)  # Receiving a request from client
	bytesToSend = str.encode(mesg_description)
	message = bytesAddressPair[0]
	address = bytesAddressPair[1]
	pw_bytes = message.decode("utf-8")
	print(pw_bytes,address)
	UDPServerSocket.sendto(bytesToSend,address)  # Sending a reply to client
	return address

# pass cient ip address
clientAddress = join()

while(True):
	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
	message = bytesAddressPair[0]
	pw_bytes = message.decode("utf-8")
	tokens = pw_bytes.split(' ')
	command = tokens[0]
	if len(tokens) > 1:
		args = tokens[1]
	if command == 'look':
		result = look()
	elif command == 'take':
		result = take(args)
	elif command == 'drop':
		result = drop(args)
	elif command == 'inventory':
		result = inventory()
	elif command == 'exit':
		signal.signal(signal.SIGINT, exit)
		sys.exit("Interrupt received, shutting down...")
	else:
		result = "Command doesn't exist."
	bytesToSend = str.encode(result)
	UDPServerSocket.sendto(bytesToSend,clientAddress)