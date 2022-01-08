import unittest
from unittest.mock import patch, MagicMock

import logging
import random
import re

from fakes import FakeFile

from lib.akl.api import ROMObj
from lib.akl.utils import io
from lib.akl import constants
from lib.akl.scrapers import Null_Scraper, ScrapeStrategy, ScraperSettings

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG) 

class Test_clean_title_scraper(unittest.TestCase):
    
    @patch('lib.akl.scrapers.io.FileName', autospec=True, side_effect=FakeFile)
    @patch('lib.akl.scrapers.api.client_get_rom')
    def test_scraping_metadata_for_game(self, api: MagicMock, fakefiles):
        
        # arrange
        settings = ScraperSettings()
        settings.scrape_metadata_policy = constants.SCRAPE_POLICY_TITLE_ONLY
        settings.scrape_assets_policy = constants.SCRAPE_ACTION_NONE
        settings.clean_tags = True
                
        fakeFilePath = '/fake/castlevania [ROM] (test) v2.rom'
        fakeId = str(random.random())
        subject = ROMObj({
          'scanned_data': { 'file': fakeFilePath}
        })
        api.return_value = subject
            
        target = ScrapeStrategy('', 0, settings, Null_Scraper(), MagicMock())
                
        # act
        actual = target.process_single_rom(fakeId)
                
        # assert
        self.assertIsNotNone(actual)
        assert u'castlevania v2' == actual.get_name()
        logger.info(actual)
        
    @patch('lib.akl.scrapers.io.FileName', autospec=True, side_effect=FakeFile)
    @patch('lib.akl.scrapers.api.client_get_rom')
    def test_when_scraping_with_cleantitlescraper_it_will_give_the_correct_result(self, api: MagicMock, fakefiles):
        
        # arrange
        settings = ScraperSettings()
        settings.scrape_metadata_policy = constants.SCRAPE_POLICY_TITLE_ONLY
        settings.scrape_assets_policy = constants.SCRAPE_ACTION_NONE
        settings.clean_tags = True
        
        fakeFilePath = '/don/el_juan [DUMMY].zip'
        fakeId = str(random.random())
        subject = ROMObj({
          'scanned_data': { 'file': fakeFilePath}
        })
        api.return_value = subject
            
        expected = 'el_juan'
        target = ScrapeStrategy('', 0, settings, Null_Scraper(), MagicMock())                
        
        # act
        actual = target.process_single_rom(fakeId)

        # assert
        self.assertIsNotNone(actual)
        self.assertTrue(actual)

        assert expected == actual.get_name()     
        
    ROM_title_list = {
      '[BIOS] CX4 (World)':                                       '[BIOS] CX4',
      '[BIOS] CX4':                                               '[BIOS] CX4',
      "'96 Zenkoku Koukou Soccer Senshuken (Japan)":              "'96 Zenkoku Koukou Soccer Senshuken",
      'Super Mario World (Europe) (Rev 1)':                       'Super Mario World',
      'Super Mario World - Super Mario Bros. 4 (Japan)':          'Super Mario World - Super Mario Bros. 4',
      "Super Mario World 2 - Yoshi's Island (Europe) (En,Fr,De)": "Super Mario World 2 - Yoshi's Island",
      "Super Mario World 2 - Yoshi's Island":                     "Super Mario World 2 - Yoshi's Island"
    }
      
    def test_rom_title_formatting(self):
      #
      # Regexp to decompose a string in tokens
      #
      reg_exp = r'\[.+?\]\s?|\(.+?\)\s?|\{.+?\}|[^\[\(\{]+'
      for ROM_filename, expected in Test_clean_title_scraper.ROM_title_list.items():
          tokens = re.findall(reg_exp, ROM_filename)
          print('---------> "{0}"'.format(ROM_filename))
          for i, token in enumerate(tokens): print('Token {0} -> "{1}"'.format(i, token.strip()))

          str_list = []
          for token in tokens:
              stripped_token = token.strip()
              if (stripped_token[0] == '[' or stripped_token[0] == '(' or stripped_token[0] == '{') and \
                stripped_token != '[BIOS]':
                  continue
              str_list.append(stripped_token)
          new_title = ' '.join(str_list)
          print('>>>>>>>>>> "{0}"'.format(new_title))
          print('')
          actual = new_title
          assert actual == expected
