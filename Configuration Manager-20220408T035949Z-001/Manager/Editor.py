import os
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Logs import Logger

try : 
    from Loader import Configuration
except ModuleNotFoundError :
    from Manager.Loader import Configuration 

ROOT = os.path.dirname(__file__)

class Chooser(QDialog) : 

    class Table(QAbstractTableModel) :
        def __init__(self, parent, rows) :
            QAbstractTableModel.__init__(self, parent)
            self.Rows = rows
        
        def rowCount(self, index) :
            return len(self.Rows)
        
        def columnCount(self, index) :
            return 1
        
        def data(self, index, role=Qt.DisplayRole) :
            if role == Qt.DisplayRole :
                r = index.row()
                return self.Rows[r]

    def __init__(self, parent, createOption = True) :
        QDialog.__init__(self, parent) 
        #
        Logger.instance().logMessage("Configuration Selection Dialog")
        #
        self.setModal(True)
        self.file = None 
        #
        self.setStyleSheet("background: \"#DCDCDC\"; font:20pt \"Arial\";")
        self.setFixedHeight(400)
        self.setFixedWidth(400)
        #
        title = QLabel(self)
        title.setText("Please Select a Configuration")
        title.setStyleSheet("qproperty-alignment: AlignCenter;")
        title.setGeometry(QRect(5, 5, self.width()-10, 30))
        #
        try :
            configurations = os.path.join(ROOT, "configurations")
            if not os.path.exists(configurations) :
                os.mkdir(configurations)
                # 
                cfg = Configuration()
                cfg.exportConfiguration(os.path.join(configurations,"default.json"))
            ##
            configlist = os.listdir(configurations)
            ##
            if len(configlist) < 1 :
                Logger.instance().logMessage("No configurations found in the local directory")
                raise ValueError("Too few elements in config dir") 

        except Exception as err :
            Logger.instance().logMessage("Permission error with local configuration directory")
            msg = QLabel(self)
            msg.setText("The configuration directory is not available.\n\nDetails:\n"+str(err))
            msg.setStyleSheet("font:20pt \"Arial\";")
            msg.setWordWrap(True)
            msg.setGeometry(QRect(5, 35, self.width()-10, self.height()-60))
        else :
            self.table = self.Table(self, configlist) 
            self.view = QTableView(self) 
            self.view.setStyleSheet("font:16pt \"Arial\";")
            self.view.setGeometry(QRect(5, 35, self.width()-10, self.height()-100))
            self.view.setModel(self.table)
            self.view.clicked.connect(self.configSelected)
            # fix the header
            self.view.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        #
        if createOption == True:
            newbtn = QPushButton(self)
            newbtn.setGeometry(QRect(5,self.height()-40,round(self.width()/2)-10,30))
            newbtn.setText("Create New")
            newbtn.setStyleSheet("background: \"#37D400\";")
            newbtn.clicked.connect(self.newConfig)

        cclbtn = QPushButton(self)
        if createOption == True :
            cclbtn.setGeometry(QRect(round(self.width()/2)+5,self.height()-40,round(self.width()/2)-10,30))
        else :
            cclbtn.setGeometry(QRect(round(self.width()/2)-50,self.height()-40,100,30))
            
        cclbtn.setText("Cancel")
        cclbtn.setStyleSheet("background: \"#FF5757\";")
        cclbtn.clicked.connect(self.reject)

        ##
        self.show()

    def newConfig(self) :
        self.file = Configuration()
        #
        self.accept()

    def configSelected(self, item) : 
        row = item.row() 
        file_name = self.table.Rows[row]
        self.file = Configuration()
        self.file.importConfiguration(os.path.join(ROOT,"configurations/"+file_name))
        #
        self.accept() 

class Editor(QDialog) :

    class ParameterTable(QAbstractTableModel) :
        def __init__(self, parent, values):
            QAbstractTableModel.__init__(self, parent)
            ##
            self.headers = ["Enabled", "Container Name","Description"]
            self.values = values

        def data(self, index, role=Qt.DisplayRole) :
            r = index.row()
            c = index.column() 
            if role == Qt.CheckStateRole and c == 0 :
                value = self.values[r][c] 
                if value == True :
                    return Qt.Checked
                else :
                    return Qt.Unchecked
            elif role == Qt.DisplayRole and not c == 0 :
                return self.values[r][c]

        def flags(self, index, role=Qt.DisplayRole) :
            r = index.row()
            c = index.column() 
            if c == 0 :
                return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable 
            return Qt.ItemIsEnabled

        def setData(self, index, value, role=Qt.EditRole) :
            if value is not None : 
                r = index.row()
                c = index.column() 
                if c == 0 and role == Qt.CheckStateRole :
                    if value == Qt.Checked :
                        self.values[r][c] = True
                    else :
                        self.values[r][c] = False
                    # emit signal 
                    self.dataChanged.emit(index, index)
                    return True
            return False 

        def rowCount(self, index) :
            return len(self.values)
        
        def columnCount(self, index) :
            return len(self.headers) 

        def headerData(self, section, orientation, role=Qt.DisplayRole) :
            if orientation == Qt.Horizontal and role == Qt.DisplayRole :
                return self.headers[section] 
            # otherwise return the default
            return QAbstractTableModel.headerData(self, section, orientation, role)

    # parameters must be a configuration object
    def __init__(self, parent, parameters) :
        QDialog.__init__(self, parent)
        #
        Logger.instance().logMessage("Loading configuration editor")
        ##
        self.setModal(True)
        #
        if parameters is None :
            Logger.instance().logMessage("No configuration object provided to the editor. Err.")
            self.reject() 
        else : 
            self.setFixedWidth(800)
            self.setFixedHeight(500)
            # 
            try :
                config = parameters.containers
            except Exception :
                ## TODO throw error
                pass
            else :
                ##
                values = []
                for v in config :
                    values.append([v["enabled"], v["name"], v["Description"]])
        
                ##
                self.table = self.ParameterTable(self, values)
                self.view = QTableView(self)
                self.view.setStyleSheet("font: 18pt \"Arial\";")
                self.view.setGeometry(QRect(5, 40, self.width()-10, self.height()-100))
                self.view.setModel(self.table)
                self.view.setAlternatingRowColors(True)
                #
                header = self.view.horizontalHeader()
                header.setSectionResizeMode(0,QHeaderView.ResizeToContents)
                header.setSectionResizeMode(1,QHeaderView.ResizeToContents)
                header.setSectionResizeMode(2,QHeaderView.Stretch)
                # Buttons

                newbtn = QPushButton(self)
                newbtn.setGeometry(QRect(5,self.height()-40,round(self.width()/2)-10,30))
                newbtn.setText("Save Configuration")
                newbtn.setStyleSheet("background: \"#37D400\";")
                newbtn.clicked.connect(self.saveConfig)

                cclbtn = QPushButton(self)
                cclbtn.setGeometry(QRect(round(self.width()/2)+5,self.height()-40,round(self.width()/2)-10,30))
                cclbtn.setText("Cancel")
                cclbtn.setStyleSheet("background: \"#FF5757\";")
                cclbtn.clicked.connect(self.reject)

                #
                self.show() 

    def saveConfig(self) :
        new_cfg = Configuration() 
        values = self.table.values 
        ##
        name_str = str(datetime.today().strftime("%Y-%m-%d"))
        for i,v in enumerate(values) : 
            print(v)
            new_cfg.containers[i]["enabled"] = v[0]
            if v[0] and not v[1] in name_str :
                name_str += "_"+v[1]
        ##
        new_cfg.exportConfiguration(os.path.join(ROOT,"configurations/"+name_str+".json"))
        Logger.instance().logMessage("Saved configuration "+name_str+".json")
        ##
        self.accept()
        
    



