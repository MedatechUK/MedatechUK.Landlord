import configparser , inspect , os
from pathlib import Path
from pyqtgraph.parametertree import ParameterTree , Parameter

class iniTree(ParameterTree):
    def __init__(self , parent=None):        
        super().__init__(parent)     
        caller_frame = inspect.currentframe().f_back                
        self.WorkingDir = Path(inspect.getframeinfo(caller_frame).filename).parent                        
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.WorkingDir , "pyLabels" , "settings.ini"))    
        p = self.getParams()        
        self.setParameters(p,showTop=False)
        for child in p.children():
            for child in child.childs:
                child.sigValueChanged.connect(self.handleChange)

    def getParams(self):
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
        sect = _param.opts["name"].split(".")[0]
        key = _param.opts["name"].split(".")[1]
        self.config.set(sect, key, _value)
        with open(self.filename, 'w') as f:
            self.config.write(f)
