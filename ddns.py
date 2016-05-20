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
import sys
from helper import DDNSHelper
from utils import DDNSUtils
from config import DDNSConfig

CONF_FILE = "/etc/ddns.conf"

if __name__ == "__main__":
    config = DDNSConfig(CONF_FILE)
    config.validate()

    utils = DDNSUtils(config.debug)
    helper = DDNSHelper(config)

    # get current public ip
    currentPublicIP = utils.getCurrentPublicIP()
    if not currentPublicIP:
        DDNSUtils.err_and_exit("Failed to get current public ip")

    for localRecord in config.localDomainRecordList:
        # if we don't have domain record's id in config file, then we never sync to server before
        if not localRecord.id or not localRecord.value:
            result = helper.syncFirstTime(localRecord,currentPublicIP)
            if result is False:
                DDNSUtils.err_and_exit("Failed doing the first time sync for record:{0}".format(localRecord.alias))
                continue

            DDNSUtils.info("Successfully sync done for record:{0}".format(localRecord.alias))
            continue

        # if current public ip is not the same as the one in server
        if currentPublicIP != localRecord.value:
            if config.debug:
                DDNSUtils.info("current public ip is:{0}, server ip is:{1}".format(currentPublicIP, localRecord.value))

            result = helper.sync(localRecord, currentPublicIP)
            if result is False:
                DDNSUtils.err_and_exit("Failed to sync the current public IP for record:{0}".format(localRecord.alias))

            DDNSUtils.info("Successfully sync done on:{0}".format(utils.getCurrentTime()))
            sys.exit(0)

        # all done for one record
        if config.debug:
            DDNSUtils.info("No changes,skipped...")
            continue







