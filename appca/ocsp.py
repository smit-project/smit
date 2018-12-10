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
import inspect
sys.path.insert(0,'../../')
sys.path.insert(0,'../../../')
from smit import utils
import traceback


class OCSP(object):
    """This class manipulate OCSP server which responds the online certificate status request.
       The parameters used by this class is assigned in the configuration file "ocspcnf".
       The configuration file allows to set the network information, local certificate information and etc.
    """
    utl = utils.Utils()
    config = {'CACERT': '', 'OCSPPORT': '', 'OCSPCERT': '', 'OCSPSK': '', 'CERTDB': ''}  # configuration keywords
    app_cnf = 'ocspcnf'  # the path to configuration file for this class
    package_path = ''  # the path to this package

    def __init__(self):
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        os.chdir(self.package_path)

    def init_config(self, **kwargs):
        """Initialize the package configuration according to the configuration file.
           This function MUST be called before other function call.
           The acceptable keywords are: config, CACERT, OCSPPORT, OCSPCERT, OCSPSK, CERTDB.
           Specifically, "config" is to set the path to configuration file.
           If arguments are passed to this function, the specified configuration file will be updated.

        :param kwargs: dictionary of passed arguments.
        """
        if kwargs.get('config', '') != '':
            self.app_cnf = os.path.expanduser(kwargs['config'])
        if not os.path.isfile(self.app_cnf):
            raise IOError('configuration file \"' + self.app_cnf + '\" doesn\'t exist or it is not a file.')
        self.config = self.utl.read_config(self.app_cnf, self.config)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.config.iteritems():
            if kwargs.get(key, '') != '' and kwargs[key] is not None:
                self.config[key] = kwargs[key]
                update += 1
        if update > 0:
            self.utl.update_config(self.app_cnf, self.config)

    def start(self):
        """This function starts an OCSP server according to the configuration.
        """
        port = self.config.get('OCSPPORT', '')
        db_path = os.path.expanduser(self.config.get('CERTDB', ''))
        signer_path = os.path.expanduser(self.config.get('OCSPCERT', ''))
        key_path = os.path.expanduser(self.config.get('OCSPSK', ''))
        ca_path = os.path.expanduser(self.config.get('CACERT', ''))
        try:
            if not os.path.isfile(signer_path):
                raise IOError('Path \"' + signer_path + '\" to OCSP certificate is invalid or it is not a file.')
            if not os.path.isfile(key_path):
                raise IOError('Path \"' + key_path + '\" to OCSP server private key is invalid or it is not a file.')
            if not os.path.isfile(db_path):
                raise IOError('Path \"' + db_path + '\" to the simulated global CA\'s database is invalid or it is '
                              'not a file.')
            if not os.path.isfile(ca_path):
                raise IOError('Path \"' + ca_path + '\" to the simulated global CA\'s certificate is invalid or it '
                              'is not a file.')
            if port != '':
                self.utl.check_call('openssl ocsp -index ' + db_path + ' -port ' + port + ' -rsigner ' + signer_path +
                                    ' -rkey ' + key_path + ' -CA ' + ca_path + ' -text -out log.txt', shell=True)
            else:
                print ('Error: port to OCSP server is not set.')
                raise
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print (e)
