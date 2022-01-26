import os,sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from channel_viewer import ChannelViewer
from config import Configuration

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
        #self.channel_list.setEnabled(False)
        self.channel_list.setModel(self.table_model)
        header = self.channel_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        #
        self.config = None 
        
        ## show the ui 
        if(screen_geo.width() <= 1100 or screen_geo.height() <= 700) : 
            self.showFullScreen()
        else :
            self.show()

        ## Button events
        self.open_btn.clicked.connect(self.handleConfiguration)
        
    def handleConfiguration(self) :
        if self.config is None :
            try :
                config = Configuration(self)
            except Exception :
                ## TODO: go back to nothing loaded
                self.config = None 
                self.open_btn.setText("Open Configuration...")
                self.err_lbl.setText("Analog Channels are not yet initialized.")
                self.err_lbl.setEnabled(True)
                self.channel_list.setEnabled(False)
            else :
                ## TODO: implement loaded stuff on UI 
                self.config = config 
                self.open_btn.setText("Close Configuration")
                self.name_lbl.setText(config.name)
                self.created_lbl.setText(config.data["created"])
                self.modified_lbl.setText(config.data["modified"])
                self.analog_lbl.setText(str(config.data["analog"]))
                self.tcp_lbl.setText(str(config.data["tcp"]))
                #
                # TODO: Link analog channel display to docker image
                self.err_lbl.setText("")
                self.err_lbl.setEnabled(False)
                self.channel_list.setEnabled(True)
        else :
            ## we have a config
            ## TODO: prompt 
            self.config.saveConfig() 
            self.config = None 
            self.open_btn.setText("Open Configuration...")
            self.name_lbl.setText(".json")
            self.created_lbl.setText("")
            self.modified_lbl.setText("")
            self.analog_lbl.setText("False")
            self.tcp_lbl.setText("False")
            #
            # TODO: Link analog channel display to docker image
            self.err_lbl.setText("Analog Channels are not yet initialized.")
            self.err_lbl.setEnabled(True)
            self.channel_list.setEnabled(False)

    def closeEvent(self, event) :
        if self.config :
            self.config.saveConfig() 
        #
        self.accept() 




app = QApplication(sys.argv)
app.setStyle('Fusion')
interface = Interface() 
sys.exit(app.exec_())
