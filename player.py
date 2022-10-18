from re import U
import socket
import argparse
from urllib.parse import urlparse
import signal
import sys

bufferSize = 1024

parser = argparse.ArgumentParser("client parameters passed")
parser.add_argument('playerName',type=str,help = "name of player")
parser.add_argument('serverAddress',type=str,help = "address of server")
options = parser.parse_args()
parse_result = urlparse(options.serverAddress)
playerName = options.playerName
hostname = parse_result.hostname
port = parse_result.port
if (playerName == None or hostname == None or port == None):
	mesg = "Invalid server address\n"
	sys.stdout.write(mesg)
	quit()

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Send to server using created UDP socket
def join():
	msgFromClient       = "Room will wait for players at port: {}\nUser {} joined from address".format(port,playerName)
	bytesToSend         = str.encode(msgFromClient)
	UDPClientSocket.sendto(bytesToSend,(hostname,port))

	msgFromServer = UDPClientSocket.recvfrom(bufferSize)
	address = msgFromServer[1]
	pw_bytes = msgFromServer[0].decode("utf-8")
	sys.stdout.write(pw_bytes + '\n')

def exit(sig, frame):
	sys.exit(0)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, exit)
	join()
# Pass user input to the server
	while(True):
		userinput = input('> ')
		if userinput == 'exit':
			quit()
		commandToSend = str.encode(userinput)
		UDPClientSocket.sendto(commandToSend,(hostname,port))
		resultFromServer = UDPClientSocket.recvfrom(bufferSize)
		result = resultFromServer[0].decode("utf-8")
		sys.stdout.write(result + '\n') 

	