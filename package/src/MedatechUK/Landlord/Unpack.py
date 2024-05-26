import os , json , inspect
from pathlib import Path

import barcode
from barcode.writer import ImageWriter
from barcode import generate

import pyqrcode

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