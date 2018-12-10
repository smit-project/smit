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


class Server(object):
    """
    This is a class to implement server functions s.t, obtain certificate from the CA and start server side for DTLS
    communication with DTLS clients.
    This class needs a configuration file 'servercnf' to configure certificate, network and other information.
    This class depends on the certificate management class CertManager.
    """
    utl = utils.Utils()
    cm = certmngr.CertManager()  # for certificate generation
    config = {'C': '', 'ST': '', 'L': '', 'O': '', 'OU': '', 'CN': '',
              'emailAddress': '', 'ECCPARAM': '', 'CAIP': '', 'CAPORT': '', 'CERT': '', 'CSR': '', 'MSG': '',
              'SIG': '', 'CACERT': '', 'SK': '', 'SERVERIP': '', 'SERVERPORT': '', 'CACHAIN': '', 'TYPE': '',
              'CERT_REQS': ''}  # configuration keywords
    server_cnf = 'servercnf'  # the path to configuration file for this client package
    package_path = ''  # the path to this package
    MAX_LEN = 1536  # the max length of packet which can be sent and received

    def __init__(self):
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        os.chdir(self.package_path)
        self.config = self.utl.read_config(self.server_cnf, self.config)
        self.cm.init_config(config=self.server_cnf)

    def init_config(self, **args):
        """This function initializes the configuration for the class object, where the parameters are read from a
        configuration file. This function should be called before other (class member) function call. The acceptable
        arguments are: config, C, ST, L, O, OU, CN, emailAddress, ECCPARAM, CAIP, CAPORT, CERT, CSR, MSG, SIG,
        CACERT, SK, SERVERIP, SERVERPORT, CACHAIN, TYPE, CERT_REQS. Specifically, the keyword "config" sets the path
        to configuration file. If arguments are passed to this function, the specified configuration file will be
        updated.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            self.server_cnf = os.path.expanduser(args['config'])
        if not os.path.isfile(self.server_cnf):
            raise IOError('configuration file \"' + self.server_cnf + '\" does not exist or it is not a file.')
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
        self.utl.call('cp -f ' + self.server_cnf + ' ' + self.config['CN'] + '.servercnf.bck', shell=True)

    def enroll(self):
        """This function request a certificate from the internal private CA.
           The function requires the input of three files: CSR, message and manufacturer's signature. Note that these
            files are configured in the configuration file.
        """
        csr_path = os.path.expanduser(self.config.get('CSR', ''))
        msg_path = os.path.expanduser(self.config.get('MSG', ''))
        sig_path = os.path.expanduser(self.config.get('SIG', ''))

        try:
            # Check if the required files are accessible
            if not os.path.isfile(csr_path):
                raise IOError('Path \"' + csr_path + '\" to the CSR file is invalid or it is not a file. Please check '
                              'the configuration file \"' + self.server_cnf + '\".')
            if not os.path.isfile(msg_path):
                raise IOError('Path \"' + msg_path + '\" to the message file is invalid or it is not a file. Please '
                              'check the configuration file \"' + self.server_cnf + '\".')
            if not os.path.isfile(sig_path):
                raise IOError('Path \"' + sig_path + '\" to the signature file is invalid or it is not a file. Please '
                              'check the configuration file \"' + self.server_cnf + '\".')

            # Generate socket and connect to CA through TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = self.config.get('CAIP', '127.0.0.1')
            port = int(self.config.get('CAPORT', 12345))
            sock.connect((host, port))
            print ('CA connected.')
            # Send three files to CA for certificate generation request.
            csr = self.utl.read_file(csr_path, 'r')
            msg = self.utl.read_file(msg_path, 'r')
            sig = self.utl.read_file(sig_path, 'r')
            buf = '#$c$#' + csr
            sock.settimeout(180)  # socket timeout after 180 seconds.
            data_len = sock.send(buf)
            print str(data_len) + ' bytes sent for CSR file.'
            ack = sock.recv(self.MAX_LEN)  # receive acknowledgement from CA.
            if ack != 'ok':
                raise RuntimeError('CA\'s acknowledgement for receiving CSR file is failedis failed.')
            buf = '#$m$#' + msg
            data_len = sock.send(buf)
            print str(data_len) + ' bytes sent for message file.'
            ack = sock.recv(self.MAX_LEN)
            if ack != 'ok':
                raise RuntimeError('CA\'s acknowledgement for receiving message file is failed.')
            buf = '#$s$#' + sig
            data_len = sock.send(buf)
            print str(data_len) + ' bytes sent for signature file.'
            ack = sock.recv(self.MAX_LEN)
            if ack != 'ok':
                raise RuntimeError('CA\'s acknowledgement for receiving signature file is failed.')

            data = ''  # received data
            ca_cert_ok = False  # indicate if CA certificate received.
            sv_cert_ok = False  # indicate if client certificate received.
            while True:
                data = data + sock.recv(self.MAX_LEN)
                if data == 'failed':  # Certificate reuqest failed.
                    print ('Certificate request rejected because provide files may not be valid.')
                    raise
                if data.count('#^#*') == 2 and data.find('#$t$#') != -1 and data.find('#$a$#') != -1:
                    # Wait the transmission complete then process data. If connection broken, this will timeout after
                    #  180 seconds. extract my certificate
                    begin = data.find('#$t$#') + len('#$t$#')
                    end = data.find('#^#*')
                    path = os.path.dirname(self.config['CERT'])
                    if path != '':
                        self.utl.makedir(path)
                    self.utl.write_file(data[begin:end], self.config['CERT'], 'w')
                    sv_cert_ok = True
                    data = data[end + len('#^#*'):]
                    print ('My certificate received and stored at: \"' + self.config['CERT'] + '\".')

                    # extract CA certificate
                    begin = data.find('#$a$#') + len('#$a$#')
                    end = data.rfind('#^#*')
                    path = os.path.dirname(self.config['CACERT'])
                    if path != '':
                        self.utl.makedir(path)
                    self.utl.write_file(data[begin:end], self.config['CACERT'], 'w')
                    ca_cert_ok = True
                    print ('CA certificate received and stored at: \"' + self.config['CACERT'] + '\".')
                if ca_cert_ok and sv_cert_ok:
                    break
            sock.close()
        except socket.timeout:
            print 'Request timeout.'
        except Exception as e:
            print (e)

    def start(self, install_all):
        """This function start a server which can interact with a DTLS client and transmit messages. This function
        checks whether the certificate and private key are valid, if not, it automatically request a new certificate
        from the CA. This function depends on DTLSWrap class and the related arguments are configured in the
        configuration file.
        """
        if install_all:
            print ('Installing dependencies.')
            self.utl.call('sudo apt-get -y --force-yes install python-pip', shell=True)
            self.utl.call('pip install Dtls', shell=True)
        print ('Start server.')
        print ('Checking certificate...')
        # Check certificate environment, if check failed, try to request (enroll) to the CA.
        try:
            ca_path = os.path.expanduser(self.config.get('CACERT', ''))
            chain_path = os.path.expanduser(self.config.get('CACHAIN', ''))
            if self.cm.verify_cert_key() and self.cm.verify_cert(chain_path, ca_path, ''):
                print ('Verification of local certificate succeeded.')
            else:
                return
        except Exception as e:
            print ('Certificate environment verification failed.')
            print ('================================================================================')
            print ('Trying to request a new certificate from CA based on the local CSR and private key.\n')
            print ('Note: if new certificate is still invalid, please make sure you have the '
                   'correct private key regarding the CSR file.')
            print ('================================================================================')
            print (e)
            # Generate CSR file according to the CSR information from the configuration file.
            # Generate private key if the file is missing. Note: the CSR information must be different from the
            # previous ones.
            try:
                sk_path = os.path.expanduser(self.config.get('SK', ''))
                if not os.path.isfile(sk_path):
                    self.cm.create_sk()
                self.cm.create_csr()
                print ('Connect to CA.')
                self.enroll()
                print ('================================================================================')
            except Exception as e:
                print (e)

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
            server.listen(0)
            print ('Listen DTLS handshake request ...')
            while True:
                acc = server.accept()
                if acc:
                    break
            print ('Client connected.')
            print ('=================================')
            client.set_dtls_socket(acc[0])

            # Interact with client.
            while True:
                print ('Awaiting message from client...')
                data = client.recvfrom(self.MAX_LEN)
                if data == 'q':
                    break
                print ('Message rcvd: ' + data)
                print ('=================================')
                c_in = raw_input('Enter a message (\'q\' for quite): ')
                sent = client.sendto(c_in)
                if sent == 0:
                    raise RuntimeError('Socket connection broken.')
                if c_in == 'q':
                    break
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            print ('DTLS connection closed.')
        except KeyboardInterrupt:
            server.shutdown(socket.SHUT_RDWR)
            server.close()
        except Exception as e:
            print (e)
