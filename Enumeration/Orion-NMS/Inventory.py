#!/usr/bin/env python3

from getpass import getpass
import xlsxwriter
import orionsdk
import time
import sys

bas_mgmt_nodes     = []
bas_ups_nodes      = []
bas_camera_nodes   = []
bas_hvac_nodes     = []
bas_rtac_nodes     = []
bas_el_meter_nodes = []

def TimeStamp():
    #
    var = time.ctime()
    #
    sans_colons = var.replace(":","_")
    #
    sans_spaces = sans_colons.replace(" ","_")
    #
    timestamp = sans_spaces
    #
    return timestamp

def GenFileName():
    #
    file_name = "SW_BAS_Inventory_"
    #
    timestamp = TimeStamp()
    #
    file_name += timestamp
    #
    file_name += ".xlsx"
    #
    return file_name

def SessionConnect(username,password,server):
    #
    try:
        #
        print("[*] Attempting connection to the Orion Server... ") ; time.sleep(1)
        #
        s = orionsdk.SwisClient(server,username,password)
        #
        if(s):
            #
            print("[*] Connection established! ")
            #
        return s
        #
    except Exception as e:
        #
        print("[!] Server Connection Error: %s " % e)
        #
        sys.exit(0)

def GatherNodes(s):
    #
    unique_nodes = []
    #
    results = s.query("SELECT NODEID,NODENAME,VENDOR,MACHINETYPE,IP,NODES.INTERFACES.PHYSICALADDRESS FROM ORION.NODES")
    #
    for row in results['results']:
        #
        node_id        = row['NODEID']
        node_name      = row['NODENAME']
        node_vendor    = row['VENDOR']
        node_type      = row['MACHINETYPE']
        ip             = row['IP']
        mac            = row['PHYSICALADDRESS']
        #
        # Node | Name | Type | IP | MAC
        #
        ups_anomalies  = ['Orion01','Orion02','FAIS-BAS-5585_PRIMARY','FAIS-BAS-5585_SECONDARY','BASBACKUP','192.168.219.1']
        hvac_anomalies = ['FAIS013.ad.wsu.edu']
        #
        if('192.168.225.' in ip and (node_id not in unique_nodes)):
            #
            entry = [node_id,node_name,node_vendor,node_type,ip,mac]
            #
            bas_mgmt_nodes.append(entry)
            #
            unique_nodes.append(node_id)
            #
        if(('192.168.219.' in ip) and (node_id not in unique_nodes) and (node_name not in ups_anomalies)):
            #
            entry = [node_id,node_name,node_vendor,node_type,ip,mac]
            #
            bas_ups_nodes.append(entry)
            #
            unique_nodes.append(node_id)
            #
        if('10.160.' in ip and (node_id not in unique_nodes)):
            #
            entry = [node_id,node_name,node_vendor,node_type,ip,mac]
            #
            bas_camera_nodes.append(entry)
            #
            unique_nodes.append(node_id)
            #
        if(('192.168.224.' in ip and node_type is not 'Windows 2008 R2 Server') and (node_id not in unique_nodes) and (node_name not in hvac_anomalies)):
            #
            entry = [node_id,node_name,node_vendor,node_type,ip,mac]
            #
            bas_hvac_nodes.append(entry)
            #
            unique_nodes.append(node_id)
            #
        if(('10.160.0.' in ip or '192.168.218.' in ip) and (node_id not in unique_nodes)):
            #
            entry = [node_id,node_name,node_vendor,node_type,ip,mac]
            #
            bas_rtac_nodes.append(entry)
            #
            unique_nodes.append(node_id)
            #
        if(('192.168.220.' in ip) and (node_id not in unique_nodes)):
            #
            entry = [node_id,node_name,node_vendor,node_type,ip,mac]
            #
            bas_el_meter_nodes.append(entry)
            #
            unique_nodes.append(node_id)

def CreateInventory():
    #
    fileName  = GenFileName()
    #
    workbook  = xlsxwriter.Workbook(fileName)
    #
    worksheet_bas_mgmt        = workbook.add_worksheet('Management Devices')
    worksheet_bas_ups_nodes   = workbook.add_worksheet('BAS UPS Devices')
    worksheet_camera_nodes    = workbook.add_worksheet('Cameras')
    worksheet_hvac_nodes      = workbook.add_worksheet('HVAC Panels')
    worksheet_rtac_nodes      = workbook.add_worksheet('RTAC Devices')
    worksheet_el_meter_nodes  = workbook.add_worksheet('EL Meters')
    #
    workbooks = [worksheet_bas_mgmt,
                 worksheet_bas_ups_nodes,
                 worksheet_camera_nodes,
                 worksheet_hvac_nodes,
                 worksheet_rtac_nodes,
                 worksheet_el_meter_nodes
                 ]
    #
    for w in workbooks:
        #
        title_format = workbook.add_format({'bold': True})
        #
        w.set_column('A:A',8)
        w.set_column('B:B',40)
        w.set_column('C:C',16)
        w.set_column('D:D',35)
        w.set_column('E:E',25)
        w.set_column('F:F',25)
        w.write('A1','Node ID',title_format)
        w.write('B1','Node Name',title_format)
        w.write('C1','Device Vendor',title_format)
        w.write('D1','Device Type',title_format)
        w.write('E1','IPv4 Address',title_format)
        w.write('F1','MAC',title_format)
        #
    node_index = 2
    name_index = 2
    vendor_index = 2
    type_index = 2
    ip_index = 2
    mac_index = 2
    #
    for b in bas_mgmt_nodes:
        #
        node_id        = b[0]         ; node_cursor    = "A"+str(node_index)
        node_name      = b[1]         ; name_cursor    = "B"+str(name_index)
        node_vendor    = b[2]         ; vendor_cursor  = "C"+str(vendor_index)
        node_type      = b[3]         ; type_cursor    = "D"+str(type_index)
        ip             = b[4]         ; ip_cursor      = "E"+str(ip_index)
        mac            = b[5]         ; mac_cursor     = "F"+str(mac_index)
        #
        worksheet_bas_mgmt.write(node_cursor,node_id)
        worksheet_bas_mgmt.write(name_cursor,node_name)
        worksheet_bas_mgmt.write(vendor_cursor,node_vendor)
        worksheet_bas_mgmt.write(type_cursor,node_type)
        worksheet_bas_mgmt.write(ip_cursor,ip)
        worksheet_bas_mgmt.write(mac_cursor,mac)
        #
        node_index += 1
        name_index += 1
        type_index += 1
        ip_index   += 1
        mac_index  += 1
        #
    node_index = 2
    name_index = 2
    vendor_index = 2
    type_index = 2
    ip_index = 2
    mac_index = 2
    #
    for b in bas_ups_nodes:
        #
        node_id        = b[0]         ; node_cursor    = "A"+str(node_index)
        node_name      = b[1]         ; name_cursor    = "B"+str(name_index)
        node_vendor    = b[2]         ; vendor_cursor  = "C"+str(vendor_index)
        node_type      = b[3]         ; type_cursor    = "D"+str(type_index)
        ip             = b[4]         ; ip_cursor      = "E"+str(ip_index)
        mac            = b[5]         ; mac_cursor     = "F"+str(mac_index)
        #
        worksheet_bas_ups_nodes.write(node_cursor,node_id)
        worksheet_bas_ups_nodes.write(name_cursor,node_name)
        worksheet_bas_ups_nodes.write(vendor_cursor,node_vendor)
        worksheet_bas_ups_nodes.write(type_cursor,node_type)
        worksheet_bas_ups_nodes.write(ip_cursor,ip)
        worksheet_bas_ups_nodes.write(mac_cursor,mac)
        #
        node_index += 1
        name_index += 1
        type_index += 1
        ip_index   += 1
        mac_index  += 1
        #
    node_index = 2
    name_index = 2
    vendor_index = 2
    type_index = 2
    ip_index = 2
    mac_index = 2
    #
    for b in bas_camera_nodes:
        #
        node_id        = b[0]         ; node_cursor    = "A"+str(node_index)
        node_name      = b[1]         ; name_cursor    = "B"+str(name_index)
        node_vendor    = b[2]         ; vendor_cursor  = "C"+str(vendor_index)
        node_type      = b[3]         ; type_cursor    = "D"+str(type_index)
        ip             = b[4]         ; ip_cursor      = "E"+str(ip_index)
        mac            = b[5]         ; mac_cursor     = "F"+str(mac_index)
        #
        worksheet_camera_nodes.write(node_cursor,node_id)
        worksheet_camera_nodes.write(name_cursor,node_name)
        worksheet_camera_nodes.write(vendor_cursor,node_vendor)
        worksheet_camera_nodes.write(type_cursor,node_type)
        worksheet_camera_nodes.write(ip_cursor,ip)
        worksheet_camera_nodes.write(mac_cursor,mac)
        #
        node_index += 1
        name_index += 1
        type_index += 1
        ip_index   += 1
        mac_index  += 1
        #
    node_index = 2
    name_index = 2
    vendor_index = 2
    type_index = 2
    ip_index = 2
    mac_index = 2
    #
    for b in bas_hvac_nodes:
        #
        node_id        = b[0]         ; node_cursor    = "A"+str(node_index)
        node_name      = b[1]         ; name_cursor    = "B"+str(name_index)
        node_vendor    = b[2]         ; vendor_cursor  = "C"+str(vendor_index)
        node_type      = b[3]         ; type_cursor    = "D"+str(type_index)
        ip             = b[4]         ; ip_cursor      = "E"+str(ip_index)
        mac            = b[5]         ; mac_cursor     = "F"+str(mac_index)
        #
        worksheet_hvac_nodes.write(node_cursor,node_id)
        worksheet_hvac_nodes.write(name_cursor,node_name)
        worksheet_hvac_nodes.write(vendor_cursor,node_vendor)
        worksheet_hvac_nodes.write(type_cursor,node_type)
        worksheet_hvac_nodes.write(ip_cursor,ip)
        worksheet_hvac_nodes.write(mac_cursor,mac)
        #
        node_index += 1
        name_index += 1
        type_index += 1
        ip_index   += 1
        mac_index  += 1
        #
    node_index = 2
    name_index = 2
    vendor_index = 2
    type_index = 2
    ip_index = 2
    mac_index = 2
    #
    for b in bas_rtac_nodes:
        #
        node_id        = b[0]         ; node_cursor    = "A"+str(node_index)
        node_name      = b[1]         ; name_cursor    = "B"+str(name_index)
        node_vendor    = b[2]         ; vendor_cursor  = "C"+str(vendor_index)
        node_type      = b[3]         ; type_cursor    = "D"+str(type_index)
        ip             = b[4]         ; ip_cursor      = "E"+str(ip_index)
        mac            = b[5]         ; mac_cursor     = "F"+str(mac_index)
        #
        worksheet_rtac_nodes.write(node_cursor,node_id)
        worksheet_rtac_nodes.write(name_cursor,node_name)
        worksheet_rtac_nodes.write(vendor_cursor,node_vendor)
        worksheet_rtac_nodes.write(type_cursor,node_type)
        worksheet_rtac_nodes.write(ip_cursor,ip)
        worksheet_rtac_nodes.write(mac_cursor,mac)
        #
        node_index += 1
        name_index += 1
        type_index += 1
        ip_index   += 1
        mac_index  += 1
        #
    node_index = 2
    name_index = 2
    vendor_index = 2
    type_index = 2
    ip_index = 2
    mac_index = 2
    #
    for b in bas_el_meter_nodes:
        #
        node_id        = b[0]         ; node_cursor    = "A"+str(node_index)
        node_name      = b[1]         ; name_cursor    = "B"+str(name_index)
        node_vendor    = b[2]         ; vendor_cursor  = "C"+str(vendor_index)
        node_type      = b[3]         ; type_cursor    = "D"+str(type_index)
        ip             = b[4]         ; ip_cursor      = "E"+str(ip_index)
        mac            = b[5]         ; mac_cursor     = "F"+str(mac_index)
        #
        worksheet_el_meter_nodes.write(node_cursor,node_id)
        worksheet_el_meter_nodes.write(name_cursor,node_name)
        worksheet_el_meter_nodes.write(vendor_cursor,node_vendor)
        worksheet_el_meter_nodes.write(type_cursor,node_type)
        worksheet_el_meter_nodes.write(ip_cursor,ip)
        worksheet_el_meter_nodes.write(mac_cursor,mac)
        #
        node_index += 1
        name_index += 1
        type_index += 1
        ip_index   += 1
        mac_index  += 1
        #
    workbook.close()

def main():
    #
    print("[*] Node Inventory Script [*]")
    #
    username = input("[+] Server Username-> ")
    #
    password = getpass("[+] Server Password-> ")
    #
    server   = input("[+] Server-> ")
    #
    session = SessionConnect(username,password,server)
    #
    GatherNodes(session)
    #
    CreateInventory()

if(__name__ == '__main__'):
    #
    main()