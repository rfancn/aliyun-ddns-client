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
from utils import DDNSUtils

from yunresolver import YunResolver

class DDNSHelper(object):
    def __init__(self, config):
        self.config = config
        self.resolver = YunResolver(self.config.accessId, self.config.accessKey, self.config.debug)

    def getRemoteDomainRecordList(self, domain):
        if not domain:
            DDNSUtils.err("getDomainReordId: You must specify domain name.")
            return None

        # try get domain record id
        domainRecordList = self.resolver.describeDomainRecords(domain)
        return domainRecordList

    def matchRemoteDomainRecord(self, domain, subDomain, type):
        if not domain:
            DDNSUtils.err("matchRemoteDomainRecord: You must specify domain.")
            return None

        if not subDomain:
            DDNSUtils.err("matchRemoteDomainRecord: You must specify sub_domain.")
            return None

        if not type:
            DDNSUtils.err("matchRemoteDomainRecord: You must specify type.")
            return None

        remoteRecordList = self.resolver.describeDomainRecords(domain, rrKeyword=subDomain, typeKeyword=type)
        if not remoteRecordList:
            return None

        return remoteRecordList[0]

    def extractDomainRecordId(self, recordInfo):
        id = None
        try:
            id = recordInfo['RecordId']
        except Exception,e:
            DDNSUtils.err("Failed to get domain record id from {0}".format(recordInfo))
            DDNSUtils.err("Exception:\n{0}".format(e))

        return id

    def extractDomainRecordValue(self, recordInfo):
        value = None
        try:
            value = recordInfo['Value']
        except Exception,e:
            DDNSUtils.err("Failed to get domain record value from {0}".format(recordInfo))
            DDNSUtils.err("Exception:\n{0}".format(e))

        return value

    def sync(self, localRecord, currentPublicIP):
        if not localRecord.id:
            DDNSUtils.err("You must specify domain record id.")
            return False

        if not localRecord.subDomain:
            DDNSUtils.err("You must specify subdomain name.")
            return False

        if not currentPublicIP:
            DDNSUtils.err("Current public ip is empty.")
            return False

        result = self.resolver.updateDomainRecord(localRecord.id, rr=localRecord.subDomain, value=currentPublicIP)
        # if we update domain record successfully, save current domain record value to config file
        if result is True:
            if not self.config.save(localRecord.alias, "value", currentPublicIP):
                DDNSUtils.err("Failed to save domain record value to config file")
                return False

        return result

    def syncFirstTime(self, localRecord, currentPublicIP):
        remoteRecord = self.matchRemoteDomainRecord(localRecord.domain, localRecord.subDomain, localRecord.type)
        if not remoteRecord:
            DDNSUtils.err("Failed to match remote domain record for {0}.{1}"
                          "".format(localRecord.subDomain, localRecord.domain))
            return False

        remoteRecordId = self.extractDomainRecordId(remoteRecord)
        if not remoteRecordId:
            DDNSUtils.err("Failed to extract domain id from remote domain record desc")
            return False

        # save domain record id for future reference
        if not self.config.save(localRecord.alias, "id", remoteRecordId):
            DDNSUtils.err("Failed to save domain record id to config file")
            return False

        remoteRecordValue = self.extractDomainRecordValue(remoteRecord)
        if not remoteRecordValue:
            DDNSUtils.err("Failed to extract domain value from remote domain record desc")
            return False

        # Now, check if domain record value is different with current public ip or not
        if currentPublicIP != remoteRecordValue or currentPublicIP != localRecord.value:
            return self.sync(localRecord, currentPublicIP)

        if self.config.debug:
            DDNSUtils.info("No change with domain record value on remote server, skip it...")
        return True





