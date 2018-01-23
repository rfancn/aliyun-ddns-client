#!/usr/bin/env python
# coding=utf-8
"""
 Copyright (C) 2010-2013, Ryan Fan <reg_info@126.com>

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
            ret = requests.get("http://members.3322.org/dyndns/getip")
        except requests.RequestException as ex:
            cls.err("network problem:{0}".format(ex))
            return None

        if ret.status_code != requests.codes.ok:
            cls.err("Failed to get current public IP: {0}\n{1}" \
                    .format(ret.status_code, ret.content))
            return None

        return ret.content.decode('utf-8').rstrip("\n")

    @classmethod
    def get_interface_address(cls, ifname):
        import netifaces as ni
        try:
            ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
            return ip
        except KeyError:
            cls.err("Can't find the interface {}".format(ifname))
            return None

    @classmethod
    def get_dns_resolved_ip(cls, subdomain, domainname):
        """
        Get current IP address resolved by DNS server

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

            ip_addr = socket.gethostbyname(hostname)
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
