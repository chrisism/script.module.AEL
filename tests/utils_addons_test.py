import unittest

import logging

from tests import fakes
from lib.akl import addons

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG) 

class Test_utils_addons_tests(unittest.TestCase):
    
    def test_create_launch_command(self):
        # arrange
        expected_host = fakes.random_string(10)
        expected_port = fakes.random.randint(0, 5000)
        expected_addonid = fakes.random_string(10)
        expected_type = fakes.random.randint(0, 1000)
        expected_id = fakes.random_string(10)
        
        # act
        actual = addons.create_launch_command(expected_host, expected_port, expected_addonid,
                                              expected_type, expected_id)
        # assert
        assert actual['--server_host'] == expected_host
        assert actual['--entity_type'] == expected_type
        
if __name__ == '__main__':
    unittest.main()