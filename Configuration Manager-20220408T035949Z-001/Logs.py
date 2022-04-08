from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime
import traceback

class Singleton : 
    def __init__(self, decorated) :
        self._decorated = decorated 
    
    def instance(self) :
        try :
            return self._instance 
        except AttributeError :
            self._instance = self._decorated()
            return self._instance
    
    def __call__(self) :
        raise TypeError("Access singleton through instance()")

    def __instancecheck__(self, instance) :
        return isinstance(instance, self._decorated)

@Singleton
class Logger(Singleton) :

    def __init__(self) :
        self.history = []
        self.subscribers = [] 

    def subscribe(self, callback) :
        try :
            for h in self.history :
                callback(h)
        except Exception :
            pass 
        else :
            self.subscribers.append(callback)

    def publish(self, message) :
        for sub in self.subscribers :
            try :
                sub(message)
            except Exception :
                self.subscribers.remove(sub)
                traceback.print_exc() 
        ##
        self.history.append(message)
        if len(self.history) > 50 :
            self.history.remove(self.history[50])
    
    def logMessage(self, message) :
        self.publish(["Message",str(datetime.now().strftime("%H:%M:%S")), message])

    def logError(self, exception) :
        ## print e or use traceback.format_exc() 
        ## this method expects a string
        self.publish(["Error",str(datetime.now()), str(exception)])


class LogsGui(QWidget) :

    class Table(QAbstractTableModel) :
        def __init__(self, parent) :
            QAbstractTableModel.__init__(self, parent)
            self.Header = ["Type","Time","Message"]
            self.Rows = [] 

        def update(self, new_data) :
            self.beginResetModel() 
            self.Rows.insert(0, new_data)
            if len(self.Rows) > 50 :
                self.Rows.remove(self.Rows[50])
            #
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
        self.setGeometry(geometry)
        self.setStyleSheet("font: 14pt \"Arial\";")
        #
        self.table = self.Table(self)
        self.view = QTableView(parent)
        self.view.setGeometry(geometry)
        self.view.setModel(self.table)
        ## Edit the header
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1,QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2,QHeaderView.Stretch)
        ## Hook the table to the logs
        Logger.instance().subscribe(self.table.update)
        #
        self.show() 