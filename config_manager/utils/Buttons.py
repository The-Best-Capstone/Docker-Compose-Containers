from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class CloseButton(QPushButton) :

    def __init__(self, parent) :
        QPushButton.__init__(self, parent)
        #
        self.setStyleSheet("background-color: rgb(255, 0, 0); font: 75 22pt \"Arial\"; color: rgb(255, 255, 255);")
        self.setText("Close")
        self.setGeometry(QRect(parent.width()-105, 5, 100, 40))
        self.show()
        #
        self.clicked.connect(self.onClick)

    def onClick(self) :
        self.parent().close() 