#!/usr/bin/env python3

import sys
import time
import socket
import ipaddress
import threading
import argparse

# Gdbserver does not have a default port so our best bet is to use
# some of the most common gdbserver ports based on Google search.

PORTS = [1234, 2345, 3333, 4444, 5000, 8000, 9000, 9999, 12345]

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
        if data is None or b'PacketSize' not in data:
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
        sys.stdout.write("Scanning %s:%d ...\r" % (address, port))
        sys.stdout.flush()
        sock = self.__connect()
        if sock is None:
            return
        if self.__probe(sock) is False:
            return
        print("\nFound gdbserver on address %s:%d" % (self.address, self.port))

parser = argparse.ArgumentParser()
parser.add_argument("network", help="The network to scan incl. CIDR netmask, e.g.: 192.168.0.0/24.")
parser.add_argument("-t", "--threads", help="The number of scanner threads. Default is 40.", type=int)
args = vars(parser.parse_args())

threads = []
thread_count = 40
if args.get('threads') is not None:
    thread_count = args.get('threads')

def process_threads():
    while len(threads) > thread_count - 1:
        for t in threads:
            if t.isAlive() is False:
                t.join()
                threads.remove(t)
        time.sleep(0.1)

for address in ipaddress.ip_network(args.get('network')).hosts():
    for port in PORTS:
        if (len(threads) >= thread_count):
            process_threads()
        try:
            scanner = Scanner(str(address), port)
            scanner.start()
            threads.append(scanner)
        except Exception as ex:
            print(str(ex))

