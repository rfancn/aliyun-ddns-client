#!/usr/bin/env python
# coding=utf-8
"""
 Copyright (C) 2010-2013, Ryan Fan <reg_info@126.com>
 Modified by Guorui Yu.

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Library General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""
import socket
from socket import error as socket_error
import sys
from datetime import datetime
import uuid
import json
import re

import requests


class DDNSUtils(object):
    # To support "*" subdomain definition,
    # We need generate a non-exist subdomain name
    # Here we generate a random UUID for that
    #fake_subdomain = ''.join([random.choice(string.lowercase) for i in xrange(12)])
    RANDOM_UUID = uuid.uuid4().hex 

    """
    Utils class wrapper
    """
    @staticmethod
    def err(msg):
        """
        Output error message
        :param msg: Message to be displayed
        """
        sys.stderr.write("{0}\t[ERROR]\t{1}\n".format(DDNSUtils.get_current_time(), msg))

    @staticmethod
    def info(msg):
        """
        Output informative message
        :param msg: Message to be displayed
        """
        sys.stdout.write("{0}\t[INFO]\t{1}\n".format(DDNSUtils.get_current_time(), msg))

    @staticmethod
    def err_and_exit(msg):
        """
        Output error message and exit
        :param msg: Message to be displayed
        """
        sys.stderr.write("{0}\t[ERROR]\t{1}\n".format(DDNSUtils.get_current_time(), msg))
        sys.exit(1)

    @classmethod
    def get_current_public_ip(cls):
        """
        Get current public IP

        @return  IP address or None
        """
        try:
            ret = requests.get("http://httpbin.org/ip")
        except requests.RequestException as ex:
            cls.err("network problem:{0}".format(ex))
            return None

        if ret.status_code != requests.codes.ok:
            cls.err("Failed to get current public IP: {0}\n{1}" \
                    .format(ret.status_code, ret.content))
            return None

        return ret.json()['origin']

    @classmethod
    def get_current_public_ipv6(cls):
        """
        Get current IPv6 address
        :return: IPv6 address or None
        """
        try:
            ret = requests.get("http://v6.ipv6-test.com/api/myip.php")
        except requests.RequestException as ex:
            cls.err("network problem:{0}".format(ex))
            return None
        return ret.text

    @classmethod
    def is_private_address(cls, addr):
        """
        Check if the address is private address.
        :param addr: str
        :return: bool
        """
        priv_lo = re.compile("^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        priv_24 = re.compile("^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        priv_20 = re.compile("^192\.168\.\d{1,3}.\d{1,3}$")
        priv_16 = re.compile("^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$")
        priv_v6 = re.compile("^fe80")
        return any([priv_16.match(addr), priv_20.match(addr), priv_24.match(addr),
                    priv_lo.match(addr), priv_v6.match(addr)])

    @classmethod
    def get_interface_address(cls, ifname, family=socket.AF_INET):
        import netifaces as ni
        try:
            for addr in ni.ifaddresses(ifname)[family]:
                ip = addr['addr']
                if not cls.is_private_address(ip):
                    return ip
        except KeyError:
            cls.err("Can't find the interface {}".format(ifname))
            return None

    @classmethod
    def get_dns_resolved_ip(cls, subdomain, domainname, family=socket.AF_INET):
        """
        Get current IP address resolved by DNS server, here we use `getaddrinfo`
        instead of `gethostbyname` because of the poor ipv6 support of `gethostname`.

        :param subdomain:  sub domain
        :param domainname:     domain name
        :return:  IP address or None
        """
        ip_addr = None
        try:
            if subdomain == "@":
                hostname = domainname 
            elif subdomain == "*":
                hostname = "{0}.{1}".format(cls.RANDOM_UUID, domainname)
            else:
                hostname = "{0}.{1}".format(subdomain, domainname)

            ip_addr = socket.getaddrinfo(hostname, 80, family)[0][4][0]
        except socket_error as ex:
            cls.err("DomainRecord[{0}] cannot be resolved because of:{1}" \
                     .format(hostname, ex))

        return ip_addr

    @staticmethod
    def get_current_time():
        """
        Get human readable standard timestamp

        :return: timestamp string
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
