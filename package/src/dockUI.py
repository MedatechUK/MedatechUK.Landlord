from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

class MyDockWidget(QDockWidget):
    
    key_press = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)        

    def keyPressEvent(self, event):
        self.key_press.emit(event.key())