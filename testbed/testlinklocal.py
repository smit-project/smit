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

from socket import *

addrinfo = getaddrinfo('fe80::6c0e:e0d6:d949:64fe%lowpan0', 56789, AF_INET6, SOCK_DGRAM, IPPROTO_UDP)
(family, socktype, proto, canonname, sockaddr) = addrinfo[0]
s = socket(family, socktype, proto)
print sockaddr
inet_pton(AF_INET6, 'fe80::6c0e:e0d6:d949:64fe')
print sockaddr
s.connect(('fe80::6c0e:e0d6:d949:64fe', 56789, 0, 6))
