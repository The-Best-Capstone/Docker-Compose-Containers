from cProfile import label
import os, time
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
            self.label.setText("Elapsed Time: "+str(elapsed))
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
        title.setText("Local IO Cube Controls")
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
        btnOffline = QPushButton(self)
        btnOffline.setGeometry(QRect(5,125,self.width()-10,30))
        btnOffline.setText("Collect Data Offline")
        btnOffline.setEnabled(False)
        btnOffline.clicked.connect(self.toggleDataCollection)
        self.btnOffline = btnOffline
        # Sub title
        sbtitle = QLabel(self)
        sbtitle.setText("Quick View Options:")
        sbtitle.setStyleSheet("qproperty-alignment: AlignCenter;")
        sbtitle.setGeometry(QRect(5, 175, self.width()-10, 30))
        #
        btnViewThermos = QPushButton(self)
        btnViewThermos.setGeometry(QRect(5,215,self.width()-10,30))
        btnViewThermos.setText("Plot Thermocouples")
        btnViewThermos.clicked.connect(lambda x:self.showPlot("Thermocouples"))
        btnViewThermos.setEnabled(False)
        self.btnThermos = btnViewThermos
        #
        btnView10V = QPushButton(self)
        btnView10V.setGeometry(QRect(5,255,self.width()-10,30))
        btnView10V.setText("Plot 0-10V Channels")
        btnView10V.clicked.connect(lambda x:self.showPlot("0-10V Channels"))
        btnView10V.setEnabled(False)
        self.btn10V = btnView10V
        #
        btnView420mA = QPushButton(self)
        btnView420mA.setGeometry(QRect(5,295,self.width()-10,30))
        btnView420mA.setText("Plot 4-20mA Channels")
        btnView420mA.clicked.connect(lambda x:self.showPlot("4-20mA Channels"))
        btnView420mA.setEnabled(False)
        self.btn420mA = btnView420mA
        #
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
                self.config = config.containers
                self.parent().setConfiguration(os.path.basename(config.path))
                #
                self.btnOffline.setEnabled(True)
                self.btnConfig.setEnabled(False)

                self.btnLoad.setText("Close Configuration")
        else :
            self.config = None
            self.btnOffline.setEnabled(False)
            self.btnConfig.setEnabled(True)
            self.btnLoad.setText("Load Configuration")
            self.parent().setConfiguration(None)

    def toggleDataCollection(self) :
        if self.collecting_data == True :
            if Logger :
                Logger.instance().logMessage("Stopping offline data collection")
            # stop
            ## TODO: run docker down script
            self.elapsed_timer.kill() 
            self.elapsed_timer = None 
            self.btnLoad.setEnabled(True)
            self.btnOffline.setText("Collect Data Offline")
            self.collecting_data = False
            #
        elif self.collecting_data == False :
            if Logger :
                Logger.instance().logMessage("Starting offline data collection")
            # start 
            self.collecting_data = True 
            self.btnOffline.setText("Stop Data Collection")
            self.btnLoad.setEnabled(False)
            self.elapsed_timer = Timer(self, self.parent().title)
            ## TODO: 
            # run docker compose up script 

    def showPlot(self, title) :
        plot_dialog = LinePlotWidget(parent=None, topic="Simulated Values", title=title, ylabel="Simulated Range")
        plot_dialog.exec()
