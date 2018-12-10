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
import os.path

sys.path.insert(0, '..')
sys.path.insert(0, '../../')
import smit.utils
import time
from multiprocessing import Process
from string import Template
from sinkserver import Sink
from sinkserver import SinkPlain
import analysis
import subprocess
from datetime import datetime
import os
import pandas as pd


class SetupExp(object):
    """Setup the experiment for experiment initialization, experiment run, data collection and etc.
    """
    utl = smit.utils.Utils()
    client_config_items = {'C': '', 'ST': '', 'L': '', 'O': '', 'OU': '', 'CN': '',
                           'emailAddress': '', 'ECCPARAM': '', 'CAIP': '', 'CAPORT': '', 'CERT': '', 'CSR': '',
                           'MSG': '',
                           'SIG': '', 'CACERT': '', 'SK': '', 'SERVERIP': '', 'SERVERPORT': '', 'CACHAIN': '',
                           'TYPE': '',
                           'CERT_REQS': '', 'TIMEZONE': '', 'SYNCTIME': '', 'REFLOWPAN': '', 'SYSWAIT': '',
                           'PAYLOADLEN': '', 'DATE': '', 'SENDTIME': '', 'SENDRATE': '', 'DEVNUM': ''}
    sink_config_items = {'C': '', 'ST': '', 'L': '', 'O': '', 'OU': '', 'CN': '',
                         'emailAddress': '', 'ECCPARAM': '', 'CAIP': '', 'CAPORT': '', 'CERT': '', 'CSR': '', 'MSG': '',
                         'SIG': '', 'CACERT': '', 'SK': '', 'SERVERIP': '', 'SERVERPORT': '', 'CACHAIN': '', 'TYPE': '',
                         'CERT_REQS': '', 'ROUTER_IP6': '', 'CLIENT_IP6': '', 'CLIENT_LINK_IP6': '', 'CLIENT_IP4': '',
                         'CLIENT_WKD': '', 'ROUTER_WKD': '', 'PASSWORD': '', 'SINK_INTERFACE': '', 'DATE': '',
                         'ROUTER_LOGDIR': '', 'SINK2CLIENT': '', 'CLIENT_SCRIPT': '', 'USER': '',
                         'CLIENT_SCRIPT_DIR': ''}

    def install_dependencies(self):
        """Install dependencies for experiment on a device, e.g., sink server, border router and client device.
        """
        self.utl.call('sudo apt-get -y --force-yes install ntp ntpdate', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install tcpdump', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install sshpass', shell=True)

    def init_client_config(self, **args):
        """This function set the configuration for client devices, where the configurations are written to the
            configuration file e.g., 'client_expcnf'.
            Note: This function does not take any input from the configuration file, but output specified configuration
            (e.g., from command line) to the configuration file.

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            client_config = os.path.expanduser(args['config'])
        else:
            client_config = 'client_expcnf'  # defualt configuration file
        if not os.path.isfile(client_config):
            raise IOError('configuration file \"' + client_config + '\" doesn\'t exist or it is not a file.')
        # Read configuration from the file to variable config.
        self.client_config_items = self.utl.read_config(client_config, self.client_config_items)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.client_config_items.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.client_config_items[key] = args[key]
                update += 1
        if args['DATE'] is None:  # date is not set from commnad line
            date = datetime.today().strftime("%m/%d/%Y")
            if date != self.client_config_items['DATE']:
                self.client_config_items['DATE'] = date
                update += 1
        if args['TIMEZONE'] is None:  # timezone is not set from commnad line
            p = subprocess.Popen('cat /etc/timezone', stdout=subprocess.PIPE, shell=True)
            (out, err) = p.communicate()
            if out.strip() != self.client_config_items['TIMEZONE']:
                self.sink_config_items['TIMEZONE'] = out.strip()
                update += 1
        if update > 0:
            self.utl.update_config(client_config, self.client_config_items)
        # Backup configuration file
        self.utl.call('cp -f ' + client_config + ' ' + client_config + '.bck', shell=True)

    def init_sink_config(self, **args):
        """This function sets configuration for sink server. The function takes the input from command line and writes
            the configuration to sink server configuation file, e.g., sink_expcnf

        :param args: dictionary of passed arguments.
        """
        if args.get('config', '') != '':
            sink_config = os.path.expanduser(args['config'])
        else:
            sink_config = 'sink_expcnf'  # default configuration file
        if not os.path.isfile(sink_config):
            raise IOError('configuration file \"' + sink_config + '\" doesn\'t exist or it is not a file.')
        self.sink_config_items = self.utl.read_config(sink_config, self.sink_config_items)
        # Set run-time configuration which will overwrite the settings in configuration file.
        update = 0
        for key, value in self.sink_config_items.iteritems():
            if args.get(key, '') != '' and args[key] is not None:
                self.sink_config_items[key] = args[key]
                update += 1
        if args['DATE'] is None:  # date is not set from commnad line
            date = datetime.today().strftime("%m/%d/%Y")
            if date != self.sink_config_items['DATE']:
                self.sink_config_items['DATE'] = date
                update += 1
        if update > 0:
            self.utl.update_config(sink_config, self.sink_config_items)
        # Backup configuration file
        self.utl.call('cp -f ' + sink_config + ' ' + sink_config + '.bck', shell=True)

    def create_shell_scripts(self):
        """This function creates shell scripts which are used during the experiment setup.
            The generated shell scripts are used to control client devices and router from sink server.
            The scripts functionality includes start clients, start router network monitor, upload files to clients and
            create connection.
        """
        self.utl.makedir('scripts')
        self.generate_start_sp()
        self.generate_router_sp()
        self.generate_upload_sp()
        self.generate_conn_sp()
        self.generate_collect_sp()
        self.generate_stop_sp()

    def generate_start_sp(self):
        """This function generates a shell script to start clients.
            The generated script is used on sink server or border router rather.
        """
        head = """\
#!/bin/bash
#
#
# Start client devices. This script should be run on sink server or border router.
#
#
        """
        client_cmd = Template("""\

echo "Running commands on $ip"
#sshpass -p $password ssh -o "StrictHostKeyChecking no" $user@$ip "echo $ip; cd $clientdir; sudo rm -f sync.log rs.log send.log; sudo nohup python $client_script > /dev/null 2>&1 &"
sshpass -p $password ssh -o "StrictHostKeyChecking no" $user@$ip "echo $ip; cd $clientdir; sudo rm -f *.log; /usr/local/bin/python2.7 $client_script > /dev/null 2>&1 &"
sleep 1

                """)
        os.chdir('scripts')
        path = self.sink_config_items['CLIENT_SCRIPT']
        dir_name = os.path.dirname(path.rstrip('/'))
        client_script = os.path.basename(path.rstrip('/'))
        if dir_name == '' or client_script == '':
            raise Exception('Error: client script path is not valid.')
        # Generate script for IPv4 control
        client_ip4 = self.sink_config_items['CLIENT_IP4'].split(',')
        if len(client_ip4) > 0:  # there are ipv6 addresses provided
            script = head
            for client_ip in client_ip4:
                script = script + client_cmd.substitute(ip=client_ip, clientdir=dir_name,
                                                        password=self.sink_config_items['PASSWORD'],
                                                        client_script=client_script,
                                                        user=self.sink_config_items['USER'])

            self.utl.write_file(script, 'start_clients_ip4.sh', 'w')
            self.utl.call('sudo chmod +x start_clients_ip4.sh', shell=True)
        # Generate script for IPv6 control
        client_ip6 = self.sink_config_items['CLIENT_IP6'].split(',')
        if len(client_ip6) > 0:  # there are ipv6 addresses provided
            script = head
            for client_ip in client_ip6:
                script = script + client_cmd.substitute(ip=client_ip, clientdir=dir_name,
                                                        password=self.sink_config_items['PASSWORD'],
                                                        client_script=client_script,
                                                        user=self.sink_config_items['USER'])

            self.utl.write_file(script, 'start_clients_ip6.sh', 'w')
            self.utl.call('sudo chmod +x start_clients_ip6.sh', shell=True)
        os.chdir('..')

    def generate_router_sp(self):
        """This function generates a shell script for router to start the experiment.
        """
        temp = Template("""\
#!/bin/bash
#
#
# Start router to monitor the netowrk interfaces.
#
#

echo "Synchronizing time with NTP server."
sudo timedatectl set-timezone $timezone
sudo date --set="$date"
sudo ntpdate -u $ntpserver
mkdir -p $workdir
cd $workdir
echo "Creating log directories."
mkdir -p eth0 lowpan0 wpan0
echo "Starting tcpdump"
cd eth0
/sbin/ifconfig > router.info
sudo nohup tcpdump -i eth0 -ttttnnvvS -w eth0.log &
cd ../lowpan0
/sbin/ifconfig > router.info
sudo nohup tcpdump -i lowpan0 -ttttnnvvS -w lowpan0.log &
cd ../wpan0
/sbin/ifconfig > router.info
sudo nohup tcpdump -i wpan0 -ttttnnvvS -w wpan0.log &
exit
        """)
        os.chdir('scripts')
        script = temp.substitute(workdir=self.sink_config_items['ROUTER_WKD'], date=self.sink_config_items['DATE'],
                                 ntpserver=self.sink_config_items['SERVERIP'],
                                 timezone=self.client_config_items['TIMEZONE'])
        self.utl.write_file(script, 'start_router.sh', 'w')
        self.utl.call('sudo chmod +x start_router.sh', shell=True)
        os.chdir('..')

    def generate_conn_sp(self):
        """This function generates a shell script to create network connection by using link-layer addresses of clients.
            This script is used on router and it is for IPv6 only.
        """
        head = """\
#!/bin/bash
#
#
# Create network connection to router via link-layer addresses.
#
#
        """
        client_cmd = Template("""\

echo "Running commands on $lladdr"
sshpass -p $password ssh -o "StrictHostKeyChecking no" $user@$lladdr%$interface "echo $lladdr; sudo rdisc6 $interface"
sleep 1

        """)
        os.chdir('scripts')
        client_ip6 = self.sink_config_items['CLIENT_LINK_IP6'].split(',')

        if len(client_ip6) > 0:  # there are ipv6 addresses provided
            script = head
            for client_ip in client_ip6:
                print ("client_ip6: " + client_ip)
                lladd = self.sink_config_items['CLIENT_LINK_IP6']
                print ("CLIENT_LINK_IP6: " + lladd)
                script = script + client_cmd.substitute(lladdr=lladd, interface='wpan0',
                                                        password=self.sink_config_items['PASSWORD'],
                                                        user=self.sink_config_items['USER'])

            self.utl.write_file(script, 'create_conn.sh', 'w')
            self.utl.call('sudo chmod +x create_conn.sh', shell=True)
        os.chdir('..')

    def generate_upload_sp(self):
        """This function generates shell scripts to be used for file uploading to clients.
            The upload can be conducted via IPv4 or IPv6, but IPv6 (6LoWPAN) is not suitable to transmit large files.
            This function will output two shell scripts: upload_ip6.sh and upload_ip4.sh
            The IP addresses (v4/v6) are taking from the sink server configuration file.
        """
        head = Template("""\
#!/bin/bash
#
#
# Upload file/directory to remote clients via $version.
#
#
        """)
        client_cmd = Template("""\

echo "Running commands on $ip"
sshpass -p $password ssh -o "StrictHostKeyChecking no" $user@$ip \"mkdir -p $remote\"
sshpass -p $password scp -o "StrictHostKeyChecking no" -r $local $user@\[$ip\]:$remote
sleep 1

        """)
        os.chdir('scripts')
        # Generate script for ipv4 addresses
        client_ip4 = self.sink_config_items['CLIENT_IP4'].split(',')
        if len(client_ip4) > 0:  # there are ipv4 addresses provided
            script = head.substitute(version='IPv4')
            for client_ip in client_ip4:
                script = script + client_cmd.substitute(ip=client_ip, local=self.sink_config_items['SINK2CLIENT'],
                                                        remote=self.sink_config_items['CLIENT_WKD'],
                                                        password=self.sink_config_items['PASSWORD'],
                                                        user=self.sink_config_items['USER'])
            self.utl.write_file(script, 'upload_ip4.sh', 'w')
            self.utl.call('sudo chmod +x upload_ip4.sh', shell=True)
        # Generate script for ipv6 addresses
        client_ip6 = self.sink_config_items['CLIENT_IP6'].split(',')
        if len(client_ip6):  # there are ipv6 addresses provided
            script = head.substitute(version='IPv6')
            for client_ip in client_ip6:
                script = script + client_cmd.substitute(ip=client_ip, local=self.sink_config_items['SINK2CLIENT'],
                                                        remote=self.sink_config_items['CLIENT_WKD'],
                                                        password=self.sink_config_items['PASSWORD'],
                                                        user=self.sink_config_items['USER'])
            self.utl.write_file(script, 'upload_ip6.sh', 'w')
            self.utl.call('sudo chmod +x upload_ip6.sh', shell=True)
        os.chdir('..')

    def generate_stop_sp(self):
        """This function generates shell scripts to be used for stopping experiment.
            The stop commands can be conducted via IPv4 or IPv6.
            This function will output two shell scripts: stop_ip6.sh and stop_ip4.sh
            The IP addresses (v4/v6) are taking from the sink server configuration file.
        """
        head = Template("""\
#!/bin/bash
#
#
# Stop the experiment via $version.
#
#

        """)
        stop_client = Template("""\

echo "Stopping client $ip"
sshpass -p $password ssh -o "StrictHostKeyChecking no" $user@$ip "echo $ip; sudo pkill python; sudo pkill tcpdump"

        """)
        stop_router = Template("""\

echo "Stopping router $router_ip"
sshpass -p $password ssh -o "StrictHostKeyChecking no" $user@$router_ip "echo $router_ip; sudo pkill tcpdump"

        """)
        stop_sink = """\

echo "Stopping sink server monitor."
sudo pkill tcpdump
echo "Please terminate the sinkerver manually by Control+C."
        """
        os.chdir('scripts')
        # Generate script for ipv4 addresses
        client_ip4 = self.sink_config_items['CLIENT_IP4'].split(',')
        if len(client_ip4) > 0:  # there are ipv4 addresses provided
            script = head.substitute(version='IPv4')
            for client_ip in client_ip4:
                script = script + stop_client.substitute(ip=client_ip, password=self.sink_config_items['PASSWORD'],
                                                         user=self.sink_config_items['USER'])
            script = script + stop_router.substitute(router_ip=self.sink_config_items['ROUTER_IP6'],
                                                     password=self.sink_config_items['PASSWORD'],
                                                     user=self.sink_config_items['USER']
                                                     )
            script += stop_sink
            self.utl.write_file(script, 'stop_ip4.sh', 'w')
            self.utl.call('sudo chmod +x stop_ip4.sh', shell=True)
        # Generate script for ipv6 addresses
        client_ip6 = self.sink_config_items['CLIENT_IP6'].split(',')
        if len(client_ip6):  # there are ipv6 addresses provided
            script = head.substitute(version='IPv6')
            for client_ip in client_ip6:
                script = script + stop_client.substitute(ip=client_ip, router_ip=self.sink_config_items['ROUTER_IP6'],
                                                         password=self.sink_config_items['PASSWORD'],
                                                         user=self.sink_config_items['USER'])
            script = script + stop_router.substitute(router_ip=self.sink_config_items['ROUTER_IP6'],
                                                     password=self.sink_config_items['PASSWORD'],
                                                     user=self.sink_config_items['USER']
                                                     )
            script += stop_sink
            self.utl.write_file(script, 'stop_ip6.sh', 'w')
            self.utl.call('sudo chmod +x stop_ip6.sh', shell=True)
        os.chdir('..')

    def generate_collect_sp(self):
        """This function generates shell scripts to be used for collecting data from clients, router and sink. The
        collection can be conducted via IPv4 or IPv6, but IPv6 (6LoWPAN) is not suitable to transmit large files.
        This function will output two shell scripts: collect_ip6.sh and collect_ip4.sh The IP addresses (v4/v6) are
        taking from the sink server configuration file.
        """
        cwd = os.getcwd()
        head = """\
#!/bin/bash
#
#
# Collect data from clients, router and sink server.
#
#

        """
        create_dirs = """\

echo "Creating log directories."
mkdir -p logs/sink logs/router logs/clients

        """
        collect_sink = """\

echo "Collecting data from sink server."
cp -r *.log logs/sink/
cp -r exp logs/sink/

        """
        collect_router = Template("""\

echo "Collecting data from border router for interface $inf."
sshpass -p $password scp -o "StrictHostKeyChecking no" -r $user@\[$ip\]:$remote/$inf/$inf.log $local
sshpass -p $password scp -o "StrictHostKeyChecking no" -r $user@\[$ip\]:$remote/$inf/router.info $local

        """)
        collect_clients = Template("""\

echo "Collecting data from client on IP: $ip."
mkdir -p $local
sshpass -p $password scp -o "StrictHostKeyChecking no" -r $user@\[$ip\]:$remote $local

        """)
        # Create scripts
        os.chdir('scripts')
        # Create script section for collecting data from sink server and border router.
        script = head
        script += create_dirs
        script += collect_sink
        script = script + collect_router.substitute(inf='eth0', password=self.sink_config_items['PASSWORD'],
                                                    user=self.sink_config_items['USER'],
                                                    ip=self.sink_config_items['ROUTER_IP6'],
                                                    remote=self.sink_config_items['ROUTER_WKD'].rstrip('/'),
                                                    local='logs/router/')
        script = script + collect_router.substitute(inf='wpan0', password=self.sink_config_items['PASSWORD'],
                                                    user=self.sink_config_items['USER'],
                                                    ip=self.sink_config_items['ROUTER_IP6'],
                                                    remote=self.sink_config_items['ROUTER_WKD'].rstrip('/'),
                                                    local='logs/router/')
        script = script + collect_router.substitute(inf='lowpan0', password=self.sink_config_items['PASSWORD'],
                                                    user=self.sink_config_items['USER'],
                                                    ip=self.sink_config_items['ROUTER_IP6'],
                                                    remote=self.sink_config_items['ROUTER_WKD'].rstrip('/'),
                                                    local='logs/router/')
        script_share = script
        # Get remote client directory which contains log files.
        path = self.sink_config_items['CLIENT_SCRIPT']
        remote_dir = os.path.dirname(path.rstrip('/'))
        # Generate script for ipv4 addresses
        client_ip4 = self.sink_config_items['CLIENT_IP4'].split(',')
        if len(client_ip4) > 0:  # there are ipv4 addresses provided
            index = 1
            for client_ip in client_ip4:
                script = script + collect_clients.substitute(ip=client_ip, local='logs/clients/' + str(index),
                                                             remote=remote_dir + '/*.log',
                                                             password=self.sink_config_items['PASSWORD'],
                                                             user=self.sink_config_items['USER'])
                index += 1
            self.utl.write_file(script, 'collect_ip4.sh', 'w')
            self.utl.call('sudo chmod +x collect_ip4.sh', shell=True)
        # Generate script for ipv6 addresses
        client_ip6 = self.sink_config_items['CLIENT_IP6'].split(',')
        if len(client_ip6):  # there are ipv6 addresses provided
            index = 1
            script = script_share
            for client_ip in client_ip6:
                script = script + collect_clients.substitute(ip=client_ip, local='logs/clients/' + str(index),
                                                             remote=remote_dir + '/*.log',
                                                             password=self.sink_config_items['PASSWORD'],
                                                             user=self.sink_config_items['USER'])
            self.utl.write_file(script, 'collect_ip6.sh', 'w')
            self.utl.call('sudo chmod +x collect_ip6.sh', shell=True)
        os.chdir('..')

    def setup(self):
        """This function sets up the experiment and then start the experiment according to the configurations.
        """
        # Install dependencies.
        self.install_dependencies()
        # Create shell scripts.
        self.create_shell_scripts()

    def start_sink(self, dtls=True):
        """Start the sink server with or without DTLS protection.
        :param dtls: enable or disable DTLS, by default it is enabled.
        """
        # restart ntp service
        print ('Initializing server.')
        self.utl.call('sudo rm -rf exp logs', shell=True)
        print ('Starting NTP server.')
        self.utl.call('sudo /etc/init.d/ntp restart', shell=True)
        self.utl.call(
            'sudo nohup tcpdump -i ' + self.sink_config_items['SINK_INTERFACE'] + ' -ttttnnvvS -w enp9s0.log &',
            shell=True)
        print ('Starting sink server.')
        if dtls:
            print ('DTLS enabled.')
            sink = Sink()
        else:
            print ('DTLS disabled.')
            sink = SinkPlain()
        sink.start()

    def start_clients(self):
        """This function is to start all clients by using the generated shell script from create_shell_scripts function.
        """
        print ('Starting clients.')
        self.utl.call('sshpass -p ' + self.sink_config_items['PASSWORD'] + ' ssh -o \"StrictHostKeyChecking no\" ' +
                      self.sink_config_items['USER'] +
                      '@' + self.sink_config_items['ROUTER_IP6'] + ' -t ' + '\"cd ' + self.sink_config_items[
                          'ROUTER_WKD'].rstrip('/') +
                      '/scripts; echo \"Sending commands to clients.\"; ./start_clients_ip6.sh\"', shell=True)
        print ('Commands sent out.')

    def start_router(self):
        """This function is to start the border router by using the generated shell script from create_shell_scripts function.
        """
        print ('Connecting router.')
        print ('Uploading scripts to router.')
        self.utl.call('sshpass -p ' + self.sink_config_items['PASSWORD'] + ' ssh -o \"StrictHostKeyChecking no\" ' +
                      self.sink_config_items['USER'] +
                      '@' + self.sink_config_items['ROUTER_IP6'] + ' -t \"mkdir -p ' + self.sink_config_items[
                          'ROUTER_WKD'].rstrip('/') + '\"', shell=True)
        self.utl.call('sudo sshpass -p ' + self.sink_config_items[
            'PASSWORD'] + ' scp -o \"StrictHostKeyChecking no\" -r scripts ' + self.sink_config_items['USER'] +
                      '@\[' + self.sink_config_items['ROUTER_IP6'] + '\]:' + self.sink_config_items['ROUTER_WKD'],
                      shell=True)
        print ('Upload finished.')
        self.utl.call('sshpass -p ' + self.sink_config_items['PASSWORD'] + ' ssh -o \"StrictHostKeyChecking no\" ' +
                      self.sink_config_items['USER'] +
                      '@' + self.sink_config_items['ROUTER_IP6'] + ' -t \"cd ' + self.sink_config_items[
                          'ROUTER_WKD'].rstrip('/') +
                      '/scripts; echo \"Creating connections to clients.\"; ./create_conn.sh\"', shell=True)
        # Run the script from border router to start.
        self.utl.call(
            'sudo sshpass -p ' + self.sink_config_items['PASSWORD'] + ' ssh -o \"StrictHostKeyChecking no\" ' +
            self.sink_config_items['USER'] +
            '@' + self.sink_config_items['ROUTER_IP6'] + ' -t \"cd ' + self.sink_config_items['ROUTER_WKD'].rstrip(
                '/') +
            '/scripts; echo \"Starting router monitor.\"; ./start_router.sh; echo \"Router monitor is running.\"; bash -l\"',
            shell=True)

    def upload_to_clients(self, inet):
        """This function upload file/directory to remote client devices via IPv6 (6LoWPAN) or IPv4 network.
            It is recommended to use IPv4 to upload large files, while small file can be uploaded through IPv6.

        :param inet: IP version of the network.
        :type inet: str.
        """
        print ('Uploading files to clients via IPv' + inet + ' network')
        os.chdir('scripts')
        subprocess.call('./upload_ip' + inet + '.sh', shell=True)
        os.chdir('..')

    def collect_data(self, inet):
        """This function collects data from clients, border router and sink server via IPv6 (6LoWPAN) or IPv4 network.
            It is recommended to use IPv4 to collect large files, while small file can be uploaded through IPv6.

        :param inet: IP version of the network.
        :type inet: str.
        """
        print('Start to collect experiment data from clients, border router and sink server.')
        self.utl.call('cp scripts/collect_ip' + inet + '.sh .', shell=True)
        self.utl.call('./collect_ip' + inet + '.sh', shell=True)
        self.utl.call('rm ./collect_ip' + inet + '.sh', shell=True)

    def analyze(self):
        """This function analyzes the log data and outputs spreadsheet as report.
        """
        anal_logs = analysis.Analysis()
        print "===== Processing sink logs ====="
        sink_summary = anal_logs.analyze_sink([self.sink_config_items['SERVERIP'], self.sink_config_items['SERVERPORT'],
                                               self.sink_config_items['SINK_INTERFACE'], 'logs/sink'])
        print "===== Processing router logs ====="
        router_summary = anal_logs.analyze_router('logs/router')
        print "===== Processing client logs ====="
        client_summary = anal_logs.analyze_client('logs/clients')
        df_client = pd.DataFrame(client_summary, columns=['(1) Client Send', '(2) Client lowpan0', '(3) Client wpan0'],
                                 index=client_summary['Client IP'])
        df_router = pd.DataFrame(router_summary, columns=['(4) Router wpan0', '(5) Router lowpan0', '(6) Router eth0'],
                                 index=router_summary['Client IP'])
        df_sink = pd.DataFrame(sink_summary, columns=['(7) Sink Eth', '(8) Sink Rcvd', 'Packet Loss', 'Latency (ms)',
                                                      'Start', 'End', 'Running time (s)'],
                               index=sink_summary['Client IP'])
        print df_sink
        print '----------------------------------'
        print df_router
        print '----------------------------------'
        print df_client
        print '----------------------------------'
        df_result = pd.concat([df_client, df_router, df_sink], axis=1)
        df_result.sort_index(ascending=True, inplace=True)
        df_result.index.name = 'Client IP'
        print df_result
        print '----------------------------------'
        mean_row = df_result[['Packet Loss', 'Latency (ms)']].mean()
        df_mean = pd.DataFrame(data=mean_row).T
        df_mean = df_mean.reindex(columns=df_result.columns)
        print df_mean
        print '----------------------------------'
        df_final = df_result.append(df_mean)
        df_final.tail()
        df_final.index.name = 'Client IP'
        print df_final
        print '----------------------------------'
        # df_result = pd.concat([df_client, df_router, df_sink], axis=1)
        # df_result.sort_index(ascending=True, inplace=True)
        # df_result.index.name = 'Client IP'
        # # Calculate mean for packet loss and latency.
        # mean_row = df_result[['Packet Loss', 'Latency (ms)']].mean()
        # df_mean = pd.DataFrame(data=mean_row).T
        # df_mean = df_mean.reindex(columns=df_result.columns)
        # df_final = df_result.append(df_mean)
        # df_final.tail()
        # df_final.index.name = 'Client IP'
        # print '----------------------------------'
        # print df_final
        # print '----------------------------------'
        writer = pd.ExcelWriter('summary.xlsx', engine='xlsxwriter')
        df_final.to_excel(writer, sheet_name='Sheet1')
        writer.save()

    def stop(self, inet):
        """This function run the scripts to stop experiment, including clients, router and local server.
        """
        print ('Stopping experiment via IPv' + inet + ' network')
        os.chdir('scripts')
        subprocess.call('./stop_ip' + inet + '.sh', shell=True)
        os.chdir('..')
