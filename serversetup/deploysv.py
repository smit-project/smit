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

sys.path.insert(0, '..')
import smit.utils
import os.path


class DeployServer(object):
    """For server configuration.
    """
    utl = smit.utils.Utils()
    config = {}

    def __init__(self):
        """Constructor initializes variables
        """
        self.config = {'EFACE': '', 'IP6': '', 'NETMASK': '', 'GW': '', 'SN': ''}

    def config_static_route(self):
        self.config = self.utl.read_config('config', self.config)
        content = []
        content.append('### Begin SMIT Config ###\n')
        content.append('auto ' + self.config.get('EFACE', '') + '\n')
        content.append('iface ' + self.config.get('EFACE', '') + ' inet6 static\n')
        content.append('address ' + self.config.get('IP6', '') + '\n')
        content.append('netmask ' + self.config.get('NETMASK', '') + '\n')
        content.append('post-up ip -6 route add ' + self.config.get('SN', '') + ' via ' + self.config.get('GW', '') +
                       ' dev ' + self.config.get('EFACE', '') + '\n')
        content.append('### End SMIT Config ###\n')

        self.utl.insert_net_interface(content)

    def setup(self):
        """Configure static route based on the configuration file.
        """
        print('=== Configure server ===')
        self.config_static_route()
