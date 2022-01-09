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
    
    NAME = tree.get('id')
    VERSION = tree.get('version')
    AUTHOR = tree.get('provider-name')
    AUTHOR_EMAIL = tree.findall('.//email')[0].text
    DESCRIPTION = tree.findall('.//description')[0].text
    PROJECT_URL = tree.findall('.//website')[0].text
    LICENSE = tree.findall('.//license')[0].text

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url=PROJECT_URL,
    license=LICENSE,
    package_dir={"": "lib"},
    packages=find_packages(where="lib"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6"
)