import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("localhost", 1234))

while 1:
    input_str = input("enter message:")
    cmd = '{"type":1, "content":"' + input_str +'"}'
    sock.sendall(cmd.encode())
    res = sock.recv(1024)
    print(res)