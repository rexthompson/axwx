
"""
Weather Underground PWS Metadata Scraping Module

Code to scrape PWS network metadata
"""

import pandas as pd
import urllib3
from bs4 import BeautifulSoup as BS
import numpy as np
import requests
# import time

def scrape_station_info(state="WA"):

    """
    A script to scrape the station information published at the following URL:
    https://www.wunderground.com/weatherstation/ListStations.asp?
    selectedState=WA&selectedCountry=United+States&MR=1
    :param state: US State by which to subset WU Station table
    :return: numpy array with station info
    """
    url = "https://www.wunderground.com/" \
          "weatherstation/ListStations.asp?selectedState=" \
          + state + "&selectedCountry=United+States&MR=1"
    raw_site_content = requests.get(url).content
    soup = BS(raw_site_content, 'html.parser')

    list_stations_info = soup.find_all("tr")

    all_station_info = np.array(['id', 'neighborhood', 'city', 'type', 'lat', 'lon', 'elevation'])

    for i in range(1, len(list_stations_info)):  # start at 1 to omit headers

        station_info = str(list_stations_info[i]).splitlines()

        # pull out station info
        station_id = station_info[1].split('ID=')[1].split('"')[0]
        station_neighborhood = station_info[2].split('<td>')[1]
        station_neighborhood = station_neighborhood.split('\xa0')[0]
        station_city = station_info[3].split('<td>')[1].split('\xa0')[0]
        station_type = station_info[4].split('station-type">')[1]
        station_type = station_type.split('\xa0')[0]

        station_id = station_id.strip()
        station_neighborhood = station_neighborhood.strip()
        station_city = station_city.strip()
        station_type = station_type.strip()

        # TODO: run lat-lon-elev scraper


        # TODO: remove lines below after lat/lon/elevation output by function above
        lat = "temp"
        lon = "temp"
        elevation = "temp"

        all_station_info = np.vstack([all_station_info,
                                      [station_id, station_neighborhood,
                                       station_city, station_type,
                                       lat, lon, elevation]])

    return all_station_info

# all_info = scrape_station_info()
# print(all_info[:,0][0:30])

# TODO: update second function below to accept
# TODO: all_station_info from first function above


def scrape_lat_lon(station_info_csv='./data/station_info-1.csv',
                   new_file_name='./data/latlonstations.csv'):

    """
    Add latitude, longitude and elevation data to csv of station metadata
    :param station_info_csv: str
        filename of csv with station info (i.e. ID, Neighborhood, City, Type)
    :param new_file_name: str
        filename for csv with updated station info (i.e. lat, lon, altitude)
    :return: None (save updated csv to new_file_name)
    """

    station = pd.read_csv(station_info_csv, sep=',', index_col=None,
                          names=['Index', 'StationID', 'Neighborhood',
                                 'City', 'WeatherStation']).ix[2:, 1:]
    station_ids = station.ix[:, 0]
    station_ids = station_ids.reset_index().ix[:, 1]

    http = urllib3.PoolManager(maxsize=10, block=True,
                               cert_reqs='CERT_REQUIRED')

    lat_list = []
    long_list = []
    elev_list = []
    station_list = []

    for i in range(len(station_ids)):
        try:
            url = 'https://api.wunderground.com/weatherstation/' \
                  'WXDailyHistory.asp?ID={0}&format=XML'.format(station_ids[i])
            r = http.request('GET', url, preload_content=False)
            soup = BS(r, 'xml')

            lat = soup.find_all('latitude')[0]
            long = soup.find_all('longitude')[0]
            elev = soup.find_all('elevation')[0]

            lat_list.append(lat.get_text())
            long_list.append(long.get_text())
            elev_list.append(elev.get_text())
            station_list.append(station_ids[i])
            print('Station' + str(i) + 'Lat' + lat.get_text())
            station_df = pd.DataFrame({'StationID': station_list,
                                       'Latitude': lat_list,
                                       'Longitude': long_list,
                                       'Elevation': elev_list})
            station_df.to_csv(new_file_name)

        except Exception as err:
            print(err)
            print('Station is empty.')
            lat_list.append('NA')
            long_list.append('NA')
            elev_list.append('NA')
            station_list.append(station_ids[i])
            station_df = pd.DataFrame({'StationID': station_list,
                                       'Latitude': lat_list,
                                       'Longitude': long_list,
                                       'Elevation': elev_list})
            station_df.to_csv(new_file_name)


def subset_stations_by_coords(station_data_csv, lat_range, lon_range):
    """
    Subset station metadata by latitude and longitude
    :param station_data_csv: str
        filename of csv with station metadata (from scrape_lat_lon)
    :param lat_range: 2-element list
        min and max latitude range, e.g. [47.4, 47.8]
    :param lon_range: 2-element list
        min and max longitude range, e.g. [-122.5, -122.2]
    :return: pandas.DataFrame with station metadata subset by lat/lon bounds
    """

    lat_range.sort()
    lon_range.sort()

    df = pd.read_csv(station_data_csv, index_col=1)
    df = df.dropna(subset=["Latitude", "Longitude"])
    df = df[(df["Latitude"] >= lat_range[0]) &
            (df["Latitude"] <= lat_range[1]) &
            (df["Longitude"] >= lon_range[0]) &
            (df["Longitude"] <= lon_range[1])]

    return df


def get_station_ids_by_coords(station_data_csv, lat_range, lon_range):
    """
    Wrapper around subset_stations_by_coords; returns just the IDs of the stations in a box
    :param station_data_csv: str
        filename of csv with station metadata (from scrape_lat_lon)
    :param lat_range: 2-element list
        min and max latitude range, e.g. [47.4, 47.8]
    :param lon_range: 2-element list
        min and max longitude range, e.g. [-122.5, -122.2]
    :return: list of station IDs (strings)
    """
    df = subset_stations_by_coords(station_data_csv, lat_range, lon_range)
    return list(df.index)

# TESTING
# station_data_csv = "data/station_data.csv"
# lat_range = [47.4, 47.8]
# lon_range = [-122.5, -122.2]

# print(get_station_ids_by_coords(station_data_csv, lat_range, lon_range))
