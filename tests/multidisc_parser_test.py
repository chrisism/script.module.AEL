#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Test the parser for multidisc support.
#

# Copyright (c) 2017 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- Python standard library ---
from __future__ import unicode_literals
import re
import unittest, os
from unittest.mock import patch, MagicMock

import logging

from lib.akl.utils import io
from lib.akl.scanners import MultiDiscInfo

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG) 

class Test_multidic_parser_tests(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):
        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
                
        print('ROOT DIR: {}'.format(cls.ROOT_DIR))
        print('TEST DIR: {}'.format(cls.TEST_DIR))
        print('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        print('---------------------------------------------------------------------------')

    # --- Main ----------------------------------------------------------------------------------------
    ROM_title_list = [
        'Final Fantasy I (USA) (Disc 1 of 2).iso',    # TOSEC
        'Final Fantasy I (USA) (Disc 2 of 2).iso',
        'Final Fantasy II (USA) - (Disc 1 of 2).iso', # Trurip
        'Final Fantasy II (USA) - (Disc 2 of 2).iso',
        'Final Fantasy VII (USA) (Disc 1).iso',       # Redump
        'Final Fantasy VII (USA) (Disc 2).iso',
        'Tomb Raider (EU).iso',
        '[BIOS] PSX bios (EU).iso'
    ]

    def text_get_ROM_basename_tokens(basename_str):
        DEBUG_TOKEN_PARSER = False

        # --- Parse ROM base_noext/basename_str into tokens ---
        reg_exp = r'\[.+?\]|\(.+?\)|\{.+?\}|[^\[\(\{]+'
        tokens_raw = re.findall(reg_exp, basename_str)
        if DEBUG_TOKEN_PARSER:
            logger.debug('text_get_ROM_basename_tokens() tokens_raw   {0}'.format(tokens_raw))

        # >> Strip tokens
        tokens_strip = list()
        for token in tokens_raw: tokens_strip.append(token.strip())
        if DEBUG_TOKEN_PARSER:
            logger.debug('text_get_ROM_basename_tokens() tokens_strip {0}'.format(tokens_strip))

        # >> Remove empty tokens ''
        tokens_clean = list()
        for token in tokens_strip: 
            if token: tokens_clean.append(token)
        if DEBUG_TOKEN_PARSER:        
            logger.debug('text_get_ROM_basename_tokens() tokens_clean {0}'.format(tokens_clean))

        # >> Remove '-' tokens from Trurip multidisc names
        tokens = list()
        for token in tokens_clean:
            if token == '-': continue
            tokens.append(token)
        if DEBUG_TOKEN_PARSER:
            logger.debug('text_get_ROM_basename_tokens() tokens       {0}'.format(tokens))

        return tokens
   
    def test_multidisc_with_rom_titles(self):
        # --- Test multidisc parser -----------------------------------------------------------------------
        for ROM_filename in Test_multidic_parser_tests.ROM_title_list:
            print('--------> "{0}"'.format(ROM_filename))
            MDSet = MultiDiscInfo.get_multidisc_info(io.FileName(ROM_filename))
            print('')
