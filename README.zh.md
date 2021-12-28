# aliyun-ddns-client(v0.3)

阿里云 Python DDNS 客户端 (<http://www.hdget.com/aliyun-ddns-client>)

中文 | [English](README.md)

## 限制

本版本的 DDNS client只支持自动更新 “A” 类型 IPv4 地址的 DomainRecord。

其他类型不支持，因为它们需要以下值格式，而不是IP地址:

- `NS`, `MX`, `CNAME` 类型 DomainRecord 需要域名格式值
- `AAAA` 类型 DomainRecord 需要 IPv6 地址格式的值
- `SRV` 类型 DomainRecord 需要 `名称.协议` 格式的值
- `显式URL` 和 `隐式URL` 需要 URL 格式值

## 先决条件

下面是 aliyun-ddns-client 需要的一些第三方 python 库，你可以通过 pip 或 easy_install 安装:

- requests
- netifaces (仅当你想从接口设置中获取IP地址时需要，当你有多个接口时可能会有用)

例如:

```sh
pip install requests
pip install netifaces # 可选
```

## 安装

### 1. 使用 cron

1. 下载所有文件到某个地方, 例如: `/opt/aliyun-ddns-client`
2. 将 `ddns.conf.example` 重命名为 `ddns.conf`
3. 创建一个 cron 任务，定时执行 `python ddns.py`, 例如:

    ```sh
    */5 * * * * cd /opt/aliyun-ddns-client && /usr/bin/python ddns.py
    ```

4. 确保 cron 用户可以访问 `ddns.conf`

### 2. 使用 SystemD

1. 下载所有文件到某个地方, 例如: `/root/tools/aliyun-ddns-client`
2. 将 `ddns.conf.example` 重命名为 `ddns.conf`
3. 复制 `ddns.timer` 和 `ddns.service` 到 `/usr/lib/systemd/system`
4. 执行:

    ```sh
    root@local# systemctl daemon-reload
    root@local# systemctl start ddns.timer
    root@local# systemctl status ddns.timer -l
    ```

## 配置

`/etc/ddns.conf` 中需要设置的选项:

- access_id
- access_key
- domain
- sub_domain

可选的选项:

- type
- debug

```ini
[DEFAULT]
# access id obtains from aliyun
access_id =
# access key obtains from aliyun
access_key =
# it is not used at this moment, you can just ignore it
interval = 600
# turn on debug mode or not
debug = true

[DomainRecord1]
# domain name, like google.com
domain =
# subdomain name, like www, blog, bbs, *, @, ...
sub_domain =
# resolve type, 'A', 'AAAA'..., currently it only supports 'A'
type = A

[feature_public_ip_from_nic]
enable = false
interface = eth0
```

## 开始使用

1. 在阿里云控制台手动创建 DNS 解析条目，例如: `blog.guanxigo.com`
2. 您可以在阿里云服务器上为该条目留下任何IP地址，如 192.168.0.1
3. 确保所有必需的选项都正确输入到 `ddns.conf`
4. 启用您想要使用的功能
5. 确保 `ddns.conf` 对于设置cron作业的用户来说是可读的

**注意**: 只更新本地配置文件和阿里云服务器中定义的域记录。

## 常见问题

- **问**: 为什么报错 `The input parameter "Timestamp" that is mandatory for processing this request is not supplied.`?
    **答**: 请检查参数 TimeStamp 的值是多少, 如果与正确时间相差较大，需要使用 `ntpdate` 将系统时间同步到正确的时间。
- **问**: 为什么报错 `Failed to save the config value`?
    **答**: 您需要确保当前的 cron 用户有权限写 `/etc/ddns.conf` 文件。
- **问**: 为什么报错 `AttributeError: 'X509' object has no attribute '_x509'`?
    **答**：PyOpenSSL 版本需要 >= 0.14，你可以尝试通过以下方法解决这个问题:

    ```sh
    sudo yum uninstall python-requests
    sudo pip uninstall pyopenssl cryptography requests
    sudo pip install requests
    ```
