import sys
import socket
import threading

class Scanner(threading.Thread):

    def __init__(self, address, port):
        threading.Thread.__init__(self)
        self.address = address
        self.port = port

    def __checksum(self, message):
        if (type(message).__name__ != 'str'):
            message = message.decode('ascii')
        lbytes = list(map(ord, message))
        return hex(sum(lbytes) % 256)[2:].encode('ascii')

    def __receive(self, sock):
        data = None
        sock.settimeout(0.5)
        try:
            data = sock.recv(4096)
        except socket.timeout:
            return None
        sock.settimeout(None)
        return data

    def __send(self, sock, command):
        chk = self.__checksum(command)
        command = bytes(command, 'ascii')
        to_send = b'+$' + command + b'#' + chk
        sock.send(to_send)
        return self.__receive(sock)

    def __probe(self, sock):
        commands = [
            'QStartNoAckMode',  # No need for acknowledgement
            '!',                # If we found a server, let's not make it 
                                # exit once we disconnect
            'qSupported'        # Ask supported features
        ]
        for command in commands:
            data = self.__send(sock, command)

        sock.close()
        if data is None:
            return False
        if data is None or 'PacketSize' not in data.decode('ascii'):
            return False
        return True

    def __connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect((self.address, self.port))
        except socket.timeout:
            return None
        except Exception as ex:
            return None
        s.settimeout(None)
        return s

    def run(self):
        sys.stdout.write("Scanning %s:%d ...\r" % (self.address, self.port))
        sys.stdout.flush()
        sock = self.__connect()
        if sock is None:
            return
        if self.__probe(sock) is False:
            return
        print("\nFound gdbserver on address %s:%d" % (self.address, self.port))
