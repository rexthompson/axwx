"""
Contains all functions used to scrape Weather Underground and clean the data.
Includes the functions used to clean WSP collision data and merge the two data
sets together.
"""


import copy
import csv
import numpy as np
import os
import pandas as pd
import pickle
import requests
import time
import urllib3

from bs4 import BeautifulSoup as BS
from geopy.distance import vincenty
from pyproj import Proj, transform


"""
Weather Underground PWS Metadata Scraping Module

Code to scrape PWS network metadata
"""


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

    all_station_info = np.array(['id', 'neighborhood', 'city', 'type', 'lat',
                                 'lon', 'elevation'])

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

        # grab the latitude, longitude, and elevation metadata
        lat, lon, elev = scrape_lat_lon_fly(station_id)

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
    return(all_station_info.to_csv('./data/station_data_from_FUN.csv'))


def scrape_lat_lon_fly(stationID):
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


def subset_stations_by_coords(station_data, lat_range, lon_range):
    """
    Subset station metadata by latitude and longitude
    :param station_data_csv: str or Pandas.DataFrame
        filename of csv with station metadata (from scrape_lat_lon)
        or
        Pandas.DataFrame with station metadata (from scrape_lat_lon)
    :param lat_range: 2-element list
        min and max latitude range, e.g. [47.4, 47.8]
    :param lon_range: 2-element list
        min and max longitude range, e.g. [-122.5, -122.2]
    :return: pandas.DataFrame with station metadata subset by lat/lon bounds
    """

    lat_range.sort()
    lon_range.sort()

    if isinstance(station_data, str):
        df = pd.read_csv(station_data, index_col=1)
        df = df.dropna(subset=["Latitude", "Longitude"])
    elif isinstance(station_data, pd.DataFrame):
        df = station_data
    else:
        pass
        # TODO: add exception here if type not supported

    df = df[(df["Latitude"] >= lat_range[0]) &
            (df["Latitude"] <= lat_range[1]) &
            (df["Longitude"] >= lon_range[0]) &
            (df["Longitude"] <= lon_range[1])]

    return df


def get_station_ids_by_coords(station_data_csv, lat_range, lon_range):
    """
    Wrapper around subset_stations_by_coords; returns just the IDs of the
    stations in a box
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


"""
Weather Underground PWS Observation Scraping Module

Code to scrape observation data from wunderground's PWS network
"""


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


def scrape_data_multiple_day(station_id, start_date, end_date,
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
    :param combined_df: pandas.DataFrame
        DataFrame to which to append new observations
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


def scrape_data_multiple_stations_and_days(station_ids, start_date,
                                           end_date, data_dir, delay=1):
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
        df = scrape_data_multiple_day(station, start_date, end_date, delay)
        filename = station + ".p"
        pickle.dump(df, open(filename, "wb"))
    os.chdir(orig_dir)


"""
Function that wraps the station IDs and scraping into a single call
"""


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


"""
Functions to clean WU PWS observation data
"""


def clean_obs_data(df):
    """
    Cleans WU PWS data for a single station. Replaces bad values (above/below
    thresholds) with NaN's.
    :param df: pandas.DataFrame
        raw data
    :return: cleaned pandas.DataFrame
    """

    df_clean = copy.deepcopy(df)

    # convert strings to numeric where possible
    for col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')

    ignore = ["Time", "WindDirection", "SoftwareType", "Conditions", "Clouds",
              "DateUTC"]

    # low/high limits
    for col in df_clean.columns:
        if col == "TemperatureF":
            df_clean.loc[df_clean[col] <= 10, col] = np.nan
            df_clean.loc[df_clean[col] >= 125, col] = np.nan
        elif col == "DewpointF":
            df_clean.loc[df_clean[col] == -99.9, col] = np.nan
            df_clean.loc[df_clean[col] >= 80, col] = np.nan
            # df_clean.loc[df_clean[col] >= df_clean["TemperatureF"], col] =
            #     np.nan
        elif col == "PressureIn":
            df_clean.loc[df_clean[col] <= 25, col] = np.nan
            df_clean.loc[df_clean[col] >= 31.5, col] = np.nan
        elif col == "WindDirectionDegrees":
            df_clean.loc[df_clean[col] < 0, col] = np.nan
            df_clean.loc[df_clean[col] > 360, col] = np.nan
        elif col == "Humidity":
            df_clean.loc[df_clean[col] <= 0, col] = np.nan
            df_clean.loc[df_clean[col] > 100, col] = np.nan
        elif col not in ignore:
            df_clean.loc[df_clean[col] < 0, col] = np.nan

    # TODO: add checks for outliers based on variance of surrounding data
    # TODO: add checks for frozen values

    return df_clean


def enhance_wu_data(df):
    """
    Enhance WU PWS data for a single station. Currently just adds cumulative
    precipitation.
    :param df: pandas.DataFrame
        cleaned data
    :return: enhanced pandas.DataFrame
    """

    # add cumulative precip data
    cum_precip_in = np.diff(df.dailyrainin)
    cum_precip_in = np.append(0, np.nancumsum(np.maximum(0, cum_precip_in)))

    df["cum_rain_in"] = cum_precip_in

    # TODO: Add code to convert wind speed/direction into vector for
    # directional averaging?

    return df


def clean_and_enhance_wu_data(raw_data_dir, cleaned_data_dir):
    """
    Clean and enhance raw WU data files (saved as Pickle files)
    :param raw_data_dir: str
        data directory where raw WU data binary files are stored
    :param cleaned_data_dir: str
        location to save cleaned WU data binary files
    :return: None
    """
    os.chdir(raw_data_dir)
    file_list = os.listdir()
    for file in file_list:
        try:
            df = pickle.load(open(file, "rb"))
            df = clean_obs_data(df)
            df = enhance_wu_data(df)
            filename_split = file.split(".")
            if len(filename_split) == 1:
                new_filename = filename_split + "_cleaned"
            else:
                new_filename = ''.join(filename_split[:-1]) + "_cleaned." + \
                               filename_split[-1]
            pickle.dump(df, open(cleaned_data_dir + "/" + new_filename, "wb"))
        except:
            print("*** skipped " + file + " ***")
            pass


"""
WSP Cleaning:
Takes a csv file from WSP's collision analysis tool and returns a new csv file
in a format that can be merged with Weather Underground data, ultimately being
used in a visualization tool
"""


def convert_stateplane_to_latlon(state_x, state_y, proj_in=2286,
                                 proj_out=4326):
    """
    This funtion takes the state plane coordinates used by the state patrol
    and converts them to latitudes and longitudes to be plotted on a map

    :param state_x: float
        x state plane coordinate (corresponding with longitude)
    :param state_y: float
        y state plane coordinate (corresponding with latitude)
    :proj_in: int
        value to convert state plane coordinate to lat/lon
    :proj_out: int
        value to convert state plane coordinate to lat/lon
    """
    inProj = Proj(init='epsg:' + str(proj_in), preserve_units=True)
    outProj = Proj(init='epsg:' + str(proj_out))
    lon, lat = transform(inProj, outProj, state_x, state_y)
    return lat, lon


def column_conversion(input_data, old_column, dictionary, record):
    """
    Converts values in columns to descriptions using dictionaries provided by
    WSP collision analysis tool

    :param input_data: dataframe
        the dataframe to be read and have column changed
    :param old_column: string
        reads old column value
    :param dictionary: dictionary
        reads the appropriate dictionary to assign new value
    :param record: int (loop parameter)
        the record number being changed (processed in loop)
    """
    if not np.isnan(input_data[old_column][record]):
        new_value = dictionary[input_data[old_column][record]]
        return new_value
    else:
        pass


def clean_wsp_collision_data(input_csv_filepath):
    """
    Takes raw input csv downloaded from WSP's collision analysis tool and
    converts it into a cleaned dataframe

    :param input csv: string
        filepath location of file to be cleaned
    """
    # read in raw data from WSP's collision analysis tool
    print('\nreading csv file...')
    df = pd.read_csv(input_csv_filepath, sep=',', low_memory=False)

    # drop any collision records with no state plane coordinates
    print('dropping records with no state plane coordinates...')
    df = df.drop(df[np.isnan(df.Colli_Dtl_Info_State_Plane_X)].index)
    df = df.drop(df[np.isnan(df.Colli_Dtl_Info_State_Plane_Y)].index)
    df = df.reset_index(drop=True)

    # convert state plane coordinates to latitudes and longitudes
    print('converting state plane coordinates/'
          'dropping records not in range...')
    x = np.array(df.Colli_Dtl_Info_State_Plane_X)
    y = np.array(df.Colli_Dtl_Info_State_Plane_Y)
    x_new, y_new = convert_stateplane_to_latlon(x, y)
    df = df.rename(columns={'Colli_Dtl_Info_State_Plane_X': 'lat',
                            'Colli_Dtl_Info_State_Plane_Y': 'lon'})
    df['lat'] = pd.DataFrame(x_new)
    df['lon'] = pd.DataFrame(y_new)

    # drop any collision records not within coordinate grid over Seattle area
    df = df.drop(df[df.lat > 47.8].index)
    df = df.drop(df[df.lat < 47.4].index)
    df = df.drop(df[df.lon > -122.2].index)
    df = df.drop(df[df.lon < -122.5].index)
    df = df.reset_index(drop=True)

    # split date/time and add as separate columns
    dates = pd.DatetimeIndex(df['Colli_Dtl_Info_Colli_Date'])
    df['date'] = dates.date
    df['time_of_day'] = dates.time
    df['month'] = dates.month
    df['day_of_week'] = dates.dayofweek
    df['hour'] = dates.hour

    # keep columns of interest
    print('removing columns not of interest...')
    df = df[['lat',
             'lon',
             'date',
             'time_of_day',
             'month',
             'day_of_week',
             'hour',
             'MV_Drvr_Restr_Sys_Typ_Cd',
             'MV_Pasngr_Restr_Sys_Typ_Cd',
             'Colli_Dtl_Info_Rdwy_Surfc_Cond_Typ_Cd',
             'Colli_Dtl_Info_Rdwy_Char_Typ_Cd',
             'Colli_Dtl_Info_Wea_Typ_Cd',
             'Colli_Dtl_Info_Litng_Cond_Typ_Cd',
             'MV_Drvr_Sobr_Typ_Cd',
             'Colli_Unit_Rdwy_Surfc_Typ_Cd',
             'Colli_Unit_Postd_Speed',
             'Ped_Colli_Surr_Key',
             'Pedcyc_Drvr_Colli_Surr_Key',
             'MV_Drvr_Injur_Typ_Cd',
             'MV_Pasngr_Injur_Typ_Cd',
             'Ped_Injur_Typ_Cd',
             'Pedcyc_Drvr_Injur_Typ_Cd',
             'MV_Unit_Veh_Actn_Typ_Cd_1',
             'MV_Drvr_Ctrb_Circums_Typ_Cd_1',
             'MV_Drvr_Ctrb_Circums_Typ_Cd_2',
             'MV_Drvr_Ctrb_Circums_Typ_Cd_3',
             'MV_Drvr_Alch_Test_Cd',
             'MV_Drvr_Air_Bag_Typ_Cd']]

    # rename columns to more interpretable names
    print('renaming columns...')
    df = df.rename(columns={
        'MV_Drvr_Restr_Sys_Typ_Cd': 'driver_restraint_type',
        'MV_Pasngr_Restr_Sys_Typ_Cd': 'passenger_restraint_type',
        'Colli_Dtl_Info_Rdwy_Surfc_Cond_Typ_Cd': 'roadway_surface_condition',
        'Colli_Dtl_Info_Rdwy_Char_Typ_Cd': 'roadway_characterization',
        'Colli_Dtl_Info_Wea_Typ_Cd': 'current_weather',
        'Colli_Dtl_Info_Litng_Cond_Typ_Cd': 'lighting_conditions',
        'MV_Drvr_Sobr_Typ_Cd': 'sobriety_type',
        'Colli_Unit_Rdwy_Surfc_Typ_Cd': 'roadway_surface_type',
        'Colli_Unit_Postd_Speed': 'posted_speed_limit',
        'Ped_Colli_Surr_Key': 'pedestrian_present',
        'Pedcyc_Drvr_Colli_Surr_Key': 'cyclist_present',
        'MV_Drvr_Injur_Typ_Cd': 'driver_injury',
        'MV_Pasngr_Injur_Typ_Cd': 'passenger_injury',
        'Ped_Injur_Typ_Cd': 'pedestrian_injury',
        'Pedcyc_Drvr_Injur_Typ_Cd': 'cyclist_injury',
        'MV_Unit_Veh_Actn_Typ_Cd_1': 'vehicle_action',
        'MV_Drvr_Ctrb_Circums_Typ_Cd_1': 'contributing_factor_1',
        'MV_Drvr_Ctrb_Circums_Typ_Cd_2': 'contributing_factor_2',
        'MV_Drvr_Ctrb_Circums_Typ_Cd_3': 'contributing_factor_3',
        'MV_Drvr_Alch_Test_Cd': 'alcohol_test_given',
        'MV_Drvr_Air_Bag_Typ_Cd': 'airbag'})

    # create dictionaries:
    print('creating dictionaries for new value assignments...')
    restraint_type_dict = {
        1: 'No Restraints Used',
        2: 'Lap Belt Used',
        3: 'Shoulder Belt Used',
        4: 'Lap & Shoulder Used',
        5: 'Child Infant Seat Used',
        6: 'Child Convertable Seat Used',
        7: 'Child Built-in Seat Used',
        8: 'Child Booster Seat Used',
        9: 'Unknown'}

    roadway_surface_condition_dict = {
        1: 'Dry',
        2: 'Wet',
        3: 'Snow/Slush',
        4: 'Ice',
        5: 'Sand/Mud/Dirt',
        6: 'Oil',
        7: 'Standing Water',
        8: 'Other',
        9: 'Unknown'}

    roadway_characterization_dict = {
        1: 'Straight & Level',
        2: 'Straight & Grade',
        3: 'Straight & Hillcrest',
        4: 'Straight in Sag',
        5: 'Curve & Level',
        6: 'Curve & Grade',
        7: 'Curve & Hillcrest',
        8: 'Curve in Sag',
        9: 'Unknown'}

    current_weather_dict = {
        0: 'Unknown',
        1: 'Clear or Partly Cloudy',
        2: 'Overcast',
        3: 'Raining',
        4: 'Snowing',
        5: 'Fog or Smog or Smoke',
        6: 'Sleet or Hail or Freezing Rain',
        7: 'Severe Crosswind',
        8: 'Blowing Sand or Dirt or Snow',
        9: 'Other'}

    lighting_conditions_dict = {
        1: 'Daylight',
        2: 'Dawn',
        3: 'Dusk',
        4: 'Dark-Street Lights On',
        5: 'Dark-Street Lights Off',
        6: 'Dark-No Street Lights',
        7: 'Other',
        9: 'Unknown'}

    sobriety_type_dict = {
        1: 'HBD - Ability Impaired',
        2: 'HBD - Ability Not Impaired',
        3: 'HBD - Sobriety Unknown',
        4: 'Had NOT Been Drinking',
        5: 'HBD - Ability Impaired (tox test)',
        6: 'HBD - Ability Not Impaired (tox test)',
        7: 'Had NOT Been Drinking (tox test)',
        9: 'Unknown'}

    roadway_surface_type_dict = {
        1: 'Concrete',
        2: 'Blacktop',
        3: 'Brick or Wood Block',
        4: 'Gravel',
        5: 'Dirt',
        6: 'Other',
        9: 'Unknown'}

    injury_dict = {
        0: 'Unknown',
        1: 'No Injury',
        2: 'Dead at Scene',
        3: 'Dead on Arrival',
        4: 'Died at Hospital',
        5: 'Serious Injury',
        6: 'Evident Injury',
        7: 'Possible Injury',
        8: 'Non-Traffic Injury',
        9: 'Non-Traffic Fatality'}

    vehicle_action_dict = {
        1: 'Going Straight Ahead',
        2: 'Overtaking and Passing',
        3: 'Making Right Turn',
        4: 'Making Left Turn',
        5: 'Making U-Turn',
        6: 'Slowing',
        7: 'Stopped for Traffic',
        8: 'Stopped at Signal or Stop Sign',
        9: 'Stopped in Roadway',
        10: 'Starting in Traffic Lane',
        11: 'Starting From Parked Position',
        12: 'Merging (Entering Traffic)',
        13: 'Legally Parked, Occupied',
        14: 'Legally Parked, Unoccupied',
        15: 'Backing',
        16: 'Going Wrong Way on Divided Hwy',
        17: 'Going Wrong Way on Ramp',
        18: 'Going Wrong Way on One-Way Street or Road',
        19: 'Other',
        20: 'Changing Lanes',
        21: 'Illegally Parked, Occupied',
        22: 'Illegally Parked, Unoccupied'}

    contributing_factor_dict = {
        1: 'Under Influence of Alcohol',
        2: 'Under Influence of Drugs',
        3: 'Exceeding Stated Speed Limit',
        4: 'Exceeding Reas. Safe Speed',
        5: 'Did Not Grant RW to Vehicle',
        6: 'Improper Passing',
        7: 'Follow Too Closely',
        8: 'Over Center Line',
        9: 'Failing to Signal',
        10: 'Improper Turn',
        11: 'Disregard Stop and Go Light',
        12: 'Disregard Stop Sign - Flashing Red',
        13: 'Disregard Yield Sign - Flashing Yellow',
        14: 'Apparently Asleep',
        15: 'Improper Parking Location',
        16: 'Operating Defective Equipment',
        17: 'Other',
        18: 'None',
        19: 'Improper Signal',
        20: 'Improper U-Turn',
        21: 'Headlight Violation',
        22: 'Fail to Yield Row to Pedestrian',
        23: 'Inattention',
        24: 'Improper Backing',
        30: 'Disregard Flagger - Officer',
        31: 'Apparently Ill',
        32: 'Apparently Fatigued',
        33: 'Had Taken Medication',
        34: 'On Wrong Side Of Road',
        35: 'Hitchhiking',
        36: 'Failure to Use Xwalk',
        40: 'Driver Operating Handheld Telecommunications Device',
        41: 'Driver Operating Hands-free Wireless Telecommunications Device',
        42: ('Driver Operating Other Electronic Devices '
             '(computers, navigational, etc.)'),
        43: 'Driver Adjusting Audio or Entertainment System',
        44: 'Driver Smoking',
        45: 'Driver Eating or Drinking',
        46: 'Driver Reading or Writing',
        47: 'Driver Grooming',
        48: ('Driver Interacting with Passengers, Animals or '
             'Objects Inside Vehicle'),
        49: 'Other Driver Distractions Inside Vehicle',
        50: 'Driver Distractions Outside Vehicle',
        51: 'Unknown Driver Distraction',
        52: 'Driver Not Distracted'}

    alcohol_test_dict = {
        97: 'Test Given - Results Pending',
        98: 'Test Given - No Results',
        99: 'Test Refused'}

    airbag_dict = {
        1: 'Not Airbag Equipped',
        2: 'Not Deployed',
        3: 'Front Airbag Deployed',
        4: 'Side Airbag Deployed',
        5: 'Other Airbag Deployed',
        6: 'Combination of Airbag Deployed',
        9: 'Unknown'}

    # initialize lists that will contain updated column values
    driver_restraint_type = []
    passenger_restraint_type = []
    roadway_surface_condition = []
    roadway_characterization = []
    current_weather = []
    lighting_conditions = []
    sobriety_type = []
    roadway_surface_type = []
    driver_injury = []
    passenger_injury = []
    pedestrian_injury = []
    cyclist_injury = []
    vehicle_action = []
    contributing_factor_1 = []
    contributing_factor_2 = []
    contributing_factor_3 = []
    alcohol_test_given = []
    airbag = []

    # loop through each record and change the corresponding column codes
    print('reading through records and updating column values...')
    for i in range(df.shape[0]):
        driver_restraint_type.append(column_conversion(
            df, 'driver_restraint_type', restraint_type_dict, i))
        passenger_restraint_type.append(column_conversion(
            df, 'passenger_restraint_type', restraint_type_dict, i))
        roadway_surface_condition.append(column_conversion(
            df, 'roadway_surface_condition', roadway_surface_condition_dict,
            i))
        roadway_characterization.append(column_conversion(
            df, 'roadway_characterization', roadway_characterization_dict, i))
        current_weather.append(column_conversion(
            df, 'current_weather', current_weather_dict, i))
        lighting_conditions.append(column_conversion(
            df, 'lighting_conditions', lighting_conditions_dict, i))
        sobriety_type.append(column_conversion(
            df, 'sobriety_type', sobriety_type_dict, i))
        roadway_surface_type.append(column_conversion(
            df, 'roadway_surface_type', roadway_surface_type_dict, i))
        driver_injury.append(column_conversion(
            df, 'driver_injury', injury_dict, i))
        passenger_injury.append(column_conversion(
            df, 'passenger_injury', injury_dict, i))
        pedestrian_injury.append(column_conversion(
            df, 'pedestrian_injury', injury_dict, i))
        cyclist_injury.append(column_conversion(
            df, 'cyclist_injury', injury_dict, i))
        vehicle_action.append(column_conversion(
            df, 'vehicle_action', vehicle_action_dict, i))
        contributing_factor_1.append(column_conversion(
            df, 'contributing_factor_1', contributing_factor_dict, i))
        contributing_factor_2.append(column_conversion(
            df, 'contributing_factor_2', contributing_factor_dict, i))
        contributing_factor_3.append(column_conversion(
            df, 'contributing_factor_3', contributing_factor_dict, i))
        alcohol_test_given.append(column_conversion(
            df, 'alcohol_test_given', alcohol_test_dict, i))
        airbag.append(column_conversion(
            df, 'airbag', airbag_dict, i))

    # change column values in file from codes to written descriptions
    df['driver_restraint_type'] = driver_restraint_type
    df['passenger_restraint_type'] = passenger_restraint_type
    df['roadway_surface_condition'] = roadway_surface_condition
    df['roadway_characterization'] = roadway_characterization
    df['current_weather'] = current_weather
    df['lighting_conditions'] = lighting_conditions
    df['sobriety_type'] = sobriety_type
    df['roadway_surface_type'] = roadway_surface_type
    df['driver_injury'] = driver_injury
    df['passenger_injury'] = passenger_injury
    df['pedestrian_injury'] = pedestrian_injury
    df['cyclist_injury'] = cyclist_injury
    df['vehicle_action'] = vehicle_action
    df['contributing_factor_1'] = contributing_factor_1
    df['contributing_factor_2'] = contributing_factor_2
    df['contributing_factor_3'] = contributing_factor_3
    df['alcohol_test_given'] = alcohol_test_given
    df['airbag'] = airbag

    # return cleaned dataframe
    print('data cleaned!')
    return df


def export_file(input_csv_filepath, cleaned_csv_filepath):
    """
    Prints cleaned csv that is ready to be merged with Weather
    Underground's data

    :param input_csv_filepath: string
        filepath location of file to be cleaned
    :param cleaned_filename: string
        cleaned output filename
    """
    df = clean_wsp_collision_data(input_csv_filepath)
    df.to_csv(cleaned_csv_filepath, sep=',')
    print('cleaned csv file exported!')


"""
Functions to combine Washington State Patrol and Weather Underground datasets
into single enhanced DF
"""


def get_bounding_box(coords, dist_mi):
    """
    Calculate lat/lon bounding box for distance from reference location
    :param coords: 2-tuple
        (latitude, longitude) pair for reference location
    :param dist_mi: numeric
        length of shortest distance of bounding box, in miles
    :return: lists of bounding box coordinate limits for latitude and longitude
    """
    lon_dist_mi = (dist_mi * 1 /
                   vincenty(coords, (coords[0], coords[1] + 1)).miles)
    lat_dist_mi = (dist_mi * 1 /
                   vincenty(coords, (coords[0] + 1, coords[1])).miles)

    lat_bounds_deg = [coords[0] - lat_dist_mi, coords[0] + lat_dist_mi]
    lon_bounds_deg = [coords[1] - lon_dist_mi, coords[1] + lon_dist_mi]

    return lat_bounds_deg, lon_bounds_deg


def enhance_wsp_with_wu_data(wu_metadata_full_filepath,
                             wsp_data_full_filepath,
                             wu_obs_filepath, radius_mi,
                             lat_range=[47.4, 47.8],
                             lon_range=[-122.5, -122.2]):
    """
    Add columns with WU data to WSP DataFrame
    :param wu_metadata_full_filepath: string
        full filepath for wu_station_list (csv file)
    :param wsp_data_full_filepath: string
        full filepath for wsp data (csv file)
    :param wu_obs_filepath: string
        filepath for directory containing WU observation data
    :param radius_mi: int
        radius (miles) for WU station use
    :param lat_range: 2-element list
        min and max latitude range, e.g. [47.4, 47.8]
    :param lon_range: 2-element list
        min and max longitude range, e.g. [-122.5, -122.2]
    :return:
    """
    station_df = subset_stations_by_coords(wu_metadata_full_filepath,
                                           lat_range, lon_range)
    wsp_df = pd.read_csv(wsp_data_full_filepath, index_col="Unnamed: 0")
    os.chdir(wu_obs_filepath)

    collision_count = wsp_df.shape[0]

    wsp_df_new = pd.DataFrame()
    unique_event_id = 1

    # # TEMP FOR TESTING
    # collision_count = 2500

    for collision_row_id in range(collision_count):

        print("-------- processing row #" + str(collision_row_id + 1) +
              " of " + str(collision_count) + " --------")

        # get collision info
        collision_coords = (wsp_df["lat"].iloc[collision_row_id],
                            wsp_df["lon"].iloc[collision_row_id])
        collision_date = wsp_df["date"].iloc[collision_row_id]
        collision_time = wsp_df["time_of_day"].iloc[collision_row_id]
        collision_datetime = np.datetime64(collision_date + " " +
                                           collision_time)
        collision_datetime_minus_15_mins = (collision_datetime -
                                            np.timedelta64(15, 'm'))
        collision_datetime_minus_60_mins = (collision_datetime -
                                            np.timedelta64(60, 'm'))
        collision_datetime_minus_24hrs = (collision_datetime -
                                          np.timedelta64(24, 'h'))

        # autopopulate wx info if duplicate collision record
        # (i.e. same lat/lon/date/time)
        if collision_row_id > 0:
            dup_record = True
            dup_record = dup_record & (collision_time == wsp_df_new
                                       ["time_of_day"][collision_row_id - 1])
            dup_record = dup_record & (collision_date == wsp_df_new
                                       ["date"][collision_row_id - 1])
            dup_record = dup_record & (collision_coords[0] == wsp_df_new
                                       ["lat"][collision_row_id - 1])
            dup_record = dup_record & (collision_coords[1] == wsp_df_new
                                       ["lon"][collision_row_id - 1])
            if dup_record:
                # print("duplicate event")
                temp_df_dict = dict(wsp_df.iloc[collision_row_id])
                temp_df_dict.update(grouped_station_dict)
                wsp_df_new = wsp_df_new.append(temp_df_dict,
                                               ignore_index=True)
                continue
            else:
                unique_event_id += 1
                pass
        else:
            pass

        # subset station DF by lat/lon bbox (to reduce # of distance
        # calculations later)
        station_df_temp = copy.deepcopy(station_df)
        bbox = get_bounding_box(collision_coords, radius_mi)
        station_df_temp = subset_stations_by_coords(station_df, bbox[0],
                                                    bbox[1])

        # initialize new DF for combined station info
        stations = pd.DataFrame()

        station_data_dict = dict()

        # loop through stations
        for station_row_id in range(station_df_temp.shape[0]):

            # get station info and distance from collision
            station_id = station_df_temp.index[station_row_id]
            station_coords = (station_df_temp["Latitude"]
                              .iloc[station_row_id],
                              station_df_temp["Longitude"]
                              .iloc[station_row_id])
            station_dist_mi = vincenty(collision_coords, station_coords).miles

            # proceed if station within max radius
            if station_dist_mi <= radius_mi:

                # load wx obs for single station (if not already in data
                # dictionary)
                if station_id not in station_data_dict.keys():
                    station_data_dict[station_id] =
                    pickle.load(open(station_id + "_cleaned.p", "rb"))
                else:
                    pass
                wu_station_data = station_data_dict[station_id]

                # subset wx obs to pre-collision only
                wu_station_datetime = pd.DatetimeIndex(wu_station_data
                                                       ["Time"])
                wu_station_data = (wu_station_data[wu_station_datetime <=
                                                   collision_datetime])
                wu_station_datetime = (wu_station_datetime
                                       [wu_station_datetime <=
                                        collision_datetime])

                # latest readings (up to 15 minutes prior to collision)
                wu_station_data_latest = (wu_station_data
                                          [wu_station_datetime >=
                                           collision_datetime_minus_15_mins])
                if wu_station_data_latest.shape[0] > 0:
                    TemperatureF_latest = (wu_station_data_latest
                                           ["TemperatureF"].iloc[-1])
                    DewpointF_latest = (wu_station_data_latest
                                        ["DewpointF"].iloc[-1])
                    PressureIn_latest = (wu_station_data_latest
                                         ["PressureIn"].iloc[-1])
                    WindDirection_latest = (wu_station_data_latest
                                            ["WindDirection"].iloc[-1])
                    WindDirectionDegrees_latest = (wu_station_data_latest
                                                   ["WindDirectionDegrees"]
                                                   .iloc[-1])
                    WindSpeedMPH_latest = (wu_station_data_latest
                                           ["WindSpeedMPH"].iloc[-1])
                    WindSpeedGustMPH_latest = (wu_station_data_latest
                                               ["WindSpeedGustMPH"].iloc[-1])
                    Humidity_latest = (wu_station_data_latest
                                       ["Humidity"].iloc[-1])
                    HourlyPrecipIn_latest = (wu_station_data_latest
                                             ["HourlyPrecipIn"].iloc[-1])
                    # TODO: ADD WIND DIRECTION
                else:
                    TemperatureF_latest = np.nan
                    DewpointF_latest = np.nan
                    PressureIn_latest = np.nan
                    WindDirection_latest = np.nan
                    WindDirectionDegrees_latest = np.nan
                    WindSpeedMPH_latest = np.nan
                    WindSpeedGustMPH_latest = np.nan
                    Humidity_latest = np.nan
                    HourlyPrecipIn_latest = np.nan
                    # TODO: ADD WIND DIRECTION

                # last 1 hr summary (note that not all parameters are
                # averaged)
                wu_station_data_last_hr = (wu_station_data
                                           [wu_station_datetime >=
                                            collision_datetime_minus_60_mins])
                nrow_last_1hr = wu_station_data_last_hr.shape[0]
                if nrow_last_1hr > 0:
                    TemperatureF_last_1hr_avg = np.round(np.mean(
                        wu_station_data_last_hr["TemperatureF"]), 1)
                    DewpointF_last_1hr_avg = np.round(np.mean(
                        wu_station_data_last_hr["DewpointF"]), 1)
                    PressureIn_last_1hr_avg = np.round(np.mean(
                        wu_station_data_last_hr["PressureIn"]), 2)
                    WindSpeedMPH_last_1hr_avg = np.round(np.mean(
                        wu_station_data_last_hr["WindSpeedMPH"]), 1)
                    WindSpeedGustMPH_last_1hr_max = np.round(np.max(
                        wu_station_data_last_hr["WindSpeedGustMPH"]), 1)
                    Humidity_last_1hr_avg = np.round(np.mean(
                        wu_station_data_last_hr["Humidity"]), 1)
                    # TODO: ADD PRECIP RATE
                    # TODO: ADD WIND DIRECTION
                else:
                    TemperatureF_last_1hr_avg = np.nan
                    DewpointF_last_1hr_avg = np.nan
                    PressureIn_last_1hr_avg = np.nan
                    WindSpeedMPH_last_1hr_avg = np.nan
                    WindSpeedGustMPH_last_1hr_max = np.nan
                    Humidity_last_1hr_avg = np.nan
                    # TODO: ADD PRECIP RATE
                    # TODO: ADD WIND DIRECTION

                # determine whether to calculate 1 hr changes
                if nrow_last_1hr > 0:
                    # get time delta in last hr to ensure good spread of data
                    # across last hr
                    wu_station_datetime_last_1hr = pd.DatetimeIndex(
                        wu_station_data_last_hr["DateUTC"])
                    last_1hr_time_delta = (wu_station_datetime_last_1hr[-1] -
                                           wu_station_datetime_last_1hr[0])
                    if last_1hr_time_delta > np.timedelta64(45, "m"):
                        last_1hr_time_delta_hrs = (last_1hr_time_delta
                                                   .seconds / 3600)
                        do_last_1hr_calcs = True
                    else:
                        do_last_1hr_calcs = False
                else:
                    do_last_1hr_calcs = False

                # last 1 hr changes
                if do_last_1hr_calcs:
                    # net change beginning to end
                    TemperatureF_last_1hr_change = (wu_station_data_last_hr
                                                    ["TemperatureF"]
                                                    .iloc[-1] -
                                                    wu_station_data_last_hr
                                                    ["TemperatureF"].iloc[0])
                    DewpointF_last_1hr_change = (wu_station_data_last_hr
                                                 ["DewpointF"].iloc[-1] -
                                                 wu_station_data_last_hr
                                                 ["DewpointF"].iloc[0])
                    PressureIn_last_1hr_change = (wu_station_data_last_hr
                                                  ["PressureIn"].iloc[-1] -
                                                  wu_station_data_last_hr
                                                  ["PressureIn"].iloc[0])
                    Humidity_last_1hr_change = (wu_station_data_last_hr
                                                ["Humidity"].iloc[-1] -
                                                wu_station_data_last_hr
                                                ["Humidity"].iloc[0])
                    # Avg net increase and decrease beginning to end
                    if nrow_last_1hr > 1:
                        TempF_diff = np.diff(wu_station_data_last_hr
                                             ["TemperatureF"])
                        TemperatureF_last_1hr_avg_increase = -1 * np.round(
                            np.sum(np.minimum(TempF_diff, 0)) /
                            (nrow_last_1hr - 1), 1)
                        TemperatureF_last_1hr_avg_decrease = np.round(
                            np.sum(np.maximum(TempF_diff, 0)) /
                            (nrow_last_1hr - 1), 1)
                        DpF_diff = np.diff(wu_station_data_last_hr
                                           ["DewpointF"])
                        DewpointF_last_1hr_avg_increase = -1 * np.round(
                            np.sum(np.minimum(DpF_diff, 0)) /
                            (nrow_last_1hr - 1), 1)
                        DewpointF_last_1hr_avg_decrease = np.round(
                            np.sum(np.maximum(DpF_diff, 0)) /
                            (nrow_last_1hr - 1), 1)
                        RH_diff = np.diff(wu_station_data_last_hr["Humidity"])
                        Humidity_last_1hr_avg_increase = -1 * np.round(
                            np.sum(np.minimum(RH_diff, 0)) /
                            (nrow_last_1hr - 1), 1)
                        Humidity_last_1hr_avg_decrease = np.round(
                            np.sum(np.maximum(RH_diff, 0)) /
                            (nrow_last_1hr - 1), 1)
                        PrecipRate_inhr_last_1hr = ((wu_station_data_last_hr
                                                     ["cum_rain_in"]
                                                     .iloc[-1] -
                                                     wu_station_data_last_hr
                                                     ["cum_rain_in"]
                                                     .iloc[0]) /
                                                    last_1hr_time_delta_hrs)
                        # TODO: ADD WIND DIRECTION
                else:
                    TemperatureF_last_1hr_change = np.nan
                    DewpointF_last_1hr_change = np.nan
                    PressureIn_last_1hr_change = np.nan
                    Humidity_last_1hr_change = np.nan
                    TemperatureF_last_1hr_avg_increase = np.nan
                    TemperatureF_last_1hr_avg_decrease = np.nan
                    DewpointF_last_1hr_avg_increase = np.nan
                    DewpointF_last_1hr_avg_decrease = np.nan
                    Humidity_last_1hr_avg_increase = np.nan
                    Humidity_last_1hr_avg_decrease = np.nan
                    PrecipRate_inhr_last_1hr = np.nan
                    # TODO: ADD WIND DIRECTION

                # save data in dataframe
                stations = stations.append({
                    "wx_station_id":
                    station_id,
                    "wx_station_dist_mi":
                    station_dist_mi,
                    "wx_TemperatureF_latest":
                    TemperatureF_latest,
                    "wx_TemperatureF_last_1hr_avg":
                    TemperatureF_last_1hr_avg,
                    "wx_TemperatureF_last_1hr_change":
                    TemperatureF_last_1hr_change,
                    "wx_TemperatureF_last_1hr_avg_increase":
                    TemperatureF_last_1hr_avg_increase,
                    "wx_TemperatureF_last_1hr_avg_decrease":
                    TemperatureF_last_1hr_avg_decrease,
                    "wx_DewpointF_latest":
                    DewpointF_latest,
                    "wx_DewpointF_last_1hr_avg":
                    DewpointF_last_1hr_avg,
                    "wx_DewpointF_last_1hr_change":
                    DewpointF_last_1hr_change,
                    "wx_DewpointF_last_1hr_avg_increase":
                    DewpointF_last_1hr_avg_increase,
                    "wx_DewpointF_last_1hr_avg_decrease":
                    DewpointF_last_1hr_avg_decrease,
                    "wx_PressureIn_latest":
                    PressureIn_latest,
                    "wx_PressureIn_last_1hr_avg":
                    PressureIn_last_1hr_avg,
                    "wx_PressureIn_last_1hr_change":
                    PressureIn_last_1hr_change,
                    "wx_WindSpeedMPH_latest":
                    WindSpeedMPH_latest,
                    "wx_WindSpeedMPH_last_1hr_avg":
                    WindSpeedMPH_last_1hr_avg,
                    "wx_WindSpeedGustMPH_latest":
                    WindSpeedGustMPH_latest,
                    "wx_WindSpeedGustMPH_last_1hr_max":
                    WindSpeedGustMPH_last_1hr_max,
                    "wx_Humidity_latest":
                    Humidity_latest,
                    "wx_Humidity_last_1hr_avg":
                    Humidity_last_1hr_avg,
                    "wx_Humidity_last_1hr_change":
                    Humidity_last_1hr_change,
                    "wx_Humidity_last_1hr_avg_increase":
                    Humidity_last_1hr_avg_increase,
                    "wx_Humidity_last_1hr_avg_decrease":
                    Humidity_last_1hr_avg_decrease,
                    "wx_PrecipRate_inhr_latest_max":
                    HourlyPrecipIn_latest,
                    "wx_PrecipRate_inhr_last_1hr":
                    PrecipRate_inhr_last_1hr},
                    # TODO: ADD WIND DIRECTION
                    ignore_index=True)
                stations = stations.sort_values("wx_station_dist_mi")
            else:
                pass

        station_count = stations.shape[0]

        # duplicate WSP data for current collision
        temp_df_dict = dict(wsp_df.iloc[collision_row_id])

        # gather WU data means and address renamed and non-mean'd parameters
        grouped_station_dict = np.mean(stations)
        grouped_station_dict["wx_mean_station_dist_mi"] = (grouped_station_dict
                                                           .pop("wx_station_"
                                                                "dist_mi"))
        grouped_station_dict["wx_WindSpeedGustMPH_latest"] = np.max(
            stations.wx_WindSpeedGustMPH_latest)
        grouped_station_dict["wx_WindSpeedGustMPH_last_1hr_max"] = np.max(
            stations.wx_WindSpeedGustMPH_last_1hr_max)
        grouped_station_dict["wx_PrecipRate_inhr_latest_max"] = np.max(
            stations.wx_PrecipRate_inhr_latest_max)
        grouped_station_dict["wx_PrecipRate_inhr_last_1hr"] = np.max(
            stations.wx_PrecipRate_inhr_last_1hr)
        grouped_station_dict["wx_station_count"] = station_count
        grouped_station_dict["wx_unique_event_id"] = unique_event_id

        # combine WSP and WU dictionaries and append to wsp_df_new
        temp_df_dict.update(grouped_station_dict)
        wsp_df_new = wsp_df_new.append(temp_df_dict, ignore_index=True)

    return wsp_df_new
