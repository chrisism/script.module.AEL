import unittest, os
from unittest.mock import patch, MagicMock

import logging
import random

from lib.ael.api import ROMObj
from lib.ael.utils import io
from lib.ael.scrapers import Null_Scraper, ScrapeStrategy, ScraperSettings

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO) 

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
        settings.scrape_metadata_policy = 3
        settings.clean_tags = True
        
        fakeFilePath = '\\fake\\castlevania [ROM] (test) v2.rom'
        fakeId = str(random.random())
        subject = ROMObj()
        subject.set_file(io.FileName(fakeFilePath))
        api.return_value = subject
            
        target = ScrapeStrategy('', 0, settings, Null_Scraper(), MagicMock())
                
        # act
        actual = target.process_single_rom(fakeId)
                
        # assert
        self.assertIsNotNone(actual)
        self.assertEqual(u'castlevania v2', actual.get_name())
        print(actual)
        