import socket
import argparse
from urllib.parse import urlparse
 
msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("127.0.0.1", 7777)
bufferSize          = 1024

parser = argparse.ArgumentParser("client parameters passed")
parser.add_argument('playerName',type=str,help = "name of player")
parser.add_argument('serverAddress',type=str,help = "address of server")
options = parser.parse_args()
parse_result = urlparse(options.serverAddress)
hostname = parse_result.hostname
port = parse_result.port

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
pw_bytes = msgFromServer[0].decode("utf-8")
print(pw_bytes)

