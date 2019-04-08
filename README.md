
# GDB Scanner

GDB Scanner is a small script to scan for GDB servers on a network.

# What is GDB?

GDB (GNU Debugger) is a portable debugger that runs on many Unix-like systems. It also works on Windows, e.g. via Cygwin. The Wikipedia page at https://en.wikipedia.org/wiki/GNU_Debugger provides a nice intro to what GDB is.

# What is GDB server?

The GDB server (or a GDB stub) is a running instance of the GDB debugger that can be accessed remotely.

# Why GDB Scanner?

Good that you asked. Imagine you are working as a penetration tester / red team member (or whatever). Would not it be great to find a quick and easy way to compromise development systems? Of course it would be great. If you find a GDB server you can interact with, it's 100% (or at least very close to it) you will be able to get a shell on the box.

# How?

What this script does:
1. It looks for ports most commonly used by GDB server. GDB server does not have a default port so the port list used is based on the most popular GDB server ports found by searching on Google.
2. If an open port is found, it sends 3 commands to probe for the presence of a GDB server. These are:
    1. `QStartNoAckMode` - This is so that we do not have to deal with acknowledgement packets (+)
    2. `!` - Switch to extended mode. As much as I wanted to have a scanner that does not change the state of the GDB server, without this, once disconnected the GDB server would terminate.
    3. `qSupported` - To fetch a list of features supported by the GDB server. This step is not really necessary but it's a very convincing way to prove it's 100% that we found a GDB server.
3. If the service on the port being probed responds to the previous commands as expected, the script will print the address and port the GDB server was found on.

# How to use?

Just type the below command for more info.

```
./gdbscanner.py -h
```

# Disclaimer

Using the tool for attacking targets without prior mutual consent is illegal. It is the end user’s responsibility to obey all applicable local, state and federal laws. I assume no liability and I am not responsible for any misuse or damage caused by this tool.

