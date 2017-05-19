import pandas as pd
import urllib3
from bs4 import BeautifulSoup as BS
import time

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
        station_df.to_csv('latlongstations.csv')
