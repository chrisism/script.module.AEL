# -*- coding: utf-8 -*-
#
# Advanced Emulator Launcher network IO module
#

# Copyright (c) 2016-2018 Wintermute0110 <wintermute0110@gmail.com>
# Portions (c) 2010-2015 Angelscry
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
from __future__ import division

import logging
import random
import json
import ssl
import xml.etree.ElementTree as ET

from urllib.request import urlopen, build_opener, Request, HTTPSHandler
from urllib.error import HTTPError
from http.client import HTTPSConnection

# AEL modules
from ael.utils import io

logger = logging.getLogger(__name__)


# --- GLOBALS -----------------------------------------------------------------
# Firefox user agents
# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0'

# Where did this user agent come from?
# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31';

# ---  -----------------------------------------------------------------
def get_random_UserAgent():
    platform = random.choice(['Macintosh', 'Windows', 'X11'])
    if platform == 'Macintosh':
        os_str  = random.choice(['68K', 'PPC'])
    elif platform == 'Windows':
        os_str  = random.choice([
            'Win3.11', 'WinNT3.51', 'WinNT4.0', 'Windows NT 5.0', 'Windows NT 5.1', 
            'Windows NT 5.2', 'Windows NT 6.0', 'Windows NT 6.1', 'Windows NT 6.2', 
            'Win95', 'Win98', 'Win 9x 4.90', 'WindowsCE'])
    elif platform == 'X11':
        os_str  = random.choice(['Linux i686', 'Linux x86_64'])
    browser = random.choice(['chrome', 'firefox', 'ie'])
    if browser == 'chrome':
        webkit = str(random.randint(500, 599))
        version = str(random.randint(0, 24)) + '.0' + str(random.randint(0, 1500)) + '.' + str(random.randint(0, 999))
        return 'Mozilla/5.0 (' + os_str + ') AppleWebKit/' + webkit + '.0 (KHTML, live Gecko) Chrome/' + version + ' Safari/' + webkit

    elif browser == 'firefox':
        year = str(random.randint(2000, 2012))
        month = random.randint(1, 12)
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = random.randint(1, 30)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        gecko = year + month + day
        version = random.choice([
            '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', 
            '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0'])
        return 'Mozilla/5.0 (' + os_str + '; rv:' + version + ') Gecko/' + gecko + ' Firefox/' + version

    elif browser == 'ie':
        version = str(random.randint(1, 10)) + '.0'
        engine = str(random.randint(1, 5)) + '.0'
        option = random.choice([True, False])
        if option == True:
            token = random.choice(['.NET CLR', 'SV1', 'Tablet PC', 'Win64; IA64', 'Win64; x64', 'WOW64']) + '; '
        elif option == False:
            token = ''
        return 'Mozilla/5.0 (compatible; MSIE ' + version + '; ' + os_str + '; ' + token + 'Trident/' + engine + ')'

def download_img(img_url, file_path:io.FileName):
    # --- Download image to a buffer in memory ---
    # If an exception happens here no file is created (avoid creating files with 0 bytes).
    try:
        req = Request(img_url)
        req.add_unredirected_header('User-Agent', USER_AGENT)
        response = urlopen(req, timeout = 120, context = ssl._create_unverified_context())
        img_buf = response.read()
        response.close()
    # If an exception happens record it in the log and do nothing.
    # This must be fixed. If an error happened when downloading stuff caller code must
    # known to take action.
    except IOError as ex:
        logger.error('(IOError) In download_img(), network code.')
        logger.error('(IOError) Object type "{}"'.format(type(ex)))
        logger.error('(IOError) Message "{0}"'.format(str(ex)))
        return
    except Exception as ex:
        logger.error('(Exception) In download_img(), network code.')
        logger.error('(Exception) Object type "{}"'.format(type(ex)))
        logger.error('(Exception) Message "{0}"'.format(str(ex)))
        return

    # --- Write image file to disk ---
    # There should be no more 0 size files with this code.
    try:
        f = file_path.open('wb')
        f.write(img_buf)
        f.close()
    except IOError as ex:
        logger.error('(IOError) In download_img(), disk code.')
        logger.error('(IOError) Object type "{}"'.format(type(ex)))
        logger.error('(IOError) Message "{0}"'.format(str(ex)))
    except Exception as ex:
        logger.error('(Exception) In download_img(), disk code.')
        logger.error('(download_img) Object type "{}"'.format(type(ex)))
        logger.error('(Exception) Message "{0}"'.format(str(ex)))

#
# User agent is fixed and defined in global var USER_AGENT
# https://docs.python.org/2/library/urllib2.html
#
# @param url: [Unicode string] URL to open
# @param url_log: [Unicode string] If not None this URL will be used in the logs.
# @param headers: [Dict(string,string)] Optional collection of custom headers to add.
# @return: [tuple] Tuple of strings. First tuple element is a string with the web content as 
#          a Unicode string or None if network error/exception. Second tuple element is the 
#          HTTP status code as integer or None if network error/exception.
def get_URL(url, url_log = None, headers = None):
    import traceback
    
    try:
        req = Request(url)
        if url_log is None: 
            logger.debug('get_URL() GET URL "{}"'.format(req.get_full_url()))
        else:
            logger.debug('get_URL() GET URL "{}"'.format(url_log))
            
        req.add_unredirected_header('User-Agent', USER_AGENT)
        if headers is not None:
            for key, value in headers.items():
                req.add_header(key, value)
        
        response = urlopen(req, timeout = 120, context = ssl._create_unverified_context())
        page_bytes = response.read()
        http_code = response.getcode()
        encoding = response.headers['content-type'].split('charset=')[-1]
        response.close()
    except HTTPError as ex:
        http_code = ex.code
        try:
            page_bytes = ex.read()
            ex.close()
        except:
            page_bytes = str(ex.reason)
        logger.error('(HTTPError) In net_get_URL()')
        logger.error('(HTTPError) Object type "{}"'.format(type(ex)))
        logger.error('(HTTPError) Message "{}"'.format(str(ex)))
        logger.error('(HTTPError) Code {}'.format(http_code))
        return page_bytes, http_code
    except Exception as ex:
        logger.error('(Exception) In net_get_URL()')
        logger.error('(Exception) Object type "{}"'.format(type(ex)))
        logger.error('(Exception) Message "{}"'.format(str(ex)))
        return page_bytes, http_code
    
       
    logger.debug('get_URL() Read {:,} bytes'.format(len(page_bytes)))
    logger.debug('get_URL() HTTP status code {}'.format(http_code))
    logger.debug('get_URL() encoding {}'.format(encoding))

    # --- Convert to Unicode ---
    page_data = decode_URL_data(page_bytes, encoding)

    return page_data, http_code

def get_URL_oneline(url, url_log = None):
    page_data, http_code = get_URL(url, url_log)
    if page_data is None: return (page_data, http_code)

    # --- Put all page text into one line ---
    page_data = page_data.replace('\r\n', '')
    page_data = page_data.replace('\n', '')

    return page_data, http_code

# Do HTTP request with POST: https://docs.python.org/2/library/urllib2.html#urllib2.Request
# If an exception happens return empty data.
def post_URL(url, data):
    page_data = ''
    http_code = 500
    try:
        req = Request(url, data)
        req.add_unredirected_header('User-Agent', USER_AGENT)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        req.add_header("Acept", "text/plain")
        logger.debug('post_URL() POST URL "{}"'.format(req.get_full_url()))
        response = urlopen(req, timeout = 120)
        page_bytes = response.read()
        encoding = response.headers['content-type'].split('charset=')[-1]
        http_code = response.getcode()
        response.close()
    except HTTPError as ex:
        http_code = ex.code
        try:
            page_bytes = ex.read()
            ex.close()
        except:
            page_bytes = str(ex.reason)
        logger.error('(HTTPError) In post_URL()')
        logger.error('(HTTPError) Object type "{}"'.format(type(ex)))
        logger.error('(HTTPError) Message "{}"'.format(str(ex)))
        logger.error('(HTTPError) Code {}'.format(http_code))
        return page_bytes, http_code
    except IOError as ex:
        logger.error('(IOError exception) In get_URL()')
        logger.error('Message: {0}'.format(str(ex)))
        return page_data, http_code
    except Exception as ex:
        logger.error('(General exception) In get_URL()')
        logger.error('Message: {0}'.format(str(ex)))
        return page_data, http_code

    num_bytes = len(page_bytes)
    logger.debug('post_URL() Read {0} bytes'.format(num_bytes))
    # --- Convert page data to Unicode ---
    page_data = decode_URL_data(page_bytes, encoding)

    return page_data, http_code

def post_JSON_URL(url, data_obj: any):
    page_data = ''
    http_code = 500
    try:
        data_str = json.dumps(data_obj)
        req = Request(url, data_str.encode('utf-8'))
        req.add_unredirected_header('User-Agent', USER_AGENT)
        req.add_header("Content-type", "application/json")
        req.add_header("Acept", "text/plain")
        logger.debug('post_JSON_URL() POST URL "{}"'.format(req.get_full_url()))
        response = urlopen(req, timeout = 120)
        page_bytes = response.read()
        encoding = response.headers['content-type'].split('charset=')[-1]
        http_code = response.getcode()
        response.close()
    except HTTPError as ex:
        http_code = ex.code
        try:
            page_bytes = ex.read()
            ex.close()
        except:
            page_bytes = str(ex.reason)
        logger.error('(HTTPError) In post_JSON_URL()')
        logger.error('(HTTPError) Object type "{}"'.format(type(ex)))
        logger.error('(HTTPError) Message "{}"'.format(str(ex)))
        logger.error('(HTTPError) Code {}'.format(http_code))
        return page_bytes, http_code
    except IOError as ex:
        logger.error('(IOError exception) In get_URL()')
        logger.error('Message: {0}'.format(str(ex)))
        return page_data, http_code
    except Exception as ex:
        logger.error('(General exception) In get_URL()')
        logger.error('Message: {0}'.format(str(ex)))
        return page_data, http_code

    num_bytes = len(page_bytes)
    logger.debug('post_JSON_URL() Read {0} bytes'.format(num_bytes))
    
    if num_bytes == 0: return '', http_code
    
    # --- Convert page data to Unicode ---
    page_data = decode_URL_data(page_bytes, encoding)
    return page_data, http_code

def get_URL_as_json(url, url_log = None):
    page_data, http_code = get_URL(url, url_log)
    return json.loads(page_data)

def get_URL_using_handler(url, handler = None):

    page_data = None
    opener = build_opener(handler)
    
    logger.debug('get_URL_using_handler() Reading URL "{0}"'.format(url))
    try:
        f = opener.open(url)
        encoding = f.headers['content-type'].split('charset=')[-1]
        page_bytes = f.read()
        f.close()
    except IOError as e:    
        logger.error('(IOError) Exception in get_URL_using_handler()')
        logger.error('(IOError) {0}'.format(str(e)))
        return page_data

    num_bytes = len(page_bytes)
    logger.debug('get_URL_using_handler() Read {0} bytes'.format(num_bytes))

    # --- Convert to Unicode ---    
    page_data = decode_URL_data(page_bytes, encoding)
    return page_data

def decode_URL_data(page_bytes, encoding):
    # --- Try to guess enconding ---
    if   encoding == 'text/html':                             encoding = 'utf-8'
    elif encoding == 'application/json':                      encoding = 'utf-8'
    elif encoding == 'text/plain' and 'UTF-8' in page_bytes:  encoding = 'utf-8'
    elif encoding == 'text/plain' and 'UTF-16' in page_bytes: encoding = 'utf-16'
    else:                                                     encoding = 'utf-8'
    
    logger.debug('decode_URL_data() encoding = "{0}"'.format(encoding))

    # --- Decode ---
    # if encoding == 'utf-16':
    #     page_data = page_bytes.encode('utf-16')
    # else:
    #     # python3: page_data = str(page_bytes, encoding)
    #     page_data = unicode(page_bytes, encoding)
    
    page_data = str(page_bytes, encoding)
    return page_data

class HTTPSClientAuthHandler(HTTPSHandler):
    def __init__(self, key, cert):
        ctx = ssl._create_unverified_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    
        HTTPSHandler.__init__(self, context = ctx)
        
        self.context = ctx
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return HTTPSConnection(host, key_file=self.key, cert_file=self.cert, context = self.context)