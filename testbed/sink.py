'''
SMIT package implements a basic IoT platform.

Copyright 2016-2018 Distributed Systems Security, Data61, CSIRO

This file is part of SMIT package.

SMIT package is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

SMIT package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SMIT package.  If not, see <https://www.gnu.org/licenses/>.
'''

import socket

host = "b:b:b:b:5:6:7:8"
port = 56789
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind((host, port))

while True:
    data, addr = sock.recvfrom(1024)
    print "From: " + str(addr)
    print "Data: " + data
    print '-' * 50
