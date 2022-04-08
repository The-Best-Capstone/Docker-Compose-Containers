import os, time
import subprocess
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

try :
    from Logs import Logger 
except ImportError :
    Logger = None 


from Plots.PlotWidget import LinePlotWidget

## 
try :
    from Manager import Editor, Chooser 
except ImportError :
    from Manager.Editor import Editor,Chooser

class Timer(QThread) :

    def __init__(self, parent, label_to_update) :
        QThread.__init__(self, parent)
        #
        self.shutdown = False 
        self.label = label_to_update
        self.start_time = datetime.now() 
        self.start() 

    def kill(self) :
        self.shutdown = True

    def run(self) :
        while not self.shutdown : 
            elapsed = (datetime.now()-self.start_time)
            self.label.setText("Up Time: "+str(elapsed))
            time.sleep(0.1)

class ControlWidget(QWidget) :

    def __init__(self, parent, position=(0,0)) :
        QWidget.__init__(self, parent) 
        #
        self.config = None 
        self.collecting_data = False 
        self.elapsed_timer = None 

        # set geometry and styles pad with 5px 
        self.setGeometry(QRect(position[0]+5,position[1]+5,290-position[0],390-position[1]))
        self.setStyleSheet("background: \"#DCDCDC\"; font:18pt \"Arial\";")
        # title label 
        title = QLabel(self)
        title.setText("Pipeline Controls")
        title.setStyleSheet("qproperty-alignment: AlignCenter;")
        title.setGeometry(QRect(5, 5, self.width()-10, 30))
        #
        btnConfig = QPushButton(self)
        btnConfig.setGeometry(QRect(5,45,self.width()-10,30))
        btnConfig.setText("Create/Edit Configuration")
        btnConfig.setStyleSheet("background: \"#37D400\";")
        btnConfig.clicked.connect(self.modifyConfiguration)
        self.btnConfig = btnConfig
        #
        btnLoad = QPushButton(self)
        btnLoad.setGeometry(QRect(5,85,self.width()-10,30))
        btnLoad.setText("Load Configuration File")
        btnLoad.clicked.connect(self.fileToggle)
        self.btnLoad = btnLoad
        #
        btnData = QPushButton(self)
        btnData.setGeometry(QRect(5,125,self.width()-10,30))
        btnData.setText("Start Data Collection")
        btnData.setEnabled(False)
        btnData.clicked.connect(self.toggleDataCollection)
        self.btnData = btnData
        #
        btnGrafana = QPushButton(self)
        btnGrafana.setGeometry(QRect(5,165,self.width()-10,30))
        btnGrafana.setText("Open Grafana")
        btnGrafana.setEnabled(False)
        btnGrafana.clicked.connect(self.openGrafana)
        self.btnGrafana = btnGrafana
        
        self.show() 

    def modifyConfiguration(self) :
        pick_dialog = Chooser(self)
        if pick_dialog.exec_() :
            editor = Editor(self, pick_dialog.file)

    def fileToggle(self) :
        if not self.config :
            file_dialog = Chooser(self, createOption=False)
            if file_dialog.exec_() :
                config = file_dialog.file 
                self.config = config
                self.parent().setConfiguration(os.path.basename(config.path))
                #
                self.btnData.setEnabled(True)
                self.btnConfig.setEnabled(False)

                self.btnLoad.setText("Close Configuration")
        else :
            self.config = None
            self.btnData.setEnabled(False)
            self.btnConfig.setEnabled(True)
            self.btnLoad.setText("Load Configuration")
            self.parent().setConfiguration(None)

    def toggleDataCollection(self) :
        if self.collecting_data == True :
            if Logger :
                Logger.instance().logMessage("Stopping offline data collection")
            # stop
            ## TODO: run docker down script
            try : 
                self.config.dockerDOWN()
            except Exception : 
                pass 
            #
            self.elapsed_timer.kill() 
            self.elapsed_timer = None 
            self.btnLoad.setEnabled(True)
            self.btnGrafana.setEnabled(False)
            self.btnData.setText("Start Data Collection")
            self.collecting_data = False
            #
        elif self.collecting_data == False :
            if Logger :
                Logger.instance().logMessage("Starting offline data collection")
            # start 
            self.collecting_data = True 
            self.btnData.setText("Stop Data Collection")
            self.btnGrafana.setEnabled(True)
            self.btnLoad.setEnabled(False)
            self.elapsed_timer = Timer(self, self.parent().title)
            ## TODO: 
            # run docker compose up script 
            try : 
                self.config.dockerUP()
            except Exception : 
                pass 

    def openGrafana(self) : 
        try :
            # windows and mac
            if not os.uname()[0] == "Linux":
                os.system("open http://0.0.0.0:3000/d/yEJAfQbnk/new-dashboard-copy?orgId=1&refresh=500ms &")
            else :
                raise ValueError("lol")
        except Exception : 
            try : # for linux
                os.system("xdg-open http://0.0.0.0:3000/d/yEJAfQbnk/new-dashboard-copy?orgId=1&refresh=500ms &") 
            except Exception :
                pass 

