# dnstricker

```
常用作dnslog平台的一部分，监听本地53/udp端口，用以模拟解析/响应dns请求，导引流量;
可以将所有请求自己子域名(原理图中为*.test.com)的dns请求记录下来，用来确定某处是否存在漏洞;
```
注: 程序兼容python2/3版本，可灵活扩展

-
## 原理图：

![dnstricker](shots/dnstricker.png "dnstricker")

## 本地测试：

#### 1.由于在本地测试所以"域名服务商绑定IP"的操作，用修改本地HOSTS文件代替    
其中添加一行，即127.0.0.1 代指原理图中的1.1.1.1:

```
127.0.0.1 dns.mid.com
```

#### 2.使用命令开启模拟dns服务

```
python dnstricker.py
```

#### 3.使用如下命令测试

```
nslookup k1.test.com dns.mid.com
nslookup others.com dns.mid.com
nslookup k2.test.com dns.mid.com
```

![queryinfo](shots/queryinfo.png "query")

#### 4.观察记录日志情况

![loginfo](shots/loginfo.png "log")

#### 5.关键配置由程序中的下列参数指定

```
dns_domain = 'test.com'
ip_address = '2.2.2.2'
default_ip = '192.168.1.1'
```
注: 实际使用中，模拟dns服务和web服务一般部署在同一个服务器上，即dns服务回复给客户端的web服务的ip地址应为1.1.1.1，而不是原理图中的2.2.2.2
