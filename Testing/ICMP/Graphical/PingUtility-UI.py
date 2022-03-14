#!/usr/bin/env python3

from concurrent.futures import thread


try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    import subprocess
    import threading
    import logging
    import math
    import time
    import sys
    import os
except Exception as e:
    print("[!] Library import error: %s " % e)

logging.basicConfig(format="%(message)s", level=logging.INFO)

class PingWorker(QObject):        

    target_status_down = pyqtSignal()
    target_status_up   = pyqtSignal()
    increment_tx_data  = pyqtSignal()

    def __init__(self,target,tx_bytes):
        super().__init__()
        self.target           = target
        self.bytes_per_packet = tx_bytes

    def SendPing(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        tx_bytes = str(self.bytes_per_packet)
        self.increment_tx_data.emit()
        if(os.name == 'nt'):
            output = subprocess.Popen(['ping','-n','1','-w','150','-l',tx_bytes,str(self.target)],startupinfo=startupinfo,stdout=subprocess.PIPE).communicate()[0]
        else:
            output = subprocess.Popen(['ping','-c','1','-w','150','-s',tx_bytes,str(self.target)],startupinfo=startupinfo,stdout=subprocess.PIPE).communicate()[0]
        if('Reply' in output.decode('utf-8')):
            self.target_status_up.emit()
        else:
            self.target_status_down.emit()

class Window(QWidget):

    def __init__(self,parent=None):
        #
        super().__init__(parent)
        #
        QMainWindow.__init__(self)
        QWidget.__init__(self)
        QLabel.__init__(self)
        #
        self.setWindowIcon(QIcon('bmb.ico'))
        #
        self.setWindowTitle('Ping Utility')
        self.setGeometry(850,400,500,500)
        self.setStyleSheet("background-color: gray; border: 2px black solid")
        #
        self.total_bytes_sent     = 0
        self.total_bytes_sent_str = ''
        #
        self.target_address_label   = QLabel("Host Name or IP Address")
        self.target_address_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                    
        self.target_address         = QLineEdit()                                          
        self.target_address.setPlaceholderText("(Target Address)")
        self.target_address.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.tx_byte_count_label    = QLabel("Bytes Per ICMP Packet") 
        self.tx_byte_count_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial")                                     
        self.tx_byte_count          = QLineEdit()                                          
        self.tx_byte_count.setPlaceholderText("(Number of bytes per packet)")
        self.tx_byte_count.setStyleSheet("height: 25px; width: 50px; background-color: black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(100,100,600,400)
        self.stop_button.setStyleSheet("margin-top: 35px; height: 50px; width: 50px; background-color: red; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.ping_button = QPushButton("Ping", self)
        self.ping_button.setGeometry(100,100,600,400)
        self.ping_button.setStyleSheet("margin-top: 35px; height: 50px; width: 50px; background-color: green; color: black; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 24px; font-family: Arial")
        #
        self.ping_count_label      = QLabel("Number of ICMP packets to send")
        self.ping_count_label.setStyleSheet("height: 25px; width: 50px; color: White; font-style: bold; font-size: 16px; font-family: Arial") 
        self.ping_count_combo_box        = QComboBox()
        self.ping_count_combo_box.setStyleSheet("height: 25px; width: 25px; background-color: Black; color: White; border: 2px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        for i in range(1,1001):
            self.ping_count_combo_box.addItem(str(i))
            #
        self.target_status_label            = QLabel("Target Host Status: Unknown")
        self.target_status_label.setStyleSheet("margin-top:10px; height: 50px; width: 50px; background-color: Black; color: White; border: 5px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.transmitted_bytes_label        = QLabel("Sent Data: 0")
        self.transmitted_bytes_label.setStyleSheet("margin-top: 10px; height: 50px; width: 50px; background-color: Black; color: White; border: 5px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")
        #
        self.output_window   = QPlainTextEdit("")
        self.output_window.resize(200,400)     
        #
        main_layout                = QFormLayout()
        self.vertical_button_box   = QVBoxLayout()
        self.horizontal_button_box = QHBoxLayout()
        #
        self.vertical_button_box.setSpacing(15)
        self.horizontal_button_box.setSpacing(10)
        #
        self.vertical_button_box.addWidget(self.target_address_label)
        self.vertical_button_box.addWidget(self.target_address)
        self.vertical_button_box.addWidget(self.tx_byte_count_label)
        self.vertical_button_box.addWidget(self.tx_byte_count)
        self.vertical_button_box.addWidget(self.ping_count_label)
        self.vertical_button_box.addWidget(self.ping_count_combo_box)
        self.vertical_button_box.addWidget(self.target_status_label)
        self.vertical_button_box.addWidget(self.transmitted_bytes_label)
        self.vertical_button_box.addWidget(self.output_window)
        #
        self.horizontal_button_box.addWidget(self.stop_button)
        self.horizontal_button_box.addWidget(self.ping_button)
        #
        main_layout.setVerticalSpacing(10)
        main_layout.addRow(self.vertical_button_box)
        main_layout.addRow(self.horizontal_button_box)
        #
        self.ping_button.clicked.connect(self.ExecutePings)
        self.stop_button.clicked.connect(self.Terminate)
        #
        self.setLayout(main_layout)

    def ConvertBytes(self,input_bytes):
        if(input_bytes == 0):
            return "0B"
        else:
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(input_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(input_bytes / p, 2)
            ret_value = "%s %s" % (s, size_name[i])
            return ret_value

    def SetStatusAlive(self):
        self.target_status_label.setText("Target Host Status: Up")
        self.target_status_label.setStyleSheet("margin-top:10px; height: 50px; width: 50px; background-color: Black; color: Green; border: 5px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")

    def SetStatusDown(self):
        self.target_status_label.setText("Target Host Status: Down")
        self.target_status_label.setStyleSheet("margin-top:10px; height: 50px; width: 50px; background-color: Black; color: Red; border: 5px solid black; border-radius: 10px; font-style: bold; font-size: 16px; font-family: Arial")

    def UpdateTotalDataDisplay(self):
        self.transmitted_bytes_label.setText("Total data sent: {0}".format(self.total_bytes_sent_str))

    def ExecutePings(self):
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        threadPool  = QThreadPool.globalInstance()
        for i in range(int(self.ping_count_combo_box.currentText())):
            self.total_bytes_sent += int(self.tx_byte_count.text())
            temp_converted_bytes   = self.ConvertBytes(self.total_bytes_sent)
            self.total_bytes_sent_str = str(temp_converted_bytes)
            self.worker = PingWorker(self.target_address.text(),self.tx_byte_count.text())
            self.worker.target_status_up.connect(self.SetStatusAlive)
            self.worker.target_status_down.connect(self.SetStatusDown)
            self.worker.increment_tx_data.connect(self.UpdateTotalDataDisplay)
            threadPool.start(self.worker.SendPing)

    def Terminate(self):
        sys.exit(1)

if(__name__ == '__main__'):
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec_())
