# -*- coding: utf-8 -*-
#
# Advanced Kodi Launcher platform and emulator information
#

# Copyright (c) Wintermute0110 <wintermute0110@gmail.com> / Chrisism <crizizz@gmail.com>
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
from __future__ import annotations

import abc
import logging
from datetime import datetime

# --- AKL modules ---
from akl.utils import io

logger = logging.getLogger(__name__)

class Reporter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, decoratorReporter: Reporter = None):
        self.decoratorReporter = decoratorReporter

    @abc.abstractmethod
    def open(self):
        pass
    
    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def _write_message(self, message:str):
        pass

    def write(self, message:str):        
        self._write_message(message)
        if self.decoratorReporter:
            self.decoratorReporter.write(message)

class LogReporter(Reporter):
    def open(self, report_title):
        return super(LogReporter, self).open()

    def close(self):
        return super(LogReporter, self).close()

    def _write_message(self, message:str):
        logger.info(message)

class FileReporter(Reporter):
    def __init__(self, reports_dir:io.FileName, scanner_name:str, decoratorReporter = None):
        now = datetime.now()
        scanner_file_name = scanner_name.replace(' ', '_')
        self.report_file = reports_dir.pjoin('{}_{}_report.txt'.format(scanner_file_name, now.strftime("%Y%m%d%H%M%S")))
        self.scanner_name = scanner_name
        
        super(FileReporter, self).__init__(decoratorReporter)

    def open(self):
        logger.info('Report file path "{0}"'.format(self.report_file.getPath()))
        report_folder = self.report_file.getDirAsFileName()
        
        report_folder.makedirs()
        self.report_file.open('w')
        
        self.write('******************** Report: {} ...  ********************'.format(self.scanner_name))
        #self.write('  Launcher name "{0}"'.format(self.launcher_data['m_name']))
        #self.write('  Launcher type "{0}"'.format(self.launcher_data['type'] if 'type' in self.launcher_data else 'Unknown'))
        #self.write('  launcher ID   "{0}"'.format(self.launcher_data['id']))
        #self.write('  ROM path      "{0}"'.format(launcher_path.getPath()))
        #self.write('  ROM ext       "{0}"'.format(self.launcher_data['romext']))
        #self.write('  Platform      "{0}"'.format(self.launcher_data['platform']))
        #self.write(  'Multidisc     "{0}"'.format(self.launcher_data['multidisc']))

    def close(self):
        self.report_file.close()

    def _write_message(self, message:str):
        self.report_file.write(message)
        self.report_file.write('\n')