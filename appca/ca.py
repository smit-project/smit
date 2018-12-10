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
import traceback
import random
import string
from multiprocessing import Process


class CA(object):
    """This class implement CA functions which start CA and handle certificate generation requests.
       The parameters used by this class is assigned in the configuration file "appcacnf".
       The configuration file allows to set the network information, local certificate information and etc.
       Such information is used to perform request verification and generate certificates.
       This class depends on the certificate management module which indeed generates certificate.
    """
    utl = utils.Utils()
    config = {'IP': '', 'PORT': '', 'CERT': 'tmpcert.pem', 'CSR': 'tmpcsr.csr', 'MSG': 'tmpmsg', 'SIG': 'tmpsig',
              'CACERT': '', 'CACHAIN': '', 'OCSP': '', 'OCSPPORT': '', 'SIGCERT': '', 'SIGCHAIN': '', 'OCSPCERT': '',
              'OCSPSK': '', 'SELFSIGN': '', 'OPENSSL_PATH': ''}  # configuration keywords
    app_cnf = 'appcacnf'  # the path to configuration file for this package
    package_path = ''  # the path to this pakcage
    MAX_LEN = 1536  # the max length of packet which can be sent and received

    def __init__(self):
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        os.chdir(self.package_path)
        self.config = self.utl.read_config(self.app_cnf, self.config)

    def init_config(self, **args):
        """Initialize the package configuration according to the configuration file.
           This function MUST be called before other function call.
           The acceptable keywords are: config, IP, PORT, CERT, CSR, MSG, SIG, CACERT, CACHAIN, OCSP, OCSPPORT,
           SIGCERT, SIGCHAIN, OCSPCERT, OCSPSK, SELFSIGN, OPENSSL_PATH.
           Specifically, "config" is to set the path to configuration file.
           If arguments are passed to this function, the specified configuration file will be updated.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            self.certcnf = os.path.expanduser(args['config'])
        if not os.path.isfile(self.certcnf):
            raise IOError('configuration file \"' + self.certcnf + '\" doesn\'t exist or it is not a file.')
        self.config = self.utl.read_config(self.certcnf, self.config)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.config.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.config[key] = args[key]
                update += 1
        if args['OCSPPORT'] is not None and args.get('OCSPPORT', '') != '':  # change ocsp server url
            url = self.config['OCSP']
            url = url[:str(url).rfind(':') + 1]  # get IP address
            self.config['OCSP'] = url + args['OCSPPORT']
        if update > 0:
            self.utl.update_config(self.app_cnf, self.config)

    def write_file(self, data, filename):
        """This function write a file in 'w' mode.

        :param data: content to write in the file.
        :param filename: path to te output file.
        :type data: str.
        :type filename: str.
        """
        f = open(filename, 'w')
        f.write(data)
        f.close()

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
        sock.settimeout(180)  # request timeout after 180 seconds to close the thread.
        print ('===== New connection from: ' + addr[0])
        try:
            # Create a directory to contain temporary files (e.g., certificate and received files)
            # generated during the interaction.
            path = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            cm = certmngr.CertManager()
            cm.init_config(config=self.app_cnf)
            self.utl.makedir('tmp/' + path)
            os.chdir('tmp/' + path)  # change the current working directory

            # The While loop processes enroll request according to the designed message follow.
            # The specified indicators like 'c' and 'm' may be changed in later version. It is currently for the test
            # and simplicity.
            while True:
                data = sock.recv(self.MAX_LEN)
                if data.startswith('#$c$#'):  # it is a CSR string and then write it to a file.
                    self.write_file(data[len('#$c$#'):], self.config['CSR'])
                    print ('CSR file received.')
                    sock.send('ok')  # send acknowledgement to the applicant
                if data.startswith('#$m$#'):  # it is a message string and then write it to a file.
                    self.write_file(data[len('#$m$#'):], self.config['MSG'])
                    print ('Message file received.')
                    sock.send('ok')
                if data.startswith('#$s$#'):  # it is a signature file then check if it is valid.
                    self.write_file(data[len('#$s$#'):], self.config['SIG'])
                    print ('Signature file received.')
                    sock.send('ok')
                    if not cm.verify_sig():  # signature verification failed and send result to applicant.
                        sock.send('failed')
                        print ('Certificate request rejected: manufacturer\'s signature verification failed.')
                        break
                    else:  # signature verified so that generate certificate.
                        print('Manufacturer\'s signature verified.')
                        if not cm.verify_cert(self.config.get('SIGCHAIN', ''), self.config.get('SIGCERT', ''),
                                              self.config.get('OCSP', '')):
                            return
                        cm.create_cert()
                        cert_path = cm.find_cert()  # path to the generated certificate.
                        cert = self.utl.read_file(cert_path, 'r')
                        cert = '#$t$#' + cert + '#^#*'
                        sock.send(cert)  # send client certificate.
                        print ('Client certificate delivered.')
                        ca_path = os.path.expanduser(self.config.get('CACERT', ''))  # path to CA certificate
                        if not os.path.isfile(ca_path):
                            raise IOError('Path \"' + ca_path + '\" to the CA certificate is invalid or it is not a '
                                          'file. Please check the configuration file \"' +
                                          self.app_cnf + '\".')
                        cert = self.utl.read_file(ca_path, 'r')
                        cert = '#$a$#' + cert + '#^#*'
                        sock.send(cert)  # send CA certificate.
                        print ('CA certificate delivered.')
                        break
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception as e:
            print (e)
        finally:
            # delete temporary directory to clean up session.
            print ('Clean up...')
            self.utl.call('rm -rf ../' + path, shell=True)
            print ('Session completed.')

    def start(self):
        """This function starts the CA to process certificate generation requests.
           This function support multi-thread processing so that requests can be handle in parallel.
        """
        try:
            # create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = self.config.get('IP', '127.0.0.1')
            port = int(self.config.get('PORT', 12345))
            sock.bind((host, port))

            # listen requests
            sock.listen(5)
            print ('CA started and awaiting request ...')
            while True:
                cnsock, addr = sock.accept()
                # create a new thread to handle the accepted connection.
                p = Process(target=self.connection_handler, args=(cnsock, addr,))
                p.start()
        except KeyboardInterrupt:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception as e:
            print (e)
