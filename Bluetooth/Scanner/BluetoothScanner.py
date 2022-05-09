#!/usr/bin/env python3

_AUTH_ = 'RWG' # 05082022

import bluetooth
import requests
import time
import os

class BluetoothScanner():

    def __init__(self):
        self.oui_data = {}
        self.ble_data = {}
        self.devices  = []
        self.filename = self.GenFileName()
        self.logfile  = open(self.filename,'w')
        self.current_data  = False
        self.existing_data = False

    def AddBuffer(self,obj,index):
        if(len(obj) < index):
            while(len(obj) < index):
                obj = obj+' '
            return obj
        else:
            return obj

    def GenFileName(self):
        file_name        = "BluetoothDevices_"
        timestamp        = time.ctime()
        replace_colons   = timestamp.replace(":",'_')
        final_timestamp  = replace_colons.replace(" ","_")
        final_timestamp += ".csv"
        file_name       += final_timestamp
        return file_name

    def FindDevicesWithOUI(self):
        try:
            while(True):
                print("[~] Scanning ...")
                devices = bluetooth.discover_devices(lookup_names=True)
                for device in devices:
                    mac           = device[0]
                    id            = device[1]
                    non_buffer_id = id
                    if(mac not in self.devices):
                        if(id == ''):
                            id            = 'Unidentified Device'
                            non_buffer_id = 'Unidentified Device'
                            id = self.AddBuffer(id,36)
                        if(len(id) < 36):
                            id = self.AddBuffer(id,36)
                        self.devices.append(mac)
                        mfg = self.QueryOUI(mac)
                        self.ble_data[mac] = [id,mfg]
                        log_entry = "%s,%s,%s\n" % (non_buffer_id,mac,mfg)
                        self.logfile.write(log_entry)
                os.system('cls')
                print("Name\t\t\t\t\t MAC    \t\t  Manufacturer")
                print("----\t\t\t\t\t ---    \t\t  ------------")
                for entry in self.ble_data.keys():
                    current_mac = entry
                    device_name = self.ble_data[entry][0]
                    device_mfg  = self.ble_data[entry][1]
                    print(device_name,'\t',current_mac,'\t ',device_mfg)
                time.sleep(6)
                os.system('cls')
        except KeyboardInterrupt:
            self.logfile.close()
        except Exception as e:
            print("[!] Error: %s " % e)
        finally:
            self.logfile.close()
             
    def FindDevicesWithoutOUI(self):
        try:
            while(True):
                print("[~] Scanning ...")
                devices = bluetooth.discover_devices(lookup_names=True)
                for device in devices:
                    mac           = device[0]
                    id            = device[1]
                    non_buffer_id = id
                    if(mac not in self.devices):
                        if(id == ''):
                            id = 'Unidentified Device'
                            non_buffer_id = id
                            id = self.AddBuffer(id,36)
                        if(len(id) < 36):
                            id = self.AddBuffer(id,36)
                        self.devices.append(mac)
                        self.ble_data[mac] = [id]
                        log_entry = "%s,%s\n" % (non_buffer_id,mac)
                        self.logfile.write(log_entry)
                os.system('cls')
                print("Name\t\t\t\t\t MAC")
                print("----\t\t\t\t\t ---")
                for entry in self.ble_data.keys():
                    current_mac = entry
                    device_name = self.ble_data[entry][0]
                    print(device_name,'\t',current_mac)
                time.sleep(6)
                os.system('cls')
        except KeyboardInterrupt:
            self.logfile.close()
        except Exception as e:
            print("[!] Error: %s " % e)
        finally:
            self.logfile.close()

    def CollectOUI(self):
        print("[~] Collecting OUI data from IEEE...")
        url = "http://standards-oui.ieee.org/oui.txt"
        res = requests.get(url)
        if(res.status_code == 200):
            print("[*] Established contact with IEEE ")
            print("[~] Parsing OUI data... ")
            raw = res.content
            tempfile = open('temp.txt','wb')
            tempfile.write(raw)
            tempfile.close()
            fileObj = open('temp.txt','rb')
            ouiFile = open('oui.csv','w',encoding='utf-8')
            for line in fileObj.readlines():
                line = line.decode('utf-8')
                if('(hex)' in line):
                    segments = line.split('\t')
                    oui      = segments[0].split('  ')[0]
                    oui      = oui.split('-')[0]+':'+oui.split('-')[1]+":"+oui.split('-')[2]
                    mfg      = segments[2]
                    mfg      = mfg.rstrip('\r\n')
                    oui      = str(oui)
                    mfg      = str(mfg)
                    ent      = "%s,%s\n" % (oui,mfg)
                    ouiFile.write(ent)
                    self.oui_data[oui] = mfg
            fileObj.close()
            ouiFile.close()
            os.remove('temp.txt')
            self.current_data = True
        else:
            print("[!] Failed to collect OUI data from IEEE")
            print("[~] Checking for OUI data locally...")
            if(os.path.exists("oui.csv")):
                print("[*] Located OUI data ")
                existing_data = open("oui.csv",'r')
                for entry in existing_data:
                    segments = entry.split(',')
                    oui      = segments[0]
                    mfg      = segments[1]
                    self.oui_data[oui] = mfg
                self.existing_data = True
            else:
                print("[!] Failed to collect OUI data locally")

    def QueryOUI(self,mac_addr):
        segments  = mac_addr.split(':')
        oui  = segments[0]+':'
        oui += segments[1]+':'
        oui += segments[2]
        if(oui in self.oui_data.keys()):
            manufacturer = self.oui_data[oui]
            return manufacturer
        else:
            return 'Unknown'

    def RunScanner(self):
        self.CollectOUI()
        if((self.current_data == True) or (self.existing_data == True)):
            print("[*] Scanning with OUI data")
            time.sleep(1)
            os.system('cls')
            self.FindDevicesWithOUI()
        else:
            print("[*] Scanning with OUI data")
            time.sleep(1)
            os.system('cls')
            self.FindDevicesWithoutOUI()

if(__name__ == '__main__'):
    print("""
[*] Python Bluetooth Scanner
----------------------------
          """)
    time.sleep(3)
    os.system('cls')
    scanner = BluetoothScanner()
    scanner.RunScanner()



