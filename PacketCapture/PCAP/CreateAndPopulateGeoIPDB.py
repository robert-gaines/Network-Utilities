#!/usr/bin/env python3

import sqlite3 as sqlite
import ipaddress
import time
import csv
import sys
import os

def LoadIPV6Data(filename,connection):
    #
    if(os.path.exists(filename)):
        #
        print("[*] Located IPV6 Geo Data File ")
        #
        fileObject = open(filename,'r')
        #
        line_index = 0
        #
        sql_statement = 'INSERT INTO IPV6GEODATA (entry_id,geoname_id,network,postal,latitude,longitude,accuracy) values (?,?,?,?,?,?,?)'
        #
        print("[~] Loading IPV6 Geo Data...")
        #
        for line in fileObject.readlines():
            #
            line_index += 1
            #
            if(line_index > 1):
                #
                segments   = line.split(',')
                #
                network    = segments[0]
                geoname_id = segments[1]
                postal     = segments[6]

                if(postal == ''):
                    postal = 'NULL' 
                latitude   = segments[7]

                longitude  = segments[8]
                accuracy   = segments[9]
                accuracy   = accuracy.rstrip('\n')
                #
                entry = (line_index,geoname_id,network,postal,latitude,longitude,accuracy)
                #
                print("Loading entry: ", entry)
                #
                connection.execute(sql_statement,entry)
                #
        connection.commit()
                
    else:
        #
        print("[!] Failed to locate IPV6 Geo Data File ")
        #
        time.sleep(1)
        #
        sys.exit(1)

def LoadIPV4Data(filename,connection):
    #
    if(os.path.exists(filename)):
        #
        print("[*] Located IPV4 Geo Data File ")
        #
        fileObject = open(filename,'r')
        #
        line_index = 0
        #
        sql_statement = 'INSERT INTO IPV4GEODATA (entry_id,geoname_id,network,postal,latitude,longitude,accuracy) values (?,?,?,?,?,?,?)'
        #
        print("[~] Loading IPV4 Geo Data...")
        #
        for line in fileObject.readlines():
            #
            line_index += 1
            #
            if(line_index > 1):
                #
                segments   = line.split(',')
                #
                network    = segments[0]
                geoname_id = segments[1]
                postal     = segments[6]

                if(postal == ''):
                    postal = 'NULL' 
                latitude   = segments[7]

                longitude  = segments[8]
                accuracy   = segments[9]
                accuracy   = accuracy.rstrip('\n')
                #
                entry = (line_index,geoname_id,network,postal,latitude,longitude,accuracy)
                #
                print("Loading entry: ", entry)
                #
                connection.execute(sql_statement,entry)
                #
        connection.commit()
                
    else:
        #
        print("[!] Failed to locate IPV4 Geo Data File ")
        #
        time.sleep(1)
        #
        sys.exit(1)

def LoadCityData(filename,connection):
    #
    if(os.path.exists(filename)):
        #
        print("[*] Located City Data File ")
        #
        fileObject = open(filename,'r',encoding='utf8')
        #
        line_index = 0
        #
        sql_statement = 'INSERT INTO CITYDATA (entry_id,geoname_id,continent,country,city,timezone) values (?,?,?,?,?,?)'
        #
        print("[~] Loading City Data...")
        #
        for line in fileObject.readlines():
            #
            line_index += 1
            #
            if(line_index > 1):
                #
                segments   = line.split(',')
                #
                geoname_id    = segments[0]
                continent     = segments[3]
                country       = segments[5]
                city          = segments[10]
                timezone      = segments[12]
                if(city == ''):
                    city = 'UNKNOWN' 
                #
                entry = (line_index,geoname_id,continent,country,city,timezone)
                #
                print("Loading entry: ", entry)
                #
                connection.execute(sql_statement,entry)
                #
        connection.commit()

def CreateIPV4Table(connection):
    #
    with connection:
        #
        connection.execute("""
            CREATE TABLE IPV4GEODATA (
                entry_id INTEGER NOT NULL PRIMARY KEY,
                geoname_id INTEGER,
                network TEXT,
                postal TEXT,
                latitude TEXT,
                longitude TEXT,
                accuracy INTEGER
            );
        """)

def CreateIPV6Table(connection):
    #
    with connection:
        #
        connection.execute("""
            CREATE TABLE IPV6GEODATA (
                entry_id INTEGER NOT NULL PRIMARY KEY,
                geoname_id INTEGER,
                network TEXT,
                postal TEXT,
                latitude TEXT,
                longitude TEXT,
                accuracy INTEGER
            );
        """)

def CreateCityTable(connection):
    #
    with connection:
        #
        connection.execute("""
            CREATE TABLE CITYDATA (
                entry_id INTEGER NOT NULL PRIMARY KEY,
                geoname_id INTEGER,
                continent TEXT,
                country TEXT,
                city TEXT,
                timezone TEXT
            );
        """)
    #
    return

def main():
    #
    ipv4_geo_data_file = 'IPV4_Cities.csv'
    #
    ipv6_geo_data_file = 'IPV6_Cities.csv'
    #
    city_data           = 'City_Locations.csv'
    #
    db_connection = sqlite.connect('ip_geodata.db')
    #
    CreateIPV4Table(db_connection)
    #
    LoadIPV4Data(ipv4_geo_data_file,db_connection)
    #
    CreateIPV6Table(db_connection)
    #
    LoadIPV6Data(ipv6_geo_data_file,db_connection)
    #
    CreateCityTable(db_connection)
    #
    LoadCityData(city_data,db_connection)
    #
    db_connection.close()    

if(__name__ =='__main__'):
    #
    main()