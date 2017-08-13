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
from __future__ import print_function
import sys
if sys.version_info < (3,):
    from urllib import urlencode, quote_plus 
else:
    from urllib.parse import urlencode, quote_plus

import hmac
import hashlib
import uuid
from datetime import datetime

import requests

class YunResolver(object):
    """
    Implementation of Aliyun Resolver API
    """
    def __init__(self, access_id, access_key, debug):
        self.url = "https://dns.aliyuncs.com/"
        self.access_id = access_id
        self.hash_key = access_key + '&'
        self.debug = debug

    def get_common_params(self):
        """
        Build common params need by Aliyun API

        :return: dict of all nessary params
        """

      # ISO8601 standard: YYYY-MM-DDThh:mm:ssZ, e,g:2015-0109T12:00:00Z (UTC Timezone)
        current_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        signature_nonce = uuid.uuid4()

        common_params = {
            'Format': 'json',
            'Version': '2015-01-09',
            'AccessKeyId': self.access_id,
            'Timestamp': current_timestamp,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': signature_nonce,
            'SignatureVersion': "1.0",
        }

        return common_params

    def get_signature(self, http_method, params):
        """
        1. params = combine specific params and common params
        2. sorted_params = sort params by key
        3. query_string = urlencode sorted_params
        4. sign_str = HTTPMethod + "&" + urlencode "/" + quote_plus queryString
        5. hash_value = sha1 with hash_key against sign_str
        6. base64_hash_value = base64 encoding hash_value
        7. signature = urlencode base64HashValue

        @return string
        """
        def sha1_hmac(key, str_to_sign):
            if sys.version_info < (3,):
                hash_value = hmac.new(self.hash_key, sign_str, hashlib.sha1).digest()
                return hash_value.encode('base64').strip('\n')
            else:
                from base64 import b64encode
                key = bytes(key, 'utf-8') 
                str_to_sign = bytes(str_to_sign, 'utf-8')
                byte_hash_value = hmac.new(key, str_to_sign, hashlib.sha1).digest()
                return str(b64encode(byte_hash_value), 'utf8').strip('\n')

        params.update(self.get_common_params())
        sorted_params = sorted(params.items())
        canon_str = urlencode(sorted_params)
        sign_str = http_method + "&" + quote_plus("/") + "&" + quote_plus(canon_str)

        # hmac sha1 algrithm
        signature = sha1_hmac(self.hash_key, sign_str) 

        return signature

    def describe_domain_records(self, domain_name, page_number=None, page_size=None,
                                rr_keyword="", type_keyword="", value_keyword=""):
        """
        query:  DomainName(*), PageNumber, PageSize, RRKeyWord, TypeKeyWord, ValueKeyWord
        return: TotalCount, PageNumber, PageSize, DomainRecords
        """
        http_method = "GET"
        params = {
            'Action': "DescribeDomainRecords",
            'DomainName': domain_name
        }

        optional_params = {}
        if page_number:
            optional_params['PageNumber'] = page_number
        if page_size:
            optional_params['PageSize'] = page_size
        if rr_keyword:
            optional_params['RRKeyWord'] = rr_keyword
        if type_keyword:
            optional_params['TypeKeyWord'] = type_keyword
        if value_keyword:
            optional_params['ValueKeyWord'] = value_keyword

        params.update(optional_params)
        # add signature
        params.update({"Signature": self.get_signature(http_method, params)})

        # do real http action
        try:
            ret = requests.get(self.url, params=params)
        except requests.RequestException as ex:
            raise ex

        if ret.status_code != requests.codes.ok:
            print("Server side problem: {0}".format(ret.status_code))
            if self.debug:
                print("Error in describeDomainRecords(), " \
                       "params: {0},\nhttp response: {1}" \
                       .format(params, ret.content))
            return None

        domain_record_list = []
        try:
            json_result = ret.json()
            total_records = json_result.get('TotalCount', 0)
            if total_records == 0:
                return None

            records = json_result['DomainRecords']['Record']
            for rec in records:
                domain_record_list.append(rec)
        except requests.RequestException as ex:
            raise ex

        return domain_record_list

    def update_domain_record(self, record_id, rr="www", record_type="A", record_value="192.168.0.1",
                             ttl=None, priority=None, line=None):
        """
        Update remote domain record on Aliyun server

        :param record_id:     record id
        :param rr:            sub domain
        :param record_type:   record type
        :param record_value:  record value
        :param ttl:           TTL
        :param priority:      priority
        :param line:          resolve line

        :return: True if succeed, of False if failed
        """
        http_method = "GET"
        params = {
            'Action': "UpdateDomainRecord",
            'RecordId': record_id,
            'RR': rr,
            'Type': record_type,
            'Value': record_value,
        }

        optional_params = {}
        if ttl:
            valid_ttl_list = [600, 1800, 3600, 43200, 86400]
            if ttl not in valid_ttl_list:
                print("Invalid TTL, it need to be one of them: %s" % valid_ttl_list)
                return False
            optional_params['TTL'] = ttl

        if priority:
            valid_priorities = range(1, 11)
            if priority not in valid_priorities:
                print("Invalid priority, it need to be one of them: %s" % valid_priorities)
            optional_params['Priority'] = priority

        if line:
            valid_lines = ['default', 'telecom', 'unicom',
                           'mobile', 'oversea', 'edu',
                           'google', 'baidu', 'biying']
            if line not in valid_lines:
                print("Invalid line, it need to be one of them: %s" % valid_lines)
                return False
            optional_params['Line'] = line

        params.update(optional_params)
        # add signature
        params.update({"Signature": self.get_signature(http_method, params)})

        # do real http action
        try:
            ret = requests.get(self.url, params=params)
        except requests.RequestException as ex:
            raise ex

        if ret.status_code != requests.codes.ok:
            print("Server side problem: {0}".format(ret.status_code))
            if self.debug:
                print("Error in updateDomainRecord(), " \
                       "params: {0},\nhttp response: {1}" \
                       .format(params, ret.content))
            return False

        return True

    def describe_domain_record_info(self, record_id):
        """
        Fetch remote domain record info by record id

        :param record_id:  domain record id
        :return:  dict
        """
        http_method = "GET"
        params = {
            'Action': "DescribeDomainRecordInfo",
            'RecordId': record_id,
        }
        # add signature
        params.update({"Signature": self.get_signature(http_method, params)})

        # do real http action
        try:
            ret = requests.get(self.url, params=params)
        except requests.RequestException as ex:
            raise ex

        if ret.status_code != requests.codes.ok:
            print("Server side problem: {0}".format(ret.status_code))
            if self.debug:
                print("Error in describeDomainRecordInfo(), " \
                       "params: {0},\nhttp response: {1}" \
                       .format(params, ret.content))
            return False

        return ret.json()
