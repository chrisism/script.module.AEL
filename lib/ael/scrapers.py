# -*- coding: utf-8 -*-

# Advanced Emulator Launcher scraping engine.
#
# --- Information about scraping ---
# https://github.com/muldjord/skyscraper
# https://github.com/muldjord/skyscraper/blob/master/docs/SCRAPINGMODULES.md

# Copyright (c) 2016-2019 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.


# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division

import logging
import collections
import abc
import datetime

from ael.utils import kodi
from ael import constants

logger = logging.getLogger(__name__)

class ScraperSettings(object): 
    
    def __init__(self):
        self.metadata_scraper_ID = constants.SCRAPER_NULL_ID
        self.assets_scraper_ID   = constants.SCRAPER_NULL_ID
        
        self.scrape_metadata_policy = constants.SCRAPE_POLICY_TITLE_ONLY
        self.scrape_assets_policy   = constants.SCRAPE_POLICY_LOCAL_ONLY
        
        self.search_term_mode       = constants.SCRAPE_AUTOMATIC
        self.game_selection_mode    = constants.SCRAPE_AUTOMATIC
        self.asset_selection_mode   = constants.SCRAPE_AUTOMATIC
        
        self.asset_IDs_to_scrape = constants.ROM_ASSET_ID_LIST
        self.overwrite_existing = False
        self.show_info_verbose = False
    
    def build_menu(self):
        options = collections.OrderedDict()        
        options['SC_METADATA_POLICY']      = 'Metadata scan policy: "{}"'.format(kodi.translate(self.scrape_metadata_policy))
        options['SC_ASSET_POLICY']         = 'Asset scan policy: "{}"'.format(kodi.translate(self.scrape_assets_policy))
        options['SC_GAME_SELECTION_MODE']  = 'Game selection mode: "{}"'.format(kodi.translate(self.game_selection_mode))
        options['SC_ASSET_SELECTION_MODE'] = 'Asset selection mode: "{}"'.format(kodi.translate(self.asset_selection_mode))
        options['SC_OVERWRITE_MODE']       = 'Overwrite existing files: "{}"'.format('Yes' if self.overwrite_existing else 'No')
        options['SC_METADATA_SCRAPER']     = 'Metadata scraper: "{}"'.format(kodi.translate(self.metadata_scraper_ID))
        options['SC_ASSET_SCRAPER']        = 'Asset scraper: "{}"'.format(kodi.translate(self.assets_scraper_ID))        
        return options
            
    @staticmethod
    def from_settings(settings, launcher):
        
        scraper_settings = ScraperSettings()        
        platform = launcher.get_platform()
        
        # --- Read addon settings and configure the scrapers selected -----------------------------
        if platform == 'MAME':
            logger.debug('ScraperSettings::from_settings() Platform is MAME.')
            logger.debug('Using MAME scrapers from settings.xml')
            scraper_settings.metadata_scraper_ID = settings['scraper_metadata_MAME']
            scraper_settings.assets_scraper_ID   = settings['scraper_asset_MAME']
        else:
            logger.debug('ScraperSettings.from_settings() Platform is NON-MAME.')
            logger.debug('Using standard scrapers from settings.xml')
            scraper_settings.metadata_scraper_ID = settings['scraper_metadata']
            scraper_settings.assets_scraper_ID   = settings['scraper_asset']
                
        scraper_settings.scrape_metadata_policy = settings['scan_metadata_policy']
        scraper_settings.scrape_assets_policy   = settings['scan_asset_policy']
        scraper_settings.game_selection_mode    = settings['game_selection_mode']
        scraper_settings.asset_selection_mode   = settings['asset_selection_mode']    
        
        return scraper_settings
     
#
# Abstract base class for all scrapers (offline or online, metadata or asset).
# The scrapers are Launcher and ROM agnostic. All the required Launcher/ROM properties are
# stored in the strategy object.
#
class Scraper(object):
    __metaclass__ = abc.ABCMeta

    # --- Class variables ------------------------------------------------------------------------
    # When then number of network error/exceptions is bigger than this threshold the scraper
    # is deactivated. This is useful in the ROM Scanner to not flood the user with error
    # messages in case something is wrong (for example, the internet connection is broken or
    # the number of API calls is exceeded).
    EXCEPTION_COUNTER_THRESHOLD = 5
    
    # Maximum amount of retries of certain requests
    RETRY_THRESHOLD = 4

    # Disk cache types. These string will be part of the cache file names.
    CACHE_CANDIDATES = 'candidates'
    CACHE_METADATA   = 'metadata'
    CACHE_ASSETS     = 'assets'
    CACHE_INTERNAL   = 'internal'
    CACHE_LIST = [
        CACHE_CANDIDATES, CACHE_METADATA, CACHE_ASSETS, CACHE_INTERNAL,
    ]

    # TODO MOVE TO TGDB Scrpaer
    #GLOBAL_CACHE_TGDB_GENRES     = 'TGDB_genres'
    #GLOBAL_CACHE_TGDB_DEVELOPERS = 'TGDB_developers'
    #GLOBAL_CACHE_LIST = [
    #    GLOBAL_CACHE_TGDB_GENRES, GLOBAL_CACHE_TGDB_DEVELOPERS,
    #]

    JSON_indent = 1
    JSON_separators = (',', ':')

    # --- Constructor ----------------------------------------------------------------------------
    # @param settings: [dict] Addon settings.
    def __init__(self, settings, fallbackScraper = None):
        self.settings = settings
        self.verbose_flag = False
        self.dump_file_flag = False # Dump DEBUG files only if this is true.
        self.dump_dir = None # Directory to dump DEBUG files.
        self.debug_checksums_flag = False
        # Record the number of network error/exceptions. If this number is bigger than a
        # threshold disable the scraper.
        self.exception_counter = 0
        # If this is True the scraper is internally disabled. A disabled scraper alwats returns
        # empty data like the NULL scraper.
        self.scraper_disabled = False
        # Directory to store on-disk scraper caches.
        self.scraper_cache_dir = settings['scraper_cache_dir']
        # Do not log here. Otherwise the same thing will be printed for every scraper instantiated.
        # logger.debug('Scraper.__init__() scraper_cache_dir "{}"'.format(self.scraper_cache_dir))

        self.last_http_call = datetime.now()
        
        # --- Disk caches ---
        self.disk_caches = {}
        self.disk_caches_loaded = {}
        self.disk_caches_dirty = {}
        for cache_name in Scraper.CACHE_LIST:
            self.disk_caches[cache_name] = {}
            self.disk_caches_loaded[cache_name] = False
            self.disk_caches_dirty[cache_name] = False
        # Candidate game is set with functions set_candidate_from_cache() or set_candidate()
        # and used by functions get_metadata() and get_assets()
        self.candidate = None

        # --- Global disk caches ---
        self.global_disk_caches = {}
        self.global_disk_caches_loaded = {}
        self.global_disk_caches_dirty = {}
        for cache_name in Scraper.GLOBAL_CACHE_LIST:
            self.global_disk_caches[cache_name] = {}
            self.global_disk_caches_loaded[cache_name] = False
            self.global_disk_caches_dirty[cache_name] = False

    # --- Methods --------------------------------------------------------------------------------
    # Scraper is much more verbose (even more than AEL Debug level).
    def set_verbose_mode(self, verbose_flag):
        logger.debug('Scraper.set_verbose_mode() verbose_flag {0}'.format(verbose_flag))
        self.verbose_flag = verbose_flag

    # Dump scraper data into files for debugging. Used in the development scripts.
    def set_debug_file_dump(self, dump_file_flag, dump_dir):
        logger.debug('Scraper.set_debug_file_dump() dump_file_flag {0}'.format(dump_file_flag))
        logger.debug('Scraper.set_debug_file_dump() dump_dir {0}'.format(dump_dir))
        self.dump_file_flag = dump_file_flag
        self.dump_dir = dump_dir

    # ScreenScraper needs the checksum of the file scraped. This function sets the checksums
    # externally for debugging purposes, for example when debugging the scraper with
    # fake filenames.
    def set_debug_checksums(self, debug_checksums, crc_str = '', md5_str = '', sha1_str = '', size = 0):
        logger.debug('Scraper.set_debug_checksums() debug_checksums {0}'.format(debug_checksums))
        self.debug_checksums_flag = debug_checksums
        self.debug_crc  = crc_str
        self.debug_md5  = md5_str
        self.debug_sha1 = sha1_str
        self.debug_size = size

    # Dump dictionary as JSON file for debugging purposes.
    # This function is used internally by the scrapers if the flag self.dump_file_flag is True.
    def _dump_json_debug(self, file_name, data_dic):
        if not self.dump_file_flag: return
        file_path = os.path.join(self.dump_dir, file_name)
        if SCRAPER_CACHE_HUMAN_JSON:
            json_str = json.dumps(data_dic, indent = 4, separators = (', ', ' : '))
        else:
            json_str = json.dumps(data_dic)
        text.dump_str_to_file(file_path, json_str)

    def _dump_file_debug(self, file_name, page_data):
        if not self.dump_file_flag: return
        file_path = os.path.join(self.dump_dir, file_name)
        text_dump_str_to_file(file_path, page_data)

    @abc.abstractmethod
    def get_id(self): pass
    
    @abc.abstractmethod
    def get_name(self): pass

    @abc.abstractmethod
    def get_filename(self): pass

    @abc.abstractmethod
    def supports_disk_cache(self): pass

    @abc.abstractmethod
    def supports_search_string(self): pass

    @abc.abstractmethod
    def supports_metadata_ID(self, metadata_ID): pass

    @abc.abstractmethod
    def supports_metadata(self): pass

    @abc.abstractmethod
    def supports_asset_ID(self, asset_ID): pass

    @abc.abstractmethod
    def supports_assets(self): pass

    # Check if the scraper is ready to work. For example, check if required API keys are
    # configured, etc. If there is some fatal errors then deactivate the scraper.
    #
    # @return: [dic] kodi_new_status_dic() status dictionary.
    @abc.abstractmethod
    def check_before_scraping(self, status_dic): pass

    # The *_candidates_cache_*() functions use the low level cache functions which are internal
    # to the Scraper object. The functions next are public, however.

    # Returns True if candidate is in disk cache, False otherwise.
    # Lazy loads candidate cache from disk.
    def check_candidates_cache(self, rom_FN, platform):
        self.cache_key = rom_FN.getBase()
        self.platform = platform

        return self._check_disk_cache(Scraper.CACHE_CANDIDATES, self.cache_key)

    # Not necesary to lazy load the cache because before calling this function
    # check_candidates_cache() must be called.
    def retrieve_from_candidates_cache(self, rom_FN, platform):
        self.cache_key = rom_FN.getBase()

        return self._retrieve_from_disk_cache(Scraper.CACHE_CANDIDATES, self.cache_key)

    def set_candidate_from_cache(self, rom_FN, platform):
        self.cache_key = rom_FN.getBase()
        self.platform  = platform
        self.candidate = self._retrieve_from_disk_cache(Scraper.CACHE_CANDIDATES, self.cache_key)

    def set_candidate(self, rom_FN, platform, candidate):
        self.cache_key = rom_FN.getBase()
        self.platform  = platform
        self.candidate = candidate
        logger.debug('Scrape.set_candidate() Setting "{}" "{}"'.format(self.cache_key, platform))
        # Do not introduce None candidates in the cache so the game will be rescraped later.
        # Keep the None candidate in the object internal variables so later calls to 
        # get_metadata() and get_assets() will know an error happened.
        if candidate is None: return
        self._update_disk_cache(Scraper.CACHE_CANDIDATES, self.cache_key, candidate)
        logger.debug('Scrape.set_candidate() Added "{}" to cache'.format(self.cache_key))

    # When the user decides to rescrape an item that was in the cache make sure all
    # the caches are purged.
    def clear_cache(self, rom_FN, platform):
        self.cache_key = rom_FN.getBase()
        self.platform = platform
        logger.debug('Scraper.clear_cache() Clearing caches "{}" "{}"'.format(
            self.cache_key, platform))
        for cache_type in Scraper.CACHE_LIST:
            if self._check_disk_cache(cache_type, self.cache_key):
                self._delete_from_disk_cache(cache_type, self.cache_key)

    # Only write to disk non-empty caches.
    # Only write to disk dirty caches. If cache has not been modified then do not write it.
    def flush_disk_cache(self, pdialog = None):
        # If scraper does not use disk cache (notably AEL Offline) return.
        if not self.supports_disk_cache():
            logger.debug('Scraper.flush_disk_cache() Scraper {} does not use disk cache.'.format(
                self.get_name()))
            return

        # Create progress dialog.
        num_steps = len(Scraper.CACHE_LIST) + len(Scraper.GLOBAL_CACHE_LIST)
        step_count = 0
        if pdialog is not None:
            pdialog.startProgress('Flushing scraper disk caches...', num_steps)

        # --- Scraper caches ---
        logger.debug('Scraper.flush_disk_cache() Saving scraper {} disk cache...'.format(
            self.get_name()))
        for cache_type in Scraper.CACHE_LIST:
            if pdialog is not None:
                pdialog.updateProgress(step_count)
                step_count += 1

            # Skip unloaded caches
            if not self.disk_caches_loaded[cache_type]:
                logger.debug('Skipping {} (Unloaded)'.format(cache_type))
                continue
            # Skip empty caches
            if not self.disk_caches[cache_type]:
                logger.debug('Skipping {} (Empty)'.format(cache_type))
                continue
            # Skip clean caches.
            if not self.disk_caches_dirty[cache_type]:
                logger.debug('Skipping {} (Clean)'.format(cache_type))
                continue

            # Get JSON data.
            json_data = json.dumps(
                self.disk_caches[cache_type], ensure_ascii = False, sort_keys = True,
                indent = Scraper.JSON_indent, separators = Scraper.JSON_separators)

            # Write to disk
            json_file_path, json_fname = self._get_scraper_file_name(cache_type, self.platform)
            file = io.open(json_file_path, 'w', encoding = 'utf-8')
            file.write(unicode(json_data))
            file.close()
            # logger.debug('Saved "{}"'.format(json_file_path))
            logger.debug('Saved "<SCRAPER_CACHE_DIR>/{}"'.format(json_fname))

            # Cache written to disk is clean gain.
            self.disk_caches_dirty[cache_type] = False

        # --- Global caches ---
        logger.debug('Scraper.flush_disk_cache() Saving scraper {} global disk cache...'.format(
                self.get_name()))
        for cache_type in Scraper.GLOBAL_CACHE_LIST:
            if pdialog is not None:
                pdialog.updateProgress(step_count)
                step_count += 1

            # Skip unloaded caches
            if not self.global_disk_caches_loaded[cache_type]:
                logger.debug('Skipping global {} (Unloaded)'.format(cache_type))
                continue
            # Skip empty caches
            if not self.global_disk_caches[cache_type]:
                logger.debug('Skipping global {} (Empty)'.format(cache_type))
                continue
            # Skip clean caches.
            if not self.global_disk_caches_dirty[cache_type]:
                logger.debug('Skipping global {} (Clean)'.format(cache_type))
                continue

            # Get JSON data.
            json_data = json.dumps(
                self.global_disk_caches[cache_type], ensure_ascii = False, sort_keys = True,
                indent = Scraper.JSON_indent, separators = Scraper.JSON_separators)

            # Write to disk
            json_file_path, json_fname = self._get_global_file_name(cache_type)
            file = io.open(json_file_path, 'w', encoding = 'utf-8')
            file.write(unicode(json_data))
            file.close()
            # logger.debug('Saved global "{}"'.format(json_file_path))
            logger.debug('Saved global "<SCRAPER_CACHE_DIR>/{}"'.format(json_fname))

            # Cache written to disk is clean gain.
            self.global_disk_caches_dirty[cache_type] = False
        if pdialog is not None: pdialog.endProgress()

    # Search for candidates and return a list of dictionaries _new_candidate_dic().
    #
    # * This function is never cached. What is cached is the chosen candidate games.
    # * If no candidates found by the scraper return an empty list and status is True.
    # * If there is an error/exception (network error, bad data returned) return None,
    #   the cause is printed in the log, status is False and the status dictionary contains
    #   a user notification.
    # * The number of network error/exceptions is recorded internally by the scraper. If the
    #   number of errors is **bigger than a threshold**, **the scraper is deactivated** (no more
    #   errors reported in the future, just empty data is returned).
    # * If the scraper is overloaded (maximum number of API/web requests) it is considered and
    #   error and the scraper is internally deactivated immediately. The error message associated
    #   with the scraper overloading must be printed once like any other error.
    #
    # @param search_term: [str] String to be searched.
    # @param rom_FN: [FileName] Scraper will get whatever part of the filename they want.
    # @param rom_checksums_FN: [FileName] File to be used when computing checksums. For
    #                          multidisc ROMs rom_FN is a fake file but rom_checksums_FN is a real
    #                          file belonging to the set.
    # @param platform: [str] AEL platform.
    # @param status_dic: [dict] kodi_new_status_dic() status dictionary.
    # @return: [list] or None.
    @abc.abstractmethod
    def get_candidates(self, search_term, rom_FN, rom_checksums_FN, platform, status_dic): pass

    # Returns the metadata for a candidate (search result).
    #
    # * See comments in get_candidates()
    #
    # @param status_dic: [dict] kodi_new_status_dic() status dictionary.
    # @return: [dict] Dictionary self._new_gamedata_dic(). If no metadata found (very unlikely)
    #          then a dictionary with default values is returned. If there is an error/exception
    #          None is returned, the cause printed in the log and status_dic has a message to show.
    @abc.abstractmethod
    def get_metadata(self, status_dic): pass

    # Returns a list of assets for a candidate (search result).
    #
    # * See comments in get_candidates()
    #
    # @param status_dic: [dict] kodi_new_status_dic() status dictionary.
    # @return: [list] List of _new_assetdata_dic() dictionaries. If no assets found then an empty
    #          list is returned. If there is an error/exception None is returned, the cause printed
    #          in the log and status_dic has a message to show.
    @abc.abstractmethod
    def get_assets(self, asset_info, status_dic): pass

    # When returning the asset list with get_assets(), some sites return thumbnails images
    # because the real assets are on a single dedicated page. For this sites, resolve_asset_URL()
    # returns the true, full size URL of the asset.
    #
    # Other scrapers, for example MobyGames, return both the thumbnail and the true asset URLs
    # in get_assets(). In such case, the implementation of this method is trivial.
    #
    # @param selected_asset: 
    # @param status_dic: [dict] kodi_new_status_dic() status dictionary.
    # @return: [tuple of strings] or None 
    #          First item, string with the URL to download the asset.
    #          Second item, string with the URL for printing in logs. URL may have sensitive
    #          information in some scrapers.
    #          None is returned in case of error and status_dic updated.
    @abc.abstractmethod
    def resolve_asset_URL(self, selected_asset, status_dic): pass

    # Get the URL image extension. In some scrapers the type of asset cannot be obtained by
    # the asset URL and must be resolved to save the asset in the filesystem.
    #
    # @param selected_asset: 
    # @param image_url: 
    # @param status_dic: [dict] kodi_new_status_dic() status dictionary.
    # @return: [str] String with the image extension in lowercase 'png', 'jpg', etc.
    #          None is returned in case or error/exception and status_dic updated.
    @abc.abstractmethod
    def resolve_asset_URL_extension(self, selected_asset, image_url, status_dic): pass

    # Downloads an image from the given url to the local path.
    # Can overwrite this method in scraper implementation to support extra actions, like
    # request throttling.
    def download_image(self, image_url, image_local_path):
        # net_download_img() never prints URLs or paths.
        net_download_img(image_url, image_local_path)
        return image_local_path

    # Not used now. candidate['id'] is used as hash value for the whole candidate dictionary.
    # candidate['id'] must be unique for each game.
    # def _dictionary_hash(self, my_dict):
    #     return hash(frozenset(sorted(my_dict.items())))

    # Nested dictionaries are not allowed. All the dictionaries here must be "hashable".
    # If your dictionary is not nested, you could make a frozenset with the dict's items
    # and use hash():
    #
    # hash(frozenset(sorted(my_dict.items())))
    #
    # This is much less computationally intensive than generating the JSON string
    # or representation of the dictionary.
    # See https://stackoverflow.com/questions/5884066/hashing-a-dictionary
    def _new_candidate_dic(self):
        return {
            'id'               : '',
            'display_name'     : '',
            'platform'         : '',
            'scraper_platform' : '',
            'order'            : 0,
        }

    def _new_gamedata_dic(self):
        return {
            'title'     : '',
            'year'      : '',
            'genre'     : '',
            'developer' : '',
            'nplayers'  : '',
            'esrb'      : '',
            'plot'      : ''
        }

    # url_thumb is always returned by get_assets().
    # url is returned by resolve_asset_URL().
    # Note that some scrapers (MobyGames) return both url_thumb and url in get_assets(). Always
    # call resolve_asset_URL() for compabilitity with all scrapers.
    def _new_assetdata_dic(self):
        return {
            'asset_ID'     : None,
            'display_name' : '',
            'url_thumb'    : '',
            'url'          : '',
            'downloadable' : True
        }

    # This functions is called when an error that is not an exception and needs to increase
    # the scraper error limit happens.
    # All messages generated in the scrapers are KODI_MESSAGE_DIALOG.
    def _handle_error(self, status_dic, user_msg):
        # Print error message to the log.
        log_error('Scraper._handle_error() user_msg "{}"'.format(user_msg))

        # Fill in the status dictionary so the error message will be propagated up in the
        # stack and the error message printed in the GUI.
        status_dic['status'] = False
        status_dic['dialog'] = KODI_MESSAGE_DIALOG
        status_dic['msg'] = user_msg
        
        # Record the number of error/exceptions produced in the scraper and disable the scraper
        # if the number of errors is higher than a threshold.
        self.exception_counter += 1
        if self.exception_counter > Scraper.EXCEPTION_COUNTER_THRESHOLD:
            err_m = 'Maximum number of errors exceeded. Disabling scraper.'
            log_error(err_m)
            self.scraper_disabled = True
            # Replace error message witht the one that the scraper is disabled.
            status_dic['msg'] = err_m

    # This function is called when an exception in the scraper code happens.
    # All messages from the scrapers are KODI_MESSAGE_DIALOG.
    def _handle_exception(self, ex, status_dic, user_msg):
        log_error('(Exception) Object type "{}"'.format(type(ex)))
        log_error('(Exception) Message "{}"'.format(str(ex)))
        self._handle_error(status_dic, user_msg)

    # --- Private disk cache functions -----------------------------------------------------------
    def _get_scraper_file_name(self, cache_type, platform):
        scraper_filename = self.get_filename()
        json_fname = scraper_filename + '__' + platform + '__' + cache_type + '.json'
        json_full_path = os.path.join(self.scraper_cache_dir, json_fname).decode('utf-8')

        return json_full_path, json_fname

    def _lazy_load_disk_cache(self, cache_type):
        if not self.disk_caches_loaded[cache_type]:
            self._load_disk_cache(cache_type, self.platform)

    def _load_disk_cache(self, cache_type, platform):
        # --- Get filename ---
        json_file_path, json_fname = self._get_scraper_file_name(cache_type, platform)
        logger.debug('Scraper._load_disk_cache() Loading cache "{}"'.format(cache_type))

        # --- Load cache if file exists ---
        if os.path.isfile(json_file_path):
            file = open(json_file_path)
            file_contents = file.read()
            file.close()
            self.disk_caches[cache_type] = json.loads(file_contents)
            # logger.debug('Loaded "{}"'.format(json_file_path))
            logger.debug('Loaded "<SCRAPER_CACHE_DIR>/{}"'.format(json_fname))
        else:
            logger.debug('Cache file not found. Resetting cache.')
            self.disk_caches[cache_type] = {}
        self.disk_caches_loaded[cache_type] = True
        self.disk_caches_dirty[cache_type] = False

    # Returns True if item is in the cache, False otherwise.
    # Lazy loads cache files from disk.
    def _check_disk_cache(self, cache_type, cache_key):
        self._lazy_load_disk_cache(cache_type)

        return True if cache_key in self.disk_caches[cache_type] else False

    # _check_disk_cache() must be called before this.
    def _retrieve_from_disk_cache(self, cache_type, cache_key):
        return self.disk_caches[cache_type][cache_key]

    # _check_disk_cache() must be called before this.
    def _delete_from_disk_cache(self, cache_type, cache_key):
        del self.disk_caches[cache_type][cache_key]
        self.disk_caches_dirty[cache_type] = True

    # Lazy loading should be done here because the internal cache for ScreenScraper
    # could be updated withouth being loaded first with _check_disk_cache().
    def _update_disk_cache(self, cache_type, cache_key, data):
        self._lazy_load_disk_cache(cache_type)
        self.disk_caches[cache_type][cache_key] = data
        self.disk_caches_dirty[cache_type] = True

    # --- Private global disk caches -------------------------------------------------------------
    def _get_global_file_name(self, cache_type):
        json_fname = cache_type + '.json'
        json_full_path = os.path.join(self.scraper_cache_dir, json_fname).decode('utf-8')

        return json_full_path, json_fname

    def _lazy_load_global_disk_cache(self, cache_type):
        if not self.global_disk_caches_loaded[cache_type]:
            self._load_global_cache(cache_type)

    def _load_global_cache(self, cache_type):
        # --- Get filename ---
        json_file_path, json_fname = self._get_global_file_name(cache_type)
        logger.debug('Scraper._load_global_cache() Loading cache "{}"'.format(cache_type))

        # --- Load cache if file exists ---
        if os.path.isfile(json_file_path):
            file = open(json_file_path)
            file_contents = file.read()
            file.close()
            self.global_disk_caches[cache_type] = json.loads(file_contents)
            # logger.debug('Loaded "{}"'.format(json_file_path))
            logger.debug('Loaded "<SCRAPER_CACHE_DIR>/{}"'.format(json_fname))
        else:
            logger.debug('Cache file not found. Resetting cache.')
            self.global_disk_caches[cache_type] = {}
        self.global_disk_caches_loaded[cache_type] = True
        self.global_disk_caches_dirty[cache_type] = False

    def _check_global_cache(self, cache_type):
        self._lazy_load_global_disk_cache(cache_type)

        return self.global_disk_caches[cache_type]

    # _check_global_cache() must be called before this.
    def _retrieve_global_cache(self, cache_type):
        return self.global_disk_caches[cache_type]

    # _check_global_cache() must be called before this.
    def _reset_global_cache(self, cache_type):
        self.global_disk_caches[cache_type] = {}
        self.global_disk_caches_dirty[cache_type] = True

    def _update_global_cache(self, cache_type, data):
        self._lazy_load_global_disk_cache(cache_type)
        self.global_disk_caches[cache_type] = data
        self.global_disk_caches_dirty[cache_type] = True

    # Generic waiting method to avoid too many requests
    # and website abuse. 
    def _wait_for_API_request(self, wait_time_in_miliseconds = 1000):
        if wait_time_in_miliseconds == 0:
            return
        
        # Make sure we dont go over the TooManyRequests limit of 1 second.
        now = datetime.now()
        if (now - self.last_http_call).total_seconds() * 1000 < wait_time_in_miliseconds:
            logger.debug('Scraper._wait_for_API_request() Sleeping {}ms to avoid overloading...'.format(wait_time_in_miliseconds))
            time.sleep(wait_time_in_miliseconds / 1000)
  