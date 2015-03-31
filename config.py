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
import ConfigParser
from utils import DDNSUtils

class LocalDomainRecord(object):
    def __init__(self, parser, section):
        # set the local record alias to be section
        self.alias = section
        self.domain = None
        self.subDomain = None
        self.type = "A"
        self.value = None
        try:
            self.domain = parser.get(section, "domain")
            self.subDomain = parser.get(section, "sub_domain")
            self.id = parser.get(section, "id")
            self.type = parser.get(section, "type")
            self.value = parser.get(section, "value")
        except:
            pass

class DDNSConfig(object):
    def __init__(self, configFile):
        self.configFile = configFile

        # default options
        self.debug = False
        self.interval = 600
        self.accessId = None
        self.accessKey = None

        # local domain record list
        self.localDomainRecordList = []

        self.configParser = ConfigParser.ConfigParser()
        self.configParser.read(configFile)

        self.parseDefaultOptions()
        self.parseDomainRecords()

    def parseDomainRecords(self):
        for section in self.configParser.sections():
            self.localDomainRecordList.append(LocalDomainRecord(self.configParser, section))

    def parseDefaultOptions(self):
        try:
            # specific handling for getboolean method
            self.debug = self.configParser.getboolean("DEFAULT", "debug")
        except:
            pass

        try:
            self.accessId = self.configParser.get("DEFAULT", "access_id")
            self.accessKey = self.configParser.get("DEFAULT", "access_key")
        except Exception,e:
            pass

    def validate(self):
        if not self.accessId or not self.accessKey:
            DDNSUtils.err_and_exit("Invalid access_id or access_key in config file.")

        for rec in self.localDomainRecordList:
            if not rec.domain or not rec.subDomain or not rec.type:
                DDNSUtils.err_and_exit("Invalid domain or sub_domain or type in config file.")

    def save(self, section, option, value):
        self.configParser.set(section, option, value)
        try:
            with open(self.configFile, 'wb') as cf:
                self.configParser.write(cf)
        except:
            DDNSUtils.err("Failed to save the config value")
            return False

        return True
