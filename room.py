import socket
import argparse
import signal

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

#def dosomthing(port=options.port, name=options.name, 
#				description=options.description, items=options.items):
#				return 0

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
		itemInRoom.append(item)
		user_inventory.remove(item)
		mesg = "You are dropping {}".format(item)
	return mesg

def exit(signum, frame):
	exit(1)

bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
mesg_description = "Room Starting Description:\n{}\n\n{}\n\nIn this room, there are:\n{}".format(name,description,"\n".join(items))
bytesToSend = str.encode(mesg_description)
message = bytesAddressPair[0]
address = bytesAddressPair[1]

clientMsg = "Room Starting Description:\n\n{}\n\n{}".format(name,description)
print(clientMsg)
  
# Sending a reply to client

UDPServerSocket.sendto(bytesToSend,address)

# Receiving a request from client
pw_bytes = message.decode("utf-8")
print(pw_bytes,address)

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
	else:
		print("Command doesn't exist.")
	bytesToSend = str.encode(result)
	UDPServerSocket.sendto(bytesToSend,address)