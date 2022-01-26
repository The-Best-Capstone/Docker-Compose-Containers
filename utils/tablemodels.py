from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TableModel(QAbstractTableModel) :
    def __init__(self, parent, headers=[], values=[]) :
        QAbstractTableModel.__init__(self, parent)
        self.headers = headers 
        self.values = values 

    def rowCount(self, index) :
        return len(self.values)
    
    def columnCount(self, index) :
        return len(self.headers) 

    def data(self, index, role=Qt.DisplayRole) :
        if role == Qt.DisplayRole :
            r = index.row()
            c = index.column() 
            return self.values[r][c]

    def headerData(self, section, orientation, role=Qt.DisplayRole) :
        if orientation == Qt.Horizontal and role == Qt.DisplayRole :
            return self.headers[section] 
        # otherwise return the default
        return QAbstractTableModel.headerData(self, section, orientation, role)


class ItemModel(QAbstractItemModel) :
    def __init__(self, parent, headers=[], values=[]) :
        QAbstractItemModel.__init__(self, parent)
        self.headers = headers 
        self.values = values 

    def rowCount(self, index) :
        return len(self.values)
    
    def columnCount(self, index) :
        return len(self.headers) 

    def data(self, index, role=Qt.DisplayRole) :
        if role == Qt.DisplayRole :
            r = index.row()
            c = index.column() 
            return self.values[r][c]

    def headerData(self, section, orientation, role=Qt.DisplayRole) :
        if orientation == Qt.Horizontal and role == Qt.DisplayRole :
            return self.headers[section] 
        # otherwise return the default
        return QAbstractTableModel.headerData(self, section, orientation, role)