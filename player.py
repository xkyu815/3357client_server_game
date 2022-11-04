import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address.

server = ('', '')

# User name for player.

name = ''

# Inventory of items.

inventory = []

# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message='exit'
    client_socket.send(message.encode())
    for item in inventory:
        message = f'drop {item}'
        client_socket.send(message.encode())
    sys.exit(0)

# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)

# Function to handle incoming messages from server.
def handle_keyboard_input(file, mask):
    # Prompt the user before beginning.

        # Get a line of input.

        line=sys.stdin.readline()[:-1]
        client_socket.send(line.encode())

        # Process command and send to the server.
        do_prompt()
        process_command(client_socket,mask)

# Function to join a room.

def join_room():
    message = f'join {name}'
    client_socket.send(message.encode())
    response = client_socket.recv(1024)
   # client_socket.setblocking(False)
    print(response.decode())

def send_player_name(sock,mask):
    playername = name
    sock.send(playername.encode())
    playerNotifyfromServer = sock.recv(1024).decode()
    print(playerNotifyfromServer)

# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(file,mask):
    # Parse command.
    command = file.recv(1024).decode()
    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        client_socket.send(message.encode())

    # Check for particular commands of interest from the user.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            client_socket.send(message.encode())
        sys.exit(0)
    elif (command == 'look'):
        response = client_socket.recv(1024)
        print(response.decode())
    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')
    elif (words[0] == 'take'):
        response = client_socket.recv(1024)
        print(response.decode())
        words = response.decode().split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])
    elif (words[0] == 'drop'):
        response = client_socket.recv(1024)
        print(response.decode())
        inventory.remove(words[1])
    else:
        response = client_socket.recv(1024)
        print(response.decode())
    client_socket.setblocking(False)

# Our main function.

def main():

    global name
    global client_socket
    global server

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("server", help="URL indicating server location in form of room://host:port")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    try:
        server_address = urlparse(args.server)
        if ((server_address.scheme != 'room') or (server_address.port == None) or (server_address.hostname == None)):
            raise ValueError
        host = server_address.hostname
        port = server_address.port
        server = (host, port)
    except ValueError:
        print('Error:  Invalid server.  Enter a URL of the form:  room://host:port')
        sys.exit(1)
    name = args.name

     # Now we try to make a connection to the server.

    print('Connecting to server ...')
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print('Error:  That host or port is not accepting connections.')
        sys.exit(1)

    # The connection was successful, so we can prep and send a registration message.

    print('Connection to server established. Sending intro message...\n')
    # Send message to enter the room.

    join_room()
   

    # Set up our selector.

    client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ,
                 send_player_name)
    #sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)

    
    # We now loop forever, sending commands to the server and reporting results

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
 

if __name__ == '__main__':
    main()
