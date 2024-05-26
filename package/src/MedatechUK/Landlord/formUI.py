from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

class MyForm(QMainWindow):
    
    keyPress_Event = pyqtSignal(int)
    close_Event = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)        
        self.closing = False

    def keyPressEvent(self, event):
        self.keyPress_Event.emit(event.key())

    def closeEvent(self, event):
        self.close_Event.emit()
        match self.closing:
            case True: event.accept()
            case _   : event.ignore()                    