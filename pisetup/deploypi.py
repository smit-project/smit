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

import sys
import os
import time
import os.path
import getpass
import inspect
import subprocess

sys.path.insert(0, '..')
import smit.utils


class DeployPi(object):
    """For kernel configuration and installation.
    """
    utl = smit.utils.Utils()
    package_path = ''
    CONFIG_FILE = '/boot/config.txt'
    LOWPAN_FILE = '/etc/default/lowpan'
    config = {'BP': '', 'RP': '', 'LD': '', 'LH': '', 'LINUX': '', 'KREPO': '',
              'KBRANCH': '', 'CHECKOUT': '', 'FD': '', 'FH': '', 'FIRMWARE': '',
              'FREPO': '', 'FBRANCH': '', 'TD': '', 'TH': '', 'TOOLS': '',
              'TREPO': '', 'PIDIR': '', 'DOWNDIR': '', 'MAC': '', 'CHN': '',
              'PAN': '', 'IP6': '', 'dtoverlay': '', 'OSDIR': '', 'RASPBIAN': '', 'OD': '', 'IMG': ''}

    def __init__(self):
        """Constructor initializes variables
        """
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def __del__(self):
        """Destructor to clean the object and delete
        """

    def get_mount_path(self, dev, mnt_path):
        """
        Set the current mount path. This is an interactive function to set the current mount path for specific device.

        :param dev: device name.
        :param mnt_path: default mount path
        :type dev: str.
        :type mnt_path: str.

        Returns:
            str. -- current mount path.

        Note::

            The device should be checked before calling this function.
        """
        default_path = mnt_path
        while True:
            c_in = raw_input('Set the mount path of ' + dev + ' to: ' + default_path + '? [Y/N]: ')
            if c_in != 'Y' and c_in != 'y':
                mnt_path = raw_input('Enter the mount path: ')
                if not os.path.exists(mnt_path) and mnt_path != default_path:
                    print('Invalid path.')
                else:
                    mnt_path = os.path.normpath(mnt_path)
                    break
            else:
                break

        return mnt_path

    def gen_mount(self, dev, mnt_path):
        """Check and Return mount device information: device name, device path and mount path.

        :param dev: device name
        :param mnt_path: the mount path
        :type mnt_path: str.
        :type dev: str.

        Returns:
            dict. -- The dictionary contains::

                DevName - device name.
                DevPath - device path.
                MountPath - mount path.
        """
        dev_info = {}
        dev_path = "/dev/" + dev
        if self.utl.check_device_exist(dev_path):
            if mnt_path != '':
                self.utl.call('sudo mkdir -p ' + mnt_path, shell=True)
                dev_info.update({'DevName': dev})
                dev_info.update({'MountPath': mnt_path})
                dev_info.update({'DevPath': dev_path})
            else:
                dev_info = {}

        return dev_info

    def install_dependency(self):
        """Install dependencies.
        """
        self.utl.call('sudo apt-get update', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install curl unzip', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install gcc-arm-linux-gnueabihf libncurses5-dev git', shell=True)

    def copy_to_pi(self, dev_path, filename, dest_path='/opt/src'):
        """Copy a file or directory to Pi.

        :param dev_path: the mounted device path
        :param filename: file or directory path
        :param dest_path: destination path of file
        :type dev_path: str.
        :type filename: str.
        :type dest_path: str.

        Returns:
            int. -- The return code::

                 1 -- succeed.
                -1 -- source file does not exist.
                -2 -- device does not exist.
        """
        filename = os.path.normpath(filename)

        if not os.path.exists(filename):
            print('File: ' + filename + ' does not exist.')
            return -1

        if not os.path.exists(dev_path):
            print('Device: ' + dev_path + ' does not exist.')
            return -2

        path = os.path.normpath(dev_path + '/' + dest_path)
        self.utl.call('sudo mkdir -p ' + path, shell=True)
        self.utl.call('sudo cp -rf ' + filename + ' ' + path, shell=True)

        return 1

    def compile_kernel(self, boot_path, root_path, config):
        """Compile kernel for Raspberry Pi

        :param boot_path: mounted boot path
        :param root_path: mounted root path
        :param config: configuration for compiling a kernel
        :type boot_path: str.
        :type boot_path: str.
        :type config: dict.
        """
        linux = 'git clone '
        firmware = 'git clone '
        tools = 'git clone '

        username = getpass.getuser()
        self.utl.call('sudo mkdir -p ' + config.get('DOWNDIR', ''), shell=True)
        self.utl.call('sudo chown ' + username + ' ' + config.get('DOWNDIR', ''), shell=True)
        os.chdir(config.get('DOWNDIR', ''))
        # generate commands to download source code
        if (config.get('LD', '') == 'Y' or config.get('LD', '') == 'y') and config.get('KREPO', '') != '':
            if config.get('LH', '') == 'Y' or config.get('LH', '') == 'y':
                linux += '--depth 1 '
            if config.get('KBRANCH', '') != '':
                linux = linux + config['KREPO'] + ' --branch ' + config['KBRANCH'] + ' --single-branch ' + config.get(
                    'LINUX', '')
            else:
                linux = linux + config['KREPO'] + ' ' + config.get('LINUX', '')
        else:
            linux = ''
        if (config.get('FD', '') == 'Y' or config.get('FD', '') == 'y') and config.get('FREPO', '') != '':
            if config.get('FH', '') == 'Y' or config.get('FH', '') == 'y':
                firmware += '--depth 1 '
            if config.get('FBRANCH', '') != '':
                firmware = firmware + config['FREPO'] + ' --branch ' + config[
                    'FBRANCH'] + ' --single-branch ' + config.get('FIRMWARE', '')
            else:
                firmware = firmware + config['FREPO'] + ' ' + config.get('FIRMWARE', '')
        else:
            firmware = ''
        if (config.get('TD', '') == 'Y' or config.get('TD', '') == 'y') and config.get('TREPO', '') != '':
            if config.get('TH', '') == 'Y' or config.get('TH', '') == 'y':
                tools = tools + '--depth 1 ' + config['TREPO'] + ' ' + config.get('TOOLS', '')
            else:
                tools = tools + config['TREPO'] + ' ' + config.get('TOOLS', '')
        else:
            tools = ''

        self.utl.call(linux, shell=True)
        self.utl.call(firmware, shell=True)
        self.utl.call(tools, shell=True)

        os.chdir(config.get('LINUX', ''))
        if config.get('CHECKOUT', '') != '':
            self.utl.call('sudo git checkout ' + config['CHECKOUT'], shell=True)
        self.utl.call('sudo cp -f ' + self.package_path + '/config_kernel ' + config.get('LINUX', '') + '/.config',
                      shell=True)
        self.utl.call('CROSS_COMPILE=arm-linux-gnueabihf- ARCH=arm make olddefconfig zImage modules dtbs -j4',
                      shell=True)

        self.utl.call('sudo cp arch/arm/boot/dts/*.dtb ' + boot_path, shell=True)
        self.utl.call('sudo mkdir -p ' + boot_path + '/overlays', shell=True)
        self.utl.call('sudo cp arch/arm/boot/dts/overlays/*.dtb* ' + boot_path + '/overlays', shell=True)
        self.utl.call('sudo scripts/mkknlimg arch/arm/boot/zImage ' + boot_path + '/kernel7.img', shell=True)
        self.utl.call(
            'sudo CROSS_COMPILE=arm-linux-gnueabihf- ARCH=arm INSTALL_MOD_PATH=' + root_path + ' make modules_install',
            shell=True)
        os.chdir(config.get('FIRMWARE', ''))
        self.utl.call('sudo rm -rf ' + root_path + '/opt/vc', shell=True)
        self.utl.call('sudo cp -r hardfp/opt/* ' + root_path + '/opt', shell=True)

        os.chdir(self.package_path)

    def mount(self, dev_path, mnt_path):
        """Mount a device.

        :param dev_path: device path
        :param mnt_path: mount path
        :type dev_path: str.
        :type mnt_path: str.
        """
        if os.path.exists(dev_path) and mnt_path != '':
            self.utl.call('sudo mkdir -p ' + mnt_path, shell=True)
            self.utl.call('sudo mount ' + dev_path + ' ' + mnt_path, shell=True)
        else:
            print('ERROR: Device information is invalid.')

    def umount(self, mnt_path):
        """Unmount boot and root devices

        :param mnt_path: mount path
        :type mnt_path: str.
        """
        if os.path.exists(mnt_path):
            self.utl.call('sudo umount ' + mnt_path, shell=True)
        else:
            print("ERROR: mount path does not exist.")

    def initialize_pi(self):
        """Install iwpan and enable radio on Raspberry Pi.
        """
        self.config = self.utl.read_config('config', self.config)
        install_path_on_pi = self.config.get('PIDIR', '')
        self.utl.call('mkdir -p ' + install_path_on_pi, shell=True)
        if not os.path.exists(install_path_on_pi):
            print('ERROR: installation path (on Raspberry Pi): \"' + install_path_on_pi + '\"does not exitst.')
            exit(1)
        username = getpass.getuser()
        # install iwpan
        self.utl.call('sudo apt-get update', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install dh-autoreconf libnl-3-dev libnl-genl-3-dev git', shell=True)
        self.utl.call('sudo mkdir -p ' + install_path_on_pi, shell=True)
        os.chdir(install_path_on_pi)
        self.utl.call('sudo rm -rf wpan-tools/', shell=True)
        self.utl.call('sudo rm -rf wpan-raspbian/', shell=True)
        self.utl.call('sudo git clone https://github.com/linux-wpan/wpan-tools', shell=True)
        os.chdir('wpan-tools')
        self.utl.call('sudo ./autogen.sh', shell=True)
        self.utl.call('./configure CFLAGS=\'-g -O0\' --prefix=/usr --sysconfdir=/etc --libdir=/usr/lib', shell=True)
        self.utl.call('make', shell=True)
        self.utl.call('sudo make install', shell=True)
        # enable radio
        self.utl.call('sudo chown ' + username + ' /opt/src', shell=True)
        os.chdir(install_path_on_pi)
        self.utl.call('sudo git clone https://github.com/riot-makers/wpan-raspbian', shell=True)
        os.chdir('wpan-raspbian')
        self.utl.call('sudo cp -r usr/local/sbin/* /usr/local/sbin/', shell=True)
        self.utl.call('sudo chmod +x /usr/local/sbin/*', shell=True)
        self.utl.call('sudo cp etc/systemd/system/lowpan.service /etc/systemd/system/.', shell=True)
        self.utl.call('sudo systemctl daemon-reload', shell=True)
        self.utl.call('sudo systemctl enable lowpan.service', shell=True)
        self.utl.call('sudo systemctl start lowpan.service', shell=True)
        self.utl.call('sudo ldconfig -v > /dev/null', shell=True)
        # install ndisc6
        self.utl.call('sudo apt-get -y --force-yes install ndisc6', shell=True)

        os.chdir(self.package_path)

    def setup_pi(self, args):
        """Configure the kernel to setup a Raspberry Pi.

        :param args: command line arguments
        """

        self.config = self.utl.read_config('config', self.config)

        print('=== Install dependencies ===')
        self.install_dependency()

        if args.force is not None:  # Download the latest raspbian os
            if not self.utl.check_device_exist('/dev/' + args.force[0]):
                print('ERROR: invalid argument: ' + args.force[0])
                exit(1)
            os_path = self.config.get('OSDIR', '')
            if os_path != '':
                self.utl.call('mkdir -p ' + os_path, shell=True)
                if self.config.get('OD', '') == 'Y' or self.config.get('OD', '') == 'y':
                    if os.listdir(os_path):
                        print('ERROR: the directory \"' + os_path + '\" is not empty.')
                        exit(1)
                    if self.config.get('RASPBIAN', '') != '':
                        os.chdir(os_path)
                        self.utl.call('curl -L -o os.zip ' + self.config['RASPBIAN'], shell=True)
                        self.utl.call('unzip os.zip', shell=True)
                        self.utl.call('mv *.img ' + self.config.get('IMG', 'os.img'), shell=True)
                else:
                    os.chdir(os_path)
            else:
                print('ERROR: invalid configuration.')
                exit(1)

            device = args.force[0]
            if device.startswith('sd'):
                boot_part = '1'
                root_part = '2'
            else:  # device starts with('mmc'):
                boot_part = 'p1'
                root_part = 'p2'
            self.utl.call('sudo umount -a /dev/' + args.force[0] + ' >> /dev/null 2>&1', shell=True)
            self.utl.call('sudo parted -s /dev/' + args.force[0] + ' mktable msdos', shell=True)
            self.utl.call('sudo parted -s /dev/' + args.force[0] + ' mkpart primary fat16 1 5%', shell=True)
            self.utl.call('sudo wipefs -a /dev/' + args.force[0] + boot_part, shell=True)
            self.utl.call('sudo mkfs.vfat /dev/' + args.force[0] + boot_part, shell=True)
            print('Copying Raspbian OS ...')
            self.utl.call('sudo dd bs=4M if=' + self.config.get('IMG', 'os.img') + ' of=/dev/' + args.force[0],
                          shell=True)
            self.utl.call('sudo partprobe /dev/' + args.force[0], shell=True)
            time.sleep(5)
            args.boot = ['']
            args.root = ['']
            args.boot[0] = args.force[0] + boot_part
            args.root[0] = args.force[0] + root_part
            os.chdir(self.package_path)

        if args.checkout is not None:
            self.config['CHECKOUT'] = ''
            for index in range(len(args.checkout)):
                self.config['CHECKOUT'] = self.config['CHECKOUT'] + args.checkout[index] + ' '

        dev_boot = self.gen_mount(args.boot[0], self.config.get('BP', ''))
        dev_root = self.gen_mount(args.root[0], self.config.get('RP', ''))
        if dev_root == {}:
            print('ERROR: invalid root arguments.')
            exit(1)
        if dev_boot == {}:
            print('ERROR: invalid root arguments.')
            exit(1)

        if self.utl.get_dev_format(dev_root['DevPath']) != 'ext4':
            print('ERROR: the format of \'root\' partition on the SD card must be \'ext4\'.')
            exit(1)
        if not os.path.exists(dev_boot['MountPath']) or not os.path.exists(dev_root['MountPath']):
            print('ERROR: invalid path.')
            exit(1)
        elif dev_boot['MountPath'] == dev_root['MountPath']:
            print('ERROR: ' + dev_boot['DevName'] + ' and ' + dev_root['DevName'] + ' are mounting to the same path.')
            exit(1)
        else:
            dev_boot['MountPath'] = os.path.normpath(dev_boot['MountPath'])
            dev_root['MountPath'] = os.path.normpath(dev_root['MountPath'])

        print('=== Mount devices ===')
        self.mount(dev_boot['DevPath'], dev_boot['MountPath'])
        self.mount(dev_root['DevPath'], dev_root['MountPath'])
        print('=== Compile kernel ===')

        self.compile_kernel(dev_boot.get('MountPath', ''), dev_root.get('MountPath', ''), self.config)
        if os.path.exists(self.config.get('PIDIR', '')):
            self.copy_to_pi(dev_root['MountPath'], '../../../CSIRO', self.config.get('PIDIR', ''))
        else:
            print('Installation path: \"' + self.config.get('PIDIR', '') + '\"does not exitst.')

        print('=== Unmount devices ===')
        self.umount(dev_boot['MountPath'])
        self.umount(dev_root['MountPath'])

    def enable_radio(self):
        """Enable an IEEE 802.15.4 radio, currently support openlab and MICROCHIP radios.
        """
        print('=== Install radio ===')
        # read configuration file
        self.config = self.utl.read_config('config', self.config)

        # write config.txt
        value = 'dtoverlay=' + self.config.get('dtoverlay', '')
        if self.config.get('dtoverlay', '') == '':  # no radio selected
            print ('ERROR: No radio selected. Please check the configuration file: \"config\".')
            exit(1)
        self.utl.delete_lines(self.CONFIG_FILE, value, 0, len(value), True)
        self.utl.write_file(value + '\n', self.CONFIG_FILE, 'a')
        if value.find('mrf24j40') > 0:
            self.utl.call("sudo cp -f mrf24j40.dtbo /boot/overlays/", shell=True)

        # write lowpan file
        f = open('tmp_lowpan', 'w')
        if self.config.get('CHN', '') != '':
            f.write('CHN=\"' + self.config['CHN'] + '\"\n')
        if self.config.get('PAN', '') != '':
            f.write('PAN=\"' + self.config['PAN'] + '\"\n')
        if self.config.get('MAC', '') == '':
            f.write("MAC=\"" + self.utl.gen_mac() + "\"\n")
        else:
            f.write('MAC=\"' + self.config['MAC'] + '\"\n')
        if self.config.get('IP6', '') != '':
            f.write('IP6=\"' + self.config['IP6'] + '\"\n')
        f.close()
        self.utl.call("sudo cp tmp_lowpan " + self.LOWPAN_FILE, shell=True)

        print('=== Install software ===')
        self.initialize_pi()

        return
