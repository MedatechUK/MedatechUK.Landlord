from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

class DragButton(QPushButton):

    def __init__(self ,  parent=None ):
        super().__init__(parent)
        self.setIconSize(self.size())
        
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()                     
            mime.setData("text/plain", bytes(self.objectName() , 'utf-8'))
            drag.setMimeData(mime) 
            drag.exec(Qt.DropAction.MoveAction)

class ClickButton(QPushButton):
    
    mouse_click = pyqtSignal(str)

    def __init__(self ,  parent=None ):
        super().__init__(parent)
        self.setIconSize(self.size())
        
    def mousePressEvent(self, e): 
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.mouse_click.emit(self.objectName())            