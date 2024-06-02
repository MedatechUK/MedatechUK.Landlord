import os , sys , importlib.util , inspect
from enum import Enum
from decimal import Decimal
from pathlib import Path
from io import BytesIO

from pyqtgraph.parametertree import Parameter, parameterTypes
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

from reportlab.graphics.shapes import Drawing 
from reportlab.graphics import renderPM
from reportlab.lib.units import mm
from reportlab.lib.colors import *
from reportlab.pdfbase import pdfmetrics

import barcode
from barcode.writer import ImageWriter
from barcode import generate
import pyqrcode

mm = Decimal(mm)
sType = Enum('Shape', ['label' , 'qr', 'barcode', 'image' , 'text', 'select'])

class BlankLabel:
    def create_module(self, spec):
        # Create a simple module with the specified attributes
        module = type(spec.name, (object,), {
            "specs": None,
            "border": False,
            "debug": False,
            "testdata": {
                "QR": {"in": [{"i": "PROJACT", "v": 3411}, {"i": "CAT", "v": 14}]}
                , "COUNT": 1
                , 'PAR1' : "Test Data 1"
                , 'PAR2' : "Test Data 2"
                , 'PAR3' : "Test Data 3"
                , 'PAR4' : "Test Data 4"
                , 'PAR5' : "Test Data 5"
                , 'PAR6' : "Test Data 6"
                , 'PAR7' : "Test Data 7"
                , 'PAR8' : "Test Data 8"
                , 'PAR9' : "Test Data 9"
                , 'PAR10' : "Test Data 10"
                , 'PAR11' : "Test Data 11"
                , 'PAR12' : "Test Data 12"
                , 'PAR13' : "Test Data 13"
                , 'PAR14' : "Test Data 14"
                , 'PAR15' : "Test Data 15"
                , 'PAR16' : "Test Data 16"
                , 'PAR17' : "Test Data 17"
                , 'PAR18' : "Test Data 18"
                , 'PAR19' : "Test Data 19"
                , 'PAR20' : "Test Data 20"
            },
            "draw_label": self.draw_label  # Assuming you have a function named draw_label
        })
        return module
    
    def draw_label(self , label, width, height, obj):        
        pass

    def exec_module(self, module):
        # No additional execution needed for this example
        pass

class labelDef:
    def __init__(self, file=None) -> None:      
        
        caller_frame = inspect.currentframe().f_back                
        self.WorkingDir = Path(inspect.getframeinfo(caller_frame).filename).parent                
        self.WorkingDir = os.path.join(self.WorkingDir , "pyLabels")                  

        match file == None:
            case True:
                self.hasFile = False
                n = 1
                self.file = "untitled-label-{}.py".format(str(n))
                while os.path.exists(os.path.join(self.WorkingDir , self.file)):
                    n = n + 1
                    self.file = "untitled-label-{}.py".format(str(n))
                                                
                spec = importlib.util.spec_from_loader("label.template" , BlankLabel())
                self.template = importlib.util.module_from_spec(spec)
                sys.modules["label.template"] = self.template
                spec.loader.exec_module(self.template)          
                
                for i in [ i for i in dir(sys.modules["label.labeldefs"]) if not i.startswith("__") and i.lower() != "labels"]:
                    match getattr( getattr(sys.modules["label.labeldefs"] , i ) , "default" ):
                        case True:
                            self.template.specs = getattr(sys.modules["label.labeldefs"] , i )
                            break

            case _:
                self.hasFile = True
                self.file = os.path.basename(file)

                spec = importlib.util.spec_from_file_location("label.template",  os.path.join(self.WorkingDir , self.file ))
                self.template = importlib.util.module_from_spec(spec)
                sys.modules["label.template"] = self.template
                spec.loader.exec_module(self.template)                                    

        # Load the template
        self.c = Drawing(
            float(self.template.specs.label_width*mm)
            , float(self.template.specs.label_height*mm)
        )        
        self.template.draw_label(
            self.c
            , float(self.template.specs.label_width*mm)
            , float(self.template.specs.label_height*mm)
            , self.template.testdata
        )       
        self.hasChanges = False    

    def __del__(self):
        self.cleanUp()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanUp()

#region "Methods"

    def cleanUp(self):
        if "c" in dir(self):
            if "contents" in dir(self.c):
                for i in [ i for i in self.c.contents if self.ShapeType(i) == sType.barcode ]:
                    os.remove(i.path)
        
        fn = os.path.join(
            self.WorkingDir
            , "tmp"
            , "preview_{}.pdf".format( self.file.split(".")[0] )        
        )
        if os.path.exists(fn): os.remove(fn)

    def render(self) :       
        png_image_buffer = BytesIO()
        renderPM.drawToFile(self.c, png_image_buffer , fmt='PNG')
        return png_image_buffer.getvalue()

    def contents(self):
        return self.c.contents
    
    def ShapeType(Self,i)->sType:        
        if i == None:
            return sType.label        
        
        if i.__name__=="selection":
            return sType.select
        
        match str(type(i)) :
            case "<class 'reportlab.graphics.shapes.Image'>":
                if i.__name__ .lower() == "qr":
                    return sType.qr
                
                elif "__encoding__" in dir(i):
                    return sType.barcode
                            
                return sType.image
                
            case "<class 'reportlab.graphics.charts.textlabels.Label'>":
                return sType.text
            
            case _:
                pass
    
    def isShape(self , Name):
        for i in [i for i in self.contents() if i.__name__ == Name]: return i
        return None
    
#endregion
    
#region "Params"    

    def Params(self, obj):    
        parameters = []
        
        parameters.append({'name': 'General',
            'type': 'group',    
            'children': [ 
                {'name': 'Name', 'type': 'str', 'value': obj.__name__, 'readonly': self.ShapeType(obj)==sType.qr},
                {'name': 'x', 'type': 'float', 'value': obj.x, 'siPrefix': True, 'suffix': 'mm', 'readonly': False},
                {'name': 'y', 'type': 'float', 'value': obj.y , 'siPrefix': True, 'suffix': 'mm', 'readonly': False}
            ]
        })

        match self.ShapeType(obj) :
            case sType.qr | sType.image | sType.barcode:
                parameters.append({'name': 'Size',
                    'type': 'group',
                    'children': [                                 
                        {'name': 'width', 'type': 'int', 'value': obj.width , 'siPrefix': True, 'suffix': 'mm', 'readonly': False},
                        {'name': 'height', 'type': 'int', 'value': obj.height , 'siPrefix': True, 'suffix': 'mm', 'readonly': False},
                    ]
                })          
                if self.ShapeType(obj)==sType.image:
                    parameters.append({'name': 'Image',
                        'type': 'group',
                        'children': []
                    })        
                    fopen = parameterTypes.FileParameter(
                        title = "Image file"
                        , name = "filename"
                        , winTitle = "Select Image..."
                        , nameFilter = 'PNG files (*.png);;Jpeg files (*.jpeg);;All files (*)'
                        , directory = self.WorkingDir
                        , relativeTo = Path(self.WorkingDir)                        
                        , filename = obj.path
                    )            
                    fopen.setValue( obj.__filename__ ) 
                    parameters[len(parameters)-1]["children"].append(fopen)

                if self.ShapeType(obj) == sType.barcode:
                    b = barcode
                    barcodeEncodings = []
                    barcodeEncodings.append("QRCODE")
                    for i in b.PROVIDED_BARCODES:
                        barcodeEncodings.append(i.upper())
                    parameters.append({'name': 'Barcode',
                        'type': 'group',
                        'children': [                                                             
                            {'title': 'Encoding' , 'name': '__encoding__', 'type': 'list', 'limits': barcodeEncodings, 'value': obj.__encoding__ }
                            , {'title': 'Data', 'name': '__formatStr__', 'type': 'str', 'value': obj.__formatStr__ }                            
                        ]
                    })                   

            case sType.text:
                font = []
                for f in pdfmetrics.getRegisteredFontNames(): font.append(f)                
                
                forecol = QColor(int(obj.fillColor.red), int(obj.fillColor.green) , int(obj.fillColor.blue) , 0 if obj.fillColor.alpha==0 else 255)
                fillcol = QColor(0,0,0,0)
                if obj.boxFillColor != None: fillcol =  QColor(obj.boxFillColor.red, obj.boxFillColor.green , obj.boxFillColor.blue , 0 if obj.boxFillColor.alpha==0 else 255)
                
                parameters.append({'name': 'Font',
                    'type': 'group',
                    'children': [                               
                        {'name': 'fontSize', 'type': 'int', 'value': obj.fontSize , 'siPrefix': True, 'suffix': 'px', 'readonly': False},
                        {'title': 'Forecolour', 'name': 'fillColor', 'type': 'color', 'value': forecol ,'readonly': False},
                        {'title': 'Fillcolour', 'name': 'boxFillColor', 'type': 'color', 'value': fillcol ,'readonly': False},                                
                        {'name': 'fontName', 'type': 'list', 'limits': font, 'value': obj.fontName }
                    ]
                })
                parameters.append({'name': 'Rotation',
                    'type': 'group',
                    'children': [ 
                        {'name': 'angle', 'type': 'int', 'value': obj.angle , 'siPrefix': True, 'suffix': 'deg', 'readonly': False},                                
                        {'name': 'boxAnchor', 'type': 'list', 'limits': ['nw','sw','ne','se'], 'value': obj.boxAnchor , 'readonly': False},                                
                    ]
                })
                parameters.append({'name': 'Padding',
                    'type': 'group',
                    'children': [ 
                        {'name': 'leftPadding', 'type': 'int', 'value': obj.leftPadding , 'siPrefix': True, 'suffix': 'mm', 'readonly': False},                                
                        {'name': 'rightPadding', 'type': 'int', 'value': obj.rightPadding , 'siPrefix': True, 'suffix': 'mm', 'readonly': False},                                
                        {'name': 'topPadding', 'type': 'int', 'value': obj.topPadding , 'siPrefix': True, 'suffix': 'mm', 'readonly': False},                                
                        {'name': 'bottomPadding', 'type': 'int', 'value': obj.bottomPadding , 'siPrefix': True, 'suffix': 'mm', 'readonly': False},                                
                    ]
                })    
                parameters.append({'name': 'Data',
                    'type': 'group',
                    'children': [ 
                        {'title': 'Format', 'name': '__formatStr__', 'type': 'text', 'value': obj.__formatStr__ , 'readonly': False}
                    ]
                })                                
        return Parameter.create(name='params', type='group', children=parameters)

#endregion

class MyLabel(QLabel):    
    
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
            event.accept()

class mkBarcode():
    def __init__(self , Label , obj , uuid):

        caller_frame = inspect.currentframe().f_back                
        self.ParentDir = Path(inspect.getframeinfo(caller_frame).filename).parent                
        self.WorkingDir = os.path.join(self.ParentDir , "tmp")         
        if not os.path.exists( self.WorkingDir ):
            os.makedirs( self.WorkingDir )

        obj["clean"] = []    
        for i in [i for i in Label.contents]:
            if "__name__" in dir(i):
                if "__formatStr__" in dir(i):
                    s = i.__formatStr__            
                    for p in range(20):
                        if "<P" not in s: break
                        s = s.replace("<P{}>".format( str(p+1) ) , obj[ "PAR{}".format( str(p+1) ) ] )

                    if "__encoding__" in dir(i):
                        try:                   
                            match i.__encoding__:
                                case "QRCODE":
                                    s = s.replace( "<QR>", json.dumps( obj ["QR"] ) )
                                    qrcode = pyqrcode.create(s)
                                    i.path = os.path.join(self.WorkingDir , "{}{}.png".format(uuid, i.__filename__))
                                    qrcode.png(i.path , scale=8)
                                    obj["clean"].append(i.path)

                                case _:
                                    barclass = barcode.get_barcode_class(i.__encoding__)                                           
                                    bar = barclass(s, writer=ImageWriter())
                                    bar.save(os.path.join( self.WorkingDir ,  "{}{}".format( uuid, i.__filename__) ))
                                    i.path = os.path.join( self.WorkingDir , "{}{}.png".format( uuid , i.__filename__) )                
                                    obj["clean"].append(i.path)

                        except Exception as e:
                            i.path = ""        
                    
                    else:
                        i.setText(s)
                
                else:
                    i.path = os.path.join( self.ParentDir , "{}".format( i.__filename__) )            