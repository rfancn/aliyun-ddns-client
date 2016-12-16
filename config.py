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

CONF_FILE = "ddns.conf"
# Compaitible consideration for v0.1
SYS_CONF_FILE = "/etc/ddns.conf"

class DDNSConfig(object):
    """
    Aliyun DDNS client config class to read/save config stuff
    """
    def __init__(self):
        # default options
        self.debug = False
        self.interval = 600
        self.access_id = None
        self.access_key = None

        self.parser = ConfigParser.ConfigParser()
        if not self.parser.read(CONF_FILE):
            # Compaitible consideration for v0.1
            if not self.parser.read(SYS_CONF_FILE):
                DDNSUtils.err_and_exit("Failed to read config file.")

        try:
            self.debug = self.parser.getboolean("DEFAULT", "debug")
            self.access_id = self.parser.get("DEFAULT", "access_id")
            self.access_key = self.parser.get("DEFAULT", "access_key")
        except ValueError as ex:
            DDNSUtils.err_and_exit("Invalid debug in config: {0}".format(ex))
        except ConfigParser.NoSectionError as ex:
            DDNSUtils.err_and_exit("Invalid config: {0}".format(ex))
        except ConfigParser.NoOptionError as ex:
            DDNSUtils.err_and_exit("Invalid config: {0}".format(ex))

        if not self.access_id or not self.access_key:
            DDNSUtils.err_and_exit("Invalid access_id or access_key in config file.")

    def get_domain_record_sections(self):
        """
        Get sections other than default, which contains DomainRecord definition

        :return: section list
        """
        return self.parser.sections()

    def get_option_value(self, section, option, default=None):
        """
        Get specific option value from section, default is None

        :param section: ini file section
        :param option:  init file option
        :param default: default value for option
        :return: option value
        """
        value = default
        try:
            value = self.parser.get(section, option)
        except ConfigParser.NoSectionError:
            print "No section: {0}".format(section)
        except ConfigParser.NoOptionError:
            print "No option {0} in section: {1}".format(option, section)

        return value
