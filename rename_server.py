#server modified from https://www.geeksforgeeks.org/socket-programming-python/
# first of all import the socket library 
import socket
from reps import FileRenamer

server_sock = socket.socket()
print("rename server created")

port = 5016

server_sock.bind(('', port))
print("rename server binded to %s" %(port))

server_sock.listen(5)
print "rename server listening for connections"

RENAMER = FileRenamer()

while True:

    connection, address = server_sock.accept()
    print('Got connection from', address)

    name = RENAMER.next_available_name()
    connection.send(name)
    print('sent name ', name)

    connection.close()
