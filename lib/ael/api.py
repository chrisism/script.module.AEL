# -*- coding: utf-8 -*-
#
# Advanced Emulator Launcher: API
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#
# API client to connect to AEL server to retrieve ROM data.
#

# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division
from __future__ import annotations

import abc
import logging

# AEL modules
from ael.utils import net, io

logger = logging.getLogger(__name__)

###############################################################
# CLIENT METHODS
###############################################################
def client_get_rom(host: str, port:int, rom_id:str) -> ROMObj:
    uri = 'http://{}:{}/query/rom/?id={}'.format(host, port, rom_id)
    rom_data = net.get_URL_as_json(uri)    
    return ROMObj(rom_data)

def client_get_roms_in_collection(host: str, port:int, rom_collection_id:str) -> ROMObj:
    uri = 'http://{}:{}/query/romcollection/roms/?id={}'.format(host, port, rom_collection_id)
    rom_data = net.get_URL_as_json(uri)
    roms = []
    for rom_entry in rom_data:
        roms.append(ROMObj(rom_entry))
    return roms

def client_get_rom_launcher_settings(host: str, port:int, rom_id: str, launcher_id:str) -> dict:
    uri = 'http://{}:{}/query/rom/launcher/settings/?id={}&launcher_id={}'.format(host, port, rom_id, launcher_id)
    launcher_settings = net.get_URL_as_json(uri)    
    return launcher_settings

def client_get_collection_launcher_settings(host: str, port:int, rom_collection_id: str, launcher_id:str) -> dict:
    uri = 'http://{}:{}/query/romcollection/launcher/settings/?id={}&launcher_id={}'.format(host, port, rom_collection_id, launcher_id)
    launcher_settings = net.get_URL_as_json(uri)    
    return launcher_settings

def client_get_collection_scanner_settings(host: str, port:int, rom_collection_id: str, scanner_id:str) -> dict:
    uri = 'http://{}:{}/query/romcollection/scanner/settings/?id={}&scanner_id={}'.format(host, port, rom_collection_id, scanner_id)
    scanner_settings = net.get_URL_as_json(uri)    
    return scanner_settings

def client_post_launcher_settings(host: str, port:int, data: dict) -> bool:
    uri = 'http://{}:{}/store/launcher/'.format(host, port)
    response_data, code = net.post_JSON_URL(uri, data)
    return code == 200

def client_post_scanner_settings(host: str, port:int, data: dict) -> bool:
    uri = 'http://{}:{}/store/scanner/'.format(host, port)
    response_data, code = net.post_JSON_URL(uri, data)
    return code == 200

def client_post_scanned_roms(host: str, port:int, data: dict) -> bool:
    uri = 'http://{}:{}/store/roms/'.format(host, port)
    response_data, code = net.post_JSON_URL(uri, data)
    return code == 200

###############################################################
# CLIENT OBJECTS
###############################################################
class MetaDataObj(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, entity_data: dict):
        if entity_data is None:
            entity_data = {}
        self.entity_data = entity_data

    def get_id(self) -> str:
        return self.entity_data['id'] if 'id' in self.entity_data else None

    def get_data_dic(self):
        return self.entity_data

    def get_custom_attribute(self, key, default_value = None):
        return self.entity_data[key] if key in self.entity_data else default_value

    # --- Metadata --------------------------------------------------------------------------------
    def get_name(self):
        return self.entity_data['m_name'] if 'm_name' in self.entity_data else 'Unknown'

    def get_releaseyear(self):
        return self.entity_data['m_year'] if 'm_year' in self.entity_data else ''

    def get_genre(self) -> str:
        return self.entity_data['m_genre'] if 'm_genre' in self.entity_data else ''

    def get_developer(self) -> str:
        return self.entity_data['m_developer'] if 'm_developer' in self.entity_data else ''

    def get_rating(self):
        return int(self.entity_data['m_rating']) if self.entity_data['m_rating'] else ''

    def get_plot(self):
        return self.entity_data['m_plot'] if 'm_plot' in self.entity_data else ''
    
    def get_data_dic(self):
        return self.entity_data
    
class ROMObj(MetaDataObj):
       
    def set_file(self, file: io.FileName):
        self.entity_data['filename'] = file.getPath()     

    def get_file(self):
        if not 'filename' in self.entity_data: return None
        path = self.entity_data['filename']
        if path == '': return None

        return io.FileName(path)