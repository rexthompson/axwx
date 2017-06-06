import pandas as pd
import urllib3
from bs4 import BeautifulSoup as BS
import numpy as np
import requests


def scrape_station_info_test(state="WA"):
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

    all_station_info = np.array(['id', 'neighborhood', 'city', 'type', 'lat',
                                 'lon', 'elevation'])

    for i in range(1, 5):  # start at 1 to omit headers
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

        # grab the latitude, longitude, and elevation metadata
        lat, lon, elev = scrape_lat_lon_fly_test(station_id)

        # put all data into an array
        header = [station_id, station_neighborhood, station_city, station_type,
                  lat, lon, elev]
        head_len = len(header)
        all_station_info = np.vstack([all_station_info, header])

        all_station_info = pd.DataFrame(all_station_info)
        all_station_info.columns = all_station_info.ix[0, :]

    # do some dataframe editing
    all_station_info = all_station_info.drop(all_station_info
                                             .index[0]).reset_index()
    all_station_info = all_station_info.drop(all_station_info.columns[0],
                                             axis=1)

    # outputs used for unit tests
    num_cols = all_station_info.shape[1]
    num_rows = all_station_info.shape[0]
    header = all_station_info.columns.values
    return(num_cols, num_rows, header)


def scrape_lat_lon_fly_test(stationID):
    """
    Add latitude, longitude and elevation data to the stationID that is
    inputted as the argument to the function. Boom.
    :param stationID: str
        a unique identifier for the weather underground personal
        weather station
    :return: (latitude,longitude,elevation) as a tuple. Double Boom.
    """
    http = urllib3.PoolManager(maxsize=10, block=True,
                               cert_reqs='CERT_REQUIRED')
    try:
        url = 'https://api.wunderground.com/weatherstation/' \
              'WXDailyHistory.asp?ID={0}&format=XML'.format(stationID)
        r = http.request('GET', url, preload_content=False)
        soup = BS(r, 'xml')

        lat = soup.find_all('latitude')[0].get_text()
        long = soup.find_all('longitude')[0].get_text()
        elev = soup.find_all('elevation')[0].get_text()
        return(lat, long, elev)

    except Exception as err:
        lat = 'NA'
        long = 'NA'
        elev = 'NA'
        return(lat, long, elev)
