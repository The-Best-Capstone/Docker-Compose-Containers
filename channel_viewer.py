from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from utils.tablemodels import TableModel 
from viewer import LinePlotWidget 

class ChannelViewer(TableModel) :
    def __init__(self, parent=None) :
        self.headers = ["Channel"]
        self.values = []
        for i in range(0,20) : 
            self.values.append(["a"+str(i)])
        ## init super class
        TableModel.__init__(self, parent, self.headers, self.values)
        #
        #
        self.parent().clicked.connect(self.rowClicked)

    def rowClicked(self, index) :
        r = index.row()
        c = index.column() 
        plotdialog = LinePlotWidget(parent=None, topic=self.values[r][0], title=self.values[r][0]+" Plot", ylabel="V DC")
        plotdialog.exec() 