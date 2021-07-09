import sqlite3 as sqlite
import ipaddress
import time
import sys
import os

def QueryIPV4(connection,subject_ipaddress):
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
            print("[*] Located: %s:%s " % (subject_ipaddress,addr_range))
            #
            matching_entry = addr_range
            #
    if(matching_entry == ''):
        #
        print("[!] Failed to identify a corresponding address range within the database")
        #
        return
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
        print("[~] Querying city database for geoname ID: %i " % geoname_id)
        #
        try:
            #
            city_data_connection = sqlite.connect('city_data.db')
            #
            city_cursor = city_data_connection.cursor()
            #
            city_query = "SELECT * FROM CITYDATA WHERE geoname_id='%i' " %  geoname_id 
            #
            city_cursor.execute(city_query)
            #
            city_query_results = city_cursor.fetchall()
            #
            city_query_results = list(city_query_results)
            #
            continent = city_query_results[0][2]
            country   = city_query_results[0][3]
            city      = city_query_results[0][4]
            timezone  = city_query_results[0][5]
            #
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
            #
            result_string = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (subject_ipaddress,network_range,postal_code,latitude,longitude,accuracy,continent,country,city,timezone)
            #
            results.write(result_string)
            #
        except:
            #
            print("[!] Failed to connect to the city database")
            #
            return

def main():
    #
    ipv4_connection = sqlite.connect('ipv4_geodata.db')
    #
    QueryIPV4(ipv4_connection,'3.211.168.29')
    #
    """
    egress_file = open('egress.csv','r')
    #
    for line in egress_file.readlines():
        #
        segments  = line.split(',')
        #
        timestamp = segments[0]
        message   = segments[2]
        #
        message_segments = message.split(' ')
        #
        try:
            source_ip = message_segments[5]
            dest_ip   = message_segments[6]
            #
            source_ip_parsed = source_ip.split('=')[1]
            dest_ip_parsed   = dest_ip.split('=')[1]
            #
            print("Source IP:      %s " % source_ip_parsed)
            print("Destination IP: %s " % dest_ip_parsed )
            #
            QueryIPV4(ipv4_connection,dest_ip_parsed)
            #
        except:
            #
            pass
    """

if(__name__ == '__main__'):
    #
    #results = open('geo_ip_egress.txt','w')
    #
    main()
    #
    #results.close()