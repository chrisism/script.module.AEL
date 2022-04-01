# -*- coding: utf-8 -*-
import xbmcaddon

from akl.utils import io

# read settings
__addon__ = xbmcaddon.Addon()

def showSettings():
    __addon__.openSettings()

def getSetting(setting):
    return __addon__.getSetting(setting).strip()

def setSetting(setting, value):
    __addon__.setSetting(setting, str(value))

def getSettingAsBool(setting):
    return getSetting(setting).lower() == "true"

def getSettingAsFloat(setting):
    try:
        return float(getSetting(setting))
    except ValueError:
        return 0

def getSettingAsInt(setting):
    try:
        return int(getSettingAsFloat(setting))
    except ValueError:
        return 0

def getSettingAsFilePath(setting) -> io.FileName:
    str_value = __addon__.getSetting(setting).strip()
    if str_value is None or len(str_value) == 0: 
        return None
    return io.FileName(str_value)
