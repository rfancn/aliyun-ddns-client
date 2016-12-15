## aliyun-ddns-client(v0.2)

Python DDNS client for Aliyun(http://www.guanxigo.com/aliyun-ddns-client/)

### LIMITATION
This version of DDNS client only supports auto updating 'A' type DomainRecord with IPV4 address.

Other types are not supported because they need following value format other than IP address:
- 'NS', 'MX', 'CNAME' types DomainRecord need domain name format value
- 'AAAA' type DomainRecord need IPV6 address format value
- 'SRV' type DomainRecord need name.protocal format value
- 'Explicit URL' and 'Implicit  URL' need URL format value

### PREREQUISITE
Some 3rd party python libraries are required for aliyun-ddns-client as below, you can install it via pip or easy_install:

- requests

For example:
```
# pip install requests
```

### INSTALLATION 
1. Download all files to somewhere, e,g: /opt/aliyun-ddns-client
2. Rename "ddns.conf.example" to "ddns.conf" in the same dir
3. Create a cronjob which execute "python ddns.py" periodly, e,g:
`
*/5 * * * * cd /opt/aliyun-ddns-client && /usr/bin/python ddns.py
`
4. Make sure ddns.conf can be accessed by cronjob user


### CONFIGURATION
Required options need to be set in /etc/ddns.conf:
* access_id
* access_key
* domain
* sub_domain

Optional options:
* type
* debug

```
[DEFAULT]
# access id obtains from aliyun
access_id=
# access key obtains from aliyun
access_key=
# it is not used at this moment, you can just ignore it
interval=600
# turn on debug mode or not
debug=true

[DomainRecord1]
# domain name, like google.com
domain=
# subdomain name, like www, blog, bbs, *, @, ...
sub_domain=
# resolve type, 'A', 'AAAA'..., currently it only supports 'A'
type=A
```

### GETTING STARTED 
1. Create a DNS resolve entry in Aliyun console manually, e,g: blog.guanxigo.com
2. You can leave any IP address on Aliyun server for this entry, like 192.168.0.1
3. Make sure all required options are inputted correctly in "ddns.conf"
4. Make sure "ddns.conf" can be readable for the user who setup cron job

NOTICE:
Only domain records both defined in local config file and Aliyun server will be updated

### FAQ

* Q: Why it failed with error message "The input parameter \"Timestamp\" that is mandatory for processing this request is not supplied." in describeDomainRecords()?

  A: Please check what's the value in params 'TimeStamp'. If the value has big difference with the correct time, you need use ntpdate to sync system time to the correct one.

* Q: Why it failed with error message "Failed to save the config value"?

  A: You need make sure current cronjob user has permission to write file /etc/ddns.conf.
