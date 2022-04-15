# -*- coding: utf-8 -*-
#
# Advanced Kodi Launcher: Executors
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

import abc
import subprocess
import webbrowser
import logging
import re 
import logging

import xbmc

from akl.utils import io
from akl.utils import kodi

logger = logging.getLogger(__name__)

# #################################################################################################
# #################################################################################################
# Executors
# #################################################################################################
# #################################################################################################
class ExecutorABC():
    __metaclass__ = abc.ABCMeta

    def __init__(self, logFile: io.FileName):
        self.logFile = logFile

    @abc.abstractmethod
    def execute(self, application: str, non_blocking: bool, *args, **kwargs): 
        """
        Executes an application with this executor implementation.
        The non blocking flag indicates if Kodi should wait/freeze for
        this executing application. 
        The arguments (args and kwargs) will be processed as the 
        arguments for the execution.
        """
        pass

class XbmcExecutor(ExecutorABC):
    """
    Execute Kodi built-in functions.
    """
    
    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        if not kwargs or len(kwargs) == 0:
            xbmc.executebuiltin(application, wait = non_blocking)
        else:
            arguments = list(args)
            for key, value in kwargs.items():
                arguments.append(f'"{key} {value}"' if value else key)

            args_string = ", ".join(arguments)
            xbmc.executebuiltin(f'{application}({args_string})', wait = non_blocking)

#
# --- Linux ---
# New in AEL 0.9.7: always close all file descriptions except 0, 1 and 2 on the child
# process. This is to avoid Kodi opens sockets be inherited by the child process. A
# wrapper script may terminate Kodi using JSON RPC and if file descriptors are not
# closed Kodi will complain that the remote interfacte cannot be initialised. I believe
# the cause is that the socket is kept open by the wrapper script.
#
class LinuxExecutor(ExecutorABC):
    def __init__(self, logFile: io.FileName, lirc_state:bool):
        self.lirc_state = lirc_state
        super(LinuxExecutor, self).__init__(logFile)


    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug('LinuxExecutor::execute() Starting ...')
        command = [application] + list(args)

        # >> Old way of launching child process. os.system() is deprecated and should not
        # >> be used anymore.
        # os.system('"{0}" {1}'.format(application, arguments).encode('utf-8'))

         # >> New way of launching, uses subproces module. Also, save child process stdout.
        if non_blocking:
            # >> In a non-blocking launch stdout/stderr of child process cannot be recorded.
            logger.info('Launching non-blocking process subprocess.Popen()')
            p = subprocess.Popen(command, close_fds = True)
        else:
            if self.lirc_state: xbmc.executebuiltin('LIRC.stop')
            with open(self.logFile.getPathTranslated(), 'w') as f:
                retcode = subprocess.call(
                    command, stdout = f, stderr = subprocess.STDOUT, close_fds = True)
            logger.info(f'Process retcode = {retcode}')
            if self.lirc_state: xbmc.executebuiltin('LIRC.start')
        logger.debug('LinuxExecutor::execute() function ENDS')

class AndroidExecutor(ExecutorABC):
    """
    Launch an Android native app.
    If args are provided it will do a general shell execution.
    If kwargs are provided it will use StartAndroidActivity(package,[intent,dataType,dataURI])
    with the given application name as the package. The kwargs are: intent, dataType, dataURI. 
    example: 
      StartAndroidActivity(com.android.chrome,android.intent.action.VIEW,,http://kodi.tv/)
      application: com.android.chrome
      intent: android.intent.action.VIEW
      dataURI: http://kodi.tv/
    """
    def __init__(self, logFile: io.FileName):
        super(AndroidExecutor, self).__init__(logFile)

    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug("AndroidExecutor::execute() Starting ...")

        if len(args) > 0:
            command = [application] + list(args)
            #retcode = os.system("{0} {1}".format(application, args).encode('utf-8'))
            with open(self.logFile.getPathTranslated(), 'w') as f:
                retcode = subprocess.call(command, stdout = f, stderr = subprocess.STDOUT)
                logger.info(f"Process retcode = {retcode}")
        else:
            intent   = kwargs.get("intent", "")
            dataType = kwargs.get("dataType", "")
            dataURI  = kwargs.get("dataURI", "")

            command = f'StartAndroidActivity("{application}", "{intent}", "{dataType}", "{dataURI}")'
            xbmc.executebuiltin(command, non_blocking)

        logger.debug("AndroidExecutor::execute() function ENDS")

class OSXExecutor(ExecutorABC):

    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug('OSXExecutor::execute() Starting ...')
        command = [application] + list(args)

        # >> Old way.
        # os.system('"{0}" {1}'.format(application, arguments).encode('utf-8'))

        # >> New way.
        with open(self.logFile.getPathTranslated(), 'w') as f:
            retcode = subprocess.call(command, stdout = f, stderr = subprocess.STDOUT)
        logger.info('Process retcode = {0}'.format(retcode))
        logger.debug('OSXExecutor::execute() function ENDS')

class WindowsLnkFileExecutor(ExecutorABC):

    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug('WindowsLnkFileExecutor::execute() Starting ...')
        logger.debug('Launching LNK application')
        # os.system('start "AKL" /b "{0}"'.format(application).encode('utf-8'))
        retcode = subprocess.call('start "AKL" /b "{0}"'.format(application).encode('utf-8'), shell = True)
        logger.info('LNK app retcode = {0}'.format(retcode))
        logger.debug('WindowsLnkFileExecutor::execute() function ENDS')

#
# CMD/BAT files in Windows
#
class WindowsBatchFileExecutor(ExecutorABC):
    def __init__(self, logFile: io.FileName, show_batch_window: bool):
        self.show_batch_window = show_batch_window
        super(WindowsBatchFileExecutor, self).__init__(logFile)

    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug('WindowsBatchFileExecutor::execute() Starting ...')
        command = [application] + list(args)
        
        apppath = io.FileName(application)
        apppath = apppath.getDir()
        
        # --- Workaround to run UNC paths in Windows ---
        # >> Retroarch now support ROMs in UNC paths (Samba remotes)
        new_command = list(command)
        for i, _ in enumerate(command):
            if command[i][0] == '\\':
                new_command[i] = '\\' + command[i]
                logger.debug('Executor (Windows BatchFile): Before arg #{0} = "{1}"'.format(i, command[i]))
                logger.debug('Executor (Windows BatchFile): Now    arg #{0} = "{1}"'.format(i, new_command[i]))
        command = list(new_command)
        logger.debug('Executor (Windows BatchFile): command = {0}'.format(command))
        
        logger.debug('Executor (Windows BatchFile) Launching BAT application')
        logger.debug('Executor (Windows BatchFile) Ignoring setting windows_cd_apppath')
        logger.debug('Executor (Windows BatchFile) Ignoring setting windows_close_fds')
        logger.debug('Executor (Windows BatchFile) show_batch_window = {0}'.format(self.show_batch_window))
        info = subprocess.STARTUPINFO()
        info.dwFlags = 1
        info.wShowWindow = 5 if self.show_batch_window else 0
        retcode = subprocess.call(command, cwd = apppath.encode('utf-8'), close_fds = True, startupinfo = info)
        logger.info('Executor (Windows BatchFile) Process BAR retcode = {0}'.format(retcode))
        logger.debug('WindowsBatchFileExecutor::execute() function ENDS')

#
# --- Windoze ---
# NOTE subprocess24_hack.py was hacked to always set CreateProcess() bInheritHandles to 0.
# bInheritHandles [in] If this parameter TRUE, each inheritable handle in the calling 
# process is inherited by the new process. If the parameter is FALSE, the handles are not 
# inherited. Note that inherited handles have the same value and access rights as the original handles.
# See https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx
#
# Same behaviour can be achieved in current version of subprocess with close_fds.
# If close_fds is true, all file descriptors except 0, 1 and 2 will be closed before the 
# child process is executed. (Unix only). Or, on Windows, if close_fds is true then no handles 
# will be inherited by the child process. Note that on Windows, you cannot set close_fds to 
# true and also redirect the standard handles by setting stdin, stdout or stderr.
#
# If I keep old launcher behaviour in Windows (close_fds = True) then program output cannot
# be redirected to a file.
#
class WindowsExecutor(ExecutorABC):
    def __init__(self, logFile, cd_apppath:bool, close_fds:bool):
        self.windows_cd_apppath = cd_apppath
        self.windows_close_fds  = close_fds
        super(WindowsExecutor, self).__init__(logFile)

    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug('WindowsExecutor::execute() Starting ...')
        command = [application] + list(args)
        apppath = io.FileName(application)
        apppath = apppath.getDir()

        # --- Workaround to run UNC paths in Windows ---
        # >> Retroarch now support ROMs in UNC paths (Samba remotes)
        new_command = list(command)
        for i, _ in enumerate(command):
            if command[i][0] == '\\':
                new_command[i] = '\\' + command[i]
                logger.debug(f'WindowsExecutor: Before arg #{i} = "{command[i]}"')
                logger.debug(f'WindowsExecutor: Now    arg #{i} = "{new_command[i]}"')
        command = list(new_command)
        logger.debug(f'WindowsExecutor: command = {command}')

        # >> cwd = apppath.encode('utf-8') fails if application path has Unicode on Windows
        # >> A workaraound is to use cwd = apppath.encode(sys.getfilesystemencoding()) --> DOES NOT WORK
        # >> For the moment AKL cannot launch executables on Windows having Unicode paths.
        logger.debug('Launching regular application')
        logger.debug(f'windows_cd_apppath = {self.windows_cd_apppath}')
        logger.debug(f'windows_close_fds  = {self.windows_close_fds}')

        # >> Note that on Windows, you cannot set close_fds to true and also redirect the 
        # >> standard handles by setting stdin, stdout or stderr.
        if self.windows_cd_apppath and self.windows_close_fds:
            retcode = subprocess.call(command, cwd = apppath.encode('utf-8'), close_fds = True)
        elif self.windows_cd_apppath and not self.windows_close_fds:
            with open(self.logFile.getPathTranslated(), 'w') as f:
                retcode = subprocess.call(command, cwd = apppath.encode('utf-8'), close_fds = False,
                                            stdout = f, stderr = subprocess.STDOUT)
        elif not self.windows_cd_apppath and self.windows_close_fds:
            retcode = subprocess.call(command, close_fds = True)
        elif not self.windows_cd_apppath and not self.windows_close_fds:
            with open(self.logFile.getPathTranslated(), 'w') as f:
                retcode = subprocess.call(command, close_fds = False, stdout = f, stderr = subprocess.STDOUT)
        else:
            raise Exception('Logical error')
        logger.info(f'Process retcode = {retcode}')
        logger.debug('WindowsExecutor::execute() function ENDS')

class WebBrowserExecutor(ExecutorABC):

    def execute(self, application: str, non_blocking: bool, *args, **kwargs):
        logger.debug('WebBrowserExecutor::execute() Starting ...')
        command = " ".join([application] + list(args))
        
        logger.debug(f'Launching URL "{command}"')
        webbrowser.open(command)
        logger.debug('WebBrowserExecutor::execute() function ENDS')

class ExecutorSettings(object):
    show_batch_window = False
    lirc_state = False
    windows_cd_apppath = False
    windows_close_fds = False

class ExecutorFactoryABC(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def create(self, application_str: str) -> ExecutorABC: pass

# -------------------------------------------------------------------------------------------------
# Abstract Factory Pattern
# See https://www.oreilly.com/library/view/head-first-design/0596007124/ch04.html
# -------------------------------------------------------------------------------------------------
class ExecutorFactory(ExecutorFactoryABC):
    def __init__(self, reportFilePath:io.FileName = None, settings: ExecutorSettings = ExecutorSettings()):
        self.settings = settings
        self.logFile  = reportFilePath
        super(ExecutorFactory).__init__()

    def create(self, application_str: str) -> ExecutorABC:
        
        application = io.FileName(application_str)
        if application.getBase().lower().replace('.exe' , '') == 'xbmc' \
            or 'xbmc-fav-' in application.getPath() or 'xbmc-sea-' in application.getPath():
            return XbmcExecutor(self.logFile)

        elif re.search('.*://.*', application.getPath()):
            return WebBrowserExecutor(self.logFile)

        elif io.is_windows():
            # >> BAT/CMD file.
            if application.getExt().lower() == '.bat' or application.getExt().lower() == '.cmd' :
                return WindowsBatchFileExecutor(self.logFile, self.settings.show_batch_window)
            # >> Standalone launcher where application is a LNK file
            elif application.getExt().lower() == '.lnk': 
                return WindowsLnkFileExecutor(self.logFile)

            # >> Standard Windows executor
            return WindowsExecutor(self.logFile,
                self.settings.windows_cd_apppath, self.settings.windows_close_fds)

        elif io.is_android():
            return AndroidExecutor(self.logFile)

        elif io.is_linux():
            return LinuxExecutor(self.logFile, self.settings.lirc_state)

        elif io.is_osx():
            return OSXExecutor(self.logFile)

        else:
            logger.error('ExecutorFactory::create() Cannot determine the running platform')
            kodi.notify_warn('Cannot determine the running platform')

        return None