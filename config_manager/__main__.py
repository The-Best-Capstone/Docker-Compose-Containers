#!/usr/bin/python3

import os,sys,traceback
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Logs container
from Logs import Logger, LogsGui
from DockerWrapper import DockerWrapper

# Cube controls
# TODO: Import IOCRemote if the hostname and platform is not Pi and linux 
if os.uname()[1] == "pi" : 
    # Control Widget for cube
    print("Raspberry Pi")
    from IOC.ControlWidget import ControlWidget
else :
    print("POSIX")
    from PCIOC.ControlWidget import ControlWidget

#
from utils.Buttons import *

ROOT = os.path.dirname(__file__)

class Interface(QMainWindow) :

    def __init__(self) :
        QMainWindow.__init__(self)
        self.setWindowTitle("Configuration Manager")
        #self.setStyleSheet("font: 18pt \"Arial\";")

        # Message Logs 
        Logger.instance().logMessage("Initializing Configuration Manager")
        self.logsgui = LogsGui(self, geometry=QRect(5, 405, 1024-10, 200-10))


        Logger.instance().logMessage("Load Control Widget")
        self.controlgui = ControlWidget(self,position=(0,50))   

        # Docker Engine stuff
        self.dockerps = DockerWrapper(self, geometry=QRect(300, 60, 1024-305, 600-260))   

        # Window Size
        try : 
            screen = QApplication.instance().primaryScreen()
            screenRect = screen.availableGeometry() 
            if screenRect.width() <= 1024 or screenRect.height() <= 600 :
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.showFullScreen() 
            else :
                self.setFixedSize(QSize(1024, 600))
        except Exception :
            # fixed size 
            self.setFixedSize(QSize(1024, 600))
            Logger.instance().logError(traceback.format_exc())     

        # Header
        self.title = QLabel(self)
        self.title.setGeometry(QRect(10, 5, 1024-10,40))
        self.title.setStyleSheet("font:22pt \"Arial\"; qproperty-alignment: AlignCenter;")
        self.title.setText("Configuration: Not Loaded")
        self.title.show()

        ## Close Button
        self.closeButton = CloseButton(self)
        self.closeButton.setGeometry(QRect(1024-105, 5, 100, 40))
        #
        self.show()

    def setConfiguration(self, file) :
        self.title.setText("Configuration: "+str(file))

#### 
## Interface
app = QApplication(sys.argv)
app.setStyle("Fusion")
interface = Interface()
sys.exit(app.exec_())
