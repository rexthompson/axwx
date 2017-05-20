
"""
Weather Underground PWS Observation Scraping Module

Code to scrape observation datafrom wunderground's PWS network

"""

import csv
import os
import time

import pandas as pd
import pickle
import requests


def scrape_data_one_day(station_id, year, month, day):
    """
    Retrieve PWS data for a single station and a single day
    :param station_id: string
        PWS station ID
    :param year: int
        year
    :param month: int
        month
    :param day: int
        day
    :return: pandas DataFrame with data for requested day

    Sample URL:
    https://www.wunderground.com/weatherstation/WXDailyHistory.asp?
    ID=KWAEDMON15&day=18&month=4&year=2017&graphspan=day&format=1

    """

    url = "https://www.wunderground.com/" \
          "weatherstation/WXDailyHistory.asp?ID=" \
          + station_id + "&day=" \
          + str(day) + "&month=" \
          + str(month) + "&year=" \
          + str(year) \
          + "&graphspan=day&format=1"

    content = requests.get(url).text
    content = content.replace("\n", "")
    content = content.replace("<br>", "\n")
    content = content.replace(",\n", "\n")

    data_csv_lines = csv.reader(content.split('\n'), delimiter=',')
    data_list = list(data_csv_lines)
    data_df = pd.DataFrame.from_records(data_list[1:-1], columns=data_list[0])

    return data_df


def scrape_data_multi_day(station_id, start_date, end_date,
                          delay=3, combined_df=None):
    """
    Retrieve PWS data for a single station over a given date range
    :param station_id: string
        PWS station ID
    :param start_date: int (yyyymmdd)
        start date for data retrieval
    :param end_date: int (yyyymmdd)
        end date for data retrieval
    :param delay: int
        delay between requests to WU server (seconds)
    :return: pandas DataFrame with combined data for period requested
    """

    if combined_df is None:
        combined_df = pd.DataFrame()
    else:
        pass

    # parse out date components
    start_date_str = str(start_date)
    start_date_yyyy = int(start_date_str[0:4])
    start_date_mm = int(start_date_str[4:6])
    start_date_dd = int(start_date_str[6:8])
    end_date_str = str(end_date)
    end_date_yyyy = int(end_date_str[0:4])
    end_date_mm = int(end_date_str[4:6])
    end_date_dd = int(end_date_str[6:8])

    # create date range
    start_date_pd = pd.datetime(start_date_yyyy, start_date_mm, start_date_dd)
    end_date_pd = pd.datetime(end_date_yyyy, end_date_mm, end_date_dd)
    date_list = pd.date_range(start_date_pd, end_date_pd)

    for date in date_list:
        temp_yyyy = date.year
        temp_mm = date.month
        temp_dd = date.day
        print('retrieving data for ' + station_id + " on " +
              str(temp_yyyy) + "-" + str(temp_mm) + "-" + str(temp_dd))
        day_df = scrape_data_one_day(station_id=station_id, year=temp_yyyy,
                                     month=temp_mm, day=temp_dd)
        combined_df = combined_df.append(day_df, ignore_index=True)
        time.sleep(delay)

    return combined_df

# examples to run
# single_day = scrape_data_one_day(station_id="KWAEDMON15",
# year=2016, month=9, day=10)
# multi_day = scrape_data_multi_day("KWAEDMON15", 20170217, 20170219)


def scrape_data_multi_stations_and_days(station_ids, start_date, end_date, data_dir, delay=1):
    """
    Retrieve PWS data for multiple stations over a given date range
    :param station_ids: list
        WU PWS station IDs 
    :param start_date: int (yyyymmdd)
        start date for data retrieval
    :param end_date: int (yyyymmdd)
        end date for data retrieval
    :param data_dir: str
        data directory to which to save pickle files for each station
    :param delay: int
        delay between requests to WU server (seconds)
    :return: None (files saved to given directory)
    """

    orig_dir = os.getcwd()
    os.chdir(data_dir)
    for station in station_ids:
        df = scrape_data_multi_day(station, start_date, end_date, delay)
        filename = station + ".p"
        pickle.dump(df, open(filename, "wb"))
    os.chdir(orig_dir)

station_ids = ['KWASEATT134','KWASEATT166']
data_dir = "/Users/Thompson/Desktop/DATA 515/Final Project/data/local/wu_station_data"
scrape_data_multi_stations_and_days(station_ids, 20160501, 20160503, data_dir)

