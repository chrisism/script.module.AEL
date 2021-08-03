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
import typing

# AEL modules
from ael.utils import net

###############################################################
# CLIENT METHODS
###############################################################
def client_get_rom(host: str, port:int, rom_id:str) -> MetaDataObj:
    uri = 'http://{}:{}/query/rom/?id={}'.format(host, port, rom_id)
    rom_data = net.get_URL_as_json(uri)    
    return MetaDataObj(rom_data)

def client_get_rom_launcher_settings(host: str, port:int, rom_id: str, launcher_id:str) -> dict:
    uri = 'http://{}:{}/query/rom/launcher/settings/?id={}&launcher_id={}'.format(host, port, rom_id, launcher_id)
    launcher_settings = net.get_URL_as_json(uri)    
    return launcher_settings

def client_get_collection_launcher_settings(host: str, port:int, rom_collection_id: str, launcher_id:str) -> dict:
    uri = 'http://{}:{}/query/romcollection/launcher/settings/?id={}&launcher_id={}'.format(host, port, rom_collection_id, launcher_id)
    launcher_settings = net.get_URL_as_json(uri)    
    return launcher_settings

def client_post_launcher_settings(host: str, port:int, data: dict) -> bool:
    uri = 'http://{}:{}/store/launcher/'.format(host, port)
    response_data, code = net.post_JSON_URL(uri, data)
    return code == 200

###############################################################
# CLIENT OBJECTS
###############################################################
class MetaDataObj(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, entity_data: typing.Dict[str, typing.Any]):
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