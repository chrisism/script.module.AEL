# -*- coding: utf-8 -*-
import xbmcaddon

from ael import constants

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