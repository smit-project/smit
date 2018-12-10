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

from datetime import datetime
import os
import sys
import subprocess

sys.path.insert(0, '../../')
sys.path.insert(0, '../../../')
from smit import utils


class Analysis(object):
    """Provide functions to read, analyze and generate summary according to the data collection
        This class is used to analyze sink, clients and border router.
    """

    sink_data = {'LogTime': [], 'Sequence': [], 'Message': [], 'SentTimestamp': [], 'RcvdTimeStamp': [], 'TimeDiff': [],
                 'SentPakcets': 0, 'RcvdPackets': 0}
    sink_summary = {'Client IP': [], '(7) Sink Eth': [], '(8) Sink Rcvd': [], 'Packet Loss': [], 'Latency (ms)': [],
                    'Start': [], 'End': [], 'Running time (s)': [], 'Client sent': [], }
    router_summary = {'Client IP': [], '(4) Router wpan0': [], '(5) Router lowpan0': [], '(6) Router eth0': []}
    client_summary = {'Client IP': [], '(1) Client Send': [], '(2) Client lowpan0': [], '(3) Client wpan0': []}
    run_time = []  # store the begin,end time of client program. this is a list of tuple (client ip, begin_time,
                   # end time)
    client_info = []  # store client connection information, this is a list of tuple (client ip, client port,
                      # sink ip, sink port)
    router_mac = ''
    utl = utils.Utils()

    def __init__(self):
        """Constructor initializes variables
        """

    def read_sink_data(self, file):
        """Read a formatted file line by line. The format: Date Time ClientID SequenceNum MessagePld Timestamp ConnInfo
        :param file: a file name.
        :type file: str.
        """
        try:
            with open(file) as s_file:
                for num, line in enumerate(s_file, 1):
                    words = str(line).split()
                    self.sink_data['LogTime'].append(words[0] + ' ' + words[1])
                    self.sink_data['Sequence'].append(words[2])
                    self.sink_data['Message'].append(words[3])
                    self.sink_data['SentTimestamp'].append(words[4])
                    self.sink_data['RcvdTimeStamp'].append(words[5])
                    self.sink_data['TimeDiff'].append(self.time_diff(words[4], words[5]))
                    self.sink_data['RcvdPackets'] = num
                    self.sink_data['SentPackets'] = words[2]
                    if num == 1:  # Get the client connection information.
                        info = words[6].split('|')  # client_info format: client|ip.port|sink|ip.port
                        client_ip, client_port = info[1].rsplit('.', 1)
                        sink_ip, sink_port = info[3].rsplit('.', 1)
                        if self.client_info.count((client_ip, client_port, sink_ip, sink_port)) == 0:
                            self.client_info.append((client_ip, client_port, sink_ip, sink_port))
        except IOError:
            print ('ERROR: cannot read the file: \"' + file + '\".')
            return {}

    def get_sink_data(self):
        """Get the data stored in the data storage.
        """
        return self.sink_data

    def time_diff(self, time_old, time_new):
        """Return (absolute) time difference, in milliseconds, between two timestamp.
        :param time_old: a timestamp in format 'HHMMSSXXX'.
        :param time_old: a timestamp in format 'HHMMSSXXX'.
        :type time_old: str.
        :type time_new: str.
        """
        begin = datetime.strptime(time_old, '%H%M%S%f')
        after = datetime.strptime(time_new, '%H%M%S%f')
        if begin > after:
            temp = begin
            begin = after
            after = temp
        difference = after - begin
        return difference.microseconds / 1000

    def get_latency(self):
        """Return the average latency (in milliseconds) of the received packets based on the dataset from log file.

        :return:
        """
        time_diff = 0
        for item in self.sink_data['TimeDiff']:
            time_diff += int(item)

        return float(time_diff) / self.sink_data['RcvdPackets']

    def clear_sink_alydata(self):
        """Reset dataset and other stateful parameters for sink log analysis.

        """
        self.sink_data = {'LogTime': [], 'Sequence': [], 'Message': [], 'SentTimestamp': [], 'RcvdTimeStamp': [],
                          'TimeDiff': [],
                          'SentPakcets': 0, 'RcvdPackets': 0}

    def analyze_sink(self, sink_info):
        """This function analysis sink server logs and output a summary of logs.

        :param sink_info: list of sink server information, including [ip, port, interface, log_path].
        :type sink_info: list

        Return:
                A summary of analyzed data. The returned values are in a dictionary.
        """
        # analysis = Analysis()
        server_ip = sink_info[0]
        server_port = sink_info[1]
        interface = sink_info[2]
        log_path = sink_info[3]
        cur_path = os.path.abspath(os.path.curdir)
        os.chdir(log_path)

        # Analyze logs in exp directory which contains the application layer logs from clients to sink server.
        for root, dirs, filenames in os.walk('exp'):
            for filename in filenames:
                os.chdir(root)
                self.read_sink_data(filename)
                data_set = self.get_sink_data()
                loss_rate = 1 - float(data_set['RcvdPackets']) / int(str(data_set['SentPackets']).lstrip('0'))

                # print statistic summary
                print ('=============================================================')
                print ('Log file: ' + filename)
                print ('Total sent packets: ' + str(data_set['SentPackets']).lstrip('0'))
                print ('Received packets: ' + str(data_set['RcvdPackets']))
                print ('Packet Loss: ' + str(loss_rate))
                print ('Average latency: ' + str(self.get_latency()))
                start = data_set['LogTime'][0].split()
                end = data_set['LogTime'][-1].split()
                begin = start[0] + ' ' + start[1]
                after = end[0] + ' ' + end[1]
                begin = datetime.strptime(begin, '%d/%m/%Y %H:%M:%S')
                after = datetime.strptime(after, '%d/%m/%Y %H:%M:%S')
                difference = after - begin
                self.sink_summary['Packet Loss'].append(loss_rate)
                self.sink_summary['Client sent'].append(int(str(data_set['SentPackets']).lstrip('0')))
                self.sink_summary['(8) Sink Rcvd'].append(int(str(data_set['RcvdPackets'])))
                self.sink_summary['Latency (ms)'].append(float(self.get_latency()))
                self.sink_summary['Client IP'].append(filename[:-21])
                self.sink_summary['Start'].append(start[0] + ' ' + start[1])
                self.sink_summary['End'].append(end[0] + ' ' + end[1])
                self.sink_summary['Running time (s)'].append(int(difference.days * 86400 + difference.seconds))
                self.run_time.append((filename[:-21], start[0] + ' ' + start[1], end[0] + ' ' + end[
                    1]))  # add client ip, endtime to list. only takes time w/o date.
                self.clear_sink_alydata()
                os.chdir(cur_path + '/logs/sink')  # change back to package directory
        # Analyze logs of Ethernet interface of sink server.
        for client in self.sink_summary['Client IP']:
            dst_port = server_port
            for info in self.client_info:  # info = (client_ip, client_port, sink_ip, sink_port)
                if client == info[0]:
                    dst_port = info[3]
                    break
            print 'Sink analysis for client IP: ' + str(client)
            begin_time, end_time = self.get_run_time(client)
            begin_time = begin_time.replace(':', '\:')
            end_time = end_time.replace(':', '\:')
            dup = 0  # multiple presence lines
            count = 0
            self.sink_summary['(7) Sink Eth'].append(count)
        os.chdir(cur_path)

        return self.sink_summary

    def get_run_time(self, ip):
        """This function finds the running time period for a specific ip.
            It returns a tuple (begin_time, end_time) corresponds to the given parameter ip.
            If any of time was not found, empty string '' will be returned.
            The return time format: %Y-%m-%d %H:%M:%S

        :param ip: ip address

        Return:

                tuple - (begin_time, end_time)
        """
        begin_time = ''
        end_time = ''
        for item in self.run_time:
            if item[0] == ip:
                begin_time = item[1]  # format: DD/MM/YYY HH:MM:SS
                end_time = item[2]  # format: DD/MM/YYYY HH:MM:SS
                # convert to format: YYYY-MM-DD HH:MM:SS
                d = datetime.strptime(begin_time, '%d/%m/%Y %H:%M:%S')
                begin_time = d.strftime('%Y-%m-%d %H:%M:%S')
                d = datetime.strptime(end_time, '%d/%m/%Y %H:%M:%S')
                end_time = d.strftime('%Y-%m-%d %H:%M:%S')
        return begin_time, end_time

    def ip6_to_mac(self, ip):
        """This function convert an IPv6 address to the mac address.
            This function can also convert a link-layer address to mac address.

        :param ip: an IPv6 address.
        :type ip: str

        Return:
                str - mac address.
        """
        items = ip.rsplit(':', 3)
        mac = ''
        if len(items) == 4:  # generate link-layer address and add commands to the script
            for i in range(1, 4):
                part = items[i].zfill(4)
                mac += part[0:2] + ':' + part[2:4] + ':'
            mac = mac.strip(':')
        else:
            raise IOError("IP address: " + ip + " is invalid.")
        return mac

    def analyze_router(self, logdir, client_info=None):
        """This function analyzes border router logs and output a summary of data.

        :param client_info: information to be used in the analysis, including a list of tuple (client_ip, client_port,
                            sink_ip, sink_port)
        :param logdir: path to the router log directory.
        :type client_info: list
        :type logdir: str

        Return:
                dict - a summary of logs.
        """
        if client_info is None:
            client_info = self.client_info
        if not os.path.exists(logdir):
            raise IOError("Log directory: " + logdir + " does not exist.")
        # Get the router mac from router.info
        cwd = os.getcwd()
        os.chdir(logdir)
        with open('router.info', 'r') as router_file:
            started = False
            for (num, line) in enumerate(router_file, 1):
                if str(line).find('lowpan0') != -1:  # lowpan information started.
                    started = True
                if started:
                    if str(line).find('Scope:Link') != -1:  # found the line contain lladdr.
                        pos_begin = str(line).find('fe80::')  # begin position of lladdr.
                        pos_end = str(line).find('/', pos_begin)  # end position of lladdr.
                        self.router_mac = self.ip6_to_mac(line[pos_begin: pos_end])
                        break
        print ('Preparing log files.')
        subprocess.call("sudo tcpdump -r wpan0.log -ttttnnvvS > read_wpan0.log", shell=True)
        # Analyze router logs for every client
        for client in client_info:
            client_ip = client[0]
            client_port = client[1]
            sink_ip = client[2]
            sink_port = client[3]
            self.router_summary['Client IP'].append(client_ip)
            print 'Analyzing router logs for Client IP: ' + str(client_ip)
            # Analyze lowpan0 log
            begin_time, end_time = self.get_run_time(client_ip)
            begin_time = begin_time.replace(':', '\:')
            end_time = end_time.replace(':', '\:')
            dup = 0  # multiple presence lines
            count = 0
            if begin_time != '' and end_time != '':  # begin/end time presented, count more precisely.
                proc = subprocess.Popen(
                    "sudo tcpdump -r lowpan0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | grep -c -e \'" + end_time.replace('\:', ':') +
                    "'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                dup = int(out.strip())
                proc = subprocess.Popen(
                    "sudo tcpdump -r lowpan0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | sed -n -e '/" + begin_time + "/,/" + end_time +
                    "/p\' | wc -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                count = int(out.strip())
            if count == 0:  # begin/end time does not present or not record found, trying to count as usual
                proc = subprocess.Popen(
                    "sudo tcpdump -r lowpan0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | wc -l",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                count = int(out.strip())
            if dup > 1:  # there are multiple lines with the same end_time point.
                count = count + dup - 1
            self.router_summary['(5) Router lowpan0'].append(count)
            # Analyze eth0 log
            begin_time, end_time = self.get_run_time(client_ip)
            begin_time = begin_time.replace(':', '\:')
            end_time = end_time.replace(':', '\:')
            dup = 0  # multiple presense lines
            count = 0
            if begin_time != '' and end_time != '':  # begin/end time presented, count more precisely.
                proc = subprocess.Popen(
                    "sudo tcpdump -r eth0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | grep -c -e \'" + end_time.replace('\:', ':') +
                    "'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                dup = int(out.strip())
                proc = subprocess.Popen(
                    "sudo tcpdump -r eth0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | sed -n -e '/" + begin_time + "/,/" + end_time +
                    "/p\' | wc -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                count = int(out.strip())
            if count == 0:  # begin/end time does not present, count as usual
                proc = subprocess.Popen(
                    "sudo tcpdump -r eth0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | wc -l",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                count = int(out.strip())
            if dup > 1:  # there are multiple lines with the same end_time point.
                count = count + dup - 1
            self.router_summary['(6) Router eth0'].append(count)
            # Analyze wpan0 log
            begin_time, end_time = self.get_run_time(client_ip)
            begin_time = begin_time.replace(':', '\:')
            end_time = end_time.replace(':', '\:')
            dup = 0  # multiple presense lines
            count = 0
            if begin_time != '' and end_time != '':  # begin/end time presented, count more precisely.
                proc = subprocess.Popen("grep read_wpan0.log -e \'" + self.router_mac + " <\' | grep -e \'" +
                                        self.ip6_to_mac(client_ip) + "\' | grep -c -e \'" +
                                        end_time.replace('\:', ':') + "'",
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                dup = int(out.strip())
                proc = subprocess.Popen("sed -n -e '/" + begin_time + "/,/" + end_time + "/p\' read_wpan0.log | \
                                                    grep -e \'" + self.router_mac + " <\' | grep -e \'" +
                                        self.ip6_to_mac(client_ip) + "\' | wc -l",
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                count = int(out.strip())
            if count == 0:  # begin/end time does not present or record not found, trying to count as usual
                proc = subprocess.Popen("grep read_wpan0.log -e \'" + self.router_mac + " <\' | grep -e \'" +
                                        self.ip6_to_mac(client_ip) + "\' | wc -l", stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                count = int(out.strip())
            if dup > 1:  # there are multiple lines with the same end_time point.
                count = count + dup - 1
            self.router_summary['(4) Router wpan0'].append(count)
        os.chdir(cwd)
        return self.router_summary

    def analyze_client(self, log_path):
        """This function analyze client logs and output a summary of data.

        :param log_path: directory of client log files

        Return:
                dict - a summary of logs.
        """
        if not os.path.exists(log_path):
            raise IOError("Log directory: " + log_path + " does not exist.")
        cur_path = os.path.abspath(os.path.curdir)
        os.chdir(log_path)
        log_dirs = []
        for root, dirs, files in os.walk('.'):
            log_dirs = dirs
            break
        # Walk though the log directory and analyze data in each subdirectory.
        for path in log_dirs:
            os.chdir(path)
            # get from conn.log for client ip, sink ip and sink port
            client_ip = ''
            sink_ip = ''
            sink_port = ''
            with open('conn.log', 'r') as c_file:
                for (num, line) in enumerate(c_file, 1):
                    if str(line).find('Client') != -1:  # line for client ip.
                        client_ip = line.strip().split('|')[1]
                    if line.find('Sink') != -1:  # line for sink|ip.port
                        sink_ip, sink_port = line.strip().split('|')[1].rsplit('.', 1)

            print 'Analyzing logs for Client IP: ' + str(client_ip)
            # proceed send.log
            p = subprocess.Popen("wc -l < send.log", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (out, err) = p.communicate()
            self.client_summary['(1) Client Send'].append(int(out.strip()))
            # proceed lowpan0.log
            begin_time, end_time = self.get_run_time(client_ip)
            begin_time = begin_time.replace(':', '\:')
            end_time = end_time.replace(':', '\:')
            dup = 0  # multiple presence lines
            count = 0
            if begin_time != '' and end_time != '':  # begin/end time presented, ount more precisely.
                p = subprocess.Popen(
                    "sudo tcpdump -r lowpan0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | grep -c -e \'" + end_time.replace('\:',
                                                                                    ':') +
                    "'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                dup = int(out.strip())
                p = subprocess.Popen(
                    "sudo tcpdump -r lowpan0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | sed -n -e '/" + begin_time + "/,/" + end_time +
                    "/p\' | wc -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                count = int(out.strip())
            if count == 0:  # begin/end time does not present or record not found, trying to count as usual
                p = subprocess.Popen(
                    "sudo tcpdump -r lowpan0.log -ttttnnvvS dst " + sink_ip + " and dst port " + sink_port +
                    " and src " + client_ip + " | wc -l",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                count = int(out.strip())
            if dup > 1:  # there are multiple lines with the same end_time point.
                count = count + dup - 1
            self.client_summary['(2) Client lowpan0'].append(count)
            # proceed wpan0.log
            begin_time, end_time = self.get_run_time(client_ip)
            begin_time = begin_time.replace(':', '\:')
            end_time = end_time.replace(':', '\:')
            dup = 0  # multiple presense lines
            count = 0
            subprocess.call('sudo tcpdump -r wpan0.log -ttttnnvvS > read_wpan0.log', shell=True)
            if begin_time != '' and end_time != '':  # begin/end time presented, count more precisely.
                p = subprocess.Popen("grep read_wpan0.log -e \'" + self.router_mac + " <\' | grep -e \'" +
                                     self.ip6_to_mac(client_ip) + "\' | grep -c -e \'" + end_time.replace('\:', ':') +
                                     "'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                dup = int(out.strip())
                p = subprocess.Popen("sed -n -e '/" + begin_time + "/,/" + end_time + "/p\' read_wpan0.log | \
                                        grep -e \'" + self.router_mac + " <\' | grep -e \'" +
                                     self.ip6_to_mac(client_ip) + "\' | wc -l",
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                count = int(out.strip())
            if count == 0:  # begin/end time does not present, count as usual
                p = subprocess.Popen("grep read_wpan0.log -e \'" + self.router_mac + " <\' | grep -e \'" +
                                     self.ip6_to_mac(client_ip) + "\' | wc -l", stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                count = int(out.strip())
            if dup > 1:  # there are multiple lines with the same end_time point.
                count = count + dup - 1
            self.client_summary['(3) Client wpan0'].append(count)
            os.chdir('..')
        os.chdir(cur_path)
        return self.client_summary
