#!/usr/bin/env python3

import sys
import time
import ipaddress
import argparse

from scanner import Scanner

# Gdbserver does not have a default port so our best bet is to use
# some of the most common gdbserver ports based on Google search.

PORTS = [1234, 2345, 3333, 4444, 5000, 8000, 9000, 9999, 12345]

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
    sys.stdout.write("Scanning %s ...\r" % (address))
    sys.stdout.flush()
    if (len(threads) >= thread_count):
        process_threads()
    try:
        scanner = Scanner(str(address), PORTS)
        scanner.start()
        threads.append(scanner)
    except Exception as ex:
        print(str(ex))

