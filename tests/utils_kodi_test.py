import unittest, os
from unittest.mock import patch, MagicMock, call

import logging

from fakes import FakeClass
from lib.akl.utils import kodi

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG) 

class Test_utils_kodi_tests(unittest.TestCase):
    
    def test_building_a_wizards_works(self):
        
        page1 = kodi.WizardDialog_Keyboard(None, 'x', 'abc')
        page2 = kodi.WizardDialog_Selection(page1, 'x2',['aa'], 'abc2')
        page3 = kodi.WizardDialog_Keyboard(page2, 'x3', 'abc3')

        props = {}

        page3.runWizard(props)
        
    @patch('lib.akl.utils.kodi.xbmc.Keyboard', autospec=True)     
    def test_starting_wizard_calls_pages_in_right_order(self, mock_keyboard:MagicMock): 
        
        # arrange
        mock_keyboard.getText().return_value = 'test'

        wizard = kodi.WizardDialog_Keyboard(None, 'x1', 'expected1')
        wizard = kodi.WizardDialog_Keyboard(wizard, 'x2', 'expected2')
        wizard = kodi.WizardDialog_Keyboard(wizard, 'x3', 'expected3')

        props = {}

        # act
        wizard.runWizard(props)
        calls = mock_keyboard.call_args_list

        # assert
        self.assertEqual(3, len(calls))
        self.assertEqual(call('','expected1'), calls[0])
        self.assertEqual(call('','expected2'), calls[1])
        self.assertEqual(call('','expected3'), calls[2])

    @patch('lib.akl.utils.kodi.xbmc.Keyboard.getText', autospec=True)     
    def test_when_i_give_the_wizardpage_a_custom_function_it_calls_it_as_expected(self, mock_keyboard:MagicMock): 
        
        # arrange
        mock_keyboard.return_value = 'expected'
        fake = FakeClass()

        props = {}
        page1 = kodi.WizardDialog_Keyboard(None, 'key','title1', fake.FakeMethod)

        # act
        page1.runWizard(props)
        
        # assert
        self.assertEqual('expected', fake.value)
                
    @patch('lib.akl.utils.kodi.xbmcgui.Dialog.select', autospec=True)
    def test_when_using_dictionary_select_dialog_it_gives_me_the_correct_result(self, mocked_dialog:MagicMock):

        # arrange
        dialog = kodi.OrdDictionaryDialog()

        options = {}
        options['10'] = 'A'
        options['20'] = 'B'
        options['30'] = 'C'

        expected = '20'
        mocked_dialog.return_value = 1

        # act
        actual = dialog.select('mytitle', options)

        # assert
        self.assertIsNotNone(actual)
        assert actual == expected
    
    def test_when_using_a_condition_function_with_the_wizard_it_will_responsd_correctly(self):

        # arrange
        expected = 'expected'
        target = kodi.WizardDialog_Dummy(None, 'actual', expected, None, lambda p1, p2: True)
        props = {}

        # act
        target.runWizard(props)
        actual = props['actual']
        
        # assert
        assert actual == expected
       
if __name__ == '__main__':
    unittest.main()