# -*- coding: utf-8 -*-
#
# Advanced Emulator Launcher: Base ROM scanners
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
from __future__ import annotations

import abc
import logging
import re
import typing

# --- AEL packages ---
from ael import report, api, platforms
from ael.utils import io, kodi, text

from ael.api import ROMObj

logger = logging.getLogger(__name__)

class ROMCandidateABC(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_ROM(self) -> ROMObj: return None
    
    @abc.abstractmethod
    def get_sort_value(self) -> str: return None
    
class ROMFileCandidate(ROMCandidateABC):
    
    def __init__(self, file: io.FileName):
        self.file = file
        super(ROMFileCandidate, self).__init__()
        
    def get_ROM(self) -> ROMObj:
        rom = ROMObj()
        rom.set_file(self.file)
        return rom
        
    def get_sort_value(self):
        return self.file.getBase()
    
class MultiDiscInfo:
    def __init__(self, ROM_FN: io.FileName):
        self.ROM_FN      = ROM_FN
        self.isMultiDisc = False
        self.setName     = ''
        self.discName    = ROM_FN.getBase()
        self.extension   = ROM_FN.getExt()
        self.order       = 0

    @staticmethod
    def get_multidisc_info(ROM_FN: io.FileName) -> MultiDiscInfo:
        MDSet = MultiDiscInfo(ROM_FN)
        
        # --- Parse ROM base_noext into tokens ---
        tokens = text.get_ROM_basename_tokens(ROM_FN.getBaseNoExt())

        # --- Check if ROM belongs to a multidisc set and get set name and order ---
        # Algortihm:
        # 1) Iterate list of tokens
        # 2) If a token marks a multidisk ROM extract set order
        # 3) Define the set basename by removing the multidisk token
        MultDiscFound = False
        for index, token in enumerate(tokens):
            # --- Redump ---
            matchObj = re.match(r'\(Dis[ck] ([0-9]+)\)', token)
            if matchObj:
                logger.debug('get_multidisc_info() ### Matched Redump multidisc ROM ###')
                tokens_idx = list(range(0, len(tokens)))
                tokens_idx.remove(index)
                tokens_nodisc_idx = list(tokens_idx)
                tokens_mdisc = [tokens[x] for x in tokens_nodisc_idx]
                MultDiscFound = True
                break

            # --- TOSEC/Trurip ---
            matchObj = re.match(r'\(Dis[ck] ([0-9]+) of ([0-9]+)\)', token)
            if matchObj:
                logger.debug('get_multidisc_info() ### Matched TOSEC/Trurip multidisc ROM ###')
                tokens_idx = list(range(0, len(tokens)))
                tokens_idx.remove(index)
                tokens_nodisc_idx = list(tokens_idx)
                # logger.debug('text_get_multidisc_info() tokens_idx         = {0}'.format(tokens_idx))
                # logger.debug('text_get_multidisc_info() index              = {0}'.format(index))
                # logger.debug('text_get_multidisc_info() tokens_nodisc_idx  = {0}'.format(tokens_nodisc_idx))
                tokens_mdisc = [tokens[x] for x in tokens_nodisc_idx]
                MultDiscFound = True
                break

        if MultDiscFound:
            MDSet.isMultiDisc = True
            MDSet.setName = ' '.join(tokens_mdisc) + MDSet.extension
            MDSet.order = int(matchObj.group(1))
            logger.debug('get_multidisc_info() base_noext   "{0}"'.format(ROM_FN.getBaseNoExt()))
            logger.debug('get_multidisc_info() tokens       {0}'.format(tokens))
            logger.debug('get_multidisc_info() tokens_mdisc {0}'.format(tokens_mdisc))
            logger.debug('get_multidisc_info() setName      "{0}"'.format(MDSet.setName))
            logger.debug('get_multidisc_info() discName     "{0}"'.format(MDSet.discName))
            logger.debug('get_multidisc_info() extension    "{0}"'.format(MDSet.extension))
            logger.debug('get_multidisc_info() order        {0}'.format(MDSet.order))

        return MDSet

# #################################################################################################
# #################################################################################################
# ROM scanners
# #################################################################################################
# #################################################################################################
class ScannerStrategyABC(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, 
                 scanner_id: str,
                 romcollection_id: str,
                 webservice_host:str,
                 webservice_port:int,
                 progress_dialog: kodi.ProgressDialog):
        
        self.scanner_settings = {}
        self.progress_dialog = progress_dialog
        
        self.scanned_roms: typing.List[ROMObj] = []
        self.marked_dead_roms: typing.List[ROMObj] = []
        
        self.scanner_id       = scanner_id
        self.romcollection_id = romcollection_id
        
        self.webservice_host = webservice_host
        self.webservice_port = webservice_port
        
        self.load_settings()

        super(ScannerStrategyABC, self).__init__()
  
    # --------------------------------------------------------------------------------------------
    # Core methods
    # --------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def get_name(self) -> str: return ''
    
    @abc.abstractmethod
    def get_scanner_addon_id(self) -> str: return ''

    def get_scanner_settings(self) -> dict: return self.scanner_settings
    
    def amount_of_scanned_roms(self) -> int:
        return len(self.scanned_roms)
  
    def amount_of_dead_roms(self) -> int:
        return len(self.marked_dead_roms)

    #
    # Configure this scanner.
    #
    @abc.abstractmethod
    def configure(self) -> bool: return True

    #
    # Scans for new roms based on the type of launcher.
    #
    @abc.abstractmethod
    def scan(self):  pass

    #
    # Cleans up ROM collection.
    # Remove Remove dead/missing ROMs ROMs
    #
    @abc.abstractmethod
    def cleanup(self): pass
        
    #
    # This method will call the AEL webservice to retrieve previously stored scanner settings for a 
    # specific romcollection in the database.
    #
    def load_settings(self):
        if self.scanner_id is None: return        
        try:
            scanner_settings = api.client_get_collection_scanner_settings(
                    self.webservice_host, 
                    self.webservice_port, 
                    self.romcollection_id, 
                    self.scanner_id)
            
            self.scanner_settings = scanner_settings
        except Exception as ex:
            logger.error('Failure while loading scanner settings', exc_info=ex)
            self.scanner_settings = {}
        
    #
    # This method will call the AEL webservice to store scanner settings for a 
    # specific romcollection in the database.
    #
    def store_settings(self):        
        scanner_settings = self.get_scanner_settings()
        post_data = {
            'romcollection_id': self.romcollection_id,
            'ael_addon_id': self.scanner_id,
            'addon_id': self.get_scanner_addon_id(),
            'settings': scanner_settings
        }        
        is_stored = api.client_post_scanner_settings(self.webservice_host, self.webservice_port, post_data)
        if not is_stored:
            kodi.notify_error('Failed to store scanner settings')
     
    def store_scanned_roms(self): 
        roms = [*(r.get_data_dic() for r in self.scanned_roms)]
        post_data = {
            'romcollection_id': self.romcollection_id,
            'ael_addon_id': self.scanner_id,
            'roms': roms
        }      
        is_stored = api.client_post_scanned_roms(self.webservice_host, self.webservice_port, post_data)
        if not is_stored:
            kodi.notify_error('Failed to store scanned ROMs')

    def remove_dead_roms(self):
        dead_rom_ids = [*(r.get_id() for r in self.marked_dead_roms)]
        post_data = {
            'romcollection_id': self.romcollection_id,
            'ael_addon_id': self.scanner_id,
            'rom_ids': dead_rom_ids
        }      
        is_removed = api.client_post_dead_roms(self.webservice_host, self.webservice_port, post_data)
        if not is_removed:
            kodi.notify_error('Failed to remove dead ROMs')        

class NullScanner(ScannerStrategyABC):
    
    def get_name(self) -> str: return 'NULL'
    
    def get_scanner_addon_id(self) -> str: return ''
    
    def configure(self): return True
    
    def scan(self): pass

    def cleanup(self): pass

class RomScannerStrategy(ScannerStrategyABC):
    __metaclass__ = abc.ABCMeta

    def __init__(self, 
                 reports_dir: io.FileName, 
                 scanner_id: str,
                 romcollection_id: str,
                 webservice_host:str,
                 webservice_port:int,
                 progress_dialog: kodi.ProgressDialog):
        
        self.reports_dir = reports_dir
        super(RomScannerStrategy, self).__init__(scanner_id, romcollection_id, webservice_host, webservice_port, progress_dialog)

    # --------------------------------------------------------------------------------------------
    # Scanner configuration wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Builds up the settings for a Scanner
    # Returns True if Scanner was sucesfully built.
    # Returns False if Scanner was not built (user canceled the dialogs or some other
    # error happened).
    #
    def configure(self) -> bool:
        logger.debug('RomScannerStrategy::build() Starting ...')
                
        # --- Call hook before wizard ---
        if not self._configure_pre_wizard_hook(): return False

        # --- Scanner configuration code ---
        wizard = kodi.WizardDialog_Dummy(None, 'addon_id', self.get_scanner_addon_id())
        # >> Call Child class wizard builder method
        wizard = self._configure_get_wizard(wizard)
        # >> Run wizard
        self.launcher_args = wizard.runWizard(self.scanner_settings)
        if not self.scanner_settings: return False

        # --- Call hook after wizard ---
        if not self._configure_post_wizard_hook(): return False

        return True

    def scan(self):
               
        # --- Open ROM scanner report file ---
        launcher_report = report.FileReporter(self.reports_dir, self.get_name(), report.LogReporter())
        launcher_report.open()
        
        # >> Check if we already have existing ROMs
        launcher_report.write('Loading existing ROMs ...')
        try:
            roms = api.client_get_roms_in_collection(self.webservice_host, self.webservice_port, self.romcollection_id)
        except Exception as ex:
            logger.error('Failure retrieving existing ROMs', exc_info=ex)
            roms = []
        
        roms_by_scanner = [rom for rom in roms if rom.get_scanned_by() == self.scanner_id]

        num_roms = len(roms)
        num_roms_by_scanner = len(roms_by_scanner)

        launcher_report.write('{} ROMs currently in database'.format(num_roms))
        launcher_report.write('{} ROMs previously scanned by this scanner'.format(num_roms_by_scanner))
        
        launcher_report.write('Collecting candidates ...')
        candidates = self._getCandidates(launcher_report)
        num_candidates = len(candidates) if candidates else 0
        launcher_report.write('{} candidates found'.format(num_candidates))
        
        launcher_report.write('Checking for dead ROMs ...') 
        dead_roms = self._getDeadRoms(candidates, roms_by_scanner)
        num_dead_roms = len(dead_roms) 

        if num_dead_roms > 0:
            kodi.notify('{0} dead ROMs found'.format(num_dead_roms))
            logger.info('{0} dead ROMs found'.format(num_dead_roms))
        else:
            logger.info('No dead ROMs found')
        
        self.marked_dead_roms = dead_roms
        
        # --- Prepare list of candidates to be processed ----------------------------------------------
        # List has candidates. List already sorted alphabetically.
        candidates = sorted(candidates, key=lambda c: c.get_sort_value())
        new_roms = self._processFoundItems(candidates, roms_by_scanner, launcher_report)
        
        if not new_roms and not dead_roms:
            return

        num_new_roms = len(new_roms)
        roms = roms + new_roms
        self.scanned_roms = new_roms

        launcher_report.write('******************** ROM scanner finished. Report ********************')
        launcher_report.write('Files checked       {0:6d}'.format(num_candidates))
        launcher_report.write('Dead ROMs           {0:6d}'.format(num_dead_roms))
        launcher_report.write('New ROMs            {0:6d}'.format(num_new_roms))
        
        if len(roms) == 0:
            launcher_report.write('WARNING ROMs has no ROMs!')
            launcher_report.close()
            kodi.dialog_OK('No ROMs found! Make sure ROM set directory and file extensions are correct.')
            return
        
        if num_new_roms == 0:
            kodi.notify('Added no new ROMs. ROM set has {0} ROMs'.format(len(roms)))
        else:
            kodi.notify('Added {0} new ROMs'.format(num_new_roms))

        # --- Close ROM scanner report file ---
        launcher_report.write('*** END of the ROM scanner report ***')
        launcher_report.close()

    def cleanup(self):
        launcher_report = report.FileReporter(self.reports_dir, self.get_name(), report.LogReporter())
        launcher_report.open()
        launcher_report.write('Dead ROM Cleaning operation')
        
        try:
            roms = api.client_get_roms_in_collection(self.webservice_host, self.webservice_port, self.romcollection_id)
        except Exception as ex:
            logger.error('Failure retrieving existing ROMs', exc_info=ex)
            roms = []
        
        if roms is None:
            launcher_report.close()
            logger.info('No roms available to cleanup')
            return {}
        
        roms_by_scanner = [rom for rom in roms if rom.get_scanned_by() == self.scanner_id]
        if roms_by_scanner is None:
            launcher_report.close()
            logger.info('No roms for this scanner available to cleanup')
            return {}
        
        num_roms = len(roms)
        num_roms_by_scanner = len(roms_by_scanner)
        launcher_report.write('{0} ROMs currently in database'.format(num_roms))
        launcher_report.write('{0} ROMs currently in database associated with this scanner'.format(num_roms_by_scanner))
        
        launcher_report.write('Collecting candidates ...')
        candidates = self._getCandidates(launcher_report)
        num_candidates = len(candidates)
        logger.info('{0} candidates found'.format(num_candidates))

        launcher_report.write('Checking for dead ROMs ...')
        dead_roms = self._getDeadRoms(candidates, roms_by_scanner)
        num_dead_roms = len(dead_roms)

        if num_dead_roms > 0:
            kodi.notify('{0} dead ROMs found'.format(num_dead_roms))
            logger.info('{0} dead ROMs found'.format(num_dead_roms))
        else:
            logger.info('No dead ROMs found')

        self.marked_dead_roms = dead_roms
        launcher_report.close()
        return roms
    
    #
    # Creates a new scanner using a wizard of dialogs.
    # Child concrete classes must implement this method.
    #
    @abc.abstractmethod
    def _configure_get_wizard(self, wizard) -> kodi.WizardDialog: pass

    # ~~~ Pre & Post configuration hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @abc.abstractmethod
    def _configure_pre_wizard_hook(self): return True

    @abc.abstractmethod
    def _configure_post_wizard_hook(self): return True

    # ~~~ Scan for new files (*.*) and put them in a list ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @abc.abstractmethod
    def _getCandidates(self, launcher_report: report.Reporter) -> typing.List[ROMCandidateABC]:
        return []

    # --- Get dead entries -----------------------------------------------------------------
    @abc.abstractmethod
    def _getDeadRoms(self, candidates:typing.List[ROMCandidateABC], roms: typing.List[ROMObj]) -> typing.List[ROMObj]:
        return []

    # ~~~ Now go processing item by item ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @abc.abstractmethod
    def _processFoundItems(self, candidates:typing.List[ROMCandidateABC], roms:typing.List[ROMObj], launcher_report: report.Reporter) -> typing.List[ROMObj]:
        return []

    def configuration_get_extensions_from_launchers(self, input, item_key, scanner_settings):
        if input: return input
        extensions = scanner_settings[item_key] if item_key in scanner_settings else ''
        if extensions != '': return extensions
        
        if self.romcollection_id:
            extensions_by_launchers = []
            launchers = api.client_get_collection_launchers(self.webservice_host, self.webservice_port, self.romcollection_id)
            for key, launcher_settings in launchers.items():
                if 'application' in launcher_settings:    
                    app = launcher_settings['application'] 
                    appPath = io.FileName(app)
                    launcher_extensions = platforms.emudata_get_program_extensions(appPath.getBase())
                    if launcher_extensions != '':
                        extensions_by_launchers.append(launcher_extensions)
                        
                if 'scanners' in launcher_settings:
                    if 'romext' in launcher_settings['scanners']:
                        extensions_by_launchers = launcher_settings['scanners']['romext'].split('|')
                
            if len(extensions_by_launchers) > 0:
                extensions = '|'.join(extensions_by_launchers)
            else:
                extensions = ''
            
        return extensions
class SteamScanner(RomScannerStrategy):
    
    # ~~~ Scan for new items not yet in the rom collection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getCandidates(self, launcher_report, rom_path = None):
               
        logger.debug('Reading Steam account')
        self.progress_dialog.startProgress('Reading Steam account...')

        apikey = self.settings['steam-api-key']
        steamid = self.launcher.get_steam_id()
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=1'.format(apikey, steamid)
        
        self.progress_dialog.updateProgress(70)
        body = net_get_URL_original(url)
        self.progress_dialog.updateProgress(80)
        
        steamJson = json.loads(body)
        games = steamJson['response']['games']
        
        self.progress_dialog.endProgress()
        return games

    # --- Remove dead entries -----------------------------------------------------------------
    def _removeDeadRoms(self, candidates, roms):
    
        if roms is None or len(roms) == 0:
            logger.info('Launcher is empty. No dead ROM check.')
            return 0

        logger.debug('Starting dead items scan')
        num_roms = len(roms)
        num_removed_roms = 0
        i = 0
            
        self.progress_dialog.startProgress('Checking for dead ROMs ...', num_roms)
        
        steamGameIds = set(steamGame['appid'] for steamGame in candidates)

        for rom in reversed(roms):
            romSteamId = rom.get_custom_attribute('steamid')
            
            logger.debug('Searching {0}'.format(romSteamId))
            self.progress_dialog.updateProgress(i)
            i += 1

            if romSteamId not in steamGameIds:
                logger.debug('Not found. Deleting from DB: "{0}"'.format(rom.get_name()))
                roms.remove(rom)
                num_removed_roms += 1
            
        self.progress_dialog.endProgress()

        return num_removed_roms

    def _processFoundItems(self, items, roms, launcher_report):
        
        if items is None or len(items) == 0:
            logger.info('No steam games available.')
            return []

        new_roms = []

        num_games = len(items)
        num_items_checked = 0
            
        self.progress_dialog.startProgress('Checking for new ROMs ...', num_games)
        steamIdsAlreadyInCollection = set(rom.get_custom_attribute('steamid') for rom in roms)
        
        for steamGame, extra_ROM_flag in items:
            
            steamId = steamGame['appid']
            logger.debug('Searching {} with #{}'.format(steamGame['name'], steamId))
            self.progress_dialog.updateProgress(num_items_checked, steamGame['name'])
            
            if steamId not in steamIdsAlreadyInCollection:
                
                logger.debug('========== Processing Steam game ==========')
                launcher_report.write('>>> title: {}'.format(steamGame['name']))
                launcher_report.write('>>> ID: {}'.format(steamGame['appid']))
        
                logger.debug('Not found. Item {} is new'.format(steamGame['name']))

                launcher_path = self.launcher.get_rom_path()
                fake_file_name = text.str_to_filename_str(steamGame['name'])
                romPath = launcher_path.pjoin('{0}.rom'.format(fake_file_name))

                # ~~~~~ Process new ROM and add to the list ~~~~~
                # --- Create new rom dictionary ---
                # >> Database always stores the original (non transformed/manipulated) path
                new_rom  = ROM()
                new_rom.set_file(romPath)

                if extra_ROM_flag: new_rom.set_as_extra_ROM()
            
                new_rom.set_custom_attribute('steamid', steamGame['appid'])
                new_rom.set_custom_attribute('steam_name', steamGame['name'])  # so that we always have the original name
                new_rom.set_name(steamGame['name'])
        
                scraping_succeeded = True
                self.progress_dialog.updateMessage(steamGame['name'], 'Scraping {}...'.format(steamGame['name']))
                try:
                    self.scraping_strategy.scanner_process_ROM(new_rom, None)
                except Exception as ex:
                    scraping_succeeded = False        
                    logger.error('(Exception) Object type "{}"'.format(type(ex)))
                    logger.error('(Exception) Message "{}"'.format(str(ex)))
                    logger.warning('Could not scrape "{}"'.format(steamGame['name']))
                    #logger.debug(traceback.format_exc())
                
                if not scraping_succeeded and skip_if_scraping_failed:
                    kodi.display_user_message({
                        'dialog': KODI_MESSAGE_NOTIFY_WARN,
                        'msg': 'Scraping "{}" failed. Skipping.'.format(steamGame['name'])
                    })
                else:
                    new_roms.append(new_rom)
                            
                # ~~~ Check if user pressed the cancel button ~~~
                if self._isProgressCanceled():
                    self.progress_dialog.endProgress()
                    kodi.dialogger.OK('Stopping ROM scanning. No changes have been made.')
                    logger.info('User pressed Cancel button when scanning ROMs. ROM scanning stopped.')
                    return None
            
                num_items_checked += 1

        self.progress_dialog.endProgress()    
        return new_roms

class NvidiaStreamScanner(RomScannerStrategy):

    # ~~~ Scan for new items not yet in the rom collection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getCandidates(self, launcher_report, rom_path = None):
        logger.debug('Reading Nvidia GameStream server')
        self.progress_dialog.startProgress('Reading Nvidia GameStream server...')

        server_host = self.launcher.get_server()
        certificates_path = self.launcher.get_certificates_path()

        streamServer = GameStreamServer(server_host, certificates_path, False)
        connected = streamServer.connect()

        if not connected:
            kodi.notify_error('Unable to connect to gamestream server')
            return None

        self.progress_dialog.updateProgress(50)
        games = streamServer.getApps()
                
        self.progress_dialog.endProgress()
        return games

    # --- Remove dead entries -----------------------------------------------------------------
    def _removeDeadRoms(self, candidates, roms):
    
        if roms is None or len(roms) == 0:
            logger.info('Launcher is empty. No dead ROM check.')
            return 0

        logger.debug('Starting dead items scan')
        num_roms = len(roms)
        num_removed_roms = 0
        i = 0
            
        self.progress_dialog.startProgress('Checking for dead ROMs ...', num_roms)
        
        streamIds = set(streamableGame['ID'] for streamableGame in candidates)

        for rom in reversed(roms):
            romStreamId = rom.get_custom_attribute('streamid')
            
            logger.debug('Searching {0}'.format(romStreamId))
            self.progress_dialog.updateProgress(i)
            i += 1

            if romStreamId not in streamIds:
                logger.debug('Not found. Deleting from DB {0}'.format(rom.get_name()))
                roms.remove(rom)
                num_removed_roms += 1
            
        self.progress_dialog.endProgress()

        return num_removed_roms

    def _processFoundItems(self, items, roms, launcher_report):
        if items is None or len(items) == 0:
            logger.info('No Nvidia Gamestream games available.')
            return []

        new_roms = []

        num_games = len(items)
        num_items_checked = 0
            
        self.progress_dialog.startProgress('Checking for new ROMs ...', num_games)
        streamIdsAlreadyInCollection = set(rom.get_custom_attribute('streamid') for rom in roms)
        skip_if_scraping_failed = self.settings['scan_skip_on_scraping_failure']
        
        for streamableGame, extra_ROM_flag in items:
            
            streamId = streamableGame['ID']
            logger.debug('Searching {} with #{}'.format(streamableGame['AppTitle'], streamId))

            self.progress_dialog.updateProgress(num_items_checked, streamableGame['AppTitle'])
            
            if streamId in streamIdsAlreadyInCollection:
                logger.debug('Game "{}" with #{} already in collection'.format(streamableGame['AppTitle'], streamId))
                continue
                
            logger.debug('========== Processing Nvidia Gamestream game ==========')
            launcher_report.write('>>> title: {0}'.format(streamableGame['AppTitle']))
            launcher_report.write('>>> ID: {0}'.format(streamableGame['ID']))
    
            logger.debug('Not found. Item {0} is new'.format(streamableGame['AppTitle']))

            launcher_path = self.launcher.get_rom_path()
            fake_file_name = text.str_to_filename_str(streamableGame['AppTitle'])
            romPath = launcher_path.pjoin('{0}.rom'.format(fake_file_name))

            # ~~~~~ Process new ROM and add to the list ~~~~~
            # --- Create new rom dictionary ---
            # >> Database always stores the original (non transformed/manipulated) path
            new_rom  = ROM()
            new_rom.set_file(romPath)

            if extra_ROM_flag: new_rom.set_as_extra_ROM()
            
            new_rom.set_custom_attribute('streamid',        streamableGame['ID'])
            new_rom.set_custom_attribute('gamestream_name', streamableGame['AppTitle'])  # so that we always have the original name
            new_rom.set_name(streamableGame['AppTitle'])
            
            scraping_succeeded = True
            self.progress_dialog.updateMessage(streamableGame['AppTitle'], 'Scraping {0}...'.format(streamableGame['AppTitle']))
            try:
                self.scraping_strategy.scanner_process_ROM(new_rom, None)
            except Exception as ex:
                scraping_succeeded = False        
                logger.error('(Exception) Object type "{}"'.format(type(ex)))
                logger.error('(Exception) Message "{}"'.format(str(ex)))
                logger.warning('Could not scrape "{}"'.format(streamableGame['AppTitle']))
                #logger.debug(traceback.format_exc())
            
            if not scraping_succeeded and skip_if_scraping_failed:
                kodi.display_user_message({
                    'dialog': constants.KODI_MESSAGE_NOTIFY_WARN,
                    'msg': 'Scraping "{}" failed. Skipping.'.format(streamableGame['AppTitle'])
                })
            else:
                new_roms.append(new_rom)
                
            # ~~~ Check if user pressed the cancel button ~~~
            if self.progress_dialog.isCanceled():
                self.progress_dialog.endProgress()
                kodi.dialogger.OK('Stopping ROM scanning. No changes have been made.')
                logger.info('User pressed Cancel button when scanning ROMs. ROM scanning stopped.')
                return None
            
            num_items_checked += 1

        self.progress_dialog.endProgress()
        return new_roms
    