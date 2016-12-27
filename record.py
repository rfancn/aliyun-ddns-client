#!/usr/bin/env python
# coding=utf-8
"""
 Copyright (C) 2010-2013, Ryan Fan

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
import string

from utils import DDNSUtils
from yunresolver import YunResolver

class LocalDomainRecord(object):# pylint: disable=too-few-public-methods
    """
    Local domain record created from config file
    """
    VALID_TYPES = ('A', 'AAAA')

    def __init__(self, config, section):
        # set the local record alias to be section
        self.alias = section
        self.domainname = config.get_option_value(section, "domain")
        self.rr = self.subdomain = config.get_option_value(section, "sub_domain")
        self.type = config.get_option_value(section, "type", default="A")

        if not self.domainname:
            raise ValueError("Failed initializing LocalDomainRecord: " \
                             "Invalid domain in config file.")

        if not self.rr:
            raise ValueError("Failed initializing LocalDomainRecord: " \
                             "Invalid sub_domain in config file.")

        if self.type.upper() not in self.VALID_TYPES:
            raise ValueError("Failed initializing LocalDomainRecord: " \
                            "Invalid type in config file.")

class RemoteDomainRecord(object):# pylint: disable=too-many-instance-attributes, too-few-public-methods
    """
    Remote domain record created from Aliyun server
    """
    def __init__(self, domain_record_info):
        self.domainname = None
        self.recordid = None
        self.rr = None
        self.type = None
        self.value = None
        self.ttl = None
        self.priority = None
        self.line = None
        self.status = None
        self.locked = False

        # convert json record key name to lowercased one
        converted_domain_record_info = dict(zip(map(string.lower, domain_record_info.keys()),
                                                domain_record_info.values()))

        for k in converted_domain_record_info.keys():
            self.__dict__[k] = converted_domain_record_info[k]


class DDNSDomainRecordManager(object):
    """
    Manager class used to manage local domain record and remote domain records
    """
    def __init__(self, config):
        self.config = config
        self.resolver = YunResolver(self.config.access_id, self.config.access_key, self.config.debug)
        self.local_record_list = self.get_local_record_list()

    def get_local_record_list(self):
        """
        Create local domain record objectes based on local config info

        :return: list of LocalDomainRecord objects
        """
        local_record_list = []

        for section in self.config.get_domain_record_sections():
            try:
                local_record = LocalDomainRecord(self.config, section)
            except ValueError:
                continue

            local_record_list.append(local_record)

        return local_record_list

    def find_local_record(self, remote_record):
        """
        Find LocalDomainRecord based on RemoteDomainRecord

        :param   RemoteDomainRecord
        :return: LocalDomainRecord or None
        """
        for local_record in self.local_record_list:
            if all(getattr(local_record, attr) == getattr(remote_record, attr)
                   for attr in ('domainname', 'rr', 'type')):
                return local_record

        return None


    def fetch_remote_record(self, local_record):
        """
        Fetch RemoteDomainReord from Aliyun server by using LocalDomainRecord info

        :param    LocalDomainRecord
        :return:  RemoteDomainRecord or None
        """
        # Aliyun use fuzzy matching pattern for RR and type keyword
        fuzzy_matched_list = self.resolver.describe_domain_records(local_record.domainname,
                                                                   rr_keyword=local_record.rr,
                                                                   type_keyword=local_record.type)
        if not fuzzy_matched_list:
            DDNSUtils.err("Failed to fetch remote DomainRecords.")
            return None

        exact_matched_list = []
        check_keys = ('DomainName', 'RR', 'Type')
        for rec in fuzzy_matched_list:
            if all(rec.get(key, None) == getattr(local_record, key.lower()) for key in check_keys):
                exact_matched_list.append(rec)

        if not exact_matched_list:
            return None

        if len(exact_matched_list) > 1:
            DDNSUtils.err("Duplicate DomainRecord in Aliyun: {rec.subdomain}.{rec.domainname}"
                          .format(rec=local_record))
            return None

        try:
            remote_record = RemoteDomainRecord(exact_matched_list[0])
        except:
            return None

        return remote_record

    def update(self, remote_record, current_public_ip):
        """
        Update RemoteDomainRecord 's value to current public IP on Aliyun server

        :param  RemoteDomainRecord:
        :param  current public IP
        :return: True or False
        """
        return self.resolver.update_domain_record(remote_record.recordid,
                                                  rr=remote_record.rr,
                                                  record_value=current_public_ip)
