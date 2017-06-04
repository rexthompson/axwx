# Unit tests for testing wu_metadata_scraping_test

import unittest
import numpy as np

from wu_metadata_scraping_test import scrape_station_info

class TestGetData(unittest.TestCase):

    """
    This class performs a unit test for the wu_metadata_scraping.py dataset by 
    testing the number of columns in the cleaned data set is equivalent 
    to the cleaned data output in order to ensure data integrity.
    """
    def test_num_columns(self):
        """
        Defining the known number of cols, rows and headers we
        should get for check in the unit test.
        """
        num_col = 7
        num_row = 4
        headers = np.asarray(['id', 'neighborhood', 'city',
        'type', 'lat', 'lon', 'elevation'])
        num_colt, num_rowt, headerst = scrape_station_info()
        self.assertEqual(num_colt, num_col)
        self.assertEqual(num_rowt, num_row)
        self.assertTrue((headerst == headers).all())

if __name__ == '__main__':
    unittest.main()
