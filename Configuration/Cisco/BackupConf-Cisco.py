
from getpass import getpass
import paramiko
import time
import sys

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

def GenFileName(hostname):
    #
    file_name = hostname+"_"
    #
    timestamp = TimeStamp()
    #
    file_name += timestamp
    #
    file_name += ".txt"
    #
    return file_name

def main():
    #
    print("[*] Backup Single Network Device Configuration - Cisco [*]")
    #
    username = input("[+] Enter the username-> ")
    #
    password = getpass("[+] Enter the password-> ")
    #
    server = input("[+] Enter the host IP address-> ")
    #
    ssh = paramiko.SSHClient()
    #
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #
    ssh.connect(server, username=username, password=password)
    #
    session = ssh.invoke_shell()
    #
    if(session):
        #
        print("[*] Connected! ")
        #
    else:
        #
        print("[!] Connection Failure ")
        #
        sys.exit()
        #
    prompt = session.recv(1000)
    #
    print(prompt.decode('utf-8')) ; decoded_prompt = prompt.decode('utf-8')
    #
    if('>' in decoded_prompt):
        #
        session.send("en\n")
        #
        time.sleep(1)
        #
        session.send(password)
        #
        session.send('\n')
        #
    session.send("terminal length 0\n")
    #
    session.send("\n")
    #
    session.send("show run\n")
    #
    time.sleep(10)
    #
    configuration = session.recv(100000).decode('utf-8') 
    #
    time.sleep(10)
    #
    hostname = ''
    #
    if('>' in decoded_prompt):
        #
        hostname = decoded_prompt.strip('>')
        #
        if('\r' in hostname):
            #
            hostname = hostname.strip('\r')
            #
        if('\n' in hostname):
            #
            hostname = hostname.strip('\n')
            #
    elif('#' in decoded_prompt):
        #
        hostname = decoded_prompt.strip('#')
        #
        if('\r' in hostname):
            #
            hostname = hostname.strip('\r')
            #
        if('\n' in hostname):
            #
            hostname = hostname.strip('\n')
            #
    else:
        #
        hostname = server
        #
    fileName = GenFileName(hostname)
    #
    print(configuration)
    #
    f = open(fileName,'+w')
    #
    f.write(configuration)
    # 
    f.close()
    #
    print("[*] Closing session ") ; time.sleep(1)
    #
    session.close()

main()
