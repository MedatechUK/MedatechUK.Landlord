from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

class CustomSlider(QSlider):
    
    keyPress_Event = pyqtSignal(int)        

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def keyPressEvent(self, event):
        self.keyPress_Event.emit(event.key())