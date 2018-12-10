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

import os
import sys
import socket
import inspect

sys.path.insert(0, '../../')
sys.path.insert(0, '../../../')
from smit.security import certmngr
from smit import utils
from smit.security import DTLSWrap
import traceback
import time
from datetime import datetime
from multiprocessing import Process
import logging
import random

TIMEOUT = 30  # timeout for scoket connection


class Sink(object):
    """
    This is a class to implement server functions s.t, accept DTLS client to receive messages.
    This class needs a configuration file 'server_expcnf' to configure certificate, network and experiment parameters.
    This class depends on the certificate management class CertManager.
    """
    utl = utils.Utils()
    cm = certmngr.CertManager()  # for certificate generation
    config = {'CERT': '', 'CACERT': '', 'SK': '', 'SERVERIP': '', 'SERVERPORT': '', 'CACHAIN': '',
              'TYPE': '', 'CERT_REQS': 'CERT_REQUIRED'}  # configuration keywords
    server_cnf = 'sink_expcnf'  # the path to configuration file for this client package
    package_path = ''  # the path to this package
    MAX_LEN = 1536  # the max length of packet which can be sent and received

    def __init__(self):
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        os.chdir(self.package_path)
        self.config = self.utl.read_config(self.server_cnf, self.config)
        self.cm.init_config(config=self.server_cnf)

    def init_config(self, **args):
        """This function initializes the configuration for the class object, where the parameters are read from a
               configuration file. This function should be called before other (class member) function call.
               The acceptable arguments are: config, CACERT, SK, SERVERIP, SERVERPORT, CACHAIN, TYPE, CERT_REQS.
               Specifically, the keyword "config" sets the path to configuration file.
               If arguments are passed to this function, the specified configuration file will be updated.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            self.server_cnf = os.path.expanduser(args['config'])
        if not os.path.isfile(self.server_cnf):
            raise IOError('configuration file \"' + self.server_cnf + '\" doesn\'t exist or it is not a file.')
        self.config = self.utl.read_config(self.server_cnf, self.config)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.config.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.config[key] = args[key]
                update += 1
        if update > 0:
            self.utl.update_config(self.server_cnf, self.config)
        # Backup configuration file
        self.utl.call('cp -f ' + self.server_cnf + ' ' + self.server_cnf + '.bck', shell=True)

    def connection_handler(self, sock, addr):
        """This is a connection handler for subthread. It process a new connection for certificate request.
           This function takes a client socket for DTLS packets transmission and the parameter addr is used to show
           the client IP address.
           This function will be called in individual thread to process a specific client's connection.

        :param sock: client socket.
        :param addr: client IP address
        :type sock: int.
        :type addr: tuple.
        """
        print ('New connection from: ' + addr[0] + ', ' + str(addr[1]))
        try:
            # Create a directory to contain log files generated during the interaction.
            dt = time.strftime('%d-%m-%Y-%H-%M-%S')  # get the date and current time of connection.
            path = addr[0]  # create direct name for this connection's log files.
            self.utl.makedir('exp/' + path)
            os.chdir('exp/' + path)  # change the current working directory
            log_name = addr[0] + '--' + dt
            logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s\t%(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            while True:
                data = sock.recvfrom(self.MAX_LEN)
                timestamp = datetime.now().strftime('%H%M%S%f')[:-3]
                # Calculate length of message other than the sequence number and timestamp.
                # The length of sequence number is fixed 8 bytes.
                other_len = len(data) - 8 - len(timestamp)
                # Log client connection information including client (IP, port) and the port assigned to client on sink.
                conn_info = 'client|' + str(addr[0]) + '.' + str(addr[1]) + '|sink|' + str(
                    self.config['SERVERIP']) + '.' + str(self.config['SERVERPORT'])
                record = data[0:8] + '\t' + data[8:8 + other_len] + '\t' + data[8 + other_len:] + '\t' + timestamp + \
                         '\t' + conn_info
                logging.info(record)
        except socket.timeout:
            print ('Time out.')
        except KeyboardInterrupt:
            print ('DTLS connection closed.')
        except Exception as e:
            print ('Unknown errors.')
            print (e)
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def start(self):
        """This function start a server which can interact with a DTLS client and receive messages.
           This function depends on DTLSWrap class and the related arguments are configured in the configuration file.
        """
        print ('Start server.')
        print ('Checking certificate...')
        # Check certificate environment
        try:
            ca_path = os.path.expanduser(self.config.get('CACERT', ''))
            chain_path = os.path.expanduser(self.config.get('CACHAIN', ''))
            if self.cm.verify_cert_key() and self.cm.verify_cert(chain_path, ca_path, ''):
                print ('Verification of local certificate succeeded.')
            else:
                return
        except Exception as e:
            print (e)
            return
        try:
            # Create socket for DTLS handshake.
            server = DTLSWrap.DtlsWrap()
            client = DTLSWrap.DtlsWrap()
            print ('Read DTLS configuration.')
            server.init_config(config=self.server_cnf)
            print ('Create DTLS socket.')
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            host = self.config.get('SERVERIP', '::1')
            port = self.config.get('SERVERPORT', 12345)
            sock.bind((host, int(port)))
            server.wrap_socket(sock)

            # Listen connection request.
            server.listen(5)
            print ('Listen DTLS handshake request ...')
            while True:
                acc = server.accept()
                if acc:
                    print ('=================================')
                    print ('Client connected.')
                    client.set_dtls_socket(
                        acc[0])  # acc[0] is SSLSocket object, acc[1] is a tuple (host, port, long, long)
                    p = Process(target=self.connection_handler, args=(client, acc[1],))
                    p.start()
        except KeyboardInterrupt:
            server.shutdown(socket.SHUT_RDWR)
            server.close()
        except Exception as e:
            print (e)


class SinkPlain(object):
    """
    This is a class to implement server functions s.t, accpet client UDP connections to receive plaintext.
    This class needs a configuration file 'sink_expcnf' to configure certificate, network and experiment parameters.
    """
    utl = utils.Utils()
    config = {'SERVERIP': '', 'SERVERPORT': ''}  # configuration keywords
    server_cnf = 'sink_expcnf'  # the path to configuration file for this client package
    package_path = ''  # the path to this pakcage
    MAX_LEN = 1536  # the max length of packet which can be sent and received

    def __init__(self):
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        os.chdir(self.package_path)
        self.config = self.utl.read_config(self.server_cnf, self.config)
        print ('This is a sink server without DTLS.')

    def init_config(self, **args):
        """This function initializes the configuration for the class object, where the parameters are read from a
               configuration file. This function should be called before other (class member) function call.
               The acceptable arguments are: config, SERVERIP, SERVERPORT.
               Specifically, the keyword "config" sets the path to configuration file.
               If arguments are passed to this function, the specified configuration file will be updated.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            self.server_cnf = os.path.expanduser(args['config'])
        if not os.path.isfile(self.server_cnf):
            raise IOError('configuration file \"' + self.server_cnf + '\" doesn\'t exist or it is not a file.')
        self.config = self.utl.read_config(self.server_cnf, self.config)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.config.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.config[key] = args[key]
                update += 1
        if update > 0:
            self.utl.update_config(self.server_cnf, self.config)
        # Backup configuration file
        self.utl.call('cp -f ' + self.server_cnf + ' ' + self.server_cnf + '..bck', shell=True)

    def connection_handler(self, addr):
        """This is a connection handler for subthread. It process a new connection for certificate request.
           This function will assign a new port to a UDP connection. That is each connection will be bind to a new port.
           This function will be called in individual thread to process a specific client's connection.

        :param addr: client IP address
        :type addr: tuple.
        """
        # sock.settimeout(TIMEOUT)    # request timeout after 180 seconds to close the thread.
        rpl_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        port = random.randint(10000, 20000)
        print "bind port: %s" % str(port)
        rpl_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        rpl_sock.bind((self.config['SERVERIP'], port))
        print 'Binding ' + str((self.config['SERVERIP'], port))
        # Log client connection information including client (IP, port) and the port assigned to client on sink.
        conn_info = 'client|' + str(addr[0]) + '.' + str(addr[1]) + '|sink|' + str(self.config['SERVERIP']) + '.' + str(
            port)
        rpl_sock.sendto('ack', addr)
        print ('New connection from: ' + addr[0] + ', ' + str(addr[1]))
        try:
            # Create a directory to contain log files generated during the interaction.
            dt = time.strftime('%d-%m-%Y-%H-%M-%S')  # get the date and current time of connection.
            path = addr[0]  # create direct name for this connection's log files.
            self.utl.makedir('exp/' + path)
            os.chdir('exp/' + path)  # change the current working directory
            log_name = addr[0] + '--' + dt
            logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s\t%(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            while True:
                data, addr = rpl_sock.recvfrom(self.MAX_LEN)
                timestamp = datetime.now().strftime('%H%M%S%f')[:-3]
                # Calculate length of message other than the sequence number and timestamp.
                # The length of sequence number is fixed 8 bytes.
                other_len = len(data) - 8 - len(timestamp)
                # Log client connection information including client (IP, port) and the port assigned to client on sink.
                conn_info = 'client|' + str(addr[0]) + '.' + str(addr[1]) + '|sink|' + str(
                    self.config['SERVERIP']) + '.' + str(port)
                record = data[0:8] + '\t' + data[8:8 + other_len] + '\t' + data[8 + other_len:] + '\t' + timestamp + \
                         '\t' + conn_info
                logging.info(record)
        except socket.timeout:
            print ('Time out.')
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print ('Unknown errors.')
            print (e)
        finally:
            rpl_sock.shutdown(socket.SHUT_RDWR)
            rpl_sock.close()

    def start(self):
        """This function start a server which can accept a DTLS client and receive messages.
        """
        print ('Start server.')
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            host = self.config.get('SERVERIP', '::1')
            port = self.config.get('SERVERPORT', 12345)
            sock.bind((host, int(port)))

            # Listen connection request.
            while True:
                data, addr = sock.recvfrom(1024)
                print ('=================================')
                print ('Client connected.')
                p = Process(target=self.connection_handler, args=(addr,))
                p.start()
        except KeyboardInterrupt:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception as e:
            print (e)


sink = Sink()
# sink = SinkPlain()
sink.start()
