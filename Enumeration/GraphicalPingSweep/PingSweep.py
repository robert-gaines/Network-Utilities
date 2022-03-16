#!/usr/bin/env python3

from concurrent.futures import thread


try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    import subprocess
    import ipaddress
    import logging
    import time
    import sys
    import os
except Exception as e:
    print("[!] Library import error: %s " % e)

logging.basicConfig(format="%(message)s", level=logging.INFO)

class PingWorker(QObject):        

    target_status_down = pyqtSignal(object)
    target_status_up   = pyqtSignal()

    def __init__(self,target):
        super().__init__()
        self.target = target

    def SendPing(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if(os.name == 'nt'):
            output = subprocess.Popen(['ping','-n','1','-w','150',str(self.target)],startupinfo=startupinfo,stdout=subprocess.PIPE).communicate()[0]
        else:
            output = subprocess.Popen(['ping','-c','1','-w','150',str(self.target)],startupinfo=startupinfo,stdout=subprocess.PIPE).communicate()[0]
        if('Reply' in output.decode('utf-8')):
            self.target_status_up.emit()
        else:
            self.target_status_down.emit(self.target)

class Window(QWidget):

    def __init__(self,parent=None):
        #
        self.hosts_to_scan = []
        self.live_hosts    = []
        self.down_hosts    = []
        #
        ipv4_subnets = [
        "255.255.255.255",
        "255.255.255.254",
        "255.255.255.252",
        "255.255.255.248",
        "255.255.255.240",
        "255.255.255.224",
        "255.255.255.192",
        "255.255.255.128",
        "255.255.255.0",
        "255.255.254.0",
        "255.255.252.0",
        "255.255.248.0",
        "255.255.240.0",
        "255.255.224.0",
        "225.255.192.0",
        "255.255.128.0",
        "255.255.0.0",
        "255.254.0.0",
        "255.252.0.0",
        "255.248.0.0",
        "255.240.0.0", 
        "255.224.0.0",  
        "255.192.0.0",
        "255.128.0.0",
        "255.0.0.0",
        "254.0.0.0",
        "252.0.0.0",
        "248.0.0.0",
        "240.0.0.0",
        "224.0.0.0",
        "192.0.0.0",
        "128.0.0.0",
        "0.0.0.0" ] 
        #
        super().__init__(parent)
        #
        QMainWindow.__init__(self)
        QTableWidget.__init__(self)
        QWidget.__init__(self)
        QLabel.__init__(self)
        #
        self.setWindowTitle('Graphical Ping Sweep')
        self.setGeometry(600,200,500,800)
        self.setStyleSheet("background-color: darkgray; border: 2px black solid")
        #
        self.total_bytes_sent     = 0
        self.total_bytes_sent_str = ''
        #
        self.target_network_label           = QLabel("Network Address")
        self.target_network_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                    
        self.target_network_address         = QLineEdit()                                          
        self.target_network_address.setPlaceholderText("(Network Address - No Host Bits)")
        self.target_network_address.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.elapsed_time_label             = QLabel("Elapsed Time")
        self.elapsed_time_label.setStyleSheet("height: 25px; width: 10px; color: White; font-style: bold; font-size: 16px; font-family: Arial")
        self.elapsed_time                   = QLineEdit() 
        self.elapsed_time.setFixedWidth(75)                                         
        self.elapsed_time.setPlaceholderText("00:00:00")
        self.elapsed_time.setStyleSheet("margin-right: 5px; height: 25px; width: 100px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial") 
        self.live_hosts_label               = QLabel("Live Hosts")
        self.live_hosts_label.setStyleSheet("text-align: center; margin-left: 5px; height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.live_hosts_field               = QLineEdit()
        self.live_hosts_field.setFixedWidth(75)                                          
        self.live_hosts_field.setPlaceholderText("0")
        self.live_hosts_field.setStyleSheet("; height: 25px; width: 25px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setGeometry(100,100,600,400)
        self.reset_button.setStyleSheet("margin-top: 35px; height: 50px; width: 50px; background-color: yellow; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.export_text_button = QPushButton("Export to TXT", self)
        self.export_text_button.setGeometry(100,100,100,100)
        self.export_text_button.setStyleSheet("margin: 2px; margin-top: 5px; height: 50px; width: 50px; background-color: orange; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 18px; font-family: Arial")
        self.export_csv_button = QPushButton("Export to CSV", self)
        self.export_csv_button.setGeometry(100,100,100,100)
        self.export_csv_button.setStyleSheet("margin: 2px; margin-top: 5px; height: 50px; width: 50px; background-color: orange; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 18px; font-family: Arial")
        self.export_xlsx_button = QPushButton("Export to XLSX", self)
        self.export_xlsx_button.setGeometry(100,100,100,100)
        self.export_xlsx_button.setStyleSheet("margin: 2px; margin-top: 5px; height: 50px; width: 50px; background-color: orange; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 18px; font-family: Arial")
        #
        self.stop_button = QPushButton("Exit", self)
        self.stop_button.setGeometry(100,100,600,400)
        self.stop_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: red; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.ping_button = QPushButton("Sweep", self)
        self.ping_button.setGeometry(100,100,600,400)
        self.ping_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: green; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.subnet_label = QLabel("Subnet Mask")
        self.subnet_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.subnet_combo_box = QComboBox()
        self.subnet_combo_box.setStyleSheet("height: 25px; width: 25px; background-color: Black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        for mask in ipv4_subnets:
            self.subnet_combo_box.addItem(mask)
            #
        self.tableWidget = QTableWidget()
        self.tableWidget.setStyleSheet("background-color: black; color: white; border: 1px solid white;")
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setItem(0,0,QTableWidgetItem("IP Address"))
        self.tableWidget.setItem(0,1,QTableWidgetItem("Host Status"))
        #
        main_layout                = QFormLayout()
        self.vertical_button_box   = QVBoxLayout()
        self.horizontal_data_box   = QHBoxLayout()
        self.vertical_table_box    = QVBoxLayout()
        self.export_button_box     = QHBoxLayout()
        self.reset_button_box      = QHBoxLayout()
        self.horizontal_button_box = QHBoxLayout()
        #
        self.vertical_button_box.setSpacing(15)
        self.horizontal_button_box.setSpacing(10)
        #
        self.vertical_button_box.addWidget(self.target_network_label)
        self.vertical_button_box.addWidget(self.target_network_address)
        self.vertical_button_box.addWidget(self.subnet_label)
        self.vertical_button_box.addWidget(self.subnet_combo_box)
        #
        self.horizontal_data_box.addWidget(self.elapsed_time_label)
        self.horizontal_data_box.addWidget(self.elapsed_time)
        self.horizontal_data_box.addWidget(self.live_hosts_label)
        self.horizontal_data_box.addWidget(self.live_hosts_field)
        #
        self.vertical_table_box.addWidget(self.tableWidget)
        #
        self.reset_button_box.addWidget(self.reset_button)
        #
        self.export_button_box.addWidget(self.export_text_button)
        self.export_button_box.addWidget(self.export_csv_button)
        self.export_button_box.addWidget(self.export_xlsx_button)
        #
        self.horizontal_button_box.addWidget(self.stop_button)
        self.horizontal_button_box.addWidget(self.ping_button)
        #
        main_layout.setVerticalSpacing(10)
        main_layout.addRow(self.vertical_button_box)
        main_layout.addRow(self.horizontal_data_box)
        main_layout.addRow(self.vertical_table_box)
        main_layout.addRow(self.reset_button_box)
        main_layout.addRow(self.export_button_box)
        main_layout.addRow(self.horizontal_button_box)
        #
        self.ping_button.clicked.connect(self.ExecuteSweep)
        self.stop_button.clicked.connect(self.Terminate)
        #
        self.setLayout(main_layout)

    def AddTableRow(self,table,data):
        current_row = table.rowCount()
        table.setRowCount(current_row+1)
        column_value = 0
        for item in data:
            cell_value = QTableWidgetItem(str(item))
            table.setItem(current_row,column_value,cell_value)
            column_value =+ 1

    def InitializeHosts(self):
        try:
            subnet_mask = self.subnet_combo_box.currentText()
            self.target_network = ''
            self.target_network += self.target_network_address.text()
            self.target_network += "/"
            self.target_network += subnet_mask
            self.hosts_to_scan = ipaddress.IPv4Network(self.target_network).hosts()
        except Exception as e:
            logging.info('%s' % e)
            sys.exit(1)

    def ResetTable(self):

        return

    def SetStatusAlive(self,addr):
        self.live_hosts.append(addr)
        self.live_hosts_field.setText(str(len(self.live_hosts)))
        current_row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(current_row+1)
        col_index   = 0
        host_addr   = str(addr)
        host_stat   = 'Alive'
        cell_value  = QTableWidgetItem(host_addr)
        cell_value.setForeground(QBrush(QColor(0, 255, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value) 
        col_index   = 1
        cell_value  = QTableWidgetItem(host_stat)
        cell_value.setForeground(QBrush(QColor(0, 255, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        self.tableWidget.update()
        self.CalculateElapsedTime()
        self.elapsed_time.setText(self.elapsed) 

    def SetStatusDown(self,addr):
        self.down_hosts.append(addr)
        current_row = self.tableWidget.rowCount() 
        self.tableWidget.setRowCount(current_row+1)
        col_index   = 0
        host_addr   = str(addr)
        host_stat   = 'Down'
        cell_value  = QTableWidgetItem(host_addr)
        cell_value.setForeground(QBrush(QColor(255, 0, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 1
        cell_value  = QTableWidgetItem(host_stat)
        cell_value.setForeground(QBrush(QColor(255, 0, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value) 
        self.tableWidget.update()
        self.CalculateElapsedTime()
        self.elapsed_time.setText(self.elapsed)  

    def CalculateElapsedTime(self):
        self.current_time = time.perf_counter()
        hours, rem = divmod(self.current_time-self.start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        self.elapsed = "{:0>2}:{:0>2}:{:02.0f}".format(int(hours),int(minutes),seconds)

    def ExecuteSweep(self):
        self.current_host = ''
        self.InitializeHosts()
        self.start_time       = time.perf_counter()
        threadCount           = QThreadPool.globalInstance().maxThreadCount()
        threadPool            = QThreadPool.globalInstance()
        for addr in self.hosts_to_scan:
            self.current_host = addr
            self.worker       = PingWorker(self.current_host)
            self.worker.target_status_up.connect(lambda curr_addr=self.current_host : self.SetStatusAlive(curr_addr))
            self.worker.target_status_down.connect(lambda curr_addr=self.current_host : self.SetStatusDown(curr_addr))
            threadPool.start(self.worker.SendPing)
            QApplication.processEvents()

    def Terminate(self):
        sys.exit(1)

if(__name__ == '__main__'):
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec_())
