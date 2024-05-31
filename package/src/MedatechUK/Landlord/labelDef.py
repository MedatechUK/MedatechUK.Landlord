import os , sys , importlib.util , inspect
from enum import Enum
from decimal import Decimal
from pathlib import Path
from io import BytesIO

from pyqtgraph.parametertree import Parameter, parameterTypes
from PyQt6.QtGui import *

from reportlab.graphics.shapes import Drawing 
from reportlab.graphics import renderPM
from reportlab.lib.units import mm
from reportlab.lib.colors import *
from reportlab.pdfbase import pdfmetrics

import barcode

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
                
                fillcol = QColor(0,0,0,0)
                if obj.boxFillColor != None: fillcol = obj.boxFillColor.int_rgb()
                R,G,B,A = obj.fillColor.int_rgb()

                parameters.append({'name': 'Font',
                    'type': 'group',
                    'children': [                                 
                        {'name': 'fontSize', 'type': 'int', 'value': obj.fontSize , 'siPrefix': True, 'suffix': 'px', 'readonly': False},
                        {'title':'Forecolour','name': 'fillColor', 'type': 'color', 'value': QColor(R,G,B) ,'readonly': False},
                        {'name': 'boxFillColor', 'type': 'color', 'value': fillcol ,'readonly': False},                                
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