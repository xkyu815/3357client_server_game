import selectors
import socket
import json
from enum import Enum

class CommandType(Enum):
    SWITCH_ROOM = 1
    NEW_MESSAGE = 2


class BaseCommand:
    def __init__(self, type: CommandType, content: str) -> None:
        self.type = type
        self.content = content


def handle_command(cmd, conn):
    type = cmd['type']
    if type == CommandType.SWITCH_ROOM:
        handle_command_switch_room(cmd, conn)
    elif type == CommandType.NEW_MESSAGE:
        handle_command_new_message(cmd, conn)


def handle_command_switch_room(cmd: BaseCommand, conn):
    print("type = " + cmd['id'] + " content = " + cmd['content'])
    conn.send("handle_command_switch_room".encode())

def handle_command_new_message(cmd: BaseCommand, conn):
    print("type = " + cmd['id'] + " content = " + cmd['content'])
    conn.send("handle_command_new_message".encode())

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    if data:
        c_str = str(data, encoding = 'UTF-8')
        print(c_str)
        cmd = json.loads(c_str)
        handle_command(cmd, conn)
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()

sock = socket.socket()
sock.bind(('localhost', 1234))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)