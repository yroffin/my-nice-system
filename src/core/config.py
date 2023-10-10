import json, yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from core.settings import settings 

class Config:
    __loader: any
    
    def __init__(self) -> any:
        self.__loader = yaml.load(open(settings.CONFIG_YAML_LOCATION, 'r'), Loader=Loader)
    
    def getLoader(self):
        return self.__loader

config = Config().getLoader()