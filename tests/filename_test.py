import unittest, os
from unittest.mock import patch, MagicMock

import logging

from lib.akl.utils import io

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO) 
class Test_filename_test(unittest.TestCase):
     
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

    def test_reading_property_file_successfull(self):
        # arrange
        p = self.TEST_ASSETS_DIR + "\\retroarch.cfg"
        target = io.FileName(p)       

        # act
        propfile = target.readPropertyFile()
        for key, value in propfile.items():
            logger.debug('{}={}'.format(key, value))

        actual = propfile['content_database_path']

        # assert
        self.assertIsNotNone(actual)
        self.assertEqual(u':\\database\\rdb', actual)
        
    def test_parsing_strings_to_folders(self):
        # arrange
        path = '/data/user/0/com.retroarch/cores/'
        
        # act       
        actual = io.FileName(path, isdir=True) 
                
        # assert
        self.assertIsNotNone(actual)
        self.assertEqual(u'/data/user/0/com.retroarch/cores/', actual.path_tr)
        logger.info(actual.path_tr)
        
if __name__ == '__main__':
    unittest.main()
