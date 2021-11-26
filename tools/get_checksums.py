#!/usr/bin/python
# -*- coding: utf-8 -*-

# Test AKL platform conversion to scraper platform names.
# Included scrapers: TheGamesDB, MobyGames, ScreenScraper.
# GameFAQs scraper is not used for now (not API available).

# AKL long name       | AKL short name | AKL compact name |
# Sega Master System  | sega-sms       | sms

# --- Python standard library ---
# --- Python standard library ---
from __future__ import unicode_literals
import copy
import os
import pprint
import sys
import logging

# --- AKL modules ---
from lib.akl.utils import io

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG) 

# --- main ----------------------------------------------------------------------------------------
if len(sys.argv) < 2:
    print('First argument must be a file name.')
    sys.exit(1)
print('Calculating checksums of "{}"'.format(sys.argv[1]))
checksums = io.misc_calculate_checksums(sys.argv[1])
pprint.pprint(checksums)
