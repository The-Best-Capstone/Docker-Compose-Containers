import threading
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np 
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime

from pandas import interval_range 
from viewer.consumer import temporaryConsumer 

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlim(0, 1000)
        self.axes.set_ylim(-10,10)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass

class LinePlotWidget(QDialog) :

    def __init__(self, parent=None, topic=None, title=None, ylabel=None) :
        QDialog.__init__(self, parent)
        #
        self.setWindowTitle(title)
        #
        self.setFixedWidth(600)
        self.setFixedHeight(400)
        #
        self.canvas = MyMplCanvas(self, width=5, height=4, dpi=100)
        #
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        #
        self.line = None
        #
        self.consumer = temporaryConsumer(topic, None, self.newValue)
        #
        self.start_time = datetime.now()
        #
        self.x = np.arange(0,1000,1)
        self.y = np.zeros(1000)
        #
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)
        #
        self.ani = animation.FuncAnimation(self.canvas.figure, self.nextFrame, blit=True, interval=10)

    @pyqtSlot (float)
    def newValue(self, value) :
        self.value = value 

    def nextFrame(self, i) :
        now = datetime.now() 
        elapsed = float((now-self.start_time).total_seconds())
        #
        self.y = np.insert(self.y, 0, self.value, axis=0)
        #
        if len(self.y) > 1000 :
            self.y = self.y[:-1]
        #
        self.line.set_ydata(self.y)             
        #
        return [self.line]
        #self.canvas.flush_events() 

    def closeEvent(self, event) :
        self.ani._stop()
        self.consumer.stop()
        self.consumer.join() 
        event.accept()
        

