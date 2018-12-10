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
import os.path
import inspect
import sys

sys.path.insert(0, '..')
import smit.utils


class DeployRouter(object):
    """For router installation and configuration
    """
    utl = smit.utils.Utils()
    package_path = ''
    install_path = ''
    config = {}

    def __init__(self):
        """Constructor initializes variables
        """
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.config = {'EFACE': '', 'IP6': '', 'NETMASK': '', 'LFACE': '', 'PREFIX': '', 'ABRO': '',
                       'AdvSendAdvert': '', 'UnicastOnly': '',
                       'AdvCurHopLimit': '', 'AdvSourceLLAddress': '', 'AdvOnLink': '', 'AdvAutonomous': '',
                       'AdvRouterAddr': '', 'AdvVersionLow': '',
                       'AdvVersionHigh': '', 'AdvValidLifeTime': ''}
        self.install_path = '/opt/src'

    def install_radvd(self):
        """Install radvd for native 6LoWPAN router
        """
        self.utl.call('sudo apt-get -y --force-yes install dh-autoreconf', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install bison', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install git', shell=True)
        self.utl.call('sudo mkdir -p ' + self.install_path, shell=True)
        os.chdir(self.install_path)
        self.utl.call('wget https://sourceforge.net/projects/flex/files/flex-2.6.0.tar.bz2', shell=True)
        self.utl.call('tar xjf flex-2.6.0.tar.bz2', shell=True)
        os.chdir('flex-2.6.0')
        self.utl.call('./configure', shell=True)
        self.utl.call('make', shell=True)
        self.utl.call('sudo make install', shell=True)
        self.utl.call('sudo apt-get -y remove bison', shell=True)
        os.chdir(self.install_path)
        self.utl.call('wget http://ftp.gnu.org/gnu/bison/bison-3.0.tar.gz', shell=True)
        self.utl.call('tar xzf bison-3.0.tar.gz', shell=True)
        os.chdir('bison-3.0')
        self.utl.call('./configure', shell=True)
        self.utl.call('sudo make', shell=True)
        self.utl.call('sudo make install', shell=True)
        os.chdir(self.install_path)
        self.utl.call('git clone https://github.com/linux-wpan/radvd.git -b 6lowpan', shell=True)
        os.chdir('radvd')
        self.utl.call('./autogen.sh', shell=True)
        self.utl.call('./configure --prefix=/usr/local --sysconfdir=/etc --mandir=/usr/share/man', shell=True)
        self.utl.call('sudo make', shell=True)
        self.utl.call('sudo make install', shell=True)
        os.chdir(self.package_path)

    def config_static_route(self):
        """Configure static route based on the configuration file.
        """
        self.config = self.utl.read_config('config', self.config)

        if os.path.isfile('/etc/radvd.conf'):
            self.utl.call('sudo cp -f /etc/radvd.conf /etc/radvd.sbck', shell=True)

        # write and replace /etc/radvd.conf file, the ole file is copied to /etc/radvd.sbck for backup.
        f = open('tmp_radvd', 'w')
        f.write('interface ' + self.config['LFACE'] + '\n')
        f.write('{\n')
        f.write(' ' * 3 + 'AdvSendAdvert ' + self.config['AdvSendAdvert'] + ';\n')
        f.write(' ' * 3 + 'UnicastOnly ' + self.config['UnicastOnly'] + ';\n')
        f.write(' ' * 3 + 'AdvCurHopLimit ' + self.config['AdvCurHopLimit'] + ';\n')
        f.write(' ' * 3 + 'AdvSourceLLAddress ' + self.config['AdvSourceLLAddress'] + ';\n\n')

        f.write(' ' * 3 + 'prefix ' + self.config['PREFIX'] + '\n')
        f.write(' ' * 3 + '{\n')
        f.write(' ' * 6 + 'AdvOnLink ' + self.config['AdvOnLink'] + ';\n')
        f.write(' ' * 6 + 'AdvAutonomous ' + self.config['AdvAutonomous'] + ';\n')
        f.write(' ' * 6 + 'AdvRouterAddr ' + self.config['AdvRouterAddr'] + ';\n')
        f.write(' ' * 3 + '};\n\n')

        f.write(' ' * 3 + 'abro ' + self.config['ABRO'] + '\n')
        f.write(' ' * 3 + '{\n')
        f.write(' ' * 6 + 'AdvVersionLow ' + self.config['AdvVersionLow'] + ';\n')
        f.write(' ' * 6 + 'AdvVersionHigh ' + self.config['AdvVersionHigh'] + ';\n')
        f.write(' ' * 6 + 'AdvValidLifeTime ' + self.config['AdvValidLifeTime'] + ';\n')
        f.write(' ' * 3 + '};\n')
        f.write('};\n')
        f.close()
        self.utl.call('sudo cp -f tmp_radvd /etc/radvd.conf', shell=True)
        self.utl.call('sudo rm -f tmp_radvd', shell=True)
        value = 'net.ipv6.conf.all.forwarding'
        self.utl.delete_lines('/etc/sysctl.conf', value, 0, len(value), True)
        value += '=1'
        self.utl.write_file(value + '\n', '/etc/sysctl.conf', 'a')

        content = []
        content.append('### Begin SMIT Config ###\n')
        content.append('auto ' + self.config.get('EFACE', '') + '\n')
        content.append('iface ' + self.config.get('EFACE', '') + ' inet6 static\n')
        content.append('address ' + self.config.get('IP6', '') + '\n')
        content.append('netmask ' + self.config.get('NETMASK', '') + '\n')
        content.append('### End SMIT Config ###\n')

        self.utl.insert_net_interface(content)

    def setup(self):
        """Install and configure a border router with dependent software.
        """
        print('=== Install radvd ===')
        self.install_radvd()
        print('=== Configure static route ===')
        self.config_static_route()
        print('=== Add radvd to system startup ===')
        self.utl.delete_lines('/etc/rc.local', 'sudo radvd', 0, len('sudo radvd'), True)
        self.utl.insert_lines([' sudo radvd\n'], '/etc/rc.local', 'exit 0')
