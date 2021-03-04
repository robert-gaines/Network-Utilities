#! /usr/bin/env python3

from queue import Queue
import subprocess
import xlsxwriter
import ipaddress
import threading
import time
import sys
import os

live_hosts         = []

def Threader(q):
    #
    while(True):
        #
        host = q.get()
        #
        PingHost(host)
        #
        q.task_done()

def GenFileName():
    #
    file_name = "PingSweep_Results_"
    #
    timestamp = time.ctime()
    #
    replace_colons = timestamp.replace(":",'_')
    #
    final_timestamp = replace_colons.replace(" ","_")
    #
    final_timestamp += ".xlsx"
    #
    file_name += final_timestamp
    #
    return file_name

def PingHost(host):
    #
    if(os.name == 'nt'):
        #
        output = subprocess.Popen(['ping','-n','1','-w','150',str(host)],stdout=subprocess.PIPE).communicate()[0]
        #
    else:
        #
        output = subprocess.Popen(['ping','-c','1','-w','150',str(host)],stdout=subprocess.PIPE).communicate()[0]
        #
    if('Reply' in output.decode('utf-8')):
        #
        live_hosts.append(host)
        #
    elif("Destination host unreachable" in output.decode('utf-8')):
        #
        return
        #
    elif("Request timed out" in output.decode('utf-8')):
        #
        return
        #
    else:
        #
        return

def ImportFileData(configuration_file):
    #
    vlan_data = list()
    #
    if(os.path.exists(configuration_file)):
        fileObject = open(configuration_file,'r')
        for line in fileObject.readlines():
            vlan    = line.split(',')[0]
            network = line.split(',')[1]
            network = network.rstrip('\n')
            entry   = [vlan,network]
            vlan_data.append(entry)
            #print("[*] VLAN: %s -> Network: %s " %(vlan,network))
        return vlan_data
    else:
        print("[!] Failed to locate the configuration file ")
        return

def CreateInventory(vlans,file_name):
    #
    global total_hosts_tested
    global total_live_hosts
    total_hosts_tested = 0
    total_live_hosts = 0
    #
    fileName = GenFileName()
    #
    workbook = xlsxwriter.Workbook(file_name)
    #
    q = Queue()
    #
    for v in vlans:
        #
        vlan    = v[0]
        network = v[1]
        #
        current_worksheet = workbook.add_worksheet(vlan)
        current_worksheet.set_column('A:A',20)
        current_worksheet.write('A1','IP Address')
        #
        hosts = list(ipaddress.ip_network(network).hosts())
        #
        total_hosts_tested += len(hosts)
        #
        for h in hosts:
            #
            q.put(h)
            #
        for i in range(100):
            #
            process = threading.Thread(target=Threader,args=(q,))
            #
            process.daemon = True 
            #
            process.start()
            #
        q.join()
        #
        ip_column_index = 'A'
        ip_row_index    = 2
        #
        for host in live_hosts:
            #
            total_live_hosts += 1
            #
            write_index = ip_column_index+str(ip_row_index)
            current_worksheet.write(write_index,str(host))
            ip_row_index += 1
            #
        live_hosts.clear()
        #
    print("[*] Ping sweep results may be found in the following file: %s " % file_name)
    #    
    workbook.close()

def main():
    #
    start_time = time.perf_counter()
    #
    print("[*] Multi-VLAN Ping Sweep [*]")
    #
    configuration_file = input("[+] Identify the configuration file-> ")
    #
    print("[*] Loading Ping Sweep Parameters... ")
    #
    subject_vlans = ImportFileData(configuration_file)
    #
    if(len(subject_vlans) > 0):
        #
        print("[*] Initiating ping sweep...")
        #
        workbook_name = GenFileName()
        #
        CreateInventory(subject_vlans,workbook_name)
        #
    else:
        #
        print("[!] No ping sweep parameters were loaded. Departing...")
        #
        time.sleep(1)
        #
        sys.exit(1)
        #
    end_time = time.perf_counter()
    #
    execution_time = end_time-start_time ; execution_time = execution_time/60
    #
    print("[*] Total hosts attempted: %i " % total_hosts_tested)
    #
    print("[*] Total hosts found: %i " % total_live_hosts)
    #
    print(f"[*] Net execution time in minutes: {execution_time:0.2f}")

if(__name__ == '__main__'):
    main()