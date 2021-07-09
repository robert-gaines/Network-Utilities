from scapy.arch.windows import get_windows_if_list
from pprint import pprint
from scapy.all import *
import datetime
import socket
import time
import csv
import sys
import os

timestamp   = time.ctime()
#
timestamp   = timestamp.replace(' ','_')
#
timestamp   = timestamp.replace(':','_')
#
filename    = 'pcap_'+timestamp+'.csv'
#
csv_file    = open(filename,'w',newline='')
#
pcap_writer = csv.writer(csv_file,delimiter=',')
#
pcap_writer.writerow(['TimeStamp','Source MAC','Destination MAC','IP Version','Transport','Source IP','Destination IP','Source Port','Destination Port'])    

def Parser(packet):
    #
    try:
        #
        transport = ''
        #
        if(packet):
            #
            print("[*] Packet received ")
            #
            #wrpcap(filename,pkt,append=True)
            #
            if(packet.haslayer('Ethernet')):
                #
                timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
                #
                source_mac = packet['Ethernet'].src
                destination_mac = packet['Ethernet'].dst
                #
                print("Source MAC:      %s " % source_mac)
                print("Destination MAC: %s " % destination_mac)
                #
                if(packet.haslayer('IP')):
                    #
                    ip_version = packet['IP'].version
                    src_ip     = packet['IP'].src
                    dst_ip     = packet['IP'].dst
                    #
                    print("IP Version:     %s " % ip_version)
                    print("Source IP:      %s " % src_ip)
                    print("Destination IP: %s " % dst_ip)
                    #
                    if(packet.haslayer('TCP') or packet.haslayer('UDP')):
                        #
                        if(packet.haslayer('TCP')):
                            #
                            transport = 'TCP'
                            #
                            src_port = packet['TCP'].sport
                            dst_port = packet['TCP'].dport
                            #
                            print("Source Port:      %s " % src_port)
                            print("Destination Port: %s " % dst_port)
                            #
                        if(packet.haslayer('UDP')):
                            #
                            transport = 'UDP'
                            #
                            src_port = packet['UDP'].sport
                            dst_port = packet['UDP'].dport
                            #
                            print("Source Port:      %s " % src_port)
                            print("Destination Port: %s " % dst_port)
                            #
                        pcap_writer.writerow([timestamp,source_mac,destination_mac,ip_version,transport,src_ip,dst_ip,src_port,dst_port])
                        #
                transport = ''
                #
                clear_host = os.system('cls')
                #
    except KeyboardInterrupt:
            #
            print("[!] Keyboard interrupt signal received, terminating session")
            #
            csv_file.close()
            #
            sys.exit(1)
    except:
            #
            pass
            #

def main():
    #
    print("[*] Packet Sniffer with CSV transcription ")
    #
    conf.verb = 0
    #
    interfaces = get_windows_if_list()
    #
    print("[*] Interfaces [*]")
    #
    print("------------------")
    #
    for i in range(0,len(interfaces)):
            #
            print( i,")\t",interfaces[i]['name'])
            #
    index = int(input("[+] Enter the interface index-> "))
    #
    interface = interfaces[index]['name']
    #    
    print("[*] Sniffing traffic on: %s ..." % interface)
    #
    sniff(filter="",store=False,iface=r'%s'%interface,prn=Parser)

if(__name__ == '__main__'):
        #
        main()
        #
        csv_file.close()
