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
import string
import urllib
import hashlib
import hmac
import uuid
from datetime import datetime

class DomainRecord(object):
    def __init__(self, domainRecord):
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
        convertedDomainRecord = dict(zip(map(string.lower,domainRecord.keys()),domainRecord.values()))
        try:
            for k in convertedDomainRecord.keys():
                self.__dict__[k] = convertedDomainRecord[k]
        except Exception,e:
            print "Failed to initiate DomainRecord object, no %s definition in DomainRecord" % k
            raise e

class YunResolver(object):
    def __init__(self, accessId, accessKey, debug):
        self.url = "http://dns.aliyuncs.com/"
        self.accessKeyId = accessId
        self.hashKey = accessKey + '&'
        self.debug = debug

    def getTimeStamp(self):
        """
        ISO8601 standard: YYYY-MM-DDThh:mm:ssZ, e,g:2015-0109T12:00:00Z (UTC Timezone)
        @return string
        """
        return  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    def getSignatureNonce(self):
        """
        Unique random value
        """
        return uuid.uuid4()

    def getCommonParams(self):
        commonParams = {
            'Format': 'json',
            'Version': '2015-01-09',
            'AccessKeyId': self.accessKeyId,
            'TimeStamp': self.getTimeStamp(),
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': self.getSignatureNonce(),
            'SignatureVersion': "1.0",
        }

        return commonParams

    def getSignatureFollowRule(self, httpMethod, params):
        """
        Exactly follow the specification to generate the signature
        """
        def percentEncode(str):
            str = str.encode("utf8")
            return urllib.quote_plus(str).replace("+", "%20").replace("*", "%2A").replace("%7E", "~")

        params.update(self.getCommonParams())
        sortedParams = sorted(params.items())

        # get Canonicalized Query String
        canonString = ""
        for k,v in sortedParams:
            canonString += "&" + percentEncode(k) + "=" + percentEncode(v)

        # format string for sign
        signString = httpMethod + "&" + percentEncode("/") + "&" + percentEncode(canonString[1:])


    def getSignature(self, httpMethod, params):
        """
        1. params = combine specific params and common params
        2. sortedParams = sort params by key
        3. queryString = urlencode sortedParams
        4. signString = HTTPMethod + "&" + urlencode "/" + quote_plus queryString
        5. hashValue = sha1 with hashKey against signString
        6. base64HashValue = base64 encoding hashValue
        7. signature = urlencode base64HashValue
        @return string
        """
        params.update(self.getCommonParams())
        sortedParams = sorted(params.items())
        canonString = urllib.urlencode(sortedParams)
        signString = httpMethod + "&" + urllib.quote_plus("/") + "&" + urllib.quote_plus(canonString)

        # hmac sha1 algrithm
        hashValue = hmac.new(self.hashKey, signString, hashlib.sha1).digest()
        signature=hashValue.encode("base64").rstrip('\n')

        return signature

    def describeDomainRecords(self, domainName, pageNumber=None, pageSize=None,
                              rrKeyword="", typeKeyword="", valueKeyword=""):
        """
        query:  DomainName(*), PageNumber, PageSize, RRKeyWord, TypeKeyWord, ValueKeyWord
        return: TotalCount, PageNumber, PageSize, DomainRecords
        """
        httpMethod = "GET"
        params = {
            'Action': "DescribeDomainRecords",
            'DomainName': domainName
        }

        optionalParams = {}
        if pageNumber:
            optionalParams['PageNumber'] = pageNumber
        if pageSize:
            optionalParams['PageSize'] = pageSize
        if rrKeyword:
            optionalParams['RRKeyWord']= rrKeyword
        if typeKeyword:
            optionalParams['TypeKeyWord']= typeKeyword
        if valueKeyword:
            optionalParams['ValueKeyWord'] = valueKeyword

        params.update(optionalParams)
        # add signature
        params.update({"Signature": self.getSignature(httpMethod, params)})

        # do real http action
        jsonResult = None
        try:
            r = requests.get(self.url, params=params)
            if r.status_code == requests.codes.ok:
                jsonResult = r.json()
        except Exception,e:
            print r.content
            raise e

        if not jsonResult:
            print "Failed to get valid Domain Records Info"
            return []

        domainRecordList = []
        try:
            records = jsonResult['DomainRecords']['Record']
            for rec in records:
                #dr = DomainRecord(rec)
                domainRecordList.append(rec)
        except Exception,e:
            raise e

        return domainRecordList

    def updateDomainRecord(self, recordId, rr="www", type="A", value="192.168.0.1",
                           ttl=None, priority=None, line=None):
        httpMethod = "GET"
        params = {
            'Action': "UpdateDomainRecord",
            'RecordId': recordId,
            'RR': rr,
            'Type': type,
            'Value': value,
        }

        optionalParams = {}
        if ttl:
            validTTLs = [600, 1800, 3600, 43200, 86400]
            if ttl not in validTTLs:
                print "TTL is not a valid value, it need to be one of them: %s" % validTTLs
                return False
            optionalParams['TTL'] = ttl

        if priority:
            validPriorities = range(1,11)
            if priority not in validPriorities:
                print "Priority is not a valid value, it need to be one of them: %s" % validPriorities
            optionalParams['Priority'] = priority

        if line:
            validLines = ['default', 'telecom', 'unicom', 'mobile', 'oversea', 'edu', 'google', 'baidu', 'biying']
            if line not in validLines:
                print "Line is not a valid value, it need to be one of them: %s" % validLines
                return False
            optionalParams['Line']= line

        params.update(optionalParams)
        # add signature
        params.update({"Signature": self.getSignature(httpMethod, params)})

        # do real http action
        try:
            r = requests.get(self.url, params=params)
            if r.status_code != requests.codes.ok:
                print "Http Status Code:%s\n%s" % (r.status_code, r.content)
                return False
        except Exception,e:
            print r.content
            raise e

        return True

    def describeDomainRecordInfo(self, recordId):
        httpMethod = "GET"
        params = {
            'Action': "DescribeDomainRecordInfo",
            'RecordId': recordId,
        }
        # add signature
        params.update({"Signature": self.getSignature(httpMethod, params)})

        # do real http action
        jsonResult = None
        try:
            r = requests.get(self.url, params=params)
            if r.status_code != requests.codes.ok:
                print "Http Status Code:%s\n%s" % (r.status_code, r.content)
                return False

            jsonResult = r.json()
        except Exception,e:
            print r.content
            raise e

        return jsonResult










