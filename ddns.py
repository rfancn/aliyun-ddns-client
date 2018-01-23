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
from utils import DDNSUtils
from config import DDNSConfig
from record import DDNSDomainRecordManager

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
        DDNSUtils.err_and_exit("Failed to get current public IP")

    for local_record in record_manager.local_record_list:
        dns_resolved_ip = DDNSUtils.get_dns_resolved_ip(local_record.subdomain,
                                                        local_record.domainname)

        if current_public_ip == dns_resolved_ip:
            DDNSUtils.info("Skipped as no changes for DomainRecord" \
                           "[{rec.subdomain}.{rec.domainname}]".format(rec=local_record))
            continue

        # If current public IP doesn't equal to current DNS resolved ip, only in three cases:
        # 1. The new synced IP for remote record in Aliyun doesn't take effect yet
        # 2. remote record's IP in Aliyun server has changed
        # 3. current public IP is changed
        remote_record = record_manager.fetch_remote_record(local_record)
        if not remote_record:
            DDNSUtils.err("Failed finding remote DomainRecord" \
                          "[{rec.subdomain}.{rec.domainname}]".format(rec=local_record))
            continue

        if current_public_ip == remote_record.value:
            DDNSUtils.info("Skipped as we already updated DomainRecord" \
                           "[{rec.subdomain}.{rec.domainname}]".format(rec=local_record))
            continue

        # if we can fetch remote record and record's value doesn't equal to public IP
        sync_result = record_manager.update(remote_record, current_public_ip)
        if not sync_result:
            DDNSUtils.err("Failed updating DomainRecord" \
                          "[{rec.subdomain}.{rec.domainname}]".format(rec=local_record))
        else:
            DDNSUtils.info("Successfully updated DomainRecord" \
                           "[{rec.subdomain}.{rec.domainname}]".format(rec=local_record))

if __name__ == "__main__":
    main()
