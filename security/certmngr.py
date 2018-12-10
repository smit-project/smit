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

import subprocess
import os
import filecmp
import sys

sys.path.insert(0, '..')
sys.path.insert(0, '../../')
import smit.utils


class CertManager(object):
    """This class provides functions to facilitate certificate generation and signature verification, etc.
       Most arguments used in the class are specified in the configuration file "certcnf".
    """
    utl = smit.utils.Utils()
    cert_cnf = 'certcnf'  # path to certificate configuration file
    # keywords supported in the configuration
    config = {'WORKPATH': '', 'C': '', 'ST': '', 'L': '', 'O': '', 'OU': '', 'CN': '',
              'emailAddress': '', 'SK': '', 'CSR': '', 'ECCPARAM': '',
              'SELFSIGN': '', 'CERT': '', 'CERTDB': '', 'CERTS': '',
              'MSG': '', 'SIG': '', 'SIGCERT': '', 'CACHAIN': '', 'OCSP': '', 'MCERT': '',
              'EXTENSIONS': '', 'OPENSSL_PATH': ''}

    def init_config(self, **args):
        """Initialize the package configuration according to the configuration file.
           This function MUST be called before other function call.
           The acceptable keywords are: config, WORKPATH, C, ST, L, O, OU, CN, emailAddress, SK, CSR, ECCPARAM,
           SELFSIGN, CERT, CERTDB, CERTS, MSG, SIG, SIGCERT, CACHAIN, OCSP, MCERT, EXTENSIONS, OPENSSL_PATH.
           Specifically, "config" is to set the path to configuration file.
           If arguments are passed to this function, the specified configuration file will be updated.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            self.cert_cnf = os.path.expanduser(args['config'])
        if not os.path.isfile(self.cert_cnf):
            raise IOError('configuration file \"' + self.cert_cnf + '\" doesn\'t exist or it is not a file.')
        self.config = self.utl.read_config(self.cert_cnf, self.config)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.config.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.config[key] = args[key]
                update += 1
        if args.get('CAPATH'):  # CA path set
            update += 1
            if not args.get('CERTDB'):  # CERTDB path not specified, then use the default
                self.config['CERTDB'] = os.path.join(args['CAPATH'], 'index.txt')
            if not args.get('CERTS'):  # CERTS path not specified, then use the default
                self.config['CERTS'] = os.path.join(args['CAPATH'], 'newcerts')
        if args.get('WORKPATH'):  # set ordinary certificate and key path
            update += 1
            if not args.get('CERT'):  # CERT path not specified, then use the default
                if self.config['SELFSIGN'].lower() == 'y':  # set CA's certificate path
                    self.config['CERT'] = os.path.join(args['WORKPATH'], 'cacert.pem')
                else:  # other entity's certificate path
                    self.config['CERT'] = os.path.join(args['WORKPATH'], self.config['CN'] + '.cert.pem')
            if not args.get('SK'):  # SK path not specified, then use the default
                if self.config['SELFSIGN'].lower() == 'y':  # set CA's certificate path
                    self.config['SK'] = os.path.join(args['WORKPATH'], 'private', 'cakey.pem')
                else:  # other entity's certificate path
                    self.config['SK'] = os.path.join(args['WORKPATH'], 'private', self.config['CN'] + '.key.pem')
            if not args.get('CSR'):  # CSR path not specified, then use the default.
                self.config['CSR'] = os.path.join(args['WORKPATH'], self.config['CN'] + '.csr')
            if not args.get('MSG'):  # MSG path not specified, then use the default.
                self.config['MSG'] = os.path.join(args['WORKPATH'], 'msg')
            if not args.get('SIG'):  # MSG path not specified, then use the default.
                self.config['SIG'] = os.path.join(args['WORKPATH'], 'sig')
        if update > 0:
            self.utl.update_config(self.cert_cnf, self.config)
        # Backup configuration file
        self.utl.call('cp -f ' + self.cert_cnf + ' ' + self.config['CN'] + '.certcnf.bck', shell=True)

    def create_csr(self):
        """Create certificate signing request (CSR) file based on the information of configuration file.
           To specify the subject of certificate, it is needed to modify the configuration file.
           This function will output the CSR file to the path specified in the configuration file with keywords "CSR".
        """
        key_path = os.path.expanduser(self.config.get('SK', ''))
        csr_path = os.path.expanduser(self.config.get('CSR', ''))

        # Check if the output path and private key path are empty.
        if csr_path == '':
            raise IOError('Certificate Signing Request (CSR) file path is empty. Please check the configuration file \"'
                          + self.cert_cnf + '\".')
        if key_path == '':
            raise Exception('No private key file specified in the configuration file \"' + self.cert_cnf + '\".')
        # No private such file for private key, then create a new private key and output to the path "key_path".
        elif not os.path.exists(key_path):
            self.create_sk()

        # Generate a CSR file and output to the path specified.
        path = os.path.dirname(csr_path)
        if path != '':
            self.utl.makedir(path)
        cmd = 'openssl req -new -key ' + key_path + ' -out ' + csr_path + ' -subj "' + \
              '/C=' + self.config.get('C', '') + '/ST=' + self.config.get('ST', '') + '/L=' + \
              self.config.get('L', '') + '/O=' + self.config.get('O', '') + '/OU=' + \
              self.config.get('OU', '') + '/CN=' + self.config.get('CN', '') + '/emailAddress=' + \
              self.config.get('emailAddress', '') + '"'
        try:
            self.utl.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            raise IOError('Can\'t create CSR file \"' + csr_path +
                          '\". Please check the configuraiton and permissions.')

    def create_sk(self):
        """This function creates an ECC based private key file.
           The ECC parameter can be modified in the configuration file, while it must be supported by openssl.
        """
        key_path = os.path.expanduser(self.config.get('SK', ''))
        try:
            # Check if the path to private key and ECC parameter are empty.
            if key_path == '':
                raise Exception(
                    'Error: private key path is empty. Please check the configuration file \"' + self.cert_cnf + '\".')
            elif self.config.get('ECCPARAM', '') == '':
                raise Exception(
                    'Error: ECC parameter is empty. Please check the configuration file \"' + self.cert_cnf + '\".')

            # Generate private key and output to the specified path.
            path = os.path.dirname(key_path)
            if path != '':
                self.utl.makedir(path)
            self.utl.check_call('openssl ecparam -name ' + self.config['ECCPARAM'] + ' -genkey -noout -out ' + key_path,
                                shell=True)
        except subprocess.CalledProcessError:
            raise IOError('Can\'t output private key to \"' + key_path + '\". Please check the configuraion for ECC '
                          'parameter and private key path.')
        except Exception as e:
            print (e)
            raise

    def create_cert(self):
        """Create a certificate from a configuration file, which should contains the inforamtion of CSR, private key
        and paths fo files.
        """
        key_path = os.path.expanduser(self.config.get('SK', ''))
        csr_path = os.path.expanduser(self.config.get('CSR', ''))
        cert_path = os.path.expanduser(self.config.get('CERT', ''))
        extensions = self.config.get('EXTENSIONS', '').strip()
        openssl_cnf = self.config.get('OPENSSL_PATH', '')
        try:
            # Check if paths are valid.
            if csr_path == '':
                raise Exception(
                    'Certificate Signing Request (CSR) file path is empty. Please check the configuraiton file \"' +
                    self.cert_cnf + '\".')
            elif (str(self.config.get('SELFSIGN', '')).lower() != 'y' and str(
                    self.config.get('SELFSIGN', '')).lower() != 'n'):
                raise Exception(
                    '\'SELFSIGN\' keyword is not properly specified in configuration file \"' + self.cert_cnf + '\".')
            elif cert_path == '':
                raise Exception(
                    'Output certificate path must be specified. Please check the configuration file \"' +
                    self.cert_cnf + '\".')

            # Create parent path to certificate
            path = os.path.dirname(cert_path)
            if path != '':
                self.utl.makedir(path)

            if (str(self.config[
                        'SELFSIGN']).lower() == 'y'):  # create self-signed certificate, usually the root CA certificate
                if key_path == '':
                    raise Exception(
                        'Private key path is empty. Please check the configuration file \"' + self.cert_cnf + '\".')
                if not os.path.exists(key_path):
                    self.create_sk()
                self.create_csr()
                self.utl.check_call(
                    'openssl req -x509 -sha256 -days 3650 -key ' + key_path + ' -in ' + csr_path + ' -out ' +
                    cert_path + ' -config ' + openssl_cnf,
                    shell=True)
            elif str(self.config['SELFSIGN']).lower() == 'n':  # create certificate signed by CA.
                cert = self.find_cert()
                if cert != '':
                    self.utl.call('cp -f ' + cert + ' ' + cert_path, shell=True)
                else:
                    if extensions == '':
                        self.utl.check_call(
                            'openssl ca -batch -in ' + csr_path + ' -out ' + cert_path + ' -config ' + openssl_cnf,
                            shell=True)
                    else:
                        self.utl.check_call(
                            'openssl ca -batch -in ' + csr_path + ' -out ' + cert_path + ' -config ' + openssl_cnf +
                            ' -extensions ' + extensions,
                            shell=True)
            else:
                print (
                    'Error: configuration for keyword \"SELFSIGN\" is empty or invalid, please check the configuration '
                    'file \"' + self.cert_cnf + '\".')
        except subprocess.CalledProcessError:
            print ('CalledProcessError: can\'t output certificate to \"' + cert_path +
                   '\". Please check the configuration and permissions.')
            raise
        except:
            raise

    def verify_cert_key(self):
        """This function checks the validity of a pair of certificate (CERT) and private key (SK). CERT and SK
        settings can be specified in the configuration file. It raises an error message if the verification failed,
        that is the private key is not for the subject specified in the certificate.

        Return:

            True -- valid pair of certificate and private key.
            Error -- otherwise.
        """
        key_path = os.path.expanduser(self.config.get('SK', ''))
        cert_path = os.path.expanduser(self.config.get('CERT', ''))
        try:
            # Check if the certificate and private key are files
            if not os.path.isfile(cert_path):
                raise Exception('Error: certificate \"' + cert_path + '\" is not a file.')
            if not os.path.isfile(key_path):
                raise Exception('Error: private key \"' + key_path + '\" is not a file.')

            # Extract public key from the private key.
            self.utl.check_call('openssl pkey -in ' + key_path + ' -out tmpk1.pem -pubout', shell=True)
            # Extract public key from the certificate.
            self.utl.check_call('openssl x509 -pubkey -noout -in ' + cert_path + ' > tmpk2.pem', shell=True)
            # Compare if two public key are identical.
            rs = filecmp.cmp('tmpk1.pem', 'tmpk2.pem')
            self.utl.call('rm tmpk1.pem tmpk2.pem', shell=True)
            if rs:
                print ('Certificate and private key pair is valid.')
                return True
            else:
                raise Exception('Certificate and private key pair is invalid.')
        except subprocess.CalledProcessError as cpe:
            if str(cpe.cmd).find('tmpk1.pem') != -1:
                print (
                    'Error: public key extraction failed from private key \"' + key_path +
                    '\". The file may not be valid.')
            if str(cpe.cmd).find('tmpk2.pem') != -1:
                print (
                    'Error: public key extraction failed from certificate \"' + cert_path +
                    '\". The file may not be valid.')
            raise
        except Exception as e:
            print (e)
            raise

    def find_cert(self):
        """This function find a certificate based on the subject information contained in CSR file.
           The function is usually called by CA, otherwise it does not mean too much.
           This function depends on the value of keywords "CSR", "CERTDB" and "CERTS".
           It checks CA's certificate database and returns the certificate path if found.

        Return:

            str. -- path of certificate on CA's certificate database.
            '' -- No certificate found.
            error -- raise an error if certificate is not found.
        """
        cert = ''
        csr_path = os.path.expanduser(self.config.get('CSR', ''))  # path to the CSR fill which will be used
        db_path = os.path.expanduser(self.config.get('CERTDB', ''))  # path to certificate database on CA
        certs_path = os.path.expanduser(self.config.get('CERTS', ''))  # path to stored certificates on CA
        try:
            # Check if CSR, CERTDB and CERTS specify to valid path.
            if not os.path.isfile(csr_path):
                raise Exception(
                    'Error: find certificate failed. Certificate Signing Request (CSR) \"' + csr_path +
                    '\" is not a file.')
            if not os.path.isfile(db_path):
                raise Exception(
                    'Error: find certificate failed. certificate database \"' + db_path + '\" is not a file.')
            if not os.path.isdir(certs_path):
                raise Exception(
                    'Error: find certificate failed. Path \"' + certs_path + '\" of certificates storage is not a '
                    'directory.')

                # Extract subject information and look up in the certificate database.
            p = subprocess.Popen('openssl req -in ' + csr_path + ' -noout -subject', stdout=subprocess.PIPE, shell=True)
            (out, err) = p.communicate()
            out = out[str(out).find('=') + 1:].strip()
            rs = self.utl.lookup(out, db_path)
            words = rs.split()
            if words is not None and len(words) > 2:  # certificate found in database
                cert = os.path.join(certs_path, words[2] + '.pem')
                if not os.path.isfile(os.path.expanduser(cert)):  # certificate not found in repository
                    raise Exception(
                        'Error: find certificate failed. The certificate was generated but it cannot be found in the '
                        'certificate storage directory \"' + certs_path + '\".')
            return cert
        except subprocess.CalledProcessError:
            print ('Error: can\'t extract subject information from CSR \"' + csr_path + '\". Please check the validity '
                   'of CSR file.')
        except Exception as e:
            print (e)

    def gen_sig(self):
        """This function generates a signature on a given message file by using the private key specified in
           the configuration.
           The dependent configuration keywords of this function are "MSG", "SK" and "SIG".
           If succeed, it outputs a signature file to the specified path, i.e "SIG",
           otherwise it may raises an error.
        """
        msg_path = os.path.expanduser(self.config.get('MSG', ''))  # path to the message file
        sig_path = os.path.expanduser(self.config.get('SIG', ''))  # path to the signature file
        key_path = os.path.expanduser(self.config.get('SK', ''))  # path to the private key file
        try:
            # Check if paths to MSG, SIG and SK files are valid.
            if msg_path == '':
                raise Exception(
                    'Error: path of message file is empty. Please check the configuration file \"' + self.cert_cnf +
                    '\".')
            if sig_path == '':
                raise Exception(
                    'Error: path of signature file is empty. Please check the configuration file \"' + self.cert_cnf +
                    '\".')
            if not os.path.isfile(key_path):
                raise Exception('Error: private key \"' + key_path + '\" is not a file.')
            # Generate a signature and output it to SIG
            self.utl.check_call('openssl dgst -sha256 -sign ' + key_path + ' -out ' + sig_path + ' ' + msg_path,
                                shell=True)
        except subprocess.CalledProcessError:
            print ('Error: generate signature failed. Please check if private key and msg files are readable')
        except Exception as e:
            print e

    def verify_sig(self):
        """This function verifies a signature on a given message file by using the certificate specified in the configuration.
           The dependent configuration keywords of this function are "MSG", "SIG" and"SIGCERT".

        Return:

            True -- signature is valid.
            error -- otherwise, error may be raised.
        """
        msg_path = os.path.expanduser(self.config.get('MSG', ''))
        sig_path = os.path.expanduser(self.config.get('SIG', ''))
        cert_path = os.path.expanduser(self.config.get('SIGCERT', ''))
        try:
            # Check if the paths to MSG, SIG and SIGNER-CERT files are valid.
            if not os.path.isfile(msg_path):
                raise Exception(
                    'Error: path \"' + msg_path + '\" to message file is invalid or it is not a file. Please check the '
                    'configuration file \"' + self.cert_cnf + '\".')
            if not os.path.isfile(sig_path):
                raise Exception(
                    'Error: path \"' + sig_path + '\" to signature file is invalid or it is not a file. Please check '
                    'the configuration file \"' + self.cert_cnf + '\".')
            if not os.path.isfile(cert_path):
                raise Exception('Error: signer\'s certificate \"' + cert_path + '\" is not a file.')

            # Extract public key from the signer's certificate (SIGNER-CERT).
            self.utl.check_call('openssl x509 -pubkey -noout -in ' + cert_path + ' > tmpk.pem', shell=True)
            # Verify the signature
            self.utl.check_call('openssl dgst -sha256 -verify tmpk.pem -signature ' + sig_path + ' ' + msg_path,
                                shell=True)
            print ('Signature is valid.')
            return True
        except subprocess.CalledProcessError as cpe:
            if str(cpe.cmd).find('-pubkey') != -1:  # Certificate SIGNER-CERT is invalid.
                print ('Error: signature verificate faild. Signer\'s certificate \"' + cert_path + '\" is invalid.')
                raise
            if str(cpe.cmd).find('-verify') != -1:  # Signature verification failed.
                print ('Error: signature verification failed. Please check if message file \"' + msg_path +
                       '\" and signatre file \"' + sig_path +
                       '\" are a pair, and if the used signer\'s certificate \"' + cert_path + '\" is correct.')
                raise
        except Exception as e:
            print (e)
            raise

    def verify_cert(self, cert_chain, cert, ocsp):
        """This function verifies a certificate according to the given certificate chain.

        :param cert_chain: path to CA chain.
        :param cert: path to certificate.
        :param ocsp: URL of OCSP server.
        :type cert_chain: str.
        :type cert: str.
        :type ocsp: str.

        Return:

            True -- verification succeeds
            False/error -- otherwise, false or error may be raised.
        """
        chain_path = os.path.expanduser(cert_chain)  # os.path.expanduser(self.config.get('CACHAIN',''))
        cert_path = os.path.expanduser(cert)  # os.path.expanduser(self.config.get('CERT',''))
        try:
            if not os.path.isfile(cert_path):
                raise IOError('Path \"' + cert_path + '\" to the certificate is invalid or it is not a file.')
            if not os.path.isfile(chain_path):
                raise IOError('Path \"' + chain_path + '\" to CA certificate chain is invalid or it is not a file.')

            # cmd to verify certificate chain and certificate
            if ocsp != '':
                # OCSP server is set and then check if certificate was revoked.
                p = subprocess.Popen(
                    ['openssl', 'ocsp', '-CAfile', chain_path, '-issuer', chain_path, '-cert', cert_path, '-url',
                     ocsp, '-resp_text'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                out, err = p.communicate()
                if err.lower().find('error') != -1:
                    raise RuntimeError(err)
                if out.find('revoked') != -1:
                    print ('Invalid certificate: ' + self.config['CERT'] + ' was revoked.')
                    return False
            self.utl.check_call('openssl verify -verbose -CAfile ' + chain_path + ' ' + cert_path, shell=True)
            print ('Certificate verified.')
            return True
        except subprocess.CalledProcessError:
            print (
                'Error: certificate verification failed because the certificate is not authenticated by the valid CA.')
            raise
        except IOError as ioe:
            print (ioe)
            raise
        except RuntimeError as re:
            print (re)
            raise
        except Exception as e:
            print ('Error: certificate verification failed.')
            print ('Unknown error.')
            print (e)
            raise
