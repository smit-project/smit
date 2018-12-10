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
import random
import os
import stat
import errno
import re


class Utils(object):
    """Common functions
    """

    def lookup(self, keyword, filename):
        """Return the line which contains the keyword.

            :param keyword: the keyword.
            :param filename: the file name.
            :type keyword: str.
            :type filename: str.

            Returns:
               str. -- The return value::

                   '' -- keyword not found.
                   line -- the first line which contains the keyword in the file

            Example:

            >>> print lookup("def enable", "deploypi.py")
            def enable_radio(self):
        """
        if not os.path.isfile(file):
            print('File: ' + filename + ' does not exist.')
            return ''
        if keyword == '':
            return ''

        with open(filename) as s_file:
            for num, line in enumerate(s_file, 1):
                if keyword in line:
                    return line
        return ''

    def gen_mac(self):
        """Generate a random MAC address for the experimental environment

        Returns:

            str. -- mac address.

        Note:

            The generated MAC address is with prefix "18:C0:FF:EE"
        """
        mac = [0X18,
               0xC0,
               0xFF,
               0xEE,
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02X" % x, mac))

    def check_device_exist(self, dev_path):
        """Check whether a device exist.

        :param dev_path: device path.
        :type dev_path: str.

        Returns:
            bool -- The return value::

                True -- device exists.
                False --  device not found.

        """
        dev_path = os.path.normpath(dev_path)
        try:
            return stat.S_ISBLK(os.stat(dev_path).st_mode)
        except Exception as e:
            print (e)
            return False

    def call(self, *args, **keywords):
        """Wrapper function for call in subprocess
        """
        return subprocess.call(*args, **keywords)

    def check_call(self, *args, **keywords):
        """Wrapper function for check_call in subprocess
        """
        return subprocess.check_call(*args, **keywords)

    def makedir(self, path):
        """Create a directory and its parent directories if necessary.
        :param path: path of directory.
        :type path: str.
        """
        try:
            os.makedirs(os.path.expanduser(path))
        except OSError as ose:
            if ose.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def write_file(self, content, *args, **keywords):
        """Write a string to the file

        :param content: content to write into a file.
        :type content: str.
        """
        try:
            f = open(*args, **keywords)
            f.write(content)
        except IOError:
            print ('ERROR: Cannot open the file or write data.')
            raise

        f.close()

    def read_file(self, *args, **keywords):
        """Read a file and return the file as a string.

        Return:
            str. -- File content.
        """
        content = ''
        try:
            f = open(*args, **keywords)
            content = f.read()
            f.close()
        except IOError:
            print ('ERROR: Cannot open the file or read data.')
            raise
        finally:
            return content

    def get_dev_format(self, dev):
        """Return the device format

        :param dev: a device path
        :type dev: str.

        Returns:
            str. -- device format, return '' if the device does not exist.

        Note::

            The input device path must be in format e.g., '/dev/sdb2'. The input e.g., '/dev/sdb' is invalid and will
            return ''.
        """
        dev = os.path.normpath(dev)
        if not os.path.exists(dev):
            return ''

        p = subprocess.Popen('sudo blkid ' + dev, stdout=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        begin = out.rfind('TYPE=\"') + len('TYPE=\"')
        end = out.find('\"', begin)
        if end < begin:
            return ''
        else:
            return out[begin:end]

    def delete_lines(self, filename, substring, start, end, ignore_spaces=False):
        """Delete lines (in file) which contain the specified substring.

        :param filename: a file.
        :param substring: a specified substring for deleting lines.
        :param start: start position of a line in file
        :param end: end position of a line in file
        :param ignore_spaces: ignore spaces at the start and end of a line
        :type filename: str.
        :type substring: str.
        :type start: int.
        :type end: int.
        :type ignore_spaces: bool.

        Returns:
            int.    -- The code value::

                   -1 -- error found
                other -- number of deleted lines
        """
        del_lines = 0
        try:
            f = open(filename, 'r')
            lines = f.readlines()
        except Exception as e:
            del_lines = -1
            print ('ERROR: cannot open or read the file: \"' + filename + '\".')
            print (e)
            return del_lines

        f.close()

        f = open(filename, 'w')
        for line in lines:
            tmp = str(line)
            if ignore_spaces and tmp.strip().find(substring, start, end) == -1:
                f.write(line)
            elif not ignore_spaces and tmp.find(substring, start, end) == -1:
                f.write(line)
            else:
                del_lines += 1
        f.close()
        return del_lines

    def update_config(self, filename, keywords):
        """

        :param filename:
        :param keywords:
        :return:
        """
        try:
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
            i = 0
            for line in lines:
                words = line.split('=')
                if words is not None and len(words) > 1:
                    key = str(words[0]).strip()
                    key = key.strip('#')  # enable keyword if it was disabled
                    if key in keywords:  # if keyword is legal
                        # if (words[1].startswith('\"') and words[1].endswith('\"')): # value was legal in
                        # configuration file, this is a check.
                        value = keywords.get(key, '')  # No value given, don't update
                        if value != '':
                            lines[i] = key + ' = \"' + value + '\"\n'
                i += 1
            f = open(filename, 'w')
            f.writelines(lines)
            f.close()
        except IOError:
            print ('ERROR: cannot read the file: \"' + filename + '\".')

    def read_config(self, filename, keywords):
        """Read a configuration file with customized recognizable keywords

        :param filename: configuration file
        :param keywords: keywords
        :type filename: str.
        :type keywords: dict.

        Return:
            dict. -- The dictionary contains keys and values.

        Note:
            Only the last matching [key:value] is stored for different keys.

        ::

            Reading format: Keyword="value"
        """
        keywords_dict = {}
        try:
            with open(filename) as s_file:
                for num, line in enumerate(s_file, 1):
                    words = line.split('=')
                    if words is not None and len(words) > 1:
                        key = str(words[0]).strip()
                        value = str(words[1]).strip()
                        for kw in keywords:
                            if key == kw:
                                begin = value.find('\"') + 1
                                end = value.find('\"', begin)
                                if end >= begin:
                                    keywords_dict[kw] = value[begin:end]
                                else:
                                    keywords_dict[kw] = ''
                                break
            for kw in keywords:
                if keywords_dict.get(kw, '') == '':
                    keywords_dict[kw] = ''
        except IOError:
            print ('ERROR: cannot read the file: \"' + filename + '\".')
            return {}
        return keywords_dict

    def read_config_v2(self, filename, keywords):
        """Read a configuration file with customized recognizable keywords. This function is specifically for the format:
           key = value

        :param filename: configuration file
        :param keywords: keywords
        :type filename: str.
        :type keywords: dict.

        Return:
            dict. -- The dictionary contains keys and values.

        Note:
            Only the last matching [key:value] is stored for different keys.

        ::

            Reading format: Keyword = value
        """
        keywrds_dict = {}
        try:
            with open(filename) as s_file:
                for num, line in enumerate(s_file, 1):
                    words = line.split('=')
                    if words is not None and len(words) > 1:
                        key = str(words[0]).strip()
                        value = str(words[1]).strip()
                        for kw in keywords:
                            if key == kw:
                                begin = 0
                                end = value.find('#', begin)
                                if end >= begin:
                                    keywrds_dict[kw] = value[begin:end]
                                else:
                                    keywrds_dict[kw] = value.strip()
                                break
            for kw in keywords:
                if keywrds_dict.get(kw, '') == '':
                    keywrds_dict[kw] = ''
        except IOError:
            print ('ERROR: cannot read the file: \"' + filename + '\".')
            return {}
        return keywrds_dict

    def insert_net_interface(self, content, filename='/etc/network/interfaces'):
        """Insert network interface settings to the beginning of the file for network configuration.

        :param content: some settings being inserted to the file.
        :param filename: the destination file.
        :type content: list.
        :type filename: string.

        Note:
            This function deletes the first block formatted as below

        ::

            ### Begin SMIT Config ###
                ...
            ### End SMIT Config ###
        """
        pos = filename.rfind('/')
        if pos > -1:
            path = filename[0:pos]
            if not os.path.exists(path):
                print('ERROR: parent directory of the target file \"' + filename[pos + 1:] + '\" does not exist.')
                return

        f = open(filename, 'r')
        lines = f.readlines()
        f.close()

        # delete old configuration and add new configuration at the beginning of the file.
        begin = -1
        end = -1
        for line in lines:
            if begin == -1 and line.find('Begin SMIT Config') != -1:
                begin = lines.index(line)
            elif end == -1 and line.find('End SMIT Config') != -1:
                end = lines.index(line)
            if begin != -1 and end != -1:
                break
        if end > begin >= 0:
            i = 0
            while i < end - begin + 1:
                lines.pop(begin)
                i += 1
        for line in lines:
            pos = -1
            if line.strip().find('#') != 0 and line.strip() != '':
                pos = lines.index(line)
                break
        if pos == -1:
            pos = len(lines)
        for c in content:
            lines.insert(pos, c)
            pos += 1

        f = open(filename, 'w')
        for line in lines:
            f.write(line)
        f.close()

    def insert_lines(self, content, filename, keyword):
        """Insert lines to a file in the position spcified by keyword.

        :param content: some lines to inserted.
        :param filename: the destination file name.
        :param keyword: a keyword to search.
        :type content: list.
        :type filename: string.
        :type keyword: string.
        """
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            if line.find(keyword) != -1:
                pos = lines.index(line)
                for c in content:
                    lines.insert(pos, c)
                    pos += 1
                break
        f = open(filename, 'w')
        for line in lines:
            f.write(line)
        f.close()
