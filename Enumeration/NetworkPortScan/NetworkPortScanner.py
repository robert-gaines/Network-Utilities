#!/usr/bin/env python3

from queue import Queue,Empty
import xlsxwriter
import ipaddress
import threading
import socket
import time
import sys
import os

host_data   = {}

def ScanHost(address,port):
    #
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #
    try:
        #
        response = s.connect_ex((address,port))
        #
        if(response == 0):
            #
            try:
                #
                protocol = socket.getservbyport(port)
                #
            except:
                #
                protocol = "Unknown"
                #
            host_data[address].append((port,protocol))
    except:
        #
        pass
        #
    finally:
        #
        s.close()
        #
        return

def GenFileName(network):
    #
    network = network.replace('/','_')
    #
    network = network.replace('.','_')
    #
    file_name = "Results_"
    #
    file_name += network 
    #
    file_name += '_'
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

def TranscribeResults(network,results):
    #
    file_name = GenFileName(network)
    #
    workbook = xlsxwriter.Workbook(file_name)
    #
    for data in results:
        #
        protocol_column_index = 'A'
        protocol_row_index    = 2
        port_column_index     = 'B'
        port_row_index        = 2
        #
        ip_address = data
        print("Processing results for IP address: %s " % ip_address)
        ports = results[data]
        if(ports == []):
            print("No ports discovered on: %s " % ip_address)
        else:
            print("Ports discovered on: %s " % ip_address)
            current_worksheet = workbook.add_worksheet(ip_address)
            current_worksheet.set_column('A:A',20)
            current_worksheet.set_column('B:B',20)
            current_worksheet.write('A1','Protocol')
            current_worksheet.write('B1','Port')
            #
            for port in ports:
                port_number = str(port[0])
                protocol    = str(port[1])
                print("Located Port:     %s " % port_number)
                print("Located Protocol: %s " % protocol)
                #
                protocol_write_index = protocol_column_index + str(protocol_row_index)
                port_write_index     = port_column_index + str(port_row_index)
                #
                current_worksheet.write(protocol_write_index,protocol)
                current_worksheet.write(port_write_index,port_number)
                #
                protocol_row_index += 1
                port_row_index += 1
                #
    print("[*] Port scan results may be found in: %s " % file_name)
    #
    workbook.close()

def Threader(portQueue,address):
    #
    while(True):
        #
        try:
            #
            port = portQueue.get_nowait()
            #
            ScanHost(address,port)
            #
            portQueue.task_done()
            #
            if(portQueue.empty()):
                #
                return
                #
        except Empty:
            #
            return
        
def ImportFileData(configuration_file):
    #
    network_data = list()
    #
    if(os.path.exists(configuration_file)):
        fileObject = open(configuration_file,'r')
        for line in fileObject.readlines():
            network       = line.split(',')[0]
            network_range = line.split(',')[1]
            network_range = network_range.rstrip('\n')
            entry   = [network,network_range]
            network_data.append(entry)
            print("[*] Network: %s -> Network Range: %s " %(network,network_range))
        return network_data
    else:
        print("[!] Failed to locate the configuration file ")
        return

def ScanSingleHost(address):
    #
    print("[*] Scanning: %s " % address)
    #
    host_data[address] = list()
    #
    portQueue = Queue()
    #
    portRange = range(0,1025)
    #
    for port in portRange:
        #
        portQueue.put(port)
        #
    for thread_index in range(1024):
        #
        spawned_thread = threading.Thread(target=Threader,args=(portQueue,address))
        #
        spawned_thread.daemon = True
        #
        spawned_thread.start()
        #
    portQueue.join()
    #
    TranscribeResults(address,host_data)

def ScanNetwork(network):
    #
    print("[*] Scanning: %s " % network)
    #
    network_hosts = list(ipaddress.ip_network(network).hosts())
    #
    for host in network_hosts:
        #
        host = str(host)
        #
        host_data[host] = list()
        #
        portQueue = Queue()
        #
        portRange = range(0,1025)
        #
        for port in portRange:
            #
            portQueue.put(port)
            #
        for thread_index in range(1025):
            #
            spawned_thread = threading.Thread(target=Threader,args=(portQueue,host))
            #
            spawned_thread.start()
            #
        portQueue.join()
        #
        live_threads = threading.enumerate()
        #
        for thread in live_threads:
            #
            if(not thread.is_alive() and (thread is not threading.main_thread())):
                #
                print("Joining thread: ",thread)
                #
                thread.join()
                #
    TranscribeResults(network,host_data)
    
def ScanNetworks(configuration_file):
    #
    print("[*] Scanning multiple networks...")
    #
    networks = ImportFileData(configuration_file)
    #
    timeStamp = time.ctime()
    timeStamp = timeStamp.replace(" ","_")
    timeStamp = timeStamp.replace(":","_")
    dirName   = "PortScans_"+timeStamp
    #
    try:
        os.mkdir(dirName)
    except:
        pass
    #
    os.chdir(dirName)
    #
    for network in networks:
        #
        network_identity = network[0]
        network_range    = network[1] 
        #
        print("[*] Scanning: %s " % network_range)
        #
        network_hosts = list(ipaddress.ip_network(network_range).hosts())
        #
        for host in network_hosts:
            #
            host = str(host)
            #
            host_data[host] = list()
            #
            portQueue = Queue()
            #
            portRange = range(1,1025)
            #
            #print("[*] Scanning host: %s " % host)
            #
            for port in portRange:
                #
                portQueue.put(port)
                #
            for thread_index in range(1025):
                #
                spawned_thread = threading.Thread(target=Threader,args=(portQueue,host))
                #
                spawned_thread.daemon = True
                #
                spawned_thread.start()
                #
            portQueue.join()
            #
            live_threads = threading.enumerate()
            #
            for thread in live_threads:
                #
                if(not thread.is_alive() and (thread is not threading.main_thread())):
                    #
                    print("Joining thread: ",thread)
                    #
                    thread.join()
                    #
        TranscribeResults(network_range,host_data)
        #
        host_data.clear()

def main():
    #
    start_time = time.perf_counter()
    #
    print("[*] Python Network Port Scanner")
    #
    print("-------------------------------")
    #
    print("""
Port Scan Options
-----------------
1) Scan Single Host
2) Scan Single Network
3) Scan Multiple Networks
""")
    #
    option = int(input("[OPTION]>"))
    #
    if(option == 1):
        #
        host_address = input("[+] Enter the host IP Address-> ")
        #
        ScanSingleHost(host_address)
        #
    if(option == 2):
        #
        network_range = input("[+] Enter the network range in CIDR-> ")
        #
        ScanNetwork(network_range)
        #
    if(option == 3):
        #
        config_file = input("[+] Enter the name or path to the configuration file containing the networks to be scanned-> ")
        #
        ScanNetworks(config_file)
        #
    if(option not in range(1,3)):
        #
        print("[!] Unrecognized option, exiting ")
        #
        time.sleep(1)
        #
        sys.exit(1)
        #
    end_time = time.perf_counter()
    #
    execution_time = end_time-start_time ; execution_time = execution_time/60
    #
    print(f"[*] Net execution time in minutes: {execution_time:0.2f}")

if(__name__ == '__main__'):
    #
    main()
    
