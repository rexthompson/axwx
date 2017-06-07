"""
Unit tests for wsp_cleaning.py (Washington State Patrol:
Collision Analysis Tool)
"""


import axwx
import os.path as op
import numpy as np
import pandas as pd
import unittest

from axwx import wu_metadata_scraping_test as wu_meta


data_path = op.join(axwx.__path__[0], 'data')


class TestWspCleaning(unittest.TestCase):
    """
    Unit tests for wsp_cleaning.py (Washington State Patrol:
    Collision Analysis Tool)
    """

    def test_clean_csv_shape(self):
        """
        Testing for a successful read of the WSP data and transformation
        to the correct shape
        """
        df = axwx.clean_wsp_collision_data(op.join(data_path,
                                                   'test_wsp_raw.csv'))
        shape = df.shape
        expected_shape = (6, 28)
        self.assertEqual(shape, expected_shape)

    def test_clean_csv_header(self):
        """
        Testing for a successful read of the WSP data and transformation
        with the correct columns
        """
        df = axwx.clean_wsp_collision_data(op.join(data_path,
                                                   'test_wsp_raw.csv'))
        header = df.head(0)
        expected_header = ('lat' and
                           'lon' and
                           'date' and
                           'time_of_day' and
                           'month' and
                           'day_of_week' and
                           'hour' and
                           'driver_restraint_type' and
                           'passenger_restraint_type' and
                           'roadway_surface_condition' and
                           'roadway_characterization' and
                           'current_weather' and
                           'lighting_conditions' and
                           'sobriety_type' and
                           'roadway_surface_type' and
                           'posted_speed_limit' and
                           'pedestrian_present' and
                           'cyclist_present' and
                           'driver_injury' and
                           'passenger_injury' and
                           'pedestrian_injury' and
                           'cyclist_injury' and
                           'vehicle_action' and
                           'contributing_factor_1' and
                           'contributing_factor_2' and
                           'contributing_factor_3' and
                           'alcohol_test_given' and
                           'airbag')
        self.assertTrue(expected_header in header)


class TestWuCleaning(unittest.TestCase):
    """
    Testing the number of columns in the scraped data set is equivalent
    to the cleaned data output in order to ensure data integrity.
    """

    def test_wu_cleaning(self):
        """
        Creating dummy dataframe to test the cleaning function wu_cleaning.py
        """
        dummy_data = pd.DataFrame({'TemperatureF': [0, 50, 150],
                                   'DewpointF': [-99.9, 50, 80],
                                   'PressureIn': [0, 30, 50],
                                   'WindDirectionDegrees': [-50, 50, 500],
                                   'Humidity': [-50, 50, 150]})

        clean_data = axwx.clean_obs_data(dummy_data)

        self.assertFalse((clean_data.ix[:, 0] <= 10).any())
        self.assertFalse((clean_data.ix[:, 0] >= 125).any())

        self.assertFalse((clean_data.ix[:, 1] == -99.9).any())
        self.assertFalse((clean_data.ix[:, 1] >= 80).any())

        self.assertFalse((clean_data.ix[:, 2] <= 25).any())
        self.assertFalse((clean_data.ix[:, 2] >= 31.5).any())

        self.assertFalse((clean_data.ix[:, 3] < 0).any())
        self.assertFalse((clean_data.ix[:, 3] >= 360).any())

        self.assertFalse((clean_data.ix[:, 4] <= 0).any())
        self.assertFalse((clean_data.ix[:, 4] > 100).any())


class TestWuMetadataScraping(unittest.TestCase):
    """
    This class performs a unit test for the wu_metadata_scraping.py dataset by
    testing the number of columns and header in the input dataset matches the
    output dataset.
    """

    def test_num_columns(self):
        """
        Defining the known number of cols, rows we
        should get for check in the unit test.
        """
        num_col = 7
        num_row = 4
        num_colt, num_rowt, headerst = wu_meta.scrape_station_info_test()
        self.assertEqual(num_colt, num_col)
        self.assertEqual(num_rowt, num_row)

    def test_headers(self):
        """
        Test for the correct header on the cleaned set of data
        """
        headers = np.asarray(['id', 'neighborhood', 'city', 'type', 'lat',
                              'lon', 'elevation'])
        num_colt, num_rowt, headerst = wu_meta.scrape_station_info_test()
        self.assertTrue((headerst == headers).all())


class TestMergeDatasets(unittest.TestCase):
    """
    This class performs a unit test for the merge_datasets.py by testing that
    the headers match the expected headers after merging the two datasets
    """

    def test_headers(self):
        """
        Test for the correct header on the merged set of data
        """
        df = axwx.enhance_wsp_with_wu_data(op.join(data_path,
                                                   'station_data.csv'),
                                           op.join(data_path,
                                                   'test_wsp_clean.csv'),
                                           op.join(data_path,
                                                   'test_wu_data'),
                                           radius_mi=2)
        header = df.head(0)
        expected_header = ('DewpointF_last_1hr_avg' and
                           'DewpointF_last_1hr_avg_decrease' and
                           'DewpointF_last_1hr_avg_increase' and
                           'DewpointF_last_1hr_change' and
                           'DewpointF_latest' and
                           'Humidity_last_1hr_avg' and
                           'Humidity_last_1hr_avg_decrease' and
                           'Humidity_last_1hr_avg_increase' and
                           'Humidity_last_1hr_change' and
                           'Humidity_latest' and
                           'PressureIn_last_1hr_avg' and
                           'PressureIn_last_1hr_change' and
                           'PressureIn_latest' and
                           'TemperatureF_last_1hr_avg' and
                           'TemperatureF_last_1hr_avg_decrease' and
                           'TemperatureF_last_1hr_avg_increase' and
                           'TemperatureF_last_1hr_change' and
                           'TemperatureF_latest' and
                           'WindSpeedGustMPH_last_1hr_max' and
                           'WindSpeedGustMPH_latest' and
                           'WindSpeedMPH_last_1hr_avg' and
                           'WindSpeedMPH_latest' and
                           'airbag' and
                           'alcohol_test_given' and
                           'contributing_factor_1' and
                           'contributing_factor_2' and
                           'contributing_factor_3' and
                           'current_weather' and
                           'cyclist_injury' and
                           'cyclist_present' and
                           'date' and
                           'day_of_week' and
                           'driver_injury' and
                           'driver_restraint_type' and
                           'hour' and
                           'lat' and
                           'lighting_conditions' and
                           'lon' and
                           'mean_station_dist_mi' and
                           'month' and
                           'passenger_injury' and
                           'passenger_restraint_type' and
                           'pedestrian_injury' and
                           'pedestrian_present' and
                           'posted_speed_limit' and
                           'roadway_characterization' and
                           'roadway_surface_condition' and
                           'roadway_surface_type' and
                           'sobriety_type' and
                           'station_count' and
                           'time_of_day' and
                           'unique_event_id' and
                           'vehicle_action')
        self.assertTrue(expected_header in header)


if __name__ == '__main__':
    unittest.main(buffer=True)
