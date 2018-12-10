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
import subprocess

sys.path.insert(0, '..')
import smit.utils
from smit.security import certmngr
import inspect
import traceback


class DeployCA(object):
    """For private Certificate Authority (CA) configuration
    """
    package_path = ''
    utl = smit.utils.Utils()
    opensslcnf = ''  # path to openssl configuration
    cert_cnf = ''  # path to certificate configuration which will consumed by certificate management object.
    openssl_config = {'CAPATH': '', 'OPENSSL_PATH': ''}
    cert_config = {'WORKPATH': '', 'CAPATH': '', 'C': '', 'ST': '', 'L': '', 'O': '', 'OU': '', 'CN': '',
                   'emailAddress': '', 'SK': '', 'CSR': '', 'ECCPARAM': '', 'OCSPPORT': '',
                   'SELFSIGN': '', 'CERT': '', 'CERTDB': '', 'CERTS': '',
                   'MSG': '', 'SIG': '', 'SIGNER-CERT': '', 'CACHAIN': '', 'OCSP': '', 'MCERT': '',
                   'EXTENSIONS': '', 'OPENSSL_PATH': ''}

    def __init__(self):
        """Constructor initializes variables
        """
        self.opensslcnf = 'opensslcnf'
        self.cert_cnf = 'certcnf'

        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def init_config(self, **args):
        """Initialize the package configuration according to the configuration file. This function MUST be called
        before other function call. The acceptable keywords are: CAPATH, OPENSSL_PATH, WORKPATH, CAPATH, C, ST, L, O,
        OU, CN, emailAddress, SK, CSR, ECCPARAM, OCSPPORT, SELFSIGN, CERT, CERTDB, CERTS, MSG, SIG, CACHAIN, OCSP,
        MCERT, EXTENSIONS, OPENSSL_PATH. If arguments are passed to this function, the configuration files will be
        updated.

        :param args: dictionary of passed arguments.
        """
        if not os.path.isfile(os.path.expanduser(self.opensslcnf)):
            raise IOError('Configuration file \"' + self.opensslcnf + '\" does not exist or it is not a file.')
        if not os.path.isfile(os.path.expanduser(self.cert_cnf)):
            raise IOError('Configuration file \"' + self.cert_cnf + '\" does not exist or it is not a file.')

        self.openssl_config = self.utl.read_config(self.opensslcnf, self.openssl_config)
        self.cert_config = self.utl.read_config(self.cert_cnf, self.cert_config)
        package = args.get('package', '')

        # Update configuration files if arguments are given.
        update = 0
        for key, value in self.openssl_config.iteritems():
            if args.get(key) is not None and args[key] is not None:
                self.openssl_config[key] = args[key]
                update += 1
        if update > 0:
            self.utl.update_config(self.opensslcnf, self.openssl_config)
            update = 0
        for key, value in self.cert_config.iteritems():
            if args.get(key) is not None and args[key] is not None:
                self.cert_config[key] = args[key]
                update += 1
        if update > 0:
            if args.get('CAPATH'):  # CA path set
                if not args.get('CERTDB'):  # CERTDB path not specified, then use the default
                    self.cert_config['CERTDB'] = os.path.join(args['CAPATH'], 'index.txt')
                if not args.get('CERTS'):  # CERTS path not specified, then use the default
                    self.cert_config['CERTS'] = os.path.join(args['CAPATH'], 'newcerts')
            if args.get('WORKPATH'):  # set ordinary certificate and key path
                if not args.get('CERT'):  # CERT path not specified, then use the default
                    if self.cert_config['SELFSIGN'].lower() == 'y':  # set CA's certificate path
                        self.cert_config['CERT'] = os.path.join(args['WORKPATH'], 'cacert.pem')
                    else:  # other entity's certificate path
                        self.cert_config['CERT'] = os.path.join(args['WORKPATH'],
                                                                self.cert_config['CN'] + '.cert.pem')
                if not args.get('SK'):  # SK path not specified, then use the default
                    if self.cert_config['SELFSIGN'].lower() == 'y':  # set CA's certificate path
                        self.cert_config['SK'] = os.path.join(args['WORKPATH'], 'private', 'cakey.pem')
                    else:  # other entity's certificate path
                        self.cert_config['SK'] = os.path.join(args['WORKPATH'], 'private',
                                                              self.cert_config['CN'] + '.key.pem')
            self.utl.update_config(self.cert_cnf, self.cert_config)
        # Backup configuration files
        self.utl.call('cp -f ' + self.opensslcnf + ' ' + self.cert_config['CN'] + '.openssl.cnf.bck', shell=True)
        self.utl.call('cp -f ' + self.cert_cnf + ' ' + self.cert_config['CN'] + '.certcnf.bck', shell=True)
        # Update depend configuration files
        if package != '':
            os.chdir(self.package_path)
            os.chdir('../appca')
            dep_config = {}
            if package == 'p41' or package == 'p5':  # for private CA setup and/or run
                dep_config = {'CACERT': self.cert_config['CERT'], 'CACHAIN': self.cert_config['CERT'],
                              'OPENSSL_PATH': self.openssl_config['OPENSSL_PATH'], 'CERTDB': self.cert_config['CERTDB'],
                              'CERTS': self.cert_config['CERTS']}  # dependent configurations
            elif package == 'p42':  # for global CA setup and/or run
                dep_config = {'CACERT': self.cert_config['CERT'], 'CERTDB': self.cert_config['CERTDB']}
                self.utl.update_config('ocspcnf', dep_config)
                dep_config = {'SIGCHAIN': self.cert_config['CERT']}
            elif package == 'p43':  # for OCSP server setup and/or run
                dep_config = {'OCSPSK': self.cert_config['SK'], 'OCSPCERT': self.cert_config['CERT']}
                self.utl.update_config('ocspcnf', dep_config)
                dep_config = {}
            elif package == 'p44':  # for private key and CSR generation.
                dep_config = {'SIGCERT': self.cert_config['CERT']}
            self.utl.update_config('appcacnf', dep_config)
            os.chdir(self.package_path)

    def setup(self, install_all):
        """Configure a private Certificate Authority (CA).
           This function creates a new CA certificate and set directories for the CA.
        """
        c_in = ''
        if not install_all:
            c_in = raw_input("Do you want to install OpenSSL? [Y/N] (skip if installed): ")
        if install_all or c_in == 'Y' or c_in == 'y':
            self.utl.call('sudo apt-get -y --force-yes install openssl', shell=True)

        print('Create CA directory')
        try:
            ca_path = os.path.expanduser(self.openssl_config['CAPATH'])
            if os.path.exists(ca_path):
                raise IOError(
                    'Error: CA directory \"' + ca_path + '\" already exists. Please remove it or choose another name.')
            self.utl.check_call('sudo mkdir -p ' + ca_path, shell=True)
        except subprocess.CalledProcessError:
            print('Error: cannot create CA directory.')
            print "".join(traceback.print_exc(file=sys.stdout))
        except IOError as ioe:
            print ioe
            print "".join(traceback.print_exc(file=sys.stdout))
        os.chdir(ca_path)
        self.utl.makedir(self.cert_config['CERTS'])
        self.utl.makedir(os.path.dirname(self.cert_config['SK']))
        self.utl.call('sudo echo \'01\' > serial  && touch index.txt', shell=True)

        # Configure CA
        print('Configure CA')
        os.chdir(self.package_path)
        fp = open(self.opensslcnf, 'r')
        lines = fp.readlines()
        fp.close()
        begin = -1
        end = -1
        flag = 0
        # Read configuration to set CA directory
        for line in lines:
            if begin == -1 and line.find('Begin SMIT Config') != -1:
                begin = lines.index(line)
            elif end == -1 and line.find('End SMIT Config') != -1:
                end = lines.index(line)
            elif line.find('$CAPATH') > -1:
                lines[lines.index(line)] = line.replace('$CAPATH', ca_path)
                flag = 1
            if begin != -1 and end != -1 and flag == 1:
                break

        if end > begin >= 0:
            i = 0
            while i < end - begin + 1:
                lines.pop(begin)
                i += 1

        # Output openssl configuration to the specified path.
        try:
            fp = open(os.path.expanduser(self.openssl_config['OPENSSL_PATH']), 'w')
            for line in lines:
                fp.write(line)
            fp.close()

            # Create CA certificate to setup the CA. The output files, i.e certificate and private key are placed in the
            # path specified by keywords CERT and SK in the configuration file.
            cm = certmngr.CertManager()
            # Read certificate environment configuration file
            cm.init_config(config=self.cert_cnf)
            # Create CA certificate and setup environment.
            cm.create_cert()
            print ('CA certificate and private key generated successfully.')
            print ('CA configuration complete.')
        except Exception as e:
            print (e)

    def ocsp_setup(self):
        """This function setup an OCSP server.
           Note: This function can be used when the OCSP server and CA are on the same host.
        """
        try:
            self.create_cert()
            print ('OCSP server certificate generation succeed.')
        except Exception as e:
            print (e)

    def create_cert(self):
        """This is a wrapper of the functions from the CertManagment class.
        """
        try:
            # Check if work path exists, if it does, raise error and exit.
            if os.path.exists(os.path.expanduser(self.cert_config['WORKPATH'])):
                print ('Error: directory \"' + self.cert_config['WORKPATH'] + '\" already exists. ' +
                       'Please remove the directory or change to another one.')
                raise
            cm = certmngr.CertManager()
            # Read certificate environment configuration file
            cm.init_config(config=self.cert_cnf)
            # Create certificate and setup environment.
            cm.create_sk()
            cm.create_csr()
            cm.create_cert()
        except Exception as e:
            print (e)
