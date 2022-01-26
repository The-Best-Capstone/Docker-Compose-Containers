import os,sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from datetime import datetime
import json 

ROOT = os.path.dirname(__file__) 

class LoadDialog(QDialog) :

    New = 1
    Existing = 2 
    Cancel = 3

    def __init__(self, parent=None) :
        QDialog.__init__(self, parent)
        loadUi(os.path.join(ROOT, "loader.ui"), self)
        #
        self.Choice = self.Cancel
        self.show() 
        # buttons 
        self.create_btn.clicked.connect(lambda choice : self.buttonPress(1))
        self.load_btn.clicked.connect(lambda choice : self.buttonPress(2))
        self.cancel_btn.clicked.connect(self.close)

    def buttonPress(self, return_value) :
        self.Choice = return_value
        self.accept() 

    def closeEvent(self, event) :
        self.Choice = 3 
        self.reject()

class Configuration : 

    BaseConfig = {
        "created":datetime.now().strftime("%m/%d/%Y %H:%M"),
        "modified":"",
        "analog":False,
        "analog_channels":[
            ["a0","raw",False],["a1","raw",False],["a2","raw",False],["a3","raw",False],["a4","raw",False],
            ["a5","raw",False],["a6","raw",False],["a7","raw",False],["a8","raw",False],["a9","raw",False],
            ["a10","raw",False],["a11","raw",False],["a12","raw",False],["a13","raw",False],["a14","raw",False],
            ["a15","raw",False],["a16","raw",False],["a17","raw",False],["a18","raw",False],["a19","raw",False],
        ],
        "tcp":False,
        "scanivalves":[
            ["191.30.80.154","16",False],
            ["191.30.80.155","16",False],
            ["191.30.80.156","16",False],
            ["191.30.80.157","24",False],
            ["191.30.80.158","24",False],
        ]
    }

    def __init__(self, parent) :
        # Prompt for file:
        self.parent = parent 
        Cancelled = False
        Path = None 
        Current = None 
        # 
        mode = LoadDialog(parent=parent)
        rtn = mode.exec()
        if rtn == QDialog.Accepted :
            if mode.Choice == mode.New :
                save_path = QFileDialog.getSaveFileName(parent, 'Save new Configuration', os.path.join(ROOT,"configurations"),"JSON Files (*.json)")
                if not save_path[0].strip() == "" :
                    Path = save_path[0]
                    Current = self.BaseConfig.copy() 
                else :
                    self.fail()
                ##
            elif mode.Choice == mode.Existing :
                load_path = QFileDialog.getOpenFileName(parent, 'Load an existing Configuration', os.path.join(ROOT,"configurations"),"JSON Files (*.json)")
                if not load_path[0].strip() == "" :
                    Path = load_path[0]
                    
                    try :
                        tmp = json.load(open(Path))
                    except Exception :
                        dlg = QMessageBox(QMessageBox.Information, "File Error","Unable to load "+os.path.basename(Path)+" :(",(QMessageBox.Ok))
                        dlg.exec()
                        self.fail() # this is temp 
                    else : 
                        Current = tmp 
                        dlg = QMessageBox(QMessageBox.Information, "Config Loaded","The configuration "+os.path.basename(Path)+" has been successfully loaded!",(QMessageBox.Ok))
                        dlg.exec() 
                else :
                    self.fail()
        else :
            print("Cancelled")
            self.fail()

        ## Else :
        self.path = Path 
        self.name = os.path.basename(Path)
        self.data = Current 
        self.data["modified"] = datetime.now().strftime("%m/%d/%Y %H:%M")

    def saveConfig(self) :
        dlg = QMessageBox(QMessageBox.Information, "Save Configuration?","Would you like to save your changes to "+self.name+"?",(QMessageBox.Yes | QMessageBox.No))
        if dlg.exec() == QMessageBox.Yes :
            try :
                json.dump(self.data, open(self.path, "w"))
            except Exception :
                dlg = QMessageBox(QMessageBox.Information, "File Error","There was an issue attempting to save "+self.name+" :(",(QMessageBox.Ok))
                dlg.exec() 
                pass 

    def fail(self) :
        raise FileNotFoundError("No configuration loaded")
