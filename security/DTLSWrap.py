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

import ssl
import socket
import sys
import os
import traceback

sys.path.insert(0, '..')
from utils import Utils
from dtls import do_patch


class DtlsWrap(object):
    """This is a wrap class for some functions from PyDTLS.
       Note that this class only wraps essential functions from PyDTLS.
       To use the class, it is requried to have the configuration file "dtlscnf".
       For more information and available functions, please see the documentation of PyDTLS.
    """
    utl = Utils()
    dtls_cnf = 'dtlscnf'
    dtls_sock = None
    config = {'SK': '', 'CERT': '', 'TYPE': '', 'CACERT': '', 'CERT_REQS': ''}

    def init_config(self, **args):
        """Initialize the package configuration according to the configuration file. Usually, this function should be
           called before other function calls. It reads the configuration files according to the given keywords list
           and initialize the DTLS environment.
           The acceptable keywords are: config, SK, CERT, TYPE, CACERT, CERT_REQS.
           Specifically, the keyword "config" sets the configuration file of the class.
           If arguments are passed to this function, the specified configuration file will be updated.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            self.dtls_cnf = os.path.expanduser(args['config'])
        if not os.path.isfile(self.dtls_cnf):
            raise IOError('configuration file \"' + self.dtls_cnf + '\" doesn\'t exist or it is not a file.')
        self.config = self.utl.read_config(self.dtls_cnf, self.config)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.config.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.config[key] = args[key]
                update += 1
        if update > 0:
            self.utl.update_config(self.dtls_cnf, self.config)
        # Backup configuration file
        self.utl.call('cp -f ' + self.dtls_cnf + ' ' + self.config['TYPE'] + '.dtls.bck', shell=True)
        do_patch()

    def wrap_socket(self, sock):
        """This a wrapper function to wrap a socket for DTLS communication. The DTLS socket is created by using security
            configurations including certificate and private key, etc. The created DTLS socket can be used to send and
            receive DTLS packets for secure communication. This function does not support SSL socket.

        :param sock: socket.
        :type sock: int.
        """
        key_path = os.path.expanduser(self.config.get('SK', ''))
        cert_path = os.path.expanduser(self.config.get('CERT', ''))
        ca_cert_path = os.path.expanduser(self.config.get('CACERT', ''))
        cert_reqs = self.config.get('CERT_REQS', 'CERT_NONE')
        cert_opt = {'CERT_NONE': ssl.CERT_NONE, 'CERT_OPTIONAL': ssl.CERT_OPTIONAL, 'CERT_REQUIRED': ssl.CERT_REQUIRED}

        try:
            # check if required files exist.
            if not os.path.isfile(key_path):
                raise IOError('My private key \"' + key_path + '\" is not a file or invalid.')
            if not os.path.isfile(cert_path) and cert_opt[cert_reqs] == ssl.CERT_REQUIRED:
                raise IOError('My certificate \"' + cert_path + '\" is not a file or invalid.')
            if not os.path.isfile(ca_cert_path) and cert_opt[cert_reqs] == ssl.CERT_REQUIRED:
                raise IOError('CA\'s certificate \"' + ca_cert_path + '\" is not a file or invalid.')
            if cert_reqs not in cert_opt:
                raise ValueError(
                    'The value of keyword \"CERT-REQS\" is invalid. Please check the configuration file \"' +
                    self.dtls_cnf + '\"')

            # wrap a socket based on the device type, i.e "server" or "client"
            if str(self.config.get('TYPE', '')).lower() == 'server':
                self.dtls_sock = ssl.wrap_socket(sock, keyfile=key_path, certfile=cert_path,
                                                 cert_reqs=cert_opt[cert_reqs],
                                                 ca_certs=ca_cert_path, server_side=True,
                                                 do_handshake_on_connect=False, ciphers="ALL")
            elif str(self.config.get('TYPE', '')).lower() == 'client':
                self.dtls_sock = ssl.wrap_socket(sock, keyfile=key_path, certfile=cert_path,
                                                 cert_reqs=cert_opt[cert_reqs],
                                                 ca_certs=ca_cert_path, ciphers='IBIHOP-AES256-SHA')
            else:
                raise ValueError(
                    'The type of device is invalid, it should be either \"server\" or \"client\". Please check the '
                    'configuration file \"' + self.dtls_cnf + '\".')
        except Exception as e:
            print (e)

    def set_dtls_socket(self, sock):
        """This function sets a wrapped DTLS socket. It is usually used to handle a connection established from the
           "accept" function. Note that it is unnecessary to call init_config before this function.

        :param sock: a socket for DTLS connection.
        :type sock: int.
        """
        self.dtls_sock = sock

    def sendto(self, *args, **keywords):
        """This a wrapper function to send a message string via DTLS which uses UDP connection.
           It is used to send DTLS packets.
        """
        return self.dtls_sock.send(*args, **keywords)

    def recvfrom(self, *args, **keywords):
        """This a wrapper function to receive a message from a DTLS connection.
           It is used to receive DTLS packets.
        """
        return self.dtls_sock.recv(*args, **keywords)

    def accept(self, *args, **keywords):
        """This is a wrapper function to accept DTLS connections.
           It is used to accept a DTLS connection and return a socket to the client.
        """
        return self.dtls_sock.accept(*args, **keywords)

    def connect(self, *args, **keywords):
        """This is a wrapper function to connect server via DTLS connection.
           It is used to connect a DTLS server.
        """
        return self.dtls_sock.connect(*args, **keywords)

        # def connect(self, addr):

    # return self.dtls_sock.connect(addr)

    def listen(self, *args, **keywords):
        """This is a wrapper function to listen the DTLS connection request.
           It is used to listen the DTLS handshake request from client devices.
        """
        return self.dtls_sock.listen(*args, **keywords)

    def close(self, *args, **keywords):
        """This is a wrapper function to close DTLS socket.
           It closes a socket.
        """
        return self.dtls_sock.close(*args, **keywords)

    def shutdown(self, *args, **keywords):
        """This is a wrapper function to shutdown the DTLS socket.
           It shuts down a socket
        """
        return self.dtls_sock.shutdown(*args, **keywords)
