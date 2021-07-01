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

# -------------------------------------------------------------------------------------------------
# Data model used in the plugin
# Internally all string in the data model are Unicode. They will be encoded to
# UTF-8 when writing files.
# -------------------------------------------------------------------------------------------------
# These three functions create a new data structure for the given object and (very importantly) 
# fill the correct default values). These must match what is written/read from/to the XML files.
# Tag name in the XML is the same as in the data dictionary.
#
def get_default_category_data_model():
    return {
        'id' : '',
        'type': constants.OBJ_CATEGORY,
        'm_name' : '',
        'm_year' : '',
        'm_genre' : '',
        'm_developer' : '',
        'm_rating' : '',
        'm_plot' : '',
        'finished' : False,
        'default_icon' : 's_icon',
        'default_fanart' : 's_fanart',
        'default_banner' : 's_banner',
        'default_poster' : 's_poster',
        'default_clearlogo' : 's_clearlogo',
        #'Asset_Prefix' : '',
        's_icon' : '',
        's_fanart' : '',
        's_banner' : '',
        's_poster' : '',
        's_clearlogo' : '',
        's_trailer' : ''
    }

def get_default_ROMSet_data_model():
    return {
        'id' : '',
        'type': constants.OBJ_ROMSET,
        'm_name' : '',
        'm_year' : '',
        'm_genre' : '',
        'm_developer' : '',
        'm_rating' : '',
        'm_plot' : '',
        'platform' : '',
        'categoryID' : '',
        #'application' : '',
        #'args' : '',
        #'args_extra' : [],
        #'rompath' : '',
        #'romext' : '',
        #'romextrapath' : '',
        'finished': False,
        #'toggle_window' : False, # Former 'minimize'
        #'non_blocking' : False,
        #'multidisc' : True,
        #'roms_base_noext' : '',
        'nointro_xml_file' : '', # deprecated? TODO: remove
        'nointro_display_mode' : constants.AUDIT_DMODE_ALL, # deprecated? TODO: remove
        'audit_state' : constants.AUDIT_STATE_OFF,
        'audit_auto_dat_file' : '',
        'audit_custom_dat_file' : '',
        'audit_display_mode' : constants.AUDIT_DMODE_ALL,
        'launcher_display_mode' : constants.LAUNCHER_DMODE_FLAT,        
        'num_roms' : 0,
        'num_parents' : 0,
        'num_clones' : 0,
        'num_have' : 0,
        'num_miss' : 0,
        'num_unknown' : 0,
        'num_extra' : 0,
        'timestamp_launcher' : 0.0,
        'timestamp_report' : 0.0,
        'default_icon' : 's_icon',
        'default_fanart' : 's_fanart',
        'default_banner' : 's_banner',
        'default_poster' : 's_poster',
        'default_clearlogo' : 's_clearlogo',
        'default_controller' : 's_controller',
        'Asset_Prefix' : '',
        's_icon' : '',
        's_fanart' : '',
        's_banner' : '',
        's_poster' : '',
        's_clearlogo' : '',
        's_controller' : '',
        's_trailer' : '',
        'roms_default_icon' : 's_boxfront',
        'roms_default_fanart' : 's_fanart',
        'roms_default_banner' : 's_banner',
        'roms_default_poster' : 's_flyer',
        'roms_default_clearlogo' : 's_clearlogo',
        'ROM_asset_path' : '',
        'path_3dbox' : '',
        'path_title' : '',
        'path_snap' : '',
        'path_boxfront' : '',
        'path_boxback' : '',
        'path_cartridge' : '',
        'path_fanart' : '',
        'path_banner' : '',
        'path_clearlogo' : '',
        'path_flyer' : '',
        'path_map' : '',
        'path_manual' : '',
        'path_trailer' : ''        
    }

def get_default_ROM_data_model():
    return {
        'id' : '',
        'type': constants.OBJ_ROM,
        'm_name' : '',
        'm_year' : '',
        'm_genre' : '',
        'm_developer' : '',
        'm_nplayers' : '',
        'm_esrb' : constants.ESRB_PENDING,
        'm_rating' : '',
        'm_plot' : '',
        'platform': '',
        'box_size': '',
        'filename' : '',
        'disks' : [],
        'finished' : False,
        'nointro_status' : constants.AUDIT_STATUS_NONE,
        'pclone_status' : constants.PCLONE_STATUS_NONE,
        'cloneof' : '',
        's_3dbox' : '',
        's_title' : '',
        's_snap' : '',
        's_boxfront' : '',
        's_boxback' : '',
        's_cartridge' : '',
        's_fanart' : '',
        's_banner' : '',
        's_clearlogo' : '',
        's_flyer' : '',
        's_map' : '',
        's_manual' : '',
        's_trailer' : ''
    }    