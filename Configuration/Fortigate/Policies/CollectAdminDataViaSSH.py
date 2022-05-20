#!/usr/bin/env python3

_AUTH_ = 'RWG' # 05192022

from asyncore import write
from netmiko import ConnectHandler
from getpass import getpass
import cryptography
import xlsxwriter
import warnings
import random
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

def RetrieveAdministrators(addr,username,password,port):
    retrievedAdministrators    = False
    administrators       = {}
    try:
        session_parameters = {
                                'device_type': 'fortinet',
                                'host'       : addr,
                                'username'   : username,
                                'password'   : password,
                                'port'       : port
                            }
        session = ConnectHandler(**session_parameters)
        host_cmd = session.send_command('sh sys global | grep hostname')
        try:
            host_cmd = host_cmd.split(' ')[6]
            host_cmd = host_cmd.rstrip('\n')
            host_cmd = host_cmd.lstrip('"')
            host_cmd = host_cmd.rstrip('"')
            filename = GenFileName(host_cmd)
        except:
            filename = GenFileName(addr)
        cmd = session.send_command('sh sys admin')
        raw_administrators = cmd.split('next')
        for admin in raw_administrators:
            entries            = admin.split('\n')
            admin_id           = str(random.randint(1,65535))
            admin_name         = ''
            admin_profile      = ''
            trusted_host_one   = ''
            trusted_host_two   = '' 
            trusted_host_three = '' 
            trusted_host_four  = '' 
            trusted_host_five  = '' 
            trusted_host_six   = '' 
            trusted_host_seven = '' 
            trusted_host_eight = '' 
            trusted_host_nine  = '' 
            trusted_host_ten   = '' 
            for entry in entries:
                if('edit' in entry):
                    name_segments = entry.split(' ')
                    admin_name = name_segments[5]
                if('trusthost1' in entry):
                    name_segments        = entry.split('trusthost1')
                    trusted_host_one     = name_segments[1]
                    trusted_host_one     = trusted_host_one.lstrip(' ')
                    trusted_host_one     = trusted_host_one.replace(' ','/')
                if('trusthost2' in entry):
                    name_segments        = entry.split('trusthost2')
                    trusted_host_two     = name_segments[1]
                    trusted_host_two     = trusted_host_two.lstrip(' ')
                    trusted_host_two     = trusted_host_two.replace(' ','/')
                if('trusthost3' in entry):
                    name_segments        = entry.split('trusthost3')
                    trusted_host_three   = name_segments[1]
                    trusted_host_three   = trusted_host_three.lstrip(' ')
                    trusted_host_three   = trusted_host_three.replace(' ','/')
                if('trusthost4' in entry):
                    name_segments        = entry.split('trusthost4')
                    trusted_host_four    = name_segments[1]
                    trusted_host_four    = trusted_host_four.lstrip(' ')
                    trusted_host_four    = trusted_host_four.replace(' ','/')
                if('trusthost5' in entry):
                    name_segments        = entry.split('trusthost5')
                    trusted_host_five    = name_segments[1]
                    trusted_host_five    = trusted_host_five.lstrip(' ')
                    trusted_host_five    = trusted_host_five.replace(' ','/')
                if('trusthost6' in entry):
                    name_segments        = entry.split('trusthost6')
                    trusted_host_six     = name_segments[1]
                    trusted_host_six     = trusted_host_six.lstrip(' ')
                    trusted_host_six     = trusted_host_six.replace(' ','/')
                if('trusthost7' in entry):
                    name_segments        = entry.split('trusthost7')
                    trusted_host_seven   = name_segments[1]
                    trusted_host_seven   = trusted_host_seven.lstrip(' ')
                    trusted_host_seven   = trusted_host_seven.replace(' ','/')
                if('trusthost8' in entry):
                    name_segments        = entry.split('trusthost8')
                    trusted_host_eight   = name_segments[1]
                    trusted_host_eight   = trusted_host_eight.lstrip(' ')
                    trusted_host_eight   = trusted_host_eight.replace(' ','/')
                if('trusthost9' in entry):
                    name_segments        = entry.split('trusthost9')
                    trusted_host_nine    = name_segments[1]
                    trusted_host_nine    = trusted_host_nine.lstrip(' ')
                    trusted_host_nine    = trusted_host_nine.replace(' ','/')
                if('trusthost10' in entry):
                    name_segments        = entry.split('trusthost10')
                    trusted_host_ten     = name_segments[1]
                    trusted_host_ten     = trusted_host_ten.lstrip(' ')
                    trusted_host_ten     = trusted_host_ten.replace(' ','/')
                if('accprofile' in entry):
                    acc_segments         = entry.split('accprofile')
                    admin_profile        = acc_segments[1]
                    #
            if(admin_id not in administrators.keys()):
                administrators[admin_id] = [admin_name,
                                            admin_profile,
                                            trusted_host_one,
                                            trusted_host_two,
                                            trusted_host_three,
                                            trusted_host_four,
                                            trusted_host_five,
                                            trusted_host_six,
                                            trusted_host_seven,
                                            trusted_host_eight,
                                            trusted_host_nine,
                                            trusted_host_ten]
        time.sleep(1)
        admin_workbook  = xlsxwriter.Workbook(filename)
        admin_worksheet = admin_workbook.add_worksheet(host_cmd)
        admin_worksheet.write('A1','Administrator')
        admin_worksheet.write('B1','Profile')
        admin_worksheet.write('C1','Trusted Host 1')
        admin_worksheet.write('D1','Trusted Host 2')
        admin_worksheet.write('E1','Trusted Host 3')
        admin_worksheet.write('F1','Trusted Host 4')
        admin_worksheet.write('G1','Trusted Host 5')
        admin_worksheet.write('H1','Trusted Host 6')
        admin_worksheet.write('I1','Trusted Host 7')
        admin_worksheet.write('J1','Trusted Host 8')
        admin_worksheet.write('K1','Trusted Host 9')
        admin_worksheet.write('L1','Trusted Host 10')
        row_index = 2
        col_indeces = ['A','B','C','D','E','F','G','H','I','J','K','L']
        for admin in administrators.keys():
            print("[~] Processing:",administrators[admin][0])
            current_administrator = administrators[admin]
            admin_index = 0
            for index in col_indeces:
                write_index = index+str(row_index)
                write_value = current_administrator[admin_index]
                write_value = write_value.rstrip('"')
                write_value = write_value.lstrip(' "')
                admin_worksheet.write(write_index,write_value)
                admin_index += 1
            row_index += 1
        admin_workbook.close()
        retrievedAdministrators = True
        return retrievedAdministrators
    except Exception as e:
        print("[!] Error: %s " % e)
        return retrievedAdministrators

def main():
    print("[*] Python - FortiGate - Administrator Account - Data Collection Utility")
    addr      = input("[+] Enter the IP/FQDN of the appliance->  ")
    username  = input("[+] Enter the username-> ")
    password  = getpass("[+] Enter the account password-> ")
    conn_port = IdentifySSHPort(addr)
    result    = RetrieveAdministrators(addr,username,password,conn_port)
    if(result):
        print("[*] Successfully retrieved administrator data from the appliance at: %s " % addr)
    else:
        print("[!] Failed to retrieve administrator data from the appliance at: %s " % addr)

if(__name__ == '__main__'):
    main()