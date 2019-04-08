import socket
import threading

class Scanner(threading.Thread):

    def __init__(self, address, ports):
        threading.Thread.__init__(self)
        self.address = address
        self.ports = ports

    def __checksum(self, message):
        if (type(message).__name__ != 'str'):
            message = message.decode('ascii')
            print(message)
        lbytes = list(map(ord, message))
        return hex(sum(lbytes) % 256)[2:].encode('ascii')

    def __read_response(self, sock):
        """
        Socket-level read of remote stub response.
        """
        d = b''
        while True:
            r_byte = sock.recv(1)
            if r_byte is None or len(r_byte) == 0 or r_byte == 0:
                break
            d += r_byte
            if r_byte == b'#' and d[::-1] != b'\\':
                d += sock.recv(2)
                return d
        return None

    def __receive(self, sock, timeout=False):
        """
        Receive data from remote stub.

            :returns Response: Data received
        """
        try:
            if timeout is True:
                sock.settimeout(2)
            rdata = self.__read_response(sock)
            if timeout is True:
                sock.settimeout(None)
            return rdata
        except socket.timeout:
            return None

    def __send(self, sock, command):
        chk = self.__checksum(command)
        to_send = b'$' + bytes(command, 'ascii') + b'#' + chk
        sock.send(to_send)

    def __connect(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((self.address, port))
        except Exception:
            return None
        s.settimeout(None)
        return s

    def __probe(self, port):
        sock = self.__connect(port)
        if sock is None:
            return False

        commands = [
            'QStartNoAckMode',  # No need for acknowledgement
            '!',                # If we found a server, let's not make it 
                                # exit once we disconnect
            'qSupported'        # Ask supported features
        ]

        for command in commands:
            self.__send(sock, command)
            data = self.__receive(sock, timeout=True)

        if data is None:
            sock.close()
            return

        if 'PacketSize' in data.decode('ascii'):
            print("\n[GDB Server @ %s:%d]: Capabilities: %s" % (
                self.address,
                port,
                data.decode('ascii'))
            )

        sock.close()

    def run(self):
        for port in self.ports:
            self.__probe(port)
