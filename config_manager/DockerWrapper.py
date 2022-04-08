from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib import container
from Logs import Logger
import time 
#
try :
    import docker 
except Exception as err :
    Logger.instance().logError(err)
else :
    Logger.instance().logMessage("Docker Module loaded successfully!")

class DockerWatchdog(QThread) :
    
    def __init__(self, parent, table) :
        QThread.__init__(self, parent)
        #
        self.table = table 
        self.start()

    def run(self) :
        Logger.instance().logMessage("Connecting to docker CLI")
        try :
            CLI = docker.DockerClient(base_url='unix://var/run/docker.sock') ## TODO make multiplatform
        except Exception as err:
            Logger.instance().logError(err)
            Logger.instance().logMessage("Docker CLI unavailable.")
        else :
            Logger.instance().logMessage("Docker CLI Connection established.")
            self.DockerCLI = CLI 
            ## 
            while True :
                # Refresh docker every second
                try :
                    containers = self.DockerCLI.containers.list(all=True)
                    tbl = [[c.status, c.name, c.id] for c in containers]
                    self.table.update(tbl)
                except Exception as e:
                    pass
                
                time.sleep(1)

class DockerWrapper(QWidget) :
    class Table(QAbstractTableModel) :
        def __init__(self, parent) :
            QAbstractTableModel.__init__(self, parent)
            self.Header = ["Container Status","Container Name"]
            self.Rows = [] 

        def update(self, new_data) :
            self.beginResetModel() 
            self.Rows = new_data
            self.endResetModel()
        
        def rowCount(self, index) :
            return len(self.Rows)
        
        def columnCount(self, index) :
            return len(self.Header)
        
        def data(self, index, role=Qt.DisplayRole) :
            if role == Qt.DisplayRole :
                r = index.row()
                c = index.column()
                return self.Rows[r][c]
        
        def headerData(self, section, orientation, role=Qt.DisplayRole) :
            if orientation == Qt.Horizontal and role == Qt.DisplayRole :
                return self.Header[section]
            return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def __init__(self, parent, geometry=QRect()) :
        QWidget.__init__(self, parent) 
        self.setStyleSheet("background: \"#00CDFF\"; font: 18pt \"Arial\";")
        self.setGeometry(geometry)
        #
        self.table = self.Table(self)
        self.view = QTableView(parent)
        self.view.setStyleSheet("font:16pt \"Arial\";")
        self.view.setGeometry(geometry)
        self.view.setModel(self.table)
        ## Edit the header
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1,QHeaderView.Stretch)
        ##
        # show gui
        self.show() 
        ##
        self.wd = DockerWatchdog(self, self.table)
