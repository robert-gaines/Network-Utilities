from scapy.arch.windows import get_windows_if_list
from pprint import pprint
import sqlite3 as sqlite
from scapy.all import *
import ipaddress
import datetime
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
pcap_writer.writerow(['TimeStamp','Source MAC','Destination MAC','IP Version','Transport','Source IP','Destination IP','Source Port','Destination Port','Source Continent','Source Country','Source City','Source Latitude','Source Longitude','Source TimeZone',' Destination Continent','Destination Country','Destination City','Destination Latitude','Destination Longitude','Destination TimeZone'])    
#
connection = sqlite.connect('ip_geodata.db')

def QueryIPV4(connection,subject_ipaddress):
    #
    results = "NULL"
    #
    candidate_ranges = {}
    #
    addr_segments = subject_ipaddress.split('.')
    #
    unique_octets_with_wildcard_opr = addr_segments[0]+'.'+addr_segments[1]+'%.%'
    #
    cursor = connection.cursor()
    #
    sql_query = "SELECT * FROM IPV4GEODATA WHERE network like '%s' " % unique_octets_with_wildcard_opr 
    #
    cursor.execute(sql_query)
    #
    query_results = cursor.fetchall()
    #
    for q in query_results:
        #
        entry = q[0]
        #
        network = q[2]
        #
        candidate_ranges[entry] = list(ipaddress.ip_network(network))
        #
    subject_ipaddress = ipaddress.IPv4Address(subject_ipaddress)
    #
    matching_entry = ''
    #
    for addr_range in candidate_ranges:
        #
        if(subject_ipaddress in candidate_ranges[addr_range]):
            #
            #print("[*] Located: %s:%s " % (subject_ipaddress,addr_range))
            #
            matching_entry = addr_range
            #
    if(matching_entry == ''):
        #
        #print("[!] Failed to identify a corresponding address range within the database")
        #
        return results
        #
    else:
        #
        geo_query = "SELECT * FROM IPV4GEODATA WHERE entry_id='%s' " % matching_entry
        #
        cursor.execute(geo_query)
        #
        geo_query_results = cursor.fetchall()
        #
        geo_query_results = list(geo_query_results)
        #
        geoname_id = geo_query_results[0][1]
        #
        network_range = geo_query_results[0][2]
        postal_code   = geo_query_results[0][3]
        latitude      = geo_query_results[0][4]
        longitude     = geo_query_results[0][5]
        accuracy      = geo_query_results[0][6]
        #
        #print("[~] Querying city database for geoname ID: %i " % geoname_id)
        #
        try:
            #
            city_query = "SELECT * FROM CITYDATA WHERE geoname_id='%i' " %  geoname_id 
            #
            cursor.execute(city_query)
            #
            city_query_results = cursor.fetchall()
            #
            city_query_results = list(city_query_results)
            #
            continent = city_query_results[0][2]
            country   = city_query_results[0][3]
            city      = city_query_results[0][4]
            timezone  = city_query_results[0][5]
            #
            """
            print("Subject IP:    %s " % subject_ipaddress)
            print("Network Range: %s " % network_range)
            print("Postal Code:   %s " % postal_code)
            print("Latitude:      %s " % latitude)
            print("longitude:     %s " % longitude)
            print("Accuracy (m):  %s " % accuracy)
            print("Continent:     %s " % continent)
            print("Country:       %s " % country)
            print("City:          %s " % city)
            print("Timezone:      %s " % timezone)
            """
            #
            results = [latitude,longitude,continent,country,city,timezone]
            #
            return results
            #
        except:
            #
            return results

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
            src_latitude  = 'Local/Unknown'
            src_longitude = 'Local/Unknown'
            src_continent = 'Local/Unknown'
            src_country   = 'Local/Unknown'
            src_city      = 'Local/Unknown'
            src_timezone  = 'Local/Unknown'
            #
            dst_latitude  = 'Local/Unknown'
            dst_longitude = 'Local/Unknown'
            dst_continent = 'Local/Unknown'
            dst_country   = 'Local/Unknown'
            dst_city      = 'Local/Unknown'
            dst_timezone  = 'Local/Unknown'
            #
            if(packet.haslayer('Ethernet')):
                #
                timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
                #
                source_mac = packet['Ethernet'].src
                destination_mac = packet['Ethernet'].dst
                #
                #print("Source MAC:      %s " % source_mac)
                #print("Destination MAC: %s " % destination_mac)
                #
                if(packet.haslayer('IP')):
                    #
                    ip_version = packet['IP'].version
                    src_ip     = packet['IP'].src
                    dst_ip     = packet['IP'].dst
                    #
                    destination_geo_data = QueryIPV4(connection,dst_ip)
                    source_geo_data      = QueryIPV4(connection,src_ip)
                    #
                    if(destination_geo_data != 'NULL'):
                        #
                        dst_latitude  = destination_geo_data[0]
                        dst_longitude = destination_geo_data[1]
                        dst_continent = destination_geo_data[2]
                        dst_country   = destination_geo_data[3]
                        dst_city      = destination_geo_data[4]
                        dst_timezone  = destination_geo_data[5]
                        #
                    if(source_geo_data != 'NULL'):
                        #
                        src_latitude  = source_geo_data[0]
                        src_longitude = source_geo_data[1]
                        src_continent = source_geo_data[2]
                        src_country   = source_geo_data[3]
                        src_city      = source_geo_data[4]
                        src_timezone  = source_geo_data[5]
                        #
                    #print("IP Version:     %s " % ip_version)
                    #print("Source IP:      %s " % src_ip)
                    #print("Destination IP: %s " % dst_ip)
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
                            #print("Source Port:      %s " % src_port)
                            #print("Destination Port: %s " % dst_port)
                            #
                        if(packet.haslayer('UDP')):
                            #
                            transport = 'UDP'
                            #
                            src_port = packet['UDP'].sport
                            dst_port = packet['UDP'].dport
                            #
                            #print("Source Port:      %s " % src_port)
                            #print("Destination Port: %s " % dst_port)
                            #
                        pcap_writer.writerow([timestamp,source_mac,destination_mac,ip_version,transport,src_ip,dst_ip,src_port,dst_port,src_continent,src_country,src_city,src_latitude,src_longitude,src_timezone,dst_continent,dst_country,dst_city,dst_latitude,dst_longitude,dst_timezone])
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
    print("[*] Packet Sniffer with CSV transcription and GeoIP Resolution ")
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
