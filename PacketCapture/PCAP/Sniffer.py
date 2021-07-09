from scapy.arch.windows import get_windows_if_list
from pprint import pprint
from scapy.all import *
import time
import sys
import os

timeStamp = time.ctime()

timeStamp = timeStamp.replace(':','_')

timeStamp = timeStamp.replace(' ','_')

filename = timeStamp+"_capture.pcap"

def Parser(pkt):
    #
    try:
        #
        if(pkt):
                #
                print("[*] Packet received ")
                #
                wrpcap(filename,pkt,append=True)
                #
                clear_host = os.system('cls')
                #
    except KeyboardInterrupt:
            #
            print("[!] Keyboard interrupt signal received, terminating session")
            #
            sys.exit(1)
    except:
            #
            pass
            #

def main():
    #
    print("""
***********************************
*                                 *
*    ___           _        _     *
*   / _ \__ _  ___| | _____| |_   *
*  / /_)/ _` |/ __| |/ / _ \ __|  *
* / ___/ (_| | (__|   <  __/ |_   *
* \/    \__,_|\___|_|\_\___|\__|  *
*                                 *
*   __       _  __  __            *
*  / _\_ __ (_)/ _|/ _| ___ _ __  *
*  \ \| '_ \| | |_| |_ / _ \ '__| *
* _ \ \ | | | |  _|  _|  __/ |    *
* \__/ _| |_|_|_| |_|  \___|_|    *
*                                 *
*                                 *
***********************************                              
          """)
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
