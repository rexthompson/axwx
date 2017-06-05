from axwx import wu_metadata_scraping as wumeta
from axwx import wu_observation_scraping as wuobs


def get_wu_obs(station_data_csv, startdate, enddate, data_dir, index_start=0,
               index_end=-1, lat_range=[47.4, 47.8],
               lon_range=[-122.5, -122.2]):
    """
    Pull PWS observations from WU
    :param station_data_csv: str
        station data csv filepath
    :param startdate int
        start date for data to retrieve (YYYYMMDD)
    :param enddate int
        end date for data to retrieve (YYYYMMDD)
    :param data_dir str
        data directory for new files
    :param index_start: int
        index start for station list
    :param index_end: int
        index end for station list
    :return: None
    """
    # get station IDs from station_data.csv and subset by lat/lon bounds

    all_station_ids_in_box = wumeta.get_station_ids_by_coords(station_data_csv,
                                                              lat_range,
                                                              lon_range)

    # subset station id list to reduce length of pull
    station_ids = all_station_ids_in_box[index_start:index_end]

    print("Attempting to pull data for the following stations:")
    print(station_ids)

    wuobs.scrape_data_multiple_stations_and_days(station_ids, startdate,
                                                 enddate, data_dir)
