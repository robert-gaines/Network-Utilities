#!/usr/bin/env python3

_AUTH_ = 'RWG' # 05062022

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    import subprocess
    import requests
    import random
    import time
    import sys
    import os
except Exception as e:
    print("[!] Library import error: %s " % e)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
Methods
-------
-> GetInterfaces
-> GetSessions
-> CreateSession
-> StartSession
-> StopSession
-> DownloadSession
-> DeleteSession
-> SetParameters
'''

class Window(QWidget):

    # Create a packet capture session on the appliance
    def CreateSession(self):
        current_interface = self.appliance_interfaces.currentText()
        session_id        = random.randint(1,9999)
        json              = {
                                'id':session_id,
                                'status':'enable',
                                'interface':current_interface,
                                'logtraffic':'all',
                                'max-packet-count':'10000'
                            }
        headers = {'Authorization': 'Bearer {}'.format(self.key)}
        device_url = "https://{0}:{1}/api/v2/cmdb/firewall/sniffer?access_token={2}".format(self.addr,self.port,self.key)
        response   = requests.post(device_url, headers=headers, json=json, timeout=3, verify=False)
        if(response.status_code == 200):
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Created packet sniffer session ID: %i on interface: %s " % (session_id,current_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()
            self.GetSessions()
        else:
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Failed to create a packet capture session")
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()

    # Starts an existing packet capture session on the appliance
    def StartSession(self):
        current_session   = self.capture_sessions.currentText()
        session_interface = current_session.split('-')[1]
        session_id        = current_session.split('-')[0]
        session_id        = int(session_id)
        json              = {
                                'mkey':session_id,
                            }
        headers = {'Authorization': 'Bearer {}'.format(self.key)}
        device_url = "https://{0}:{1}/api/v2/monitor/system/sniffer/start?access_token={2}".format(self.addr,self.port,self.key)
        response = requests.post(device_url, headers=headers, json=json, timeout=3, verify=False)
        if(response.status_code == 200):
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Packet sniffer session ID: %i started on interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button = dialogue.exec()
        else:
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Failed to start packet sniffer session ID: %i on interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()

    # Stops an existing pcaket capture session on the appliance
    def StopSession(self):
        current_session   = self.capture_sessions.currentText()
        session_interface = current_session.split('-')[1]
        session_id        = current_session.split('-')[0]
        session_id        = int(session_id)
        json              = {
                                'mkey':session_id,
                            }
        headers    = {'Authorization': 'Bearer {}'.format(self.key)}
        device_url = "https://{0}:{1}/api/v2/monitor/system/sniffer/stop?access_token={2}".format(self.addr,self.port,self.key)
        response   = requests.post(device_url, headers=headers, json=json, timeout=3, verify=False)
        if(response.status_code == 200):
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Packet sniffer session ID: %i stopped on interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()
        else:
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Failed to stop packet sniffer session ID: %i on interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()

    # Retrieves the PCAP file from the appliance
    def DownloadSession(self):
        current_session   = self.capture_sessions.currentText()
        session_interface = current_session.split('-')[1]
        session_id        = current_session.split('-')[0]
        session_id        = int(session_id)
        try:
            headers    = {'Authorization': 'Bearer {}'.format(self.key)}
            del_url    = "https://{0}:{1}/api/v2/monitor/system/sniffer/download?mkey={2}&access_token={3}".format(self.addr,self.port,session_id,self.key)
            response   = requests.get(del_url, headers=headers, timeout=3, verify=False)
            filename   = self.GenerateFilename()
            with open(filename,'wb') as binarywriter:
                binarywriter.write(response.content)
            if(response.status_code == 200):
                dialogue = QMessageBox(self)
                dialogue.setWindowTitle("Alert")
                dialogue.setText("Successfully retrieved PCAP from session ID: %i on interface: %s \n Capture file identified as: \n %s" % (session_id,session_interface,filename))
                dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
                button   = dialogue.exec()
            else:
                dialogue = QMessageBox(self)
                dialogue.setWindowTitle("Alert")
                dialogue.setText("Failed to retrieve PCAP from session ID: %i on interface: %s " % (session_id,session_interface))
                dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
                button   = dialogue.exec()
        except:
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Error retrieving PCAP from session ID: %i on interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()

    # Deletes an existing packet capture session on the appliance
    def DeleteSession(self):
        current_session   = self.capture_sessions.currentText()
        session_interface = current_session.split('-')[1]
        session_id        = current_session.split('-')[0]
        session_id        = int(session_id)
        headers    = {'Authorization': 'Bearer {}'.format(self.key)}
        del_url    = "https://{0}:{1}/api/v2/cmdb/firewall/sniffer/{2}?access_token={3}".format(self.addr,self.port,session_id,self.key)
        response   = requests.delete(del_url, headers=headers, timeout=3, verify=False)
        if(response.status_code == 200):
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Packet sniffer session ID: %i was deleted for interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()
            self.GetSessions()
        else:
            dialogue = QMessageBox(self)
            dialogue.setWindowTitle("Alert")
            dialogue.setText("Failed to delete packet sniffer session ID: %i on interface: %s " % (session_id,session_interface))
            dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
            button   = dialogue.exec()

    # Test connectivity with the appliance ; establishes connectivity parameters
    def SetParameters(self):
        self.addr = self.appliance_address.text()
        self.port = self.management_port.text()
        self.key  = self.api_key.text()
        try:
            headers = {'Authorization': 'Bearer {}'.format(self.key)}
            device_url = "https://{0}:{1}/api/v2/cmdb/system/global?access_token={2}".format(self.addr,self.port,self.key)
            response = requests.get(device_url, headers=headers, timeout=3, verify=False)
            if(response.status_code == 200):
                self.hostname = self.GetApplianceHostname()
                dialogue      = QMessageBox(self)
                dialogue.setWindowTitle("Alert")
                dialogue.setText("Established contact with the appliance identified as: %s " % self.hostname )
                dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
                button = dialogue.exec()
                self.GetInterfaces()
                self.GetSessions()
        except:
                dialogue = QMessageBox(self)
                dialogue.setWindowTitle("Alert")
                dialogue.setText("Failed to establish contact with the appliance")
                dialogue.setStyleSheet("background-color: none; color: black; border: 2px black solid")
                button   = dialogue.exec()

    # Retrieves a list of interfaces from the appliance
    def GetInterfaces(self):
        headers  = {'Authorization': 'Bearer {}'.format(self.key)}
        intf_url = "https://{0}:{1}/api/v2/cmdb/system/interface?access_token={2}".format(self.addr,self.port,self.key)
        response = requests.get(intf_url,headers=headers,timeout=3,verify=False)
        if(response.status_code == 200):
            content = response.json()
            results = content['results']
            for item in results:
                self.appliance_interfaces.addItem(item['name'])
            self.appliance_interfaces.update()

    # Retrieves a list of existing packet capture sessions on the appliance
    def GetSessions(self):
        self.capture_sessions.clear()
        headers  = {'Authorization': 'Bearer {}'.format(self.key)}
        ses_url  = "https://{0}:{1}/api/v2/cmdb/firewall/sniffer?access_token={2}".format(self.addr,self.port,self.key)
        response = requests.get(ses_url,headers=headers,timeout=3,verify=False)
        if(response.status_code == 200):
            response = response.json()
            data     = response['results']
            for entry in data:
                session_id  = entry['id']
                session_int = entry['interface']
                session     = str(session_id)+'-'+session_int
                self.capture_sessions.addItem(session)
            self.capture_sessions.update()

    # Retrieve the appliance's system name
    def GetApplianceHostname(self):
        headers    = {'Authorization': 'Bearer {}'.format(self.key)}
        device_url = "https://{0}:{1}/api/v2/cmdb/system/global?access_token={2}".format(self.addr,self.port,self.key)
        response = requests.get(device_url, headers=headers, timeout=3, verify=False)
        if(response.status_code == 200):
            host_data = response.json()
            appliance_hostname = host_data['results']['hostname']
            return appliance_hostname
        else:
            return "Unidentified_Firewall"

    # Generate a filename for the PCAP file
    def GenerateFilename(self):
        current_session = self.capture_sessions.currentText()
        file_name  = self.hostname+"_"
        file_name += current_session+"_"  
        timestamp = time.ctime()
        replace_colons = timestamp.replace(":",'_')
        final_timestamp = replace_colons.replace(" ","_")
        final_timestamp += ".pcap"
        file_name += final_timestamp
        return file_name

    # Clear the text input fields
    def ResetFields(self):
        self.appliance_address.setText("")
        self.management_port.setText("")
        self.api_key.setText("")

    # Close the application
    def Terminate(self):
        sys.exit(1)

    def __init__(self,parent=None):
        #
        super().__init__(parent)
        #
        QMainWindow.__init__(self)
        QWidget.__init__(self)
        QLabel.__init__(self)
        #
        self.setWindowTitle('Fortigate Packet Capture Manager')
        self.setGeometry(400,200,500,100)
        self.setStyleSheet("background-color: darkgray; border: 2px black solid")
        #
        self.appliance_address_label           = QLabel("Security Appliance Address")
        self.appliance_address_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                    
        self.appliance_address                 = QLineEdit()                                          
        self.appliance_address.setPlaceholderText("(IP Address")
        self.appliance_address.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.management_port_label           = QLabel("Management Port")
        self.management_port_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                    
        self.management_port                 = QLineEdit()                                          
        self.management_port.setPlaceholderText("(Port)")
        self.management_port.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.api_key_label = QLabel("API Key")
        self.api_key_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                    
        self.api_key = QLineEdit()                                          
        self.api_key.setPlaceholderText("(Key)")
        self.api_key.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.set_parameters_button = QPushButton("Set Parameters", self)
        self.set_parameters_button.setGeometry(100,100,600,400)
        self.set_parameters_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: Blue; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.appliance_interfaces_label = QLabel("Firewall Interfaces")
        self.appliance_interfaces_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.appliance_interfaces = QComboBox()
        self.appliance_interfaces.setStyleSheet("height: 25px; width: 25px; background-color: Black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.appliance_interfaces.setPlaceholderText('Firewall Interfaces')
        #
        self.capture_sessions_label = QLabel("Active Packet Capture Sessions")
        self.capture_sessions_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.capture_sessions = QComboBox()
        self.capture_sessions.setStyleSheet("height: 25px; width: 25px; background-color: Black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.download_pcap_button = QPushButton("Download PCAP", self)
        self.download_pcap_button.setGeometry(100,100,600,400)
        self.download_pcap_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: Blue; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.delete_capture_button = QPushButton("Delete Sniffer", self)
        self.delete_capture_button.setGeometry(100,100,600,400)
        self.delete_capture_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: Red; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.create_capture_button = QPushButton("Create Sniffer", self)
        self.create_capture_button.setGeometry(100,100,600,400)
        self.create_capture_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: Green; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.stop_capture_button = QPushButton("Stop Sniffer", self)
        self.stop_capture_button.setGeometry(100,100,600,400)
        self.stop_capture_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: Red; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.start_capture_button = QPushButton("Start Sniffer", self)
        self.start_capture_button.setGeometry(100,100,600,400)
        self.start_capture_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: Green; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setGeometry(100,100,600,400)
        self.cancel_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: white; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setGeometry(100,100,600,400)
        self.reset_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: black; color: white; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        main_layout                       = QFormLayout()
        self.vertical_data_box            = QVBoxLayout()
        self.top_horizontal_data_box      = QHBoxLayout()
        self.middle_horizontal_data_box   = QHBoxLayout()
        self.bottom_horizontal_data_box   = QHBoxLayout()
        #
        self.vertical_data_box.addWidget(self.appliance_address_label)
        self.vertical_data_box.addWidget(self.appliance_address)
        self.vertical_data_box.addWidget(self.management_port_label)
        self.vertical_data_box.addWidget(self.management_port)
        self.vertical_data_box.addWidget(self.api_key_label)
        self.vertical_data_box.addWidget(self.api_key)
        self.vertical_data_box.addWidget(self.set_parameters_button)
        self.vertical_data_box.addWidget(self.appliance_interfaces_label)
        self.vertical_data_box.addWidget(self.appliance_interfaces)
        self.vertical_data_box.addWidget(self.capture_sessions_label)
        self.vertical_data_box.addWidget(self.capture_sessions)
        self.vertical_data_box.addWidget(self.download_pcap_button)
        #
        self.top_horizontal_data_box.addWidget(self.delete_capture_button)
        self.top_horizontal_data_box.addWidget(self.create_capture_button)
        self.middle_horizontal_data_box.addWidget(self.stop_capture_button)
        self.middle_horizontal_data_box.addWidget(self.start_capture_button)
        self.bottom_horizontal_data_box.addWidget(self.cancel_button)
        self.bottom_horizontal_data_box.addWidget(self.reset_button)
        #
        main_layout.addRow(self.vertical_data_box)
        main_layout.addRow(self.top_horizontal_data_box)
        main_layout.addRow(self.middle_horizontal_data_box)
        main_layout.addRow(self.bottom_horizontal_data_box)
        #
        self.set_parameters_button.clicked.connect(self.SetParameters)
        self.download_pcap_button.clicked.connect(self.DownloadSession)
        self.create_capture_button.clicked.connect(self.CreateSession)
        self.start_capture_button.clicked.connect(self.StartSession)
        self.stop_capture_button.clicked.connect(self.StopSession)
        self.delete_capture_button.clicked.connect(self.DeleteSession)
        self.reset_button.clicked.connect(self.ResetFields)
        self.cancel_button.clicked.connect(self.Terminate)
        #
        self.setLayout(main_layout)

if(__name__ == '__main__'):
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec_())
