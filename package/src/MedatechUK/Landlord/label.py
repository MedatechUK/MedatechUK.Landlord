import os , sys , importlib.util , inspect , json
from enum import Enum
from decimal import Decimal
from pathlib import Path
from io import BytesIO

from reportlab.graphics.shapes import Drawing 
from reportlab.graphics import renderPM
from reportlab.lib.units import mm
from reportlab.lib.colors import *

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
    # The labelDef class is responsible for managing label definitions. 
    
    def __init__(self, file=None) -> None:      

        # It has a constructor that sets up the working directory and loads a label template.     
        caller_frame = inspect.currentframe().f_back                
        self.WorkingDir = Path(inspect.getframeinfo(caller_frame).filename).parent                
        self.WorkingDir = os.path.join(self.WorkingDir , "pyLabels")                  
        
        match file == None:
            case True: # If no file is provided, it creates a new file with a unique name and loads a blank label template. 
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

            case _: # If a file is provided, it loads the label template from the file. 
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

    # The cleanUp method is used to remove temporary files created during the label creation process. 
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

    # The render method is used to render the label as a PNG image. 
    def render(self) :       
        png_image_buffer = BytesIO()
        renderPM.drawToFile(self.c, png_image_buffer , fmt='PNG')
        return png_image_buffer.getvalue()

    # The contents method returns the contents of the label. 
    def contents(self):
        return self.c.contents
    
    # The ShapeType method determines the type of a shape in the label. 
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
    
    # The isShape method checks if a shape with a given name exists in the label.    
    def isShape(self , Name):
        for i in [i for i in self.contents() if i.__name__ == Name]: return i
        return None
    
#endregion
    
class mkBarcode():
    """    
    This class is used by both Landlord.py and mkLabel.py to generate barcodes and QR codes.
    
    Args:
        Label (object): The label object.
        obj (dict): The dictionary containing data from a labelDef() class for generating the barcodes and QR codes.
        uuid (str): The UUID for the barcode.

    Attributes:
        ParentDir (str): The parent directory path.
        WorkingDir (str): The working directory path.

    Methods:
        __init__: Initializes the mkBarcode class.

    """

    def __init__(self, Label, obj, uuid):
        """
        Initializes a Label object.

        Args:
            Label: The Label object.
            obj: A dictionary containing data for the label.
            uuid: A unique identifier for the label.

        Raises:
            Exception: If an error occurs during initialization.

        Returns:
            None
        """
        try:
            caller_frame = inspect.currentframe().f_back    # Get the caller's frame
            self.ParentDir = Path(inspect.getframeinfo(caller_frame).filename).parent   # Get the parent directory
            self.WorkingDir = os.path.join(self.ParentDir, "tmp") # Set the working directory
            if not os.path.exists(self.WorkingDir): # Create the working directory if it does not exist
                os.makedirs(self.WorkingDir)    # Create the working directory

            obj["clean"] = []
            for i in [i for i in Label.contents]:   # Iterate through the shapes in the label
                if "__name__" in dir(i):    # Check if the shape has a name
                    if "__formatStr__" in dir(i):   # Check if the shape has a format string
                        s = i.__formatStr__ # Get the format string
                        for p in range(20): # Iterate through the placeholders
                            if "<P" not in s:   # Check if there are any more placeholders
                                break   # Break the loop if there are no more placeholders
                            s = s.replace("<P{}>".format(str(p + 1)), obj["PAR{}".format(str(p + 1))]) # Replace the placeholders with the data

                        if "__encoding__" in dir(i):    # Check if the shape is a barcode
                            try:
                                match i.__encoding__:
                                    case "QRCODE":
                                        s = s.replace("<QR>", json.dumps(obj["QR"])) # Replace the placeholder with the QR code data
                                        qrcode = pyqrcode.create(s) # Create the QR code
                                        i.path = os.path.join(self.WorkingDir, "{}{}.png".format(uuid, i.__filename__)) # Set the path to the QR code image
                                        qrcode.png(i.path, scale=8) # Save the QR code image
                                        obj["clean"].append(i.path) # Add the QR code image to the list of files to be cleaned up

                                    case _:
                                        barclass = barcode.get_barcode_class(i.__encoding__)    # Get the barcode class
                                        bar = barclass(s, writer=ImageWriter()) # Create the barcode
                                        bar.save(os.path.join(self.WorkingDir, "{}{}".format(uuid, i.__filename__))) # Save the barcode image
                                        i.path = os.path.join(self.WorkingDir, "{}{}.png".format(uuid, i.__filename__)) # Set the path to the barcode image
                                        obj["clean"].append(i.path) # Add the barcode image to the list of files to be cleaned up

                            except Exception as e:
                                i.path = "" # Set the path to an empty string

                        else:
                            i.setText(s)

                    else:
                        i.path = os.path.join(self.ParentDir, "{}".format(i.__filename__))

        except Exception as e:
            print(e)