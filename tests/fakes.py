import os
import random 

from lib.ael.utils import io
from lib.ael.executors import ExecutorABC

def random_string(length:int):
    return ''.join(random.choice([chr(i) for i in range(ord('a'),ord('z'))]) for _ in range(length))

class FakeFile(io.FileName):

    def __init__(self, pathString):
        self.fakeContent  = ''
        self.path_str     = pathString
        self.path_tr      = pathString       

        self.exists = self.exists_fake
        self.write = self.write_fake

    def setFakeContent(self, content):
        self.fakeContent = content
        
    def getFakeContent(self):
        return self.fakeContent   

    def loadFileToStr(self, encoding = 'utf-8'):
        return self.fakeContent     

    def readAllUnicode(self, encoding='utf-8'):
        contents = self.fakeContent
        return contents

    def saveStrToFile(self, data_str, encoding = 'utf-8'):
        self.fakeContent = data_str       

    def write_fake(self, bytes):
        self.fakeContent = self.fakeContent + bytes

    def open(self, mode):
        pass
    
    def close(self):
        pass

    def writeAll(self, bytes, flags='w'):
        self.fakeContent = self.fakeContent + bytes

    def pjoin(self, *args):
        child = FakeFile(self.path_str)
        child.setFakeContent(self.fakeContent)
        for arg in args:
            child.path_str = os.path.join(child.path_str, arg)
            child.path_tr = os.path.join(child.path_tr, arg)
            
        return child      

    def changeExtension(self, targetExt):
        switched_fake = super(FakeFile, self).changeExtension(targetExt)
        switched_fake = FakeFile(switched_fake.getPath())
        
        switched_fake.setFakeContent(self.fakeContent)
        return switched_fake

    def exists_fake(self):
        return True

    def scanFilesInPathAsFileNameObjects(self, mask = '*.*'):
        return []
    
class FakeExecutor(ExecutorABC):
    
    def __init__(self):
        self.actualApplication = None
        self.actualArgs = None
        super(FakeExecutor, self).__init__(None)
    
    def getActualApplication(self):
        return self.actualApplication

    def getActualArguments(self):
        return self.actualArgs

    def execute(self, application, arguments, non_blocking):
        self.actualApplication = application
        self.actualArgs = arguments
        pass        
    
class FakeClass():

    def FakeMethod(self, value, key, launcher):
        self.value = value
