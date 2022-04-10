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
import logging
import socket
import uuid
from datetime import datetime
from socket import error as socket_error

import requests

log = logging.getLogger(__file__)


class DDNSUtils(object):
    # To support "*" subdomain definition,
    # We need generate a non-exist subdomain name
    # Here we generate a random UUID for that
    # fake_subdomain = ''.join([random.choice(string.lowercase) for i in xrange(12)])
    RANDOM_UUID = uuid.uuid4().hex

    """
    Utils class wrapper
    """

    @classmethod
    def get_current_public_ip(cls):
        """
        Get current public IP

        @return  IP address or None
        """
        resp = requests.get("https://jsonip.com/")
        resp.raise_for_status()
        return resp.json()["ip"]

    @classmethod
    def get_interface_address(cls, ifname):
        import netifaces as ni
        return ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']

    @classmethod
    def get_interface_ipv6_address(cls, ifname):
        import netifaces as ni
        return ni.ifaddresses(ifname)[ni.AF_INET6][0]['addr']

    @classmethod
    def get_dns_resolved_ip(cls, subdomain, domainname):
        """
        Get current IP address resolved by DNS server

        :param subdomain:  sub domain
        :param domainname:     domain name
        :return:  IP address or None
        """
        ip_addr = None
        hostname = None
        try:
            if subdomain == "@":
                hostname = domainname
            elif subdomain == "*":
                hostname = "{0}.{1}".format(cls.RANDOM_UUID, domainname)
            else:
                hostname = "{0}.{1}".format(subdomain, domainname)

            ip_addr = socket.gethostbyname(hostname)
        except socket_error as ex:
            log.error(f"DomainRecord[{hostname}] cannot be resolved because of:{ex}")

        return ip_addr

    @staticmethod
    def get_current_time():
        """
        Get human readable standard timestamp

        :return: timestamp string
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
