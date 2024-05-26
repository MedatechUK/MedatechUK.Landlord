from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

class OkOnlyDialog(QMessageBox):
    def __init__(self , title="OK Dialog", message="message"):
        super().__init__()
        self.setWindowTitle(title)                                            
        self.setText(message)
        self.setStandardButtons(QMessageBox.StandardButton.Ok )
        
