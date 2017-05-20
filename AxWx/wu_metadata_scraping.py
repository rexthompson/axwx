
"""
Weather Underground PWS Metadata Scraping Module

Code to scrape PWS network metadata

"""

import pandas as pd
import urllib3
from bs4 import BeautifulSoup as BS
import requests
import time

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

    all_station_info = np.array(['id', 'neighborhood', 'city', 'type'])

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

        all_station_info = np.vstack([all_station_info,
                                      [station_id, station_neighborhood,
                                       station_city, station_type]])

    return all_station_info

# all_info = scrape_station_info()
# print(all_info[:,0][0:30])

# TODO: update second function below to accept all_station_info from first function above

def scrape_lat_lon(station_info_csv='station_info-1.csv', new_file_name='latlonstations.csv'):

    """
    Add latitude, longitude and elevation data to csv of station metadata
    :param station_info_csv: str
        filename of csv with station info (i.e. ID, Neighborhood, City, Type)
    :param new_file_name: str
        filename for csv with updated station info (i.e. lat, lon, altitude)
    :return: None (save updated csv to new_file_name)
    """

    station = pd.read_csv('station_info-1.csv', sep = ',', index_col = None,
                          names=['Index','StationID','Neighborhood','City','WeatherStation']).ix[2:,1:]
    stationIDs = station.ix[:,0]
    stationIDs = stationIDs.reset_index().ix[:,1]

    http = urllib3.PoolManager(maxsize = 10, block = True, cert_reqs = 'CERT_REQUIRED')

    lat_list = []
    long_list = []
    elev_list = []
    station_list = []

    for i in range(len(stationIDs)):
        try:
            url = 'https://api.wunderground.com/weatherstation/WXDailyHistory.asp?ID={0}&format=XML'.format(stationIDs[i])
            r = http.request('GET', url, preload_content=False)
            soup = BS(r, 'xml')

            lat = soup.find_all('latitude')
            long = soup.find_all('longitude')
            elev = soup.find_all('elevation')

            lat_list.append(lat[0].get_text())
            long_list.append(long[0].get_text())
            elev_list.append(elev[0].get_text())
            station_list.append(stationIDs[i])
            print('Station', i,'Lat',lat.get_text())
            station_df = pd.DataFrame({'StationID': station_list, 'Latitude': lat_list, 'Longitude': long_list, 'Elevation': elev_list})
            station_df.to_csv('latlongstations.csv')
        except Exception as err:
            print(err)
            print('Station is empty.')
            lat_list.append('NA')
            long_list.append('NA')
            elev_list.append('NA')
            station_list.append(stationIDs[i])
            station_df = pd.DataFrame({'StationID': station_list,
                               'Latitude': lat_list,
                               'Longitude': long_list,
                               'Elevation': elev_list})
            station_df.to_csv('latlonstations.csv')