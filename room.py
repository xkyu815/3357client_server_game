import socket
import signal
import sys
import argparse
import selectors
from optparse import OptionParser
from urllib.parse import urlparse

# Saved information on the room.

name = ''
description = ''
items = []
connections = []
adjacent_rooms = [] # Order of tuple contents: direction, hostname, port

# Constant list used for checking if a movement command was called
directions = ['north', 'south', 'east', 'west', 'up', 'down']

# Selector for helping us select incoming data and connections from multiple sources.

sel = selectors.DefaultSelector()
# List of clients currently in the room.

client_list = []

# Signal handler for graceful exiting.  

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)

# Search the client list for a particular player.

# initialize inventory
user_inventory = []
playername_list = []
my_clientList = []
# Items in the room initially

def look():
    if len(items)>0 :
        mesg = "\n{}\n\n{}\n\nIn this room, there are:\n{}\n{}".format(name,description,"\n".join(items),"\n".join(playername_list))
    elif len(items)==0 and len(playername_list)>0:
        mesg = "\n{}\n\n{}\n\nIn this room, there are:\n{}".format(name,description,"\n".join(playername_list))
    elif len(items)>0 and len(playername_list)==0:
        mesg = "\n{}\n\n{}\n\nIn this room, there are:\n{}".format(name,description)
    else:
        mesg = "\n{}\n\n{}\n\nThe room is empty.".format(name,description)
    return mesg

def take(item):
    if item not in items:
        mesg = "{} cannot be taken.The item must exist in the room to be taken".format(item)
    else:
        mesg = "{} taken".format(item)
        user_inventory.append(item)
        items.remove(item)
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
        items.append(item)
        mesg = "You are dropping {}".format(item)
    return mesg

def exit(sig, frame):
    while user_inventory != []:
        drop(user_inventory[0])
    sys.exit("Interrupt received, shutting down...")

def client_search(player):
    for reg in client_list:
        if reg[0] == player:
            return reg[1]
    return None


    
# Search the client list for a particular player by their address.

def client_search_by_address(address):
    for reg in client_list:
        if reg[1] == address:
            return reg[0]
    return None

# Add a player to the client list.

def client_add(player, address):
    registration = (player, address)
    client_list.append(registration)

# Remove a client when disconnected.

def client_remove(player):
    for reg in client_list:
        if reg[0] == player:
            client_list.remove(reg)
            break

# Printing the list of player's in the room that
def get_other_players(address):
    summary = ""
    # Adding list of other players/ clients in the room to the summary
    if len(playername_list) == 1:
        summary += "There are no other players in this room."
    elif len(playername_list) == 2:
        summary += "There is one other player in this room: "
        for client in playername_list:
            if client[1] != address:
                summary += '{}.\n'.format(client[0])
    else:
        summary += 'The other players in this room are: \n'
        for client in playername_list:
            if client[1] != address:
                summary += '{}\n'.format(client[0])
# Summarize the room into text.

def summarize_room():
    
    global name
    global description
    global items

    # Pack description into a string and return it.

    summary = name + '\n\n' + description + '\n\n'
    if len(items) == 0:
        summary += "The room is empty.\n"
    elif len(items) == 1:
        summary += "In this room, there is:\n"
        summary += f'  {items[0]}\n'
    else:
        summary += "In this room, there are:\n"
        for item in items:
            summary += f'  {item}\n'

    return summary

# Print a room's description.

def print_room_summary():

    print(summarize_room()[:-1])

def move_to_room(direction):
    global adjacent_rooms
    global directions
    global port

    for each_server in adjacent_rooms:
        if each_server[0] == direction:
            print_room_summary
            room1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(port)
            room1_socket.bind(('', port))
            print('\nRoom will wait for players at port: ' + str(room1_socket.getsockname()[1]))
            room1_socket.listen(100)
            room1_socket.setblocking(False)
            print('Waiting for incoming client connections ...')
            sel.register(room1_socket,selectors.EVENT_READ, accept_client)
            

# Process incoming message.
def handle_message_from_client(sock,addr):
    message = sock.recv(1024).decode()
    tokens = message.split()
    command = tokens[0]
    if command in directions:
        result = move_to_room(command)
    elif command == 'say':
        msg = '{} said \"{}\"'.format(client_search_by_address(addr),message[4:-1])
        for client in connections:
            if client is not sock:
                client.send(msg.encode())
        response = 'You said \"{}\".'.format(message[4:-1])
        sock.send(response.encode())
    
    else:
        if len(tokens) > 1:
            args = tokens[1]
        if command == 'look':
            #summary = summarize_room()[:-1]
            #summary += get_other_players(addr)
            #result = summary[:-1]
            result = look()
        elif command == 'take':
            result = take(args)
        elif command == 'drop':
            result = drop(args)
        elif command == 'inventory':
            result = inventory()
        else:
            result = "Command doesn't exist."
        sock.send(result.encode())

def accept_client(sock,mask):
    player_sock, addr = sock.accept()
    welcome = summarize_room().encode()
    player_sock.send(welcome)
    playername = player_sock.recv(1024).decode()
    client_add(player_sock,playername)
    for playersock, player_name in client_list:
        if playername not in playername_list:
            playername_list.append(playername)
        if player_name != playername:
            message = "\n{} enters the room.".format(playername)
            playersock.send(message.encode())
            
   # player_sock.setblocking(False)
    sel.register(player_sock, selectors.EVENT_READ, handle_message_from_client)

# Our main function.

def main():
    global name
    global description
    global items
    global connections
    global port

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments for room settings.

    parser = argparse.ArgumentParser()
    parser.add_argument("-s",type=str,nargs=1)
    parser.add_argument("-n",type=str,nargs=1)
    parser.add_argument("-e",type=str,nargs=1)
    parser.add_argument("-w",type=str,nargs=1)
    parser.add_argument("-u",type=str,nargs=1)
    parser.add_argument("-d",type=str,nargs=1)
    parser.add_argument("port", type=int, help="port number to list on")
    parser.add_argument("name", help="name of the room")
    parser.add_argument("description", help="description of the room")
    parser.add_argument("items", nargs='*', help="items found in the room by default")
    args = parser.parse_args()
    port=args.port
    name = args.name
    description = args.description
    items = args.items

    if args.n:
        server_addr = urlparse(args.n[0])
        adjacent_rooms.append(("north", str(server_addr.hostname), server_addr.port))
        print(args.n[0])
    if args.s:
        server_addr = urlparse(args.s[0])
        adjacent_rooms.append(("south", str(server_addr.hostname), server_addr.port))
    if args.e:
        server_addr = urlparse(args.e[0])
        adjacent_rooms.append(("east", str(server_addr.hostname), server_addr.port))
    if args.w:
        server_addr = urlparse(args.w[0])
        adjacent_rooms.append(("west", str(server_addr.hostname), server_addr.port))
    if args.u:
        server_addr = urlparse(args.u[0])
        adjacent_rooms.append(("up", str(server_addr.hostname), server_addr.port))
    if args.d:
        server_addr = urlparse(args.d[0])
        adjacent_rooms.append(("down", str(server_addr.hostname), server_addr.port))

    # Report initial room state.
    print('Room Starting Description:\n')
    print_room_summary()

    # Create the socket.  We will ask this to work on any interface and to use
    # the port given at the command line.  We'll print this out for clients to use.

    room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    room_socket.bind(('', port))
    print('\nRoom will wait for players at port: ' + str(room_socket.getsockname()[1]))
    room_socket.listen(100)
    room_socket.setblocking(False)
    print('Waiting for incoming client connections ...')
    sel.register(room_socket,selectors.EVENT_READ, accept_client)
    
     # Loop forever waiting for messages from clients.

    while True:
        events = sel.select()
        for key,mask in events:
            callback = key.data
            callback(key.fileobj,mask)
        
        # Receive a packet from a client and process it.
       # conn, addr = room_socket.accept()

        # Process the message and retrieve a response.
       # response = process_message(room_socket,mask)

        # Send the response message back to the client.

       # conn.send(response.encode())



if __name__ == '__main__':
    main()

