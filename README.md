## aliyun-ddns-client

Python DDNS client for Aliyun(http://www.guanxigo.com/netcn-ddns-client/)

### INSTALLATION 
1. copy all files to somewhere, e,g: /opt/aliyun-ddns-client
2. copy ddns.conf.example to /etc/ddns.conf
3. create a cronjob which execute "python ddns.py" periodly, e,g:
4. make sure /etc/ddns.conf can be accessed by user
`
*/5 * * * * cd /opt/aliyun-ddns-client && /usr/bin/python ddns.py
`

### CONFIGURATION
Required options need to be set in /etc/ddns.conf:
* access_id
* access_key
* domain
* sub_domain
* type

Optional options:
* id
* debug
* value

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

[1]
# domain name, like google.com
domain=
# subdomain name, like www, blog, bbs
sub_domain=
# record id which get from DNS service provider
id=
# it can be IP address, alias to another hostname...
value=
# resolve type, 'A', 'MX'...
type=
```

### GETTING STARTED 
1. Create a subdomain on net.cn manually, e,g: blog
2. You can leave any IP address on net.cn for this subdomain, like 192.168.0.120
3. Make sure all mandantory options inputted correctly in /etc/ddns.conf 
4. Make sure /etc/ddns.conf can be readable and writable for the user who setup cron job

### WORK FLOW
1. When Aliyun ddns client rums first time, it will fetch subdomain record's id and save to local /etc/ddns.conf
2. Then it will compare current public ip with local value in /etc/ddns.conf, if it doesn't match, it will sync the current public ip to net.cn server 
3. If sync operation done successfully, the new updated value(IP) in server side will be saved in local /etc/ddns.conf too
