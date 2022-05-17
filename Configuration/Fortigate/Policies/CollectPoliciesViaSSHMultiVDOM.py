#!/usr/bin/env python3

_AUTH_ = 'RWG' # 05102022

from asyncore import write
from netmiko import ConnectHandler
from getpass import getpass
import cryptography
import xlsxwriter
import warnings
import socket
import time

warnings.simplefilter("ignore", cryptography.utils.CryptographyDeprecationWarning)

def TimeStamp():
    var = time.ctime()
    sans_colons = var.replace(":","_")
    sans_spaces = sans_colons.replace(" ","_")
    timestamp   = sans_spaces
    return timestamp

def GenFileName(hostname):
    file_name = hostname+"_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".xlsx"
    return file_name

def IdentifySSHPort(addr):
    print("[~] Checking for ports on: %s " % addr)
    candidate_ports = [22,222,2222,2022,822]
    open_port = None
    for port in candidate_ports:
        print("Checking: %i " % port)
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            result = s.connect_ex((addr,port))
            if(result == 0):
                print("[*] Port %i is open " % port)
                open_port = port
                s.close()
                return open_port
            else:
                print("[!] Port %i is closed" % port)
        except:
            pass
        s.close()

def RetrievePolicies(addr,username,password,port):
    retrievedPolicies    = False
    policies             = {}
    try:
        session_parameters = {
                                'device_type': 'fortinet',
                                'host'       : addr,
                                'username'   : username,
                                'password'   : password,
                                'port'       : port
                                }
        session = ConnectHandler(**session_parameters)
        session.enable()
        host_cmd = session.send_command('get system status | grep Hostname:')
        try:
            host_cmd = host_cmd.split(':')[1]
            host_cmd = host_cmd.rstrip('\n')
            host_cmd = host_cmd.lstrip(' ')
            host_cmd = host_cmd.lstrip('"')
            host_cmd = host_cmd.rstrip('"')
            filename = GenFileName(host_cmd)
        except:
            filename = GenFileName(addr)
        cmd = session.send_command('conf vdom',expect_string='#') 
        cmd = session.send_command('edit root',expect_string='#') 
        cmd = session.send_command('sh firewall policy',expect_string='#')
        raw_policies = cmd.split('next')
        for raw_policy in raw_policies:
            entries        = raw_policy.split('\n')
            pol_id         = ''
            pol_name       = 'No Policy Name'
            uuid           = ''
            pol_status     = 'enable'
            src_intf       = ''
            src_addr       = ''
            dst_intf       = ''
            dst_addr       = ''
            action         = ''
            schedule       = '' 
            service        = ''
            utm_status     = ''
            ssl_prof       = ''
            av_prof        = ''
            ips_prof       = ''
            web_prof       = ''
            app_prof       = ''
            logging_status = ''
            nat            = ''
            ip_pool        = 'Not Applicable'
            ip_pool_name   = 'Not Applicable'
            user_groups    = 'None'
            comments       = ''
            for entry in entries:
                if('edit' in entry):
                    id_segments = entry.split(' ')
                    pol_id = id_segments[5]
                if('name' in entry):
                    name_segments = entry.split('name')
                    pol_name      = name_segments[1]
                if('uuid' in entry):
                    uui_segments = entry.split('uuid')
                    uuid         = uui_segments[1]
                if('status' in entry and 'utm-status' not in entry):
                    pol_status_segments = entry.split('status')
                    pol_status          = pol_status_segments[1]
                if('srcintf' in entry):
                    src_intf_segments = entry.split('srcintf')
                    src_intf          = src_intf_segments[1]
                if('dstintf' in entry):
                    dst_intf_segments = entry.split('dstintf')
                    dst_intf          = dst_intf_segments[1]
                if('srcaddr' in entry):
                    src_addr_segments = entry.split('srcaddr')
                    src_addr          = src_addr_segments[1]
                if('dstaddr' in entry):
                    dst_addr_sgements = entry.split('dstaddr')
                    dst_addr          = dst_addr_sgements[1]
                if('action' in entry):
                    action_segments = entry.split('action')
                    action          = action_segments[1]
                if('schedule' in entry):
                    schedule_segments = entry.split('schedule')
                    schedule          = schedule_segments[1]
                if('service' in entry):
                    service_segments = entry.split('service')
                    service          = service_segments[1]
                if('utm-status' in entry):
                    utm_segments = entry.split('utm-status')
                    utm_status   = utm_segments[1]
                if('ssl-ssh-profile' in entry):
                    ssl_segments = entry.split('ssl-ssh-profile')
                    ssl_prof     = ssl_segments[1]
                if('av-profile' in entry):
                    av_segments = entry.split('av-profile')
                    av_prof     = av_segments[1]
                if('ips-sensor' in entry):
                    ips_segments = entry.split('ips-sensor')
                    ips_prof     = ips_segments[1]
                if('webfilter-profile' in entry):
                    web_prof_segments = entry.split('webfilter-profile')
                    web_prof          = web_prof_segments[1]
                if('application-list' in entry):
                    app_prof_segments = entry.split('application-list')
                    app_prof          = app_prof_segments[1]
                if('logtraffic' in entry):
                    log_segments = entry.split('logtraffic')
                    logging_status = log_segments[1]
                if('comments' in entry):
                    comment_segments = entry.split('comments')
                    comments         = comment_segments[1]
                if('nat' in entry):
                    nat_segments = entry.split('nat')
                    nat = nat_segments[1]
                if('ippool' in entry):
                    ip_pool_segments = entry.split('ippool')
                    ip_pool          = ip_pool_segments[1]
                if('poolname' in entry):
                    pool_name_segments = entry.split('poolname')
                    ip_pool_name       = pool_name_segments[1]
                if('groups' in entry):
                    group_segments = entry.split('groups')
                    user_groups    = group_segments[1]
            if(uuid not in policies.keys() and uuid != ''):
                policies[uuid] = [pol_name,pol_id,uuid,pol_status,src_intf,src_addr,dst_intf,dst_addr,action,schedule,service,utm_status,ssl_prof,av_prof,ips_prof,web_prof,app_prof,nat,ip_pool,ip_pool_name,user_groups,logging_status,comments]
            time.sleep(1)
        policy_workbook  = xlsxwriter.Workbook(filename)
        policy_worksheet = policy_workbook.add_worksheet(host_cmd)
        policy_worksheet.write('A1','Policy Name')
        policy_worksheet.write('B1','Policy ID')
        policy_worksheet.write('C1','Policy UUID')
        policy_worksheet.write('D1','Policy Status')
        policy_worksheet.write('E1','Source Interface')
        policy_worksheet.write('F1','Source Address')
        policy_worksheet.write('G1','Destination Interface')
        policy_worksheet.write('H1','Destination Address')
        policy_worksheet.write('I1','Action')
        policy_worksheet.write('J1','Schedule')
        policy_worksheet.write('K1','Service')
        policy_worksheet.write('L1','UTM Status')
        policy_worksheet.write('M1','SSL Inspection Profile')
        policy_worksheet.write('N1','AntiVirus Profile')
        policy_worksheet.write('O1','IPS Profile')
        policy_worksheet.write('P1','Web Filter Profile')
        policy_worksheet.write('Q1','Application Control Profile')
        policy_worksheet.write('R1','Network Address Translation')
        policy_worksheet.write('S1','IP Pool')
        policy_worksheet.write('T1','IP Pool Name')
        policy_worksheet.write('U1','User Groups')
        policy_worksheet.write('V1','Logging Status')
        policy_worksheet.write('W1','Comments')
        row_index = 2
        col_indeces = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W']
        for policy in policies.keys():
            print("[~] Processing:",policies[policy][2])
            single_policy = policies[policy]
            pol_index = 0
            for index in col_indeces:
                write_index = index+str(row_index)
                write_value = single_policy[pol_index]
                write_value = write_value.rstrip('"')
                write_value = write_value.lstrip(' "')
                policy_worksheet.write(write_index,write_value)
                pol_index += 1
            row_index += 1
        policy_workbook.close()
        session.disconnect()
        retrievedPolicies = True
        return retrievedPolicies
    except Exception as e:
        print("[!] Error: %s " % e)
        return retrievedPolicies

def main():
    print("[*] Python FortiGate Policy Collection Utility")
    addr      = input("[+] Enter the IP/FQDN of the appliance->  ")
    username  = input("[+] Enter the username-> ")
    password  = getpass("[+] Enter the account password-> ")
    conn_port = IdentifySSHPort(addr)
    result    = RetrievePolicies(addr,username,password,conn_port)
    if(result):
        print("[*] Successfully retrieved policies from the appliance at: %s " % addr)
    else:
        print("[!] Failed to retrieve the policies from the appliance at: %s " % addr)

if(__name__ == '__main__'):
    main()