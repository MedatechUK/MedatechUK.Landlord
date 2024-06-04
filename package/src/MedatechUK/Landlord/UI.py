import configparser , os

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QDockWidget, QSlider, QMessageBox, QPushButton

from pyqtgraph.parametertree import ParameterTree , Parameter
from MedatechUK.Landlord.label import sType

class MyLabel(QLabel):    

    """Custom QLabel widget with additional signals and functionality.

    This class extends the QLabel widget and adds the following features:
    - Signals for wheel events, mouse clicks, mouse movement, mouse drops, and right clicks.
    - Ability to set and get the current pixmap.
    - Scaling the pixmap to fit the label size.
    - Accepting drops and handling drag events.
    - Converting label coordinates to pixmap coordinates.
    - Handling mouse press, move, and release events.
    """

    wheel_event = pyqtSignal(int)
    mouse_click = pyqtSignal(QPointF)
    mouse_Move = pyqtSignal(QPointF)    
    mouse_drop = pyqtSignal(str, QPointF)
    right_click = pyqtSignal(QPointF)

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
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.drag_start_position = self.relPos(event)
                self.mouse_click.emit(self.relPos(event))
                
            case Qt.MouseButton.RightButton:      
                self.drag = False          
                self.right_click.emit(self.relPos(event))
        
    def mouseMoveEvent(self, event):
        # Emit the signal when the mouse is moved
        self.drag = False
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        # Calculate the distance moved by the mouse
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
            event.accept()

class MyForm(QMainWindow):
    """
    This class represents a custom form widget.

    It inherits from the QMainWindow class and provides additional functionality
    for handling key press and close events.

    Signals:
        - keyPress_Event: Signal emitted when a key press event occurs.
        - close_Event: Signal emitted when the form is being closed.

    Attributes:
        - closing: Boolean flag indicating whether the form is being closed.

    Methods:
        - keyPressEvent: Overrides the keyPressEvent method to emit the keyPress_Event signal.
        - closeEvent: Overrides the closeEvent method to emit the close_Event signal and handle the close event.

    """

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

class myProps(ParameterTree):
    """
    A class representing properties.

    This class inherits from the ParameterTree class.

    Parameters:
        parent (QWidget): The parent widget for the myProps instance.

    Attributes:
        None

    Methods:
        __init__(self, parent=None): Initializes a new instance of the myProps class.

    """
    def __init__(self , parent=None):
        super().__init__(parent)

class DragButton(QPushButton):
    """
    A custom button that supports dragging and dropping.

    Inherits from QPushButton.

    Attributes:
        None

    Methods:
        __init__(self, parent=None): Initializes the DragButton object.
        mouseMoveEvent(self, e): Handles the mouse move event for dragging the button.

    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(self.size())
        
    def mouseMoveEvent(self, e):
        """
        Handles the mouse move event for dragging the button.

        Args:
            e (QMouseEvent): The mouse event object.

        Returns:
            None

        """
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()                     
            mime.setData("text/plain", bytes(self.objectName(), 'utf-8'))
            drag.setMimeData(mime) 
            drag.exec(Qt.DropAction.MoveAction)

class ClickButton(QPushButton):
    """
    A custom QPushButton that emits a signal when clicked.

    Inherits from QPushButton and adds a custom signal `mouse_click` that is emitted
    when the button is clicked with the left mouse button.

    Attributes:
        mouse_click (pyqtSignal): A signal that is emitted when the button is clicked.

    Methods:
        __init__(self, parent=None): Initializes the ClickButton object.
        mousePressEvent(self, e): Overrides the mousePressEvent to emit the `mouse_click` signal.

    """

    mouse_click = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initializes the ClickButton object.

        Args:
            parent (QWidget): The parent widget of the button.

        """
        super().__init__(parent)
        self.setIconSize(self.size())

    def mousePressEvent(self, e):
        """
        Overrides the mousePressEvent to emit the `mouse_click` signal.

        Args:
            e (QMouseEvent): The mouse event object.

        """
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.mouse_click.emit(self.objectName())

class OkOnlyDialog(QMessageBox):
    """
    Custom dialog box with only an 'OK' button.

    Args:
        title (str): The title of the dialog box. Default is 'OK Dialog'.
        message (str): The message to be displayed in the dialog box. Default is 'message'.
    """
    def __init__(self, title="OK Dialog", message="message"):
        super().__init__()
        self.setWindowTitle(title)                                            
        self.setText(message)
        self.setStandardButtons(QMessageBox.StandardButton.Ok )
                    
class MyDockWidget(QDockWidget):
    """
    Custom dock widget class that emits a signal when a key is pressed.
    """

    key_press = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)        

    def keyPressEvent(self, event):
        """
        Overrides the keyPressEvent method to emit a signal when a key is pressed.

        Args:
            event (QKeyEvent): The key event object.

        Returns:
            None
        """
        self.key_press.emit(event.key())

class CustomSlider(QSlider):
    """
    A custom slider widget that emits a signal when a key is pressed.
    """

    keyPress_Event = pyqtSignal(int)        

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def keyPressEvent(self, event):
        """
        Overrides the keyPressEvent method of QSlider.
        Emits the keyPress_Event signal with the key code of the pressed key.
        
        Args:
            event (QKeyEvent): The key event object.
        """
        self.keyPress_Event.emit(event.key())

class iniTree(ParameterTree):
    """
    A custom class that extends the ParameterTree class.
    This class represents a tree structure for managing and displaying parameters.

    Attributes:
        _WorkingDir (str): The working directory path.
    """

    def __init__(self, parent=None):        
        super().__init__(parent)     
        self._WorkingDir = None

    @property
    def WorkingDir(self):
        """
        Get the working directory path.

        Returns:
            str: The working directory path.
        """
        return self._WorkingDir

    @WorkingDir.setter
    def WorkingDir(self, value):
        """
        Set the working directory path.

        Args:
            value (str): The working directory path.
        """
        self._WorkingDir = value
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.WorkingDir, "Settings.ini"))    
        p = self.getParams()        
        self.setParameters(p, showTop=False)
        for child in p.children():
            for child in child.childs:
                child.sigValueChanged.connect(self.handleChange)

    def getParams(self):
        """
        Get the parameters from the configuration file.

        Returns:
            Parameter: The parameters as a Parameter object.
        """
        parameters = []

        for c in self.config.sections():                
            parameters.append({'name': c,
                'type': 'group',
                'children': []
            })        
            for ch in dict(self.config.items(c)):                
                parameters[len(parameters)-1]['children'].append(
                    { 'title': ch, 'name': "{}.{}".format(c,ch), 'type': 'str', 'value': self.config[c][ch] }
                )

        return Parameter.create(name='params', type='group', children=parameters)
    
    def handleChange(self, _param, _value):
        """
        Handle the change event when a parameter value is modified.

        Args:
            _param (Parameter): The parameter object that triggered the event.
            _value (str): The new value of the parameter.
        """
        sect = _param.opts["name"].split(".")[0]
        key = _param.opts["name"].split(".")[1]
        self.config.set(sect, key, _value)
        with open(self.filename, 'w') as f:
            self.config.write(f)

class UI(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 626)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ico/qrcode"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(166, 166, 165))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(166, 166, 165))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(166, 166, 165))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(166, 166, 165))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        self.centralwidget.setPalette(palette)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.frame = QtWidgets.QFrame(parent=self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.label = MyLabel(parent=self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText("")
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.gridLayout_4.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.gridLayout_3.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 21))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(parent=self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Tools = QtWidgets.QMenu(parent=self.menubar)
        self.menu_Tools.setObjectName("menu_Tools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockTools = QtWidgets.QDockWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockTools.sizePolicy().hasHeightForWidth())
        self.dockTools.setSizePolicy(sizePolicy)
        self.dockTools.setMinimumSize(QtCore.QSize(55, 250))
        self.dockTools.setMaximumSize(QtCore.QSize(55, 300))
        self.dockTools.setAutoFillBackground(True)
        self.dockTools.setFloating(False)
        self.dockTools.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dockTools.setAllowedAreas(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea|QtCore.Qt.DockWidgetArea.LeftDockWidgetArea|QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockTools.setObjectName("dockTools")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents_3.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents_3.setSizePolicy(sizePolicy)
        self.dockWidgetContents_3.setMinimumSize(QtCore.QSize(60, 0))
        self.dockWidgetContents_3.setMaximumSize(QtCore.QSize(60, 16777215))
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.dockWidgetContents_3)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.gridLayout_2.setContentsMargins(3, 2, 10, 2)
        self.gridLayout_2.setSpacing(2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btnAddTextBox = DragButton(parent=self.dockWidgetContents_3)
        self.btnAddTextBox.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAddTextBox.sizePolicy().hasHeightForWidth())
        self.btnAddTextBox.setSizePolicy(sizePolicy)
        self.btnAddTextBox.setMinimumSize(QtCore.QSize(0, 0))
        self.btnAddTextBox.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ico/text"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnAddTextBox.setIcon(icon1)
        self.btnAddTextBox.setIconSize(QtCore.QSize(32, 32))
        self.btnAddTextBox.setObjectName("btnAddTextBox")
        self.verticalLayout_2.addWidget(self.btnAddTextBox)
        self.btnAddImg = DragButton(parent=self.dockWidgetContents_3)
        self.btnAddImg.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAddImg.sizePolicy().hasHeightForWidth())
        self.btnAddImg.setSizePolicy(sizePolicy)
        self.btnAddImg.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/ico/image"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnAddImg.setIcon(icon2)
        self.btnAddImg.setIconSize(QtCore.QSize(32, 32))
        self.btnAddImg.setObjectName("btnAddImg")
        self.verticalLayout_2.addWidget(self.btnAddImg)
        self.btnAddBarcode = DragButton(parent=self.dockWidgetContents_3)
        self.btnAddBarcode.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAddBarcode.sizePolicy().hasHeightForWidth())
        self.btnAddBarcode.setSizePolicy(sizePolicy)
        self.btnAddBarcode.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/ico/barcode"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnAddBarcode.setIcon(icon3)
        self.btnAddBarcode.setIconSize(QtCore.QSize(32, 32))
        self.btnAddBarcode.setObjectName("btnAddBarcode")
        self.verticalLayout_2.addWidget(self.btnAddBarcode)
        self.btnAddQR = DragButton(parent=self.dockWidgetContents_3)
        self.btnAddQR.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAddQR.sizePolicy().hasHeightForWidth())
        self.btnAddQR.setSizePolicy(sizePolicy)
        self.btnAddQR.setText("")
        self.btnAddQR.setIcon(icon)
        self.btnAddQR.setIconSize(QtCore.QSize(32, 32))
        self.btnAddQR.setObjectName("btnAddQR")
        self.verticalLayout_2.addWidget(self.btnAddQR)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.dockTools.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockTools)
        self.dockProperties = QtWidgets.QDockWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockProperties.sizePolicy().hasHeightForWidth())
        self.dockProperties.setSizePolicy(sizePolicy)
        self.dockProperties.setMinimumSize(QtCore.QSize(300, 90))
        self.dockProperties.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dockProperties.setAllowedAreas(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea|QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockProperties.setObjectName("dockProperties")
        self.dockWidgetContents_6 = QtWidgets.QWidget()
        self.dockWidgetContents_6.setObjectName("dockWidgetContents_6")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents_6)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout_6.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_6.setSpacing(2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.comboBox = QtWidgets.QComboBox(parent=self.dockWidgetContents_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_6.addWidget(self.comboBox)
        self.line_3 = QtWidgets.QFrame(parent=self.dockWidgetContents_6)
        self.line_3.setMinimumSize(QtCore.QSize(5, 5))
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_6.addWidget(self.line_3)
        self.btnCopyShape = ClickButton(parent=self.dockWidgetContents_6)
        self.btnCopyShape.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCopyShape.sizePolicy().hasHeightForWidth())
        self.btnCopyShape.setSizePolicy(sizePolicy)
        self.btnCopyShape.setMaximumSize(QtCore.QSize(32, 22))
        self.btnCopyShape.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.btnCopyShape.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/ico/copy"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnCopyShape.setIcon(icon4)
        self.btnCopyShape.setObjectName("btnCopyShape")
        self.horizontalLayout_6.addWidget(self.btnCopyShape)
        self.btnUpDown = ClickButton(parent=self.dockWidgetContents_6)
        self.btnUpDown.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnUpDown.sizePolicy().hasHeightForWidth())
        self.btnUpDown.setSizePolicy(sizePolicy)
        self.btnUpDown.setMaximumSize(QtCore.QSize(32, 22))
        self.btnUpDown.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/ico/sendfront"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnUpDown.setIcon(icon5)
        self.btnUpDown.setObjectName("btnUpDown")
        self.horizontalLayout_6.addWidget(self.btnUpDown)
        self.btnDeleteShape = ClickButton(parent=self.dockWidgetContents_6)
        self.btnDeleteShape.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeleteShape.sizePolicy().hasHeightForWidth())
        self.btnDeleteShape.setSizePolicy(sizePolicy)
        self.btnDeleteShape.setMaximumSize(QtCore.QSize(32, 22))
        self.btnDeleteShape.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/ico/delete"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnDeleteShape.setIcon(icon6)
        self.btnDeleteShape.setObjectName("btnDeleteShape")
        self.horizontalLayout_6.addWidget(self.btnDeleteShape)
        self.btnUp = QtWidgets.QPushButton(parent=self.dockWidgetContents_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnUp.sizePolicy().hasHeightForWidth())
        self.btnUp.setSizePolicy(sizePolicy)
        self.btnUp.setMaximumSize(QtCore.QSize(0, 0))
        self.btnUp.setObjectName("btnUp")
        self.horizontalLayout_6.addWidget(self.btnUp)
        self.btnDown = QtWidgets.QPushButton(parent=self.dockWidgetContents_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDown.sizePolicy().hasHeightForWidth())
        self.btnDown.setSizePolicy(sizePolicy)
        self.btnDown.setMaximumSize(QtCore.QSize(0, 0))
        self.btnDown.setObjectName("btnDown")
        self.horizontalLayout_6.addWidget(self.btnDown)
        self.btnDelete = QtWidgets.QPushButton(parent=self.dockWidgetContents_6)
        self.btnDelete.setMaximumSize(QtCore.QSize(0, 0))
        self.btnDelete.setText("")
        self.btnDelete.setObjectName("btnDelete")
        self.horizontalLayout_6.addWidget(self.btnDelete)
        self.btnLeft = QtWidgets.QPushButton(parent=self.dockWidgetContents_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnLeft.sizePolicy().hasHeightForWidth())
        self.btnLeft.setSizePolicy(sizePolicy)
        self.btnLeft.setMaximumSize(QtCore.QSize(0, 0))
        self.btnLeft.setObjectName("btnLeft")
        self.horizontalLayout_6.addWidget(self.btnLeft)
        self.btnRight = QtWidgets.QPushButton(parent=self.dockWidgetContents_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRight.sizePolicy().hasHeightForWidth())
        self.btnRight.setSizePolicy(sizePolicy)
        self.btnRight.setMaximumSize(QtCore.QSize(0, 0))
        self.btnRight.setObjectName("btnRight")
        self.horizontalLayout_6.addWidget(self.btnRight)
        self.gridLayout.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.propertyWidget = myProps(parent=self.dockWidgetContents_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.propertyWidget.sizePolicy().hasHeightForWidth())
        self.propertyWidget.setSizePolicy(sizePolicy)
        self.propertyWidget.setStyleSheet("QTreeView {\n"
"                background-color: rgb(46, 52, 54);\n"
"                alternate-background-color: rgb(39, 44, 45);    \n"
"                color: rgb(238, 238, 238);\n"
"            }\n"
"            QLabel {\n"
"                color: rgb(238, 238, 238);\n"
"            }\n"
"            QTreeView::item:has-children {\n"
"                background-color: \'#212627\';\n"
"                color: rgb(233, 185, 110);\n"
"            }\n"
"            QTreeView::item:selected {\n"
"                background-color: rgb(92, 53, 102);\n"
"            }")
        self.propertyWidget.setObjectName("propertyWidget")
        self.verticalLayout.addWidget(self.propertyWidget)
        self.gridLayout.addLayout(self.verticalLayout, 2, 0, 1, 1)
        self.dockProperties.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockProperties)
        self.btnDock = QtWidgets.QDockWidget(parent=MainWindow)
        self.btnDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.btnDock.setAllowedAreas(QtCore.Qt.DockWidgetArea.TopDockWidgetArea)
        self.btnDock.setObjectName("btnDock")
        self.dockWidgetContents = QtWidgets.QWidget()
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        self.dockWidgetContents.setPalette(palette)
        self.dockWidgetContents.setAutoFillBackground(True)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout_5.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnNew = ClickButton(parent=self.dockWidgetContents)
        self.btnNew.setEnabled(False)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        self.btnNew.setPalette(palette)
        self.btnNew.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/ico/newfile"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnNew.setIcon(icon7)
        self.btnNew.setIconSize(QtCore.QSize(32, 32))
        self.btnNew.setObjectName("btnNew")
        self.horizontalLayout.addWidget(self.btnNew)
        self.btnOpen = ClickButton(parent=self.dockWidgetContents)
        self.btnOpen.setEnabled(False)
        self.btnOpen.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/ico/openfile"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnOpen.setIcon(icon8)
        self.btnOpen.setIconSize(QtCore.QSize(32, 32))
        self.btnOpen.setObjectName("btnOpen")
        self.horizontalLayout.addWidget(self.btnOpen)
        self.line = QtWidgets.QFrame(parent=self.dockWidgetContents)
        self.line.setMinimumSize(QtCore.QSize(10, 0))
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.btnSave = ClickButton(parent=self.dockWidgetContents)
        self.btnSave.setEnabled(False)
        self.btnSave.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/ico/savefile"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnSave.setIcon(icon9)
        self.btnSave.setIconSize(QtCore.QSize(32, 32))
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout.addWidget(self.btnSave)
        self.btnSaveas = ClickButton(parent=self.dockWidgetContents)
        self.btnSaveas.setEnabled(False)
        self.btnSaveas.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/ico/saveasfile"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnSaveas.setIcon(icon10)
        self.btnSaveas.setIconSize(QtCore.QSize(32, 32))
        self.btnSaveas.setObjectName("btnSaveas")
        self.horizontalLayout.addWidget(self.btnSaveas)
        self.line_2 = QtWidgets.QFrame(parent=self.dockWidgetContents)
        self.line_2.setMinimumSize(QtCore.QSize(10, 0))
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.btnPrint = ClickButton(parent=self.dockWidgetContents)
        self.btnPrint.setEnabled(False)
        self.btnPrint.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/ico/printfile"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.btnPrint.setIcon(icon11)
        self.btnPrint.setIconSize(QtCore.QSize(32, 32))
        self.btnPrint.setObjectName("btnPrint")
        self.horizontalLayout.addWidget(self.btnPrint)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.gridLayout_5.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.btnDock.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.btnDock)
        self.dockLabels = QtWidgets.QDockWidget(parent=MainWindow)
        self.dockLabels.setMinimumSize(QtCore.QSize(300, 90))
        self.dockLabels.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockLabels.setAllowedAreas(QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockLabels.setObjectName("dockLabels")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents_2.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents_2.setSizePolicy(sizePolicy)
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_7.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_7.setSpacing(2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_6.setSpacing(2)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.labelCombo = QtWidgets.QComboBox(parent=self.dockWidgetContents_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCombo.sizePolicy().hasHeightForWidth())
        self.labelCombo.setSizePolicy(sizePolicy)
        self.labelCombo.setObjectName("labelCombo")
        self.gridLayout_6.addWidget(self.labelCombo, 0, 0, 1, 1)
        self.line_4 = QtWidgets.QFrame(parent=self.dockWidgetContents_2)
        self.line_4.setMinimumSize(QtCore.QSize(5, 0))
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout_6.addWidget(self.line_4, 0, 1, 1, 1)
        self.btnCopyLabel = ClickButton(parent=self.dockWidgetContents_2)
        self.btnCopyLabel.setMaximumSize(QtCore.QSize(32, 22))
        self.btnCopyLabel.setText("")
        self.btnCopyLabel.setIcon(icon4)
        self.btnCopyLabel.setIconSize(QtCore.QSize(19, 16))
        self.btnCopyLabel.setObjectName("btnCopyLabel")
        self.gridLayout_6.addWidget(self.btnCopyLabel, 0, 2, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.labelWidget = myProps(parent=self.dockWidgetContents_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelWidget.sizePolicy().hasHeightForWidth())
        self.labelWidget.setSizePolicy(sizePolicy)
        self.labelWidget.setStyleSheet("QTreeView {\n"
"                background-color: rgb(46, 52, 54);\n"
"                alternate-background-color: rgb(39, 44, 45);    \n"
"                color: rgb(238, 238, 238);\n"
"            }\n"
"            QLabel {\n"
"                color: rgb(238, 238, 238);\n"
"            }\n"
"            QTreeView::item:has-children {\n"
"                background-color: \'#212627\';\n"
"                color: rgb(233, 185, 110);\n"
"            }\n"
"            QTreeView::item:selected {\n"
"                background-color: rgb(92, 53, 102);\n"
"            }")
        self.labelWidget.setObjectName("labelWidget")
        self.verticalLayout_4.addWidget(self.labelWidget)
        self.gridLayout_7.addLayout(self.verticalLayout_4, 1, 0, 1, 1)
        self.dockLabels.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockLabels)
        self.dockSettings = QtWidgets.QDockWidget(parent=MainWindow)
        self.dockSettings.setEnabled(True)
        self.dockSettings.setMinimumSize(QtCore.QSize(300, 90))
        self.dockSettings.setStyleSheet("QTreeView {\n"
"                background-color: rgb(46, 52, 54);\n"
"                alternate-background-color: rgb(39, 44, 45);    \n"
"                color: rgb(238, 238, 238);\n"
"            }\n"
"            QLabel {\n"
"                color: rgb(238, 238, 238);\n"
"            }\n"
"            QTreeView::item:has-children {\n"
"                background-color: \'#212627\';\n"
"                color: rgb(233, 185, 110);\n"
"            }\n"
"            QTreeView::item:selected {\n"
"                background-color: rgb(92, 53, 102);\n"
"            }")
        self.dockSettings.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockSettings.setAllowedAreas(QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockSettings.setObjectName("dockSettings")
        self.dockWidgetContents_4 = QtWidgets.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.dockWidgetContents_4)
        self.gridLayout_8.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_8.setSpacing(2)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.settingsWidget = iniTree(parent=self.dockWidgetContents_4)
        self.settingsWidget.setObjectName("settingsWidget")
        self.verticalLayout_5.addWidget(self.settingsWidget)
        self.gridLayout_8.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        self.dockSettings.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockSettings)
        self.action_Open = QtGui.QAction(parent=MainWindow)
        self.action_Open.setIcon(icon8)
        self.action_Open.setObjectName("action_Open")
        self.actionSave = QtGui.QAction(parent=MainWindow)
        self.actionSave.setIcon(icon9)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtGui.QAction(parent=MainWindow)
        self.actionSaveAs.setIcon(icon10)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionExit = QtGui.QAction(parent=MainWindow)
        self.actionExit.setIcon(icon)
        self.actionExit.setObjectName("actionExit")
        self.action_New = QtGui.QAction(parent=MainWindow)
        self.action_New.setIcon(icon7)
        self.action_New.setObjectName("action_New")
        self.action = QtGui.QAction(parent=MainWindow)
        self.action.setObjectName("action")
        self.action_2 = QtGui.QAction(parent=MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_Print = QtGui.QAction(parent=MainWindow)
        self.action_Print.setIcon(icon11)
        self.action_Print.setObjectName("action_Print")
        self.btnRefreshFont = QtGui.QAction(parent=MainWindow)
        self.btnRefreshFont.setIcon(icon1)
        self.btnRefreshFont.setObjectName("btnRefreshFont")
        self.btnLabels = QtGui.QAction(parent=MainWindow)
        self.btnLabels.setCheckable(True)
        self.btnLabels.setChecked(False)
        self.btnLabels.setObjectName("btnLabels")
        self.btnSettings = QtGui.QAction(parent=MainWindow)
        self.btnSettings.setCheckable(True)
        self.btnSettings.setObjectName("btnSettings")
        self.menu_File.addAction(self.action_New)
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSave)
        self.menu_File.addAction(self.actionSaveAs)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Print)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionExit)
        self.menu_Tools.addAction(self.btnLabels)
        self.menu_Tools.addAction(self.btnSettings)
        self.menu_Tools.addSeparator()
        self.menu_Tools.addAction(self.btnRefreshFont)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Tools.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Landlord Labels"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Tools.setTitle(_translate("MainWindow", "&View"))
        self.dockTools.setWindowTitle(_translate("MainWindow", "Tools"))
        self.btnAddTextBox.setToolTip(_translate("MainWindow", "Add Text Shape"))
        self.btnAddTextBox.setStatusTip(_translate("MainWindow", "Add Text Shape"))
        self.btnAddImg.setToolTip(_translate("MainWindow", "Add Image Shape"))
        self.btnAddImg.setStatusTip(_translate("MainWindow", "Add Image Shape"))
        self.btnAddBarcode.setToolTip(_translate("MainWindow", "Add Barcode"))
        self.btnAddBarcode.setStatusTip(_translate("MainWindow", "Add Barcode"))
        self.btnAddQR.setToolTip(_translate("MainWindow", "Add QR Code"))
        self.btnAddQR.setStatusTip(_translate("MainWindow", "Add QR Code"))
        self.dockProperties.setWindowTitle(_translate("MainWindow", "Properties"))
        self.btnCopyShape.setToolTip(_translate("MainWindow", "Copy Shape"))
        self.btnCopyShape.setStatusTip(_translate("MainWindow", "Copy Shape"))
        self.btnUpDown.setToolTip(_translate("MainWindow", "Z-Order"))
        self.btnUpDown.setStatusTip(_translate("MainWindow", "Z-Order"))
        self.btnDeleteShape.setToolTip(_translate("MainWindow", "Delete Shape"))
        self.btnDeleteShape.setStatusTip(_translate("MainWindow", "Delete Shape"))
        self.btnUp.setText(_translate("MainWindow", "up"))
        self.btnUp.setShortcut(_translate("MainWindow", "Up"))
        self.btnDown.setText(_translate("MainWindow", "down"))
        self.btnDown.setShortcut(_translate("MainWindow", "Down"))
        self.btnDelete.setShortcut(_translate("MainWindow", "Del"))
        self.btnLeft.setText(_translate("MainWindow", "left"))
        self.btnLeft.setShortcut(_translate("MainWindow", "Left"))
        self.btnRight.setText(_translate("MainWindow", "right"))
        self.btnRight.setShortcut(_translate("MainWindow", "Right"))
        self.btnNew.setToolTip(_translate("MainWindow", "New Label"))
        self.btnNew.setStatusTip(_translate("MainWindow", "New Label"))
        self.btnOpen.setToolTip(_translate("MainWindow", "Open Label"))
        self.btnOpen.setStatusTip(_translate("MainWindow", "Open Label"))
        self.btnSave.setToolTip(_translate("MainWindow", "Save Label"))
        self.btnSave.setStatusTip(_translate("MainWindow", "Save Label"))
        self.btnSaveas.setToolTip(_translate("MainWindow", "Save Label As"))
        self.btnSaveas.setStatusTip(_translate("MainWindow", "Save Label As"))
        self.btnPrint.setToolTip(_translate("MainWindow", "Print Label"))
        self.btnPrint.setStatusTip(_translate("MainWindow", "Print Label"))
        self.dockLabels.setWindowTitle(_translate("MainWindow", "Label Stock"))
        self.btnCopyLabel.setToolTip(_translate("MainWindow", "Copy Label"))
        self.btnCopyLabel.setStatusTip(_translate("MainWindow", "Copy Label"))
        self.dockSettings.setWindowTitle(_translate("MainWindow", "Settings"))
        self.action_Open.setText(_translate("MainWindow", "&Open"))
        self.actionSave.setText(_translate("MainWindow", "&Save"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save &As"))
        self.actionExit.setText(_translate("MainWindow", "E&xit"))
        self.action_New.setText(_translate("MainWindow", "&New"))
        self.action.setText(_translate("MainWindow", "-"))
        self.action_2.setText(_translate("MainWindow", "-"))
        self.action_Print.setText(_translate("MainWindow", "&Print"))
        self.btnRefreshFont.setText(_translate("MainWindow", "Import Fonts"))
        self.btnLabels.setText(_translate("MainWindow", "Label Stock"))
        self.btnSettings.setText(_translate("MainWindow", "Settings"))

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Landlord Labels"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Tools.setTitle(_translate("MainWindow", "&View"))
        self.dockTools.setWindowTitle(_translate("MainWindow", "Tools"))
        self.btnAddTextBox.setToolTip(_translate("MainWindow", "Add Text Shape"))
        self.btnAddTextBox.setStatusTip(_translate("MainWindow", "Add Text Shape"))
        self.btnAddImg.setToolTip(_translate("MainWindow", "Add Image Shape"))
        self.btnAddImg.setStatusTip(_translate("MainWindow", "Add Image Shape"))
        self.btnAddBarcode.setToolTip(_translate("MainWindow", "Add Barcode"))
        self.btnAddBarcode.setStatusTip(_translate("MainWindow", "Add Barcode"))
        self.btnAddQR.setToolTip(_translate("MainWindow", "Add QR Code"))
        self.btnAddQR.setStatusTip(_translate("MainWindow", "Add QR Code"))
        self.dockProperties.setWindowTitle(_translate("MainWindow", "Properties"))
        self.btnCopyShape.setToolTip(_translate("MainWindow", "Copy Shape"))
        self.btnCopyShape.setStatusTip(_translate("MainWindow", "Copy Shape"))
        self.btnUpDown.setToolTip(_translate("MainWindow", "Z-Order"))
        self.btnUpDown.setStatusTip(_translate("MainWindow", "Z-Order"))
        self.btnDeleteShape.setToolTip(_translate("MainWindow", "Delete Shape"))
        self.btnDeleteShape.setStatusTip(_translate("MainWindow", "Delete Shape"))
        self.btnUp.setText(_translate("MainWindow", "up"))
        self.btnUp.setShortcut(_translate("MainWindow", "Up"))
        self.btnDown.setText(_translate("MainWindow", "down"))
        self.btnDown.setShortcut(_translate("MainWindow", "Down"))
        self.btnDelete.setShortcut(_translate("MainWindow", "Del"))
        self.btnLeft.setText(_translate("MainWindow", "left"))
        self.btnLeft.setShortcut(_translate("MainWindow", "Left"))
        self.btnRight.setText(_translate("MainWindow", "right"))
        self.btnRight.setShortcut(_translate("MainWindow", "Right"))
        self.btnNew.setToolTip(_translate("MainWindow", "New Label"))
        self.btnNew.setStatusTip(_translate("MainWindow", "New Label"))
        self.btnOpen.setToolTip(_translate("MainWindow", "Open Label"))
        self.btnOpen.setStatusTip(_translate("MainWindow", "Open Label"))
        self.btnSave.setToolTip(_translate("MainWindow", "Save Label"))
        self.btnSave.setStatusTip(_translate("MainWindow", "Save Label"))
        self.btnSaveas.setToolTip(_translate("MainWindow", "Save Label As"))
        self.btnSaveas.setStatusTip(_translate("MainWindow", "Save Label As"))
        self.btnPrint.setToolTip(_translate("MainWindow", "Print Label"))
        self.btnPrint.setStatusTip(_translate("MainWindow", "Print Label"))
        self.dockLabels.setWindowTitle(_translate("MainWindow", "Label Stock"))
        self.btnCopyLabel.setToolTip(_translate("MainWindow", "Copy Label"))
        self.btnCopyLabel.setStatusTip(_translate("MainWindow", "Copy Label"))
        self.dockSettings.setWindowTitle(_translate("MainWindow", "Settings"))
        self.action_Open.setText(_translate("MainWindow", "&Open"))
        self.actionSave.setText(_translate("MainWindow", "&Save"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save &As"))
        self.actionExit.setText(_translate("MainWindow", "E&xit"))
        self.action_New.setText(_translate("MainWindow", "&New"))
        self.action.setText(_translate("MainWindow", "-"))
        self.action_2.setText(_translate("MainWindow", "-"))
        self.action_Print.setText(_translate("MainWindow", "&Print"))
        self.btnRefreshFont.setText(_translate("MainWindow", "Import Fonts"))
        self.btnLabels.setText(_translate("MainWindow", "Label Stock"))
        self.btnSettings.setText(_translate("MainWindow", "Settings"))
