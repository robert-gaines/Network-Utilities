from scapy.all import *
import os

def main():
    #
    print("[*] Python PCAP Reader ")
    #
    subject_file = input("[+] Enter the filename-> ")
    #
    if(os.path.exists(subject_file)):
        #
        print("[*] File exists ")
        #
        capture_contents = rdpcap(subject_file)
        #
        for packet in capture_contents:
            #
            if(packet.haslayer('Ethernet')):
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
                            src_port = packet['TCP'].sport
                            dst_port = packet['TCP'].dport
                            #
                            print("Source Port:      %s " % src_port)
                            print("Destination Port: %s " % dst_port)
    else:
        #
        print("[!] File could not be located")
        #
        return

if(__name__ == '__main__'):
    #
    main()
