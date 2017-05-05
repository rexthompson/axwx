# placeholder for Weather Underground data scraping script

# Sample URL:
# https://www.wunderground.com/weatherstation/WXDailyHistory.asp?
# ID=KWAEDMON15&day=18&month=4&year=2017&graphspan=day&format=1

import pandas as pd
import requests
import csv
import os

def scrape_data_one_day(station_id, year, month, day):

    """
    Retrieve PWS data for given station and a given day
    :param station_id: string
        PWS station ID
    :param year: int
        year
    :param month: int
        month
    :param day:
        day
    :return: None
    """
    url = "https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID="\
          + station_id + "&day="\
          + str(day) + "&month="\
          + str(month) + "&year="\
          + str(year)\
          + "&graphspan=day&format=1"

    print(url)

    temp_file_name = station_id + "_" + str(year) + \
               str("{0:0>2}".format(month)) + str(day) + '.csv'

    download = requests.get(url).text
    download = download.replace("\n", "")
    download = download.replace("<br>", "\n")

    with open(temp_file_name, 'w') as temp_file:
        temp_file.writelines(download)

    print(temp_file_name)

    # return(download)


def save_wu_data(data_string):
    with open(temp_file_name, 'w') as temp_file:
        temp_file.writelines(data_string)


def scrape_data_multi_day(station_id, start_date, end_date):
    """
    Retrieve PWS data for given station and a given date range
    :param station_id: string
        PWS station ID
    :param startdate: int (yyyymmdd)
        start date for data retrieval
    :param enddate: int (yyyymmdd)
        end date for data retrieval
    :return: 
    """

    start_date = str(start_date)
    start_date_yyyy = int(start_date[0:4])
    start_date_mm = int(start_date[4:6])
    start_date_dd = int(start_date[6:8])

    end_date = str(end_date)
    end_date_yyyy = int(end_date[0:4])
    end_date_mm = int(end_date[4:6])
    end_date_dd = int(end_date[6:8])

    start_date = pd.datetime(start_date_yyyy, start_date_mm, start_date_dd)
    end_date = pd.datetime(end_date_yyyy, end_date_mm, end_date_dd)

    date_list = pd.date_range(start_date, end_date)

    for date in date_list:
        yyyy = date.year
        mm = date.month
        dd = date.day
        scrape_data_one_day(station_id=station_id, year=yyyy, month=mm, day=dd)


# data_string = scrape_data_one_day(station_id="KWAEDMON15", year=2016, month=9, day=10)
scrape_data_multi_day("KWAEDMON15", 20170410, 20170418)

# save_wu_data(data_string)

