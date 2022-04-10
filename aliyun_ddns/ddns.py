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
import logging

from aliyun_ddns.config import DDNSConfig
from aliyun_ddns.record import DDNSDomainRecordManager
from aliyun_ddns.utils import DDNSUtils

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def main():
    """
    Main routine
    """
    config = DDNSConfig()
    record_manager = DDNSDomainRecordManager(config)

    # get current public ip for this server
    if config.pifn_enable:
        current_public_ip = DDNSUtils.get_interface_address(config.pifn_interface)
    else:
        current_public_ip = DDNSUtils.get_current_public_ip()
    if not current_public_ip:
        raise Exception("Failed to get current public IP")

    for local_record in record_manager.local_record_list:
        dns_resolved_ip = DDNSUtils.get_dns_resolved_ip(
            local_record.subdomain,
            local_record.domainname
        )

        if local_record.type == "AAAA":
            current_ip = DDNSUtils.get_interface_ipv6_address(local_record.interface)
        else:
            current_ip = current_public_ip

        if current_ip == dns_resolved_ip:
            log.info(f"Skipped as no changes for DomainRecord [{local_record.subdomain}.{local_record.domainname}]")
            continue

        # If current public IP doesn't equal to current DNS resolved ip, only in three cases:
        # 1. The new synced IP for remote record in Aliyun doesn't take effect yet
        # 2. remote record's IP in Aliyun server has changed
        # 3. current public IP is changed
        remote_record = record_manager.fetch_remote_record(local_record)
        if not remote_record:
            log.error(f"Failed finding remote DomainRecord [{local_record.subdomain}.{local_record.domainname}]")
            continue

        if current_ip == remote_record.value:
            log.info(f"Skipped as we already updated DomainRecord [{local_record.subdomain}.{local_record.domainname}]")
            continue

        # if we can fetch remote record and record's value doesn't equal to public IP
        sync_result = record_manager.update(remote_record, current_ip, local_record.type)

        if not sync_result:
            log.error(f"Failed updating DomainRecord [{local_record.subdomain}.{local_record.domainname}]")
        else:
            log.info(f"Successfully updated DomainRecord [{local_record.subdomain}.{local_record.domainname}]")
