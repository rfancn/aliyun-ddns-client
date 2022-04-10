# Aliyun DDNS Client

## Preface

Forked from [rfancn/aliyun-ddns-client](https://github.com/rfancn/aliyun-ddns-client).
But seems the author seems does not want to accept PRs, so this repo will be independent from the original one.

## Usage

## Prepare DDNS

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

[feature_public_ip_from_nic]
enable=false
interface=eth0
```

## Run with docker

```shell
docker run -it --rm -v $YOUR_CONF_FILE_PATH:/etc/ddns.conf tsingjyujing/aliyun-ddns-client
```

## Install from PIP

You can install/update the command line tool from PIP:

```shell
pip3 install -U aliyun-ddns-client
# You can also install from github if you want
pip3 install -U git+https://github.com/TsingJyujing/aliyun-ddns-client.git
```

Save your config file to `$(pwd)/ddns.conf` or `/etc/ddns.conf`, and run `aliyun-ddns` directly.

## Limitations

This version of DDNS client only supports auto updating 'A' type DomainRecord with IPV4 address.

Other types are not supported because they need following value format other than IP address:
- 'NS', 'MX', 'CNAME' types DomainRecord need domain name format value
- 'AAAA' type DomainRecord need IPV6 address format value
- 'SRV' type DomainRecord need name.protocal format value
- 'Explicit URL' and 'Implicit  URL' need URL format value

## References

- [Python DDNS client for Aliyun](http://www.hdget.com/aliyun-ddns-client)
