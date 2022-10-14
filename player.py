import socket
import argparse
from urllib.parse import urlparse
import signal
import sys

serverAddressPort   = ("127.0.0.1", 7777)
bufferSize          = 1024

parser = argparse.ArgumentParser("client parameters passed")
parser.add_argument('playerName',type=str,help = "name of player")
parser.add_argument('serverAddress',type=str,help = "address of server")
options = parser.parse_args()
parse_result = urlparse(options.serverAddress)
playerName = options.playerName
hostname = parse_result.hostname
port = parse_result.port

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Send to server using created UDP socket
def join():
	msgFromClient       = "Room will wait for players at port: {}\nUser {} joined from address".format(port,playerName)
	bytesToSend         = str.encode(msgFromClient)
	UDPClientSocket.sendto(bytesToSend,serverAddressPort)

	msgFromServer = UDPClientSocket.recvfrom(bufferSize)
	address = msgFromServer[1]
	pw_bytes = msgFromServer[0].decode("utf-8")
	print(pw_bytes)

def exit(sig, frame):
	sys.exit(0)

join()

# Pass user input to the server
while(True):
	signal.signal(signal.SIGINT, exit)
	userinput = input('> ')
	commandToSend = str.encode(userinput)
	UDPClientSocket.sendto(commandToSend,serverAddressPort)
	resultFromServer = UDPClientSocket.recvfrom(bufferSize)
	result = resultFromServer[0].decode("utf-8")
	print(result)

	