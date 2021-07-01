# -*- coding: utf-8 -*-
#
# Advanced Emulator Launcher: Base launchers
#
# Copyright (c) 2016-2018 Wintermute0110 <wintermute0110@gmail.com>
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
import logging

import xbmc

# --- AEL packages ---
from ael import settings
from ael.utils import io, kodi
from ael.executors import ExecutorSettings, ExecutorFactory, ExecutorFactoryABC

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------------------
# Helper methods
# -------------------------------------------------------------------------------------------------
def get_executor_factory(report_file_path:io.FileName) -> ExecutorFactoryABC:
    executorSettings                    = ExecutorSettings()
    executorSettings.lirc_state         = settings.getSettingAsBool('lirc_state')
    executorSettings.show_batch_window  = settings.getSettingAsBool('show_batch_window')
    executorSettings.windows_cd_apppath = settings.getSettingAsBool('windows_cd_apppath')
    executorSettings.windows_close_fds  = settings.getSettingAsBool('windows_close_fds')
    
    executorFactory = ExecutorFactory(report_file_path, executorSettings)
    return executorFactory

class ExecutionSettings(object):
    is_non_blocking = True
    toggle_window = False
    display_launcher_notify = True
    media_state_action = 0 # id="media_state_action" default="0" values="Stop|Pause|Let Play"
    suspend_audio_engine = False
    suspend_screensaver = True
    delay_tempo = 1000
    
    
# -------------------------------------------------------------------------------------------------
# Abstract base class for launching anything that is supported.
# Implement classes that inherit this base class to support new ways of launching.
# -------------------------------------------------------------------------------------------------
class LauncherABC(object):
    __metaclass__ = abc.ABCMeta

    #
    # In an abstract class launcher_data is mandatory.
    #
    def __init__(self, 
        executorFactory: ExecutorFactoryABC, 
        execution_settings: ExecutionSettings,
        launcher_settings):
        self.executorFactory    = executorFactory
        self.execution_settings = execution_settings
        
        self.launcher_settings  = launcher_settings

    # --------------------------------------------------------------------------------------------
    # Core methods
    # --------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def get_name(self) -> str: return ''
    
    @abc.abstractmethod
    def get_launcher_addon_id(self) -> str: return ''

    def get_launcher_settings(self) -> dict:
        return self.launcher_settings
    
    def get_application(self) -> str:
        return self.launcher_settings['application'] if 'application' in self.launcher_settings else None

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Builds a new Launcher.
    # Returns True if Launcher  was sucesfully built.
    # Returns False if Launcher was not built (user canceled the dialogs or some other
    # error happened).
    #
    def build(self) -> bool:
        logger.debug('LauncherABC::build() Starting ...')
                
        # --- Call hook before wizard ---
        if not self._build_pre_wizard_hook(): return False

        # --- Launcher build code (ask user about launcher stuff) ---
        wizard = kodi.WizardDialog_Dummy(None, 'addon_id', self.get_launcher_addon_id())
        # >> Call Child class wizard builder method
        wizard = self._builder_get_wizard(wizard)
        # >> Run wizard
        self.launcher_args = wizard.runWizard(self.launcher_settings)
        if not self.launcher_settings: return False

        # --- Call hook after wizard ---
        if not self._build_post_wizard_hook(): return False

        return True

    def edit(self) -> bool:
        logger.debug('LauncherABC::edit() Starting ...')
        
        # --- Call hook before wizard ---
        if not self._build_pre_wizard_hook(): return False

        # --- Launcher edit code (ask user about launcher stuff) ---
        wizard = self._editor_get_wizard(None)
        
        # >> Run wizard
        self.launcher_args = wizard.runWizard(self.launcher_settings)
        if not self.launcher_settings: return False

        # --- Call hook after wizard ---
        if not self._build_post_wizard_hook(): return False

        return True

    #
    # Creates a new launcher using a wizard of dialogs.
    # Child concrete classes must implement this method.
    #
    @abc.abstractmethod
    def _builder_get_wizard(self, wizard) -> kodi.WizardDialog: pass

    @abc.abstractmethod
    def _editor_get_wizard(self, wizard) -> kodi.WizardDialog: pass

    @abc.abstractmethod
    def _build_pre_wizard_hook(self): return True

    @abc.abstractmethod
    def _build_post_wizard_hook(self): return True

    def _builder_get_appbrowser_filter(self, item_key, launcher):
        if item_key in launcher:
            application = launcher[item_key]
            if application == 'JAVA':
                return '.jar'

        return '.bat|.exe|.cmd|.lnk' if io.is_windows() else ''

    #
    # Wizard helper, when a user wants to set a custom value instead of the predefined list items.
    #
    def _builder_user_selected_custom_browsing(self, item_key, launcher):
        return launcher[item_key] == 'BROWSE'
    
    #
    # This method will call the AEL event to store launcher settings for a 
    # specific romset in the database.
    #
    def store_launcher_settings(self, romset_id: str, launcher_id: str = None):
        
        launcher_settings = self.get_launcher_settings()
        params = {
            'romset_id': romset_id,
            'launcher_id': launcher_id,
            'addon_id': self.get_launcher_addon_id(),
            'settings': launcher_settings
        }        
        kodi.event(sender='plugin.program.AEL',command='SET_LAUNCHER_SETTINGS', data=params)
           
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    #
    # Launchs a custom launcher.
    # Arguments are those send through the URI.
    #
    @abc.abstractmethod
    def launch(self, arguments: str):
        logger.debug('LauncherABC::launch() Starting ...')

        # --- Create executor object ---
        if self.executorFactory is None:
            logger.error('LauncherABC::launch() self.executorFactory is None')
            logger.error('Cannot create an executor for {}'.format(self.get_name()))
            kodi.notify_error('LauncherABC::launch() self.executorFactory is None'
                              'This is a bug, please report it.')
            return
        
        executor = self.executorFactory.create(self.launcher_settings)
        
        if executor is None:
            logger.error('Cannot create an executor for {}'.format(self.get_name()))
            kodi.notify_error('Cannot execute application')
            return

        logger.debug('Name        = "{}"'.format(self.get_name()))
        logger.debug('Application = "{}"'.format(self.get_application()))
        logger.debug('Arguments   = "{}"'.format(arguments))
        logger.debug('Executor    = "{}"'.format(executor.__class__.__name__))

        # --- Execute app ---
        self._launch_pre_exec(self.get_name(), self.execution_settings.toggle_window)
        executor.execute(self.get_application(), arguments, self.execution_settings.is_non_blocking)
        self._launch_post_exec(self.execution_settings.toggle_window)

    #
    # These two functions do things like stopping music before lunch, toggling full screen, etc.
    # Variables set in this function:
    # self.kodi_was_playing      True if Kodi player was ON, False otherwise
    # self.kodi_audio_suspended  True if Kodi audio suspended before launching
    #
    def _launch_pre_exec(self, title, toggle_screen_flag):
        logger.debug('LauncherABC::_launch_pre_exec() Starting ...')

        # --- User notification ---
        if self.execution_settings.display_launcher_notify:
            kodi.notify('Launching {}'.format(title))

        # --- Stop/Pause Kodi mediaplayer if requested in settings ---
        self.kodi_was_playing = False
        # id="media_state_action" default="0" values="Stop|Pause|Let Play"
        media_state_action = self.execution_settings.media_state_action
        media_state_str = ['Stop', 'Pause', 'Let Play'][media_state_action]
        logger.debug('_launch_pre_exec() media_state_action is "{}" ({})'.format(media_state_str, media_state_action))
        if media_state_action == 0 and xbmc.Player().isPlaying():
            logger.debug('_launch_pre_exec() Calling xbmc.Player().stop()')
            xbmc.Player().stop()
            xbmc.sleep(100)
            self.kodi_was_playing = True
        elif media_state_action == 1 and xbmc.Player().isPlaying():
            logger.debug('_launch_pre_exec() Calling xbmc.Player().pause()')
            xbmc.Player().pause()
            xbmc.sleep(100)
            self.kodi_was_playing = True

        # --- Force audio suspend if requested in "Settings" --> "Advanced"
        # >> See http://forum.kodi.tv/showthread.php?tid=164522
        self.kodi_audio_suspended = False
        if self.execution_settings.suspend_audio_engine:
            logger.debug('_launch_pre_exec() Suspending Kodi audio engine')
            xbmc.audioSuspend()
            xbmc.enableNavSounds(False)
            xbmc.sleep(100)
            self.kodi_audio_suspended = True
        else:
            logger.debug('_launch_pre_exec() DO NOT suspend Kodi audio engine')

        # --- Force joystick suspend if requested in "Settings" --> "Advanced"
        # >> See https://forum.kodi.tv/showthread.php?tid=287826&pid=2627128#pid2627128
        # >> See https://forum.kodi.tv/showthread.php?tid=157499&pid=1722549&highlight=input.enablejoystick#pid1722549
        # >> See https://forum.kodi.tv/showthread.php?tid=313615
        self.kodi_joystick_suspended = False
        # if self.settings['suspend_joystick_engine']:
            # logger.debug('_launch_pre_exec() Suspending Kodi joystick engine')
            # >> Research. Get the value of the setting first
            # >> Apparently input.enablejoystick is not supported on Kodi Krypton anymore.
            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.GetSettingValue",'
            #          ' "params" : {"setting":"input.enablejoystick"}}')
            # response = xbmc.executeJSONRPC(c_str)
            # logger.debug('JSON      ''{0}'''.format(c_str))
            # logger.debug('Response  ''{0}'''.format(response))

            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.SetSettingValue",'
            #          ' "params" : {"setting" : "input.enablejoystick", "value" : false} }')
            # response = xbmc.executeJSONRPC(c_str)
            # logger.debug('JSON      ''{0}'''.format(c_str))
            # logger.debug('Response  ''{0}'''.format(response))
            # self.kodi_joystick_suspended = True

            # logger.error('_launch_pre_exec() Suspending Kodi joystick engine not supported on Kodi Krypton!')
        # else:
            # logger.debug('_launch_pre_exec() DO NOT suspend Kodi joystick engine')

        # --- Toggle Kodi windowed/fullscreen if requested ---
        if toggle_screen_flag:
            logger.debug('_launch_pre_exec() Toggling Kodi fullscreen')
            kodi.toggle_fullscreen()
        else:
            logger.debug('_launch_pre_exec() Toggling Kodi fullscreen DEACTIVATED in Launcher')

        # Disable screensaver
        if self.execution_settings.suspend_screensaver:
            kodi.disable_screensaver()
        else:
            screensaver_mode = kodi.get_screensaver_mode()
            logger.debug('_launch_pre_exec() Screensaver status "{}"'.format(screensaver_mode))

        # --- Pause Kodi execution some time ---
        delay_tempo_ms = self.execution_settings.delay_tempo
        logger.debug('_launch_pre_exec() Pausing {} ms'.format(delay_tempo_ms))
        xbmc.sleep(delay_tempo_ms)
        logger.debug('LauncherABC::_launch_pre_exec() function ENDS')

    def _launch_post_exec(self, toggle_screen_flag):
        logger.debug('LauncherABC::_launch_post_exec() Starting ...')

        # --- Stop Kodi some time ---
        delay_tempo_ms = self.execution_settings.delay_tempo
        logger.debug('_launch_post_exec() Pausing {} ms'.format(delay_tempo_ms))
        xbmc.sleep(delay_tempo_ms)

        # --- Toggle Kodi windowed/fullscreen if requested ---
        if toggle_screen_flag:
            logger.debug('_launch_post_exec() Toggling Kodi fullscreen')
            kodi.toggle_fullscreen()
        else:
            logger.debug('_launch_post_exec() Toggling Kodi fullscreen DEACTIVATED in Launcher')

        # --- Resume audio engine if it was suspended ---
        # Calling xmbc.audioResume() takes a loong time (2/4 secs) if audio was not properly suspended!
        # Also produces this in Kodi's log:
        # WARNING: CActiveAE::StateMachine - signal: 0 from port: OutputControlPort not handled for state: 7
        #   ERROR: ActiveAE::Resume - failed to init
        if self.kodi_audio_suspended:
            logger.debug('_launch_post_exec() Kodi audio engine was suspended before launching')
            logger.debug('_launch_post_exec() Resuming Kodi audio engine')
            xbmc.audioResume()
            xbmc.enableNavSounds(True)
            xbmc.sleep(100)
        else:
            logger.debug('_launch_post_exec() DO NOT resume Kodi audio engine')

        # --- Resume joystick engine if it was suspended ---
        if self.kodi_joystick_suspended:
            logger.debug('_launch_post_exec() Kodi joystick engine was suspended before launching')
            logger.debug('_launch_post_exec() Resuming Kodi joystick engine')
            # response = xbmc.executeJSONRPC(c_str)
            # logger.debug('JSON      ''{0}'''.format(c_str))
            # logger.debug('Response  ''{0}'''.format(response))
            logger.debug('_launch_post_exec() Not supported on Kodi Krypton!')
        else:
            logger.debug('_launch_post_exec() DO NOT resume Kodi joystick engine')

        # Restore screensaver status.
        if self.execution_settings.suspend_screensaver:
            kodi.restore_screensaver()
        else:
            screensaver_mode = kodi.get_screensaver_mode()
            logger.debug('_launch_post_exec() Screensaver status "{}"'.format(screensaver_mode))

        # --- Resume Kodi playing if it was paused. If it was stopped, keep it stopped. ---
        media_state_action = self.execution_settings.media_state_action
        media_state_str = ['Stop', 'Pause', 'Let Play'][media_state_action]
        logger.debug('_launch_post_exec() media_state_action is "{}" ({})'.format(media_state_str, media_state_action))
        logger.debug('_launch_post_exec() self.kodi_was_playing is {}'.format(self.kodi_was_playing))
        if self.kodi_was_playing and media_state_action == 1:
            logger.debug('_launch_post_exec() Calling xbmc.Player().play()')
            xbmc.Player().play()
        logger.debug('LauncherABC::_launch_post_exec() function ENDS')
