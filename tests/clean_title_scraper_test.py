import unittest, os
from unittest.mock import patch, MagicMock

import logging
import random
import re

from lib.ael.api import ROMObj
from lib.ael.utils import io
from lib.ael import constants
from lib.ael.scrapers import Null_Scraper, ScrapeStrategy, ScraperSettings

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG) 

class Test_clean_title_scraper(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
                
        logger.info('ROOT DIR: {}'.format(cls.ROOT_DIR))
        logger.info('TEST DIR: {}'.format(cls.TEST_DIR))
        logger.info('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        logger.info('---------------------------------------------------------------------------')

    @patch('lib.ael.scrapers.api.client_get_rom')
    def test_scraping_metadata_for_game(self, api: MagicMock):
        
        # arrange
        settings = ScraperSettings()
        settings.scrape_metadata_policy = constants.SCRAPE_POLICY_TITLE_ONLY
        settings.scrape_assets_policy = constants.SCRAPE_ACTION_NONE
        settings.clean_tags = True
                
        fakeFilePath = '\\fake\\castlevania [ROM] (test) v2.rom'
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
        self.assertEqual(u'castlevania v2', actual.get_name())
        logger.info(actual)
        
    @patch('lib.ael.scrapers.api.client_get_rom')
    def test_when_scraping_with_cleantitlescraper_it_will_give_the_correct_result(self, api: MagicMock):
        
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

        self.assertEqual(expected, actual.get_name())        
        
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
      reg_exp = '\[.+?\]\s?|\(.+?\)\s?|\{.+?\}|[^\[\(\{]+'
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
          self.assertEquals(actual , expected)
