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
import requests
import socket
import sys
from datetime import datetime

class DDNSUtils:
    def __init__(self, debug):
        self.debug = debug

    @staticmethod
    def err(str):
        sys.stderr.write("{0}\t[ERROR]\t{1}\n".format(DDNSUtils.getCurrentTime(), str))

    @staticmethod
    def info(str):
        sys.stdout.write("{0}\t[INFO]\t{1}\n".format(DDNSUtils.getCurrentTime(), str))

    @staticmethod
    def err_and_exit(str):
        sys.stderr.write("{0}\t[ERROR]\t{1}\n".format(DDNSUtils.getCurrentTime(), str))
        sys.exit(1)

    def getCurrentPublicIP(self):
        """
        Get current public IP

        @return None or ip string
        """
        ip = None
        try:
            r = requests.get("http://members.3322.org/dyndns/getip")
            if r.status_code == requests.codes.ok:
                ip = r.content.rstrip("\n")
            else:
                if self.debug:
                    self.info("Http Status Code:{0}\n{1}".format(r.status_code, r.content))
                else:
                    self.err("Failed to get current public IP, pls check network settings")
        except Exception,e:
            self.err("network problem:{0}".format(e))

        return ip

    def getCurrenDNSResolvedIP(self, domainName, subDomainName):
        """
        Get current ip resolved by DNS server,
        Due for local DNS cache, it may be not synced to the one recorded in DNS service provider
        """
        ip = None
        try:
            ip = socket.gethostbyname("{0}.{1}".format(subDomainName,domainName))
        except Exception,e:
            self.err("network problem:{0}".format(e))

        return ip

    @staticmethod
    def getCurrentTime():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")






