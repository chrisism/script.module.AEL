from setuptools import setup, find_packages
import io
import os
import sys

import xml.etree.ElementTree as ET

VERSION = ''
NAME = ''
AUTHOR = ''
AUTHOR_EMAIL = ''
DESCRIPTION = ''
PROJECT_URL = ''
LICENSE = ''
LONG_DESCRIPTION = ''

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'addon.xml'), encoding='utf-8') as f:
    str_data = f.read()
    tree = ET.fromstring(str_data)
    
    NAME = tree.get('name')
    VERSION = tree.get('version')
    AUTHOR = tree.get('provider-name')
    AUTHOR_EMAIL = tree.find('email').text
    DESCRIPTION = tree.find('summary').text
    LONG_DESCRIPTION = tree.find('description').text
    PROJECT_URL = tree.find('website').text
    LICENSE = tree.find('license').text

setup(
    name=NAME,
    version=VERSION
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION
    url=PROJECT_URL
    license=LICENSE,
    packages=find_packages(exclude=[".build", "tests"]),
    classifiers=[]
)