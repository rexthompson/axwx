from axwx import wu_metadata_scraping as wumeta
from axwx import wu_observation_scraping as wuobs

# get station IDs from station_data.csv and subset by lat/lon bounds
station_data_csv = "../data/station_data.csv"
lat_range = [47.4, 47.8]
lon_range = [-122.5, -122.2]
all_station_ids_in_box = wumeta.get_station_ids_by_coords(station_data_csv, lat_range, lon_range)

# subset station id list to reduce length of pull
station_ids = all_station_ids_in_box[300:]

print("Attempting to pull data for the following stations:")
print(station_ids)

data_dir = "/Users/Thompson/Desktop/DATA 515/" \
           "Final Project/data/local/wu_station_data/full_period/"

# wuobs.scrape_data_multiple_stations_and_days(station_ids, 20160430, 20170430, data_dir)

# filepath = print(data_dir + "IWAKIRKL2.p")
# print(filepath)

# import pickle
# IWAKIRKL2 = pickle.load(open("/Users/Thompson/Desktop/DATA 515/Final Project/"
#                              "data/local/wu_station_data/full_period/IWAKIRKL2.p", "rb"))
# print(IWAKIRKL2.shape)
