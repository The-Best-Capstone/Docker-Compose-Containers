import os,sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from channel_viewer import ChannelViewer

ROOT = os.path.dirname(__file__) 
CFG_ROOT = os.path.join(ROOT, "configurations")

# Create the default configurations if not exists
if not os.path.exists(CFG_ROOT) :
    os.mkdir(CFG_ROOT)

class Interface(QMainWindow) :

    """
        edutor.ui file:
        details_box GroupBox
            open_btn
            name_lbl
            created_lbl
            modified_lbl
            analog_lbl
            tcp_lbl
        raw_channel_box GroupBox
            channel_list QTableWidget
            err_lbl

    """

    def __init__(self, parent=None) :
        QMainWindow.__init__(self, parent)
        #
        self.setWindowTitle("PowerCube Configuration Editor")
        #
        loadUi(os.path.join(ROOT, "editor.ui"), self)
        ## Window Size
        size = QSize()
        size.setHeight(600)
        size.setWidth(1024)
        self.setFixedSize(size)
        #
        screen = QApplication.instance().primaryScreen()
        screen_geo = screen.availableGeometry() 
        ## channels:
        self.table_model = ChannelViewer(parent=self.channel_list)
        self.channel_list.setModel(self.table_model)

        ## show the ui 
        if(screen_geo.width() <= 1100 or screen_geo.height() <= 700) : 
            self.showFullScreen()
        else :
            self.show()
        
        


app = QApplication(sys.argv)
app.setStyle('Fusion')
interface = Interface() 
sys.exit(app.exec_())
