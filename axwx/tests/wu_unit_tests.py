# Unit tests for wu_cleaning.py
import unittest
import numpy as np

from wu_metadata_scraping_test import scrape_station_info

class TestGetData(unittest.TestCase):

    # Test number of columns
    def test_num_columns(self):
        #define the known number of cols, rows and headers we should get
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
