# Unit tests for wsp_cleaning.py

import unittest
import urllib3

from SEDS_HW4 import delete_data
from SEDS_HW4 import get_data


class TestGetData(unittest.TestCase):


    delete_data('https://github.com/UWSEDS/LectureNotes/blob/master/open_data_year_two_set1.zip')
    # Test get_data
    def test_file_present_locally(self):
        # 1 - file is present locally
        urllib3.disable_warnings()
        test_valid_url = 'https://github.com/UWSEDS/LectureNotes/blob/master/open_data_year_two_set1.zip'
        get_data(test_valid_url)
        result = get_data(test_valid_url)
        expected_explanation = "Data exists locally. No action was taken."
        self.assertEqual(result, expected_explanation)
        delete_data(test_valid_url)

    def test_invalid_url(self):
        # 1 - URL does not point to a file that exists (missing 'o' in open)
        urllib3.disable_warnings()
        result = get_data('https://github.com/UWSEDS/LectureNotes/blob/master/pen_data_year_two_set1.zip')
        expected_explanation = "Sorry! You have entered an invalid URL."
        self.assertEqual(result, expected_explanation)
        # 2 - URL = 'asdf'
        result = get_data('asdf')
        expected_explanation = "Sorry! You have entered an invalid URL."
        self.assertEqual(result, expected_explanation)

    def test_no_file_locally_url_exists(self):
        # 1 - file is not present locally, and the URL points to a file that exists
        urllib3.disable_warnings()
        test_valid_url = 'https://github.com/UWSEDS/LectureNotes/blob/master/open_data_year_two_set1.zip'
        result = get_data(test_valid_url)
        expected_explanation = "Data downloaded successfully!"
        self.assertEqual(result, expected_explanation)
        delete_data(test_valid_url)


class TestDeleteData(unittest.TestCase):


    # Test delete_data
    def test_file_present_locally(self):
        # 1 - delete data if locally present
        urllib3.disable_warnings()
        test_valid_url = 'https://github.com/UWSEDS/LectureNotes/blob/master/open_data_year_two_set1.zip'
        get_data(test_valid_url)
        result = delete_data(test_valid_url)
        expected_explanation = "Data has been removed locally."
        self.assertEqual(result, expected_explanation)

    def test_invalid_url(self):
        # 1 - invalid URL (missing 'o' in open)
        result = delete_data('https://github.com/UWSEDS/LectureNotes/blob/master/pen_data_year_two_set1.zip')
        expected_explanation = "Sorry! You have entered an invalid URL."
        self.assertEqual(result, expected_explanation)

    def test_no_file_locally_no_action(self):
        # 1 - data does not exist; no action taken
        result = delete_data('https://github.com/UWSEDS/LectureNotes/blob/master/open_data_year_two_set1.zip')
        expected_explanation = "Data not found locally. No file was removed."
        self.assertEqual(result, expected_explanation)


if __name__ == '__main__':
    unittest.main()