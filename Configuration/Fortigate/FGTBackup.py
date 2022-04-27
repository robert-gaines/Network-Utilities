#!/usr/env python3

from netmiko import ConnectHandler
from getpass import getpass
import cryptography
import warnings
import socket
import time

warnings.simplefilter("ignore", cryptography.utils.CryptographyDeprecationWarning)

def TimeStamp():
    var = time.ctime()
    sans_colons = var.replace(":","_")
    sans_spaces = sans_colons.replace(" ","_")
    timestamp = sans_spaces
    return timestamp

def GenFileName(hostname):
    file_name = hostname+"_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".conf"
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

def RetrieveConfiguration(addr,username,password,port):
    retrievedConfig    = False
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
        cmd = session.send_command('sh full')
        confObj = open(filename,'w')
        confObj.write(cmd)
        confObj.close()
        retrievedConfig = True
        return retrievedConfig
    except Exception as e:
        return retrievedConfig

def main():
    print("[*] FortiGate SSH Configuration Backup Utility ")
    addr     = input("[+] Enter the firewall address-> ")
    username = input("[+] Enter the username-> ")
    password = getpass("[+] Enter the password-> ")
    print("Attempting back up of: %s " % addr)
    conn_port = IdentifySSHPort(addr)
    if(conn_port is not None):
        result = RetrieveConfiguration(addr,username,password,conn_port)
        if(result):
            print("[*] Successful configuration retrieval for: %s " % addr)
        else:
            print("[!] Failed to retrieve configuration for: %s " % addr)
    else:
        print("[!] Failed to identify an SSH port on the host: %s " % addr)

main()
    
