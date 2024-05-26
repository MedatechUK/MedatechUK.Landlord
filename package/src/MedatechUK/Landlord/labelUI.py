from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

class MyLabel(QLabel):
    
    wheel_event = pyqtSignal(int)
    mouse_click = pyqtSignal(QPointF)
    mouse_Move = pyqtSignal(QPointF)    
    mouse_drop = pyqtSignal(str, QPointF)
    
    @property
    def pixmap(self):
        """Get the current pixmap."""
        return self._pixmap

    @pixmap.setter
    def pixmap(self, value):
        """Set a new pixmap."""
        self._pixmap = value
        self.setPixmap(self._pixmap)  # Update the label's display    

    def __init__(self ,  parent=None ):
        super().__init__(parent)

        self._pixmap = QPixmap()
        self.setScaledContents(True)  # Scale pixmap to label size        
        self.setAcceptDrops(True)
        self.drag = True

    def wheelEvent(self, event):
        # Get the rotation angle (positive for forward, negative for backward)        
        self.wheel_event.emit(( event.angleDelta().y() // 120 ) * 50)
    
    def relPos(self, event):
        # Get the position of the mouse click
        x, y = event.pos().x(), event.pos().y()

        # Convert label coordinates to pixmap coordinates
        pixmap_rect = self.pixmap.rect()
        return QPointF(
            (x - pixmap_rect.x()) / pixmap_rect.width()
            , 1 - (y - pixmap_rect.y()) / pixmap_rect.height() 
        )

    def mousePressEvent(self, event):        
        # Call the Scale method when the label is clicked
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = self.relPos(event)
            self.mouse_click.emit(self.relPos(event))
    
    def mouseMoveEvent(self, event):
        self.drag = False
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        pos = self.relPos(event)        
        self.mouse_Move.emit(
            QPointF(
                self.drag_start_position.x()-pos.x()
                , self.drag_start_position.y()-pos.y()
        ))
        self.drag_start_position = pos
        self.drag = True

    def mouseReleaseEvent(self, event):
        # Emit the signal when the mouse is released
        if self.drag :
            self.drag = False            
            
        # Call the parent class's mouseReleaseEvent to ensure proper event handling
        super(MyLabel, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/plain"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("text/plain"):
            x, y = event.position().x(), event.position().y()

            # Convert label coordinates to pixmap coordinates
            pixmap_rect = self.pixmap.rect()            
            self.mouse_drop.emit( 
                event.mimeData().text() 
                , QPointF(
                    (x - pixmap_rect.x()) / pixmap_rect.width()
                    , 1 - (y - pixmap_rect.y()) / pixmap_rect.height() 
                )      
            )


