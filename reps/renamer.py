import socket

#FileRenamer
# @purpose - an object used to get the next available names using the RepS naming scheme
class FileRenamer:

    def __init__(self, basename='syalper-'):
        self._base = basename
        self._count = 0

    #next_available_name
    # @params - no params
    # @return - the next available file name
    # @purpose - return the next available file name following the RepS naming scheme
    def next_available_name(self):
        name = self._base + str(self._count)
        self._count = self._count + 1
        return name

    #get_name_from_remote
    # @params - ip address and port number
    # @return - the next available file name from remote naming server
    # @purpose - return the next available file name, but the name comes from
    #           a remote server.
    def get_name_from_remote(self, ipaddress, port):
        try:
            sock = socket.socket()
            sock.connect((ipaddress, port))
        except socket.error as ex:
            raise Exception('couldn\'t connect to rename server')

        name = ''
        try:
            name = sock.recv(1024)
        except socket.error as ex:
            raise Exception('couldn\'t recieve name from rename server')

        try:
            sock.close()
        except socket.error as ex:
            raise Exception('couldn\'t close connection to rename server')

        return name