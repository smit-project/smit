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
from smit import utils
import traceback
import time
from datetime import datetime
import signal
from multiprocessing import Process
import logging
import subprocess
import random


class SinkClientPlain(object):
    """
    This class implements a client which can connect and send messages to sink server via plaintext.
    This class needs a configuration file 'clien_expcnf' to configure experiment parameters.
    """
    seq = 0
    utl = utils.Utils()
    config = {'SERVERIP': '', 'SERVERPORT': '', 'TIMEZONE': '', 'SYNCTIME': 0, 'REFLOWPAN': 0,
              'SYSWAIT': 0, 'PAYLOADLEN': 0, 'DATE': '', 'SENDTIME': 0, 'SENDRATE': 0, 'DEVNUM': 0}
    clientcnf = 'client_expcnf'  # the path to configuration file for this client package
    package_path = ''  # the path to this pakcage
    send_logger = None  # a log handler for recording the information of sending messages.
    sock = 0
    addr = None
    is_first_time = 1  # indicate if it is an initial time synchronization.

    def __init__(self):
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        os.chdir(self.package_path)
        self.config = self.utl.read_config(self.clientcnf, self.config)

    def install_dependencies(self):
        """Install dependencies for experiment on a device.
        """
        self.utl.call('sudo apt-get -y --force-yes install ntp ntpdate', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install tcpdump', shell=True)
        self.utl.call('sudo apt-get -y --force-yes install sshpass', shell=True)

    def create_conn_log(self, dst_addr):
        """This function creates a connection log file which contains local network
            interface information and destination address.
        :param dst_addr: destination address (host, port)
        :type dst_addr: tuple
        """
        if os.path.exists('conn.log'):
            self.utl.call('sudo rm -f conn.log', shell=True)
            print 'Old connection log has been removed.'
        formatter = logging.Formatter(fmt='%(asctime)s\t\n%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        conn_logger = self.create_logger('Connection log.', 'conn.log', logging.INFO, formatter)
        p = subprocess.Popen('/sbin/ifconfig', stdout=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        if out is None:
            out = 'No output!'
        # get local ip for 6LoWPAN
        tmp_pos = out.find('lowpan0')
        end_pos = tmp_pos + out[tmp_pos:].find('  prefixlen 64  scopeid 0x0<global>')
        begin_pos = out[:end_pos].rfind('inet6 ')
        local_ip = out[(begin_pos + 6): end_pos].strip()
        # local_ip, netmask = host.split()[1].split('/')  # inet6 addr: ip/mask Scope:Global
        print ("local_ip: -> " + local_ip)
        out = out + '\nClient|' + str(local_ip)
        out = out + '\nSink|' + str(dst_addr[0]) + '.' + str(dst_addr[1])
        tail = '\n' + "#" * 40 + '\n'
        conn_log = out + tail
        conn_logger.info(conn_log)

    def create_logger(self, log_name, logfile, level, formatter=None):
        """Create and return a reference to a logger. This is used to create difference log files in different settings.

        :param log_name: the name of a log.
        :param logfile: the file name of the log.
        :param level: the log level.
        :param formatter: the format of log items.
        :type log_name: str.
        :type logfile: str.
        :type level: int.
        :type formatter: logging.Formatter
        """
        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        handler = logging.FileHandler(logfile)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def signal_handler(self, signum, frame):
        """This function handles message sending task.
        """
        # send data in some probability (decided from configuration file) per each sending request.
        # by default, every 100 milliseconds, it tries to send a message.
        sock = self.sock  # socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        packet_per_sec = float(self.config['SENDRATE']) / float(self.config['DEVNUM'])
        probability = int(packet_per_sec / (1.0 / float(self.config['SENDTIME'])) * 100)
        coin = random.randint(0, 99)
        if coin in range(0, probability):  # coin is in {0,1,...,probability}, then send a message, otherwise, ignore.
            timestamp = datetime.now().strftime('%H%M%S%f')[:-3]
            self.seq += 1
            # create payload
            seq_str = str(self.seq).zfill(8)
            other_len = int(self.config['PAYLOADLEN']) - len(seq_str) - len(timestamp)
            if other_len < 0:
                other_len = 0
            data = seq_str + '-' * other_len + timestamp
            if data == '' or data is None:
                self.send_logger.info('DATA ERRORS: the generated date is empty or None.')
            # print self.addr
            # local_ip = "fe80::cc1c:954d:e4e6:364f"
            # sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            # sock.bind((local_ip, 34311, 0, 6))
            sent = sock.sendto(data, self.addr)
            # sent = 1
            if sent == 0:
                self.send_logger.info('SENDING ERRORS: sent message length is ' + str(sent) + ' bytes.')
                raise RuntimeError('Socket connection broken.')
            else:
                self.send_logger.info('Sent message length: ' + str(sent) + ' | Message content: ' + data)

    def refresh(self, timer, cmd, logger):
        """Refresh net information periodically. If the parameter num is a negative number, the function will execute in
        endless mode.

        :param timer: a timer (in seconds) which specifies a period.
        :param cmd: the scheduled command to execute.
        :param logger: a handler to record log into a file.
        :type timer: long
        :type cmd: str.
        :type logger: Logger object.
        """
        try:
            while True:
                i = 0
                while i < 30:
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                    (out, err) = p.communicate()
                    if out is None:
                        out = 'No output!'
                    if err is None:
                        err = 'None.'
                    logger.info(out + '\nError (if any): ' + err + '\n=======================')
                    if out.find('No response.') == -1:
                        break
                    else:
                        i += 1
                time.sleep(float(timer))
        except KeyboardInterrupt:
            return

    def sync_time(self, timezone, server_addr, timer, logger):
        """Synchronize time with a specified server.
        :param timezone: local timezone.
        :param server_addr: server IP address.
        :param timer: a periodical time to do the time synchronization.
        :param logger: a handler to record log into a file.
        :type timezone: str.
        :type server_addr: str.
        :type timer: float
        :type logger: Logger object.
        """
        try:
            while True:
                print ('Time synchronizing...')
                if self.is_first_time == 1:
                    self.utl.call('sudo date --set=\'' + self.config['DATE'] + '\'', shell=True)
                    self.is_first_time = 0
                if not os.path.exists('/usr/share/zoneinfo/' + timezone):
                    print('Error: timezone is invalid.')
                    return
                self.utl.call('timedatectl set-timezone ' + timezone, shell=True)
                p = subprocess.Popen('sudo ntpdate -u ' + server_addr, stdout=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                if err is None:
                    err = 'None.'
                logger.info(out + '\nError (if any): ' + err + '\n=======================')
                print ('Time synchronization finished.')
                time.sleep(timer)
        except KeyboardInterrupt:
            return

    def run_tcpdump(self, tcpdump_cmd):
        """Run tcpdump by using the given command.

        :param tcpdump_cmd: a command to run tcpdump.
        :type tcpdump_cmd: str.
        """
        try:
            subprocess.check_call(tcpdump_cmd, shell=True)
        except KeyboardInterrupt:
            return
        except:
            raise

    def get_scope_id_inet6(self, addr):
        """This function returns the scope id of a given lladdr if the address exists.

        :param addr: IPv6 address
        :return: int. scope id of interface.
        """
        scope_id = -1
        try:
            full_addr = self.expand_address_inet6(addr)
            key = full_addr.replace(':', '')
            with open('/proc/net/if_inet6', 'r') as ifaces:
                for line in ifaces:
                    if line.lower().find(key.lower()) != -1:  # found the interface
                        scope_id = int(line.split()[1])
                        break
            return scope_id
        except:
            raise

    def expand_address_inet6(self, addr):
        """This function expand an IPv6 address to a full description.

        :param addr: an IPv6 address

        Return:
                str. - a full IPv6 address.
        """
        try:
            prefix, suffix = addr.strip().split('::')
            num_items = str(prefix).count(':') + str(suffix).count(':')
            fill_items = 7 - num_items  # calculate the items missed in given ip address
            items = prefix.split(':')
            for index, item in enumerate(items):
                if len(item) < 4:
                    items[index] = item.zfill(4)
                elif len(item) > 4:
                    raise ValueError('Passed IPv6 address is invalid.')
            prefix = ':'.join(items)
            items = suffix.split(':')
            for index, item in enumerate(items):
                if len(item) < 4:
                    items[index] = item.zfill(4)
                elif len(item) > 4:
                    raise ValueError('Passed IPv6 address is invalid.')
            suffix = ':'.join(items)
            prefix += ':'
            for i in range(0, fill_items - 1):
                prefix += '0000:'
                i += 1
            return prefix + suffix
        except:
            raise ValueError('Passed IPv6 address is invalid.')

    def start(self):
        """This function start a client which can interact with a sink server via plaintext.
            This function will start sub-processes to log status, synchronize time and refresh network.
        """
        print ('Starting client ...')
        try:
            print ('Initializing program ...')
            # create a process to refresh 6LoWPAN connection periodically.
            # if REFLOWPAN <= 0, disable the refresh process.
            if int(self.config['REFLOWPAN']) > 0:
                formatter = logging.Formatter(fmt='%(asctime)s\n\t%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
                rf_logger = self.create_logger('Connection refreshing log', 'rs.log', logging.INFO, formatter)
                rf = Process(target=self.refresh,
                             args=(float(self.config['REFLOWPAN']), 'sudo rdisc6 lowpan0', rf_logger,))
                rf.start()
            # create a process to synchronize time periodically.
            # if SYNCTIME <= 0, disable the time synchronization.
            if int(self.config['SYNCTIME']) > 0:
                formatter = logging.Formatter(fmt='%(asctime)s\n\t%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
                sync_logger = self.create_logger('Time synchronization log.', 'sync.log', logging.INFO, formatter)
                sync = Process(target=self.sync_time, args=(
                    self.config['TIMEZONE'], self.config['SERVERIP'], float(self.config['SYNCTIME']), sync_logger,))
                sync.start()
            # create a process to run tcpdump
            tcpdump_lowpan = Process(target=self.run_tcpdump,
                                     args=('sudo nohup tcpdump -i lowpan0 -ttttnnvvS -w lowpan0.log &',))
            tcpdump_lowpan.start()
            tcpdump_wpan = Process(target=self.run_tcpdump,
                                   args=('sudo nohup tcpdump -i wpan0 -ttttnnvvS -w wpan0.log &',))
            tcpdump_wpan.start()
            time.sleep(15)  # wait for initial time synchronization
            print ('Program initialization finished.')

            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            host = self.config['SERVERIP']
            port = int(self.config['SERVERPORT'])
            print ('HOST: ' + host)
            print ('PORT: %d' % port)

            # get local ip for 6LoWPAN
            p = subprocess.Popen('/sbin/ifconfig', stdout=subprocess.PIPE, shell=True)
            (out, err) = p.communicate()
            if out is None:
                out = 'No output!'

            tmp_pos = out.find('lowpan0')
            end_pos = tmp_pos + out[tmp_pos:].find('  prefixlen 64  scopeid 0x20<link>')
            begin_pos = out[:end_pos].rfind('inet6 ')
            local_ip = out[(begin_pos + 5): end_pos].strip()
            print ("local_ip: [" + local_ip + "]")
            # local_ip = "fe80::d9eb:c371:783f:f22"
            # local_ip = "fe80::cc1c:954d:e4e6:364f"
            scope_id = self.get_scope_id_inet6(local_ip)
            print ('Scope id: %d ' % scope_id)
            # self.dw.connect((host, int(port), 0, scope_id))

            # self.sock.bind(('', 34311, 0, scope_id))
            # self.sock.bind((local_ip, 34311, 0, scope_id))
            self.sock.sendto('start', (host, int(port), 0, scope_id))
            # self.sock.bind((local_ip, 34311, 0, scope_id))
            print ('Sent')
            # Connect to sink with retransmission enabled, that is requiring acknowledgement.
            while True:
                try:
                    self.sock.settimeout(2.0)
                    print ('Going to receive...')
                    data, self.addr = self.sock.recvfrom(1024)
                    print ('Received!')
                    self.create_conn_log(self.addr)
                    break
                except socket.timeout:
                    self.sock.sendto('start', (host, port, 0, scope_id))
            # wait a while for other devices to start the experiment.
            print ('Wait ' + self.config['SYSWAIT'] + ' seconds to start the experiment.')
            time.sleep(float(self.config['SYSWAIT']))
            print ('Start to send packages.')

            # Create a logger for recording sending information.
            formatter = logging.Formatter(fmt='%(asctime)s\t%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
            self.send_logger = self.create_logger('Sending information log.', 'send.log', logging.INFO, formatter)
            signal.signal(signal.SIGALRM, self.signal_handler)
            signal.setitimer(signal.ITIMER_REAL, float(self.config['SENDTIME']), float(self.config['SENDTIME']))
            # sleep main function to let signal handlers execute
            while True:
                time.sleep(1000)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print (e)


if __name__ == '__main__':
    client = SinkClientPlain()
    client.install_dependencies()
    client.start()
