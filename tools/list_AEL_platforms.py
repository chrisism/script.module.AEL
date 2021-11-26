#!/usr/bin/python
# -*- coding: utf-8 -*-

# List AKL platforms using the new engine object-based.
# Included scrapers: TheGamesDB, MobyGames, ScreenScraper.
# GameFAQs scraper is not used for now (not API available).

# AKL long name       | AKL short name | AKL compact name |
# Sega Master System  | sega-sms       | sms

# --- Python standard library ---
from __future__ import unicode_literals
import copy
import os
import pprint
import sys

# --- AKL modules ---
from lib.akl import platforms
from lib.akl.utils import text

# --- configuration ------------------------------------------------------------------------------
fname_longname_txt  = 'data/AKL_platform_list_longname.txt'
fname_longname_csv  = 'data/AKL_platform_list_longname.csv'
fname_shortname_txt = 'data/AKL_platform_list_shortname.txt'
fname_shortname_csv = 'data/AKL_platform_list_shortname.csv'
fname_category_txt  = 'data/AKL_platform_list_category.txt'
fname_category_csv  = 'data/AKL_platform_list_category.csv'

# --- functions ----------------------------------------------------------------------------------
def write_txt_file(filename, text):
    with open(filename, 'w') as text_file:
        text_file.write(text)

# --- main ---------------------------------------------------------------------------------------
# --- Check that short names are unique ---
print('Checking that platform short names are unique...')
for index in range(len(platforms.AKL_platforms)):
    for subindex in range(len(platforms.AKL_platforms)):
        if index == subindex: continue
        if platforms.AKL_platforms[index].short_name == platforms.AKL_platforms[subindex].short_name:
            print('Short name {} is repeated!'.format(platforms.AKL_platforms[index].short_name))
            sys.exit(1)

# --- Check that compact names are unique ---
print('Checking that platform compact names are unique...')
for index in range(len(platforms.AKL_platforms)):
    for subindex in range(len(platforms.AKL_platforms)):
        if index == subindex: continue
        if platforms.AKL_platforms[index].compact_name == platforms.AKL_platforms[subindex].compact_name:
            print('Compact name {} is repeated!'.format(platforms.AKL_platforms[index].compact_name))
            sys.exit(1)

# --- Check that the platform object list is alphabetically sorted ---
# Unknown platform is special and it's always in last position. Remove from alphabetical check.
p_longname_list = [pobj.long_name for pobj in platforms.AKL_platforms[:-1]]
p_longname_list_sorted = sorted(p_longname_list, key = lambda s: s.lower())
table_str = [ ['left', 'left', 'left'], ['Marker', 'Original', 'Sorted'] ]
not_sorted_flag = False
for i in range(len(p_longname_list)):
    a = p_longname_list[i]
    b = p_longname_list_sorted[i]
    if a != b:
        table_str.append([' *** ', a, b])
        not_sorted_flag = True
    else:
        table_str.append(['', a, b])
if not_sorted_flag:
    print('\n'.join(text.render_table(table_str)))
    print('Platforms not sorted alphabetically. Exiting.')
    sys.exit(1)
print('Platforms sorted alphabetically.')

# --- List platforms sorted by long name ---
table_str = [
    ['left', 'left', 'left', 'left', 'left', 'left', 'left', 'left', 'left'],
    ['Long name', 'Short name', 'Compact name', 'Alias', 'TGDB', 'MG', 'SS', 'GF', 'DAT'],
]
for p_obj in platforms.AKL_platforms:
    table_str.append([
        p_obj.long_name, p_obj.short_name, p_obj.compact_name, str(p_obj.aliasof), 
        str(p_obj.TGDB_plat), str(p_obj.MG_plat), str(p_obj.SS_plat), str(p_obj.GF_plat),
        str(p_obj.DAT),
    ])
header_list = []
header_list.append('Number of AKL platforms {}'.format(len(platforms.AKL_platforms)))
header_list.append('')
table_str_list = text.render_table_str(table_str)
header_list.extend(table_str_list)
text_str = '\n'.join(header_list)
print(text_str)
# Output file in TXT and CSV format
print('\nWriting file "{}"'.format(fname_longname_txt))
write_txt_file(fname_longname_txt, text_str)
text_csv = '\n'.join(text.render_table_CSV_slist(table_str))
print('Writing file "{}"'.format(fname_longname_csv))
write_txt_file(fname_longname_csv, text_csv)

# --- List platforms sorted by short name ---
table_str = [
    ['left', 'left', 'left', 'left', 'left', 'left', 'left', 'left', 'left'],
    ['Long name', 'Short name', 'Compact name', 'Alias', 'TGDB', 'MG', 'SS', 'GF', 'DAT'],
]
for p_obj in sorted(platforms.AKL_platforms, key = lambda x: x.short_name.lower(), reverse = False):
    table_str.append([
        p_obj.long_name, p_obj.short_name, p_obj.compact_name, p_obj.aliasof,
        p_obj.TGDB_plat, p_obj.MG_plat, p_obj.SS_plat, p_obj.GF_plat,
        p_obj.DAT,
    ])
header_list = []
header_list.append('Number of AKL platforms {}'.format(len(platforms.AKL_platforms)))
header_list.append('')
table_str_list = text.render_table_str(table_str)
header_list.extend(table_str_list)
text_str = '\n'.join(header_list)
# Output file in TXT and CSV format
print('\nWriting file "{}"'.format(fname_shortname_txt))
write_txt_file(fname_shortname_txt, text_str)
text_csv = '\n'.join(text.render_table_CSV_slist(table_str))
print('Writing file "{}"'.format(fname_shortname_csv))
write_txt_file(fname_shortname_csv, text_csv)

# --- List platforms sorted by category and then long name ---
table_str = [
    ['left', 'left', 'left', 'left', 'left', 'left', 'left', 'left', 'left'],
    ['Long name', 'Short name', 'Compact name', 'Alias', 'TGDB', 'MG', 'SS', 'GF', 'DAT'],
]
for p_obj in sorted(platforms.AKL_platforms, key = lambda x: (x.category.lower(), x.long_name.lower()), reverse = False):
    table_str.append([
        p_obj.long_name, p_obj.short_name, p_obj.compact_name, p_obj.aliasof,
        p_obj.TGDB_plat, p_obj.MG_plat, p_obj.SS_plat, p_obj.GF_plat,
        p_obj.DAT,
    ])
header_list = []
header_list.append('Number of AKL platforms {}'.format(len(platforms.AKL_platforms)))
header_list.append('')
table_str_list = text.render_table_str(table_str)
header_list.extend(table_str_list)
text_str = '\n'.join(header_list)
# Output file in TXT and CSV format
print('\nWriting file "{}"'.format(fname_category_txt))
write_txt_file(fname_category_txt, text_str)
text_csv = '\n'.join(text.render_table_CSV_slist(table_str))
print('Writing file "{}"'.format(fname_category_csv))
write_txt_file(fname_category_csv, text_csv)
