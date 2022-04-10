#!/usr/bin/env python3

from concurrent.futures import thread

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    import subprocess
    import xlsxwriter
    import ipaddress
    import logging
    import socket
    import time
    import csv
    import sys
    import os
except Exception as e:
    print("[!] Library import error: %s " % e)

logging.basicConfig(format="%(message)s", level=logging.INFO)

class ScanWorker(QObject):        

    target_port_closed     = pyqtSignal(object)
    target_port_open       = pyqtSignal()

    def __init__(self,target,port):
        super().__init__()
        self.target     = target 
        self.port       = port
        socket.setdefaulttimeout(1)
        self.sock_obj   = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

    def TCPScan(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.tcp_connect = self.sock_obj.connect_ex((self.target,self.port)) 
        if(self.tcp_connect == 0):
            self.target_port_open.emit()
        else:
            self.target_port_closed.emit(self.port)
        self.sock_obj.close()

class Window(QWidget):

    def __init__(self,parent=None):
        #
        self.open_ports      = []
        self.closed_ports    = []
        #
        super().__init__(parent)
        #
        QMainWindow.__init__(self)
        QTableWidget.__init__(self)
        QWidget.__init__(self)
        QLabel.__init__(self)
        #
        self.setWindowTitle('Graphical TCP Port Scanner')
        self.setGeometry(600,200,500,800)
        self.setStyleSheet("background-color: darkgray; border: 2px black solid")
        #
        self.target_host_label              = QLabel("Host IP Address")
        self.target_host_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                    
        self.target_host_address            = QLineEdit()                                          
        self.target_host_address.setPlaceholderText("(IP address of the target host)")
        self.target_host_address.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        self.elapsed_time_label             = QLabel("Elapsed Time")
        self.elapsed_time_label.setStyleSheet("height: 25px; width: 10px; color: White; font-style: bold; font-size: 16px; font-family: Arial")
        self.elapsed_time                   = QLineEdit() 
        self.elapsed_time.setFixedWidth(75)                                         
        self.elapsed_time.setPlaceholderText("00:00:00")
        self.elapsed_time.setStyleSheet("margin-right: 5px; height: 25px; width: 100px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial") 
        self.open_ports_label               = QLabel("Open Ports")
        self.open_ports_label.setStyleSheet("text-align: center; margin-left: 5px; height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.open_ports_field               = QLineEdit()
        self.open_ports_field.setFixedWidth(75)                                          
        self.open_ports_field.setPlaceholderText("0")
        self.open_ports_field.setStyleSheet("height: 25px; width: 25px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
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
        self.ping_button = QPushButton("Scan", self)
        self.ping_button.setGeometry(100,100,600,400)
        self.ping_button.setStyleSheet("margin-top: 5px; height: 50px; width: 50px; background-color: green; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.first_port_label = QLabel("First Port")
        self.first_port_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.first_port_combo_box = QComboBox()
        self.first_port_combo_box.setStyleSheet("height: 25px; width: 25px; background-color: Black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.last_port_label = QLabel("Last Port")
        self.last_port_label.setStyleSheet("margin-left: 5px; height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.last_port_combo_box = QComboBox()
        self.last_port_combo_box.setStyleSheet("margin-left: 5px; height: 25px; width: 25px; background-color: Black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        #
        for port in range(1,65536):
            self.first_port_combo_box.addItem(str(port))
            self.last_port_combo_box.addItem(str(port))
            #
        self.tableWidget = QTableWidget()
        self.tableWidget.setStyleSheet("background-color: black; color: white; border: 1px solid white;")
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setItem(0,0,QTableWidgetItem("Port"))
        self.tableWidget.setItem(0,1,QTableWidgetItem("Service"))
        self.tableWidget.setItem(0,2,QTableWidgetItem("Status"))
        #
        main_layout                = QFormLayout()
        self.vertical_button_box   = QVBoxLayout()
        self.horizontal_combo_box  = QHBoxLayout()
        self.horizontal_data_box   = QHBoxLayout()
        self.vertical_table_box    = QVBoxLayout()
        self.export_button_box     = QHBoxLayout()
        self.reset_button_box      = QHBoxLayout()
        self.horizontal_button_box = QHBoxLayout()
        #
        self.vertical_button_box.setSpacing(15)
        self.horizontal_button_box.setSpacing(10)
        #
        self.vertical_button_box.addWidget(self.target_host_label)
        self.vertical_button_box.addWidget(self.target_host_address)
        #
        self.horizontal_combo_box.addWidget(self.first_port_label)
        self.horizontal_combo_box.addWidget(self.first_port_combo_box)
        self.horizontal_combo_box.addWidget(self.last_port_label)
        self.horizontal_combo_box.addWidget(self.last_port_combo_box)
        #
        self.horizontal_data_box.addWidget(self.elapsed_time_label)
        self.horizontal_data_box.addWidget(self.elapsed_time)
        self.horizontal_data_box.addWidget(self.open_ports_label)
        self.horizontal_data_box.addWidget(self.open_ports_field)
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
        main_layout.addRow(self.horizontal_combo_box)
        main_layout.addRow(self.horizontal_data_box)
        main_layout.addRow(self.vertical_table_box)
        main_layout.addRow(self.reset_button_box)
        main_layout.addRow(self.export_button_box)
        main_layout.addRow(self.horizontal_button_box)
        #
        self.reset_button.clicked.connect(self.ResetTable)
        self.export_text_button.clicked.connect(self.ExportToTextFile)
        self.export_csv_button.clicked.connect(self.ExportToCSVFile)
        self.export_xlsx_button.clicked.connect(self.ExportToXLSX)
        #
        self.ping_button.clicked.connect(self.ExecutePortScan)
        self.stop_button.clicked.connect(self.Terminate)
        #
        self.setLayout(main_layout)

    def GenerateFilename(self,network,file_type):
        valid_types = ['.txt','.csv','.xlsx']
        if(file_type in valid_types):
            timestamp = time.ctime()
            timestamp = timestamp.replace(' ','_')
            timestamp = timestamp.replace(':','_')
            filename  = str(network)+'_'+timestamp+'_'+file_type
            return filename
        else:
            return 'UnrecognizedFileExtension'

    def ExportToTextFile(self):
        try:
            self.filename = self.GenerateFilename(self.target_host_address.text(),'.txt')
            self.fileObject = open(self.filename,'w')
            for port in self.open_ports:
                port_value = str(port[0])
                serv_value = str(port[1])
                self.fileObject.write("Open->"+port_value+':'+serv_value)
                self.fileObject.write('\n')
            self.fileObject.close()
        except:
            sys.exit(1)

    def ExportToCSVFile(self):
        try:
            self.filename = self.GenerateFilename(self.target_host_address.text(),'.csv')
            with open(self.filename,'w',newline='') as csvfile:
                port_writer = csv.writer(csvfile,delimiter=',')
                col_titles  = ['Port','Service','Status']
                port_writer.writerow(col_titles)
                for port in self.open_ports:
                    port_value = str(port[0])
                    serv_value = str(port[1])
                    entry = [port_value,serv_value,'Open']
                    port_writer.writerow(entry)
        except:
            sys.exit(1)

    def ExportToXLSX(self):
        try:
            self.filename = self.GenerateFilename(self.target_host_address.text(),'.xlsx')
            workbook = xlsxwriter.Workbook(self.filename)
            open_ports_worksheet = workbook.add_worksheet('Open Ports')
            open_ports_worksheet.set_column('A:A',20)
            closed_ports_worksheet = workbook.add_worksheet('Closed Ports')
            closed_ports_worksheet.set_column('A:A',20)
            row_index   =  1
            alpha_index = 'A'
            beta_index  = 'B'
            port_write_index    = alpha_index + str(row_index)
            service_write_index = beta_index  + str(row_index)
            open_ports_worksheet.write(port_write_index,'Port')
            open_ports_worksheet.write(service_write_index,'Service')
            closed_ports_worksheet.write(port_write_index,'Port')
            closed_ports_worksheet.write(service_write_index,'Service')
            row_index += 1
            for port in self.open_ports:
                current_port    = str(port[0]) 
                current_service = str(port[1])
                port_write_index    = alpha_index + str(row_index)
                service_write_index = beta_index + str(row_index)
                open_ports_worksheet.write(port_write_index,current_port)
                open_ports_worksheet.write(service_write_index,current_service)
                row_index += 1
            row_index = 2
            for port in self.closed_ports:
                current_port    = str(port[0]) 
                current_service = str(port[1])
                port_write_index    = alpha_index + str(row_index)
                service_write_index = beta_index + str(row_index)
                closed_ports_worksheet.write(port_write_index,current_port)
                closed_ports_worksheet.write(service_write_index,current_service)
                row_index += 1
            workbook.close()
        except Exception:
            sys.exit(1)

    def ResetTable(self):
        self.open_ports   = []
        self.closed_ports = []
        self.open_ports_field.setText('0')
        for row in range(self.tableWidget.rowCount()-1):
            try:
                self.tableWidget.removeRow(self.tableWidget.rowCount()-1)
                self.tableWidget.update()
            except:
                sys.exit(1)

    def SetStatusOpen(self,port):
        port_str    = str(port)
        port_srv    = ''
        try:
            port_srv    = socket.getservbyport(port)
        except OSError:
            port_srv    = 'Unknown Service'
        port_stat   = 'Open'
        self.open_ports.append((port_str,port_srv))
        self.open_ports_field.setText(str(len(self.open_ports)))
        current_row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(current_row+1)
        col_index   = 0
        cell_value  = QTableWidgetItem(port_str)
        cell_value.setForeground(QBrush(QColor(0, 255, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value) 
        col_index   = 1
        cell_value  = QTableWidgetItem(port_srv)
        cell_value.setForeground(QBrush(QColor(0, 255, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 2
        cell_value  = QTableWidgetItem(port_stat)
        cell_value.setForeground(QBrush(QColor(0, 255, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        self.tableWidget.update()
        self.CalculateElapsedTime()
        self.elapsed_time.setText(self.elapsed) 

    def SetStatusClosed(self,port):
        port_str    = str(port)
        port_srv    = ''
        try:
            port_srv    = socket.getservbyport(port)
        except OSError:
            port_srv    = 'Unknown Service'
        port_stat   = 'Closed'
        self.closed_ports.append((port_str,port_srv))
        current_row = self.tableWidget.rowCount() 
        self.tableWidget.setRowCount(current_row+1)
        col_index   = 0
        cell_value  = QTableWidgetItem(port_str)
        cell_value.setForeground(QBrush(QColor(255, 0, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value)
        col_index   = 1
        cell_value  = QTableWidgetItem(port_srv)
        cell_value.setForeground(QBrush(QColor(255, 0, 0)))
        self.tableWidget.setItem(current_row,col_index,cell_value) 
        self.tableWidget.update()
        col_index   = 2
        cell_value  = QTableWidgetItem(port_stat)
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

    def ExecutePortScan(self):
        #
        first_port = int(self.first_port_combo_box.currentText())
        last_port  = int(self.last_port_combo_box.currentText())
        #
        if(first_port <= last_port):
            #
            self.start_time       = time.perf_counter()
            threadCount           = QThreadPool.globalInstance().maxThreadCount()
            threadPool            = QThreadPool.globalInstance()
            #
            for port in range(first_port,last_port+1):
                self.current_port = port
                self.worker = ScanWorker(self.target_host_address.text(),self.current_port)
                self.worker.target_port_open.connect(lambda curr_port = self.current_port : self.SetStatusOpen(curr_port))
                self.worker.target_port_closed.connect(lambda curr_port = self.current_port : self.SetStatusClosed(curr_port))
                threadPool.start(self.worker.TCPScan)
                QApplication.processEvents()
        else:
            sys.exit(1)

    def Terminate(self):
        sys.exit(1)

if(__name__ == '__main__'):
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec_())
