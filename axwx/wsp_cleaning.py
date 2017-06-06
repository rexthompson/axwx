"""
WSP Cleaning:
Takes a csv file from WSP's collision analysis tool and returns a new csv file
in a format that can be merged with Weather Underground data, ultimately being
used in a visualization tool
"""


import numpy as np
import pandas as pd

from IPython.core.interactiveshell import InteractiveShell
from pyproj import Proj, transform

InteractiveShell.ast_node_interactivity = "all"


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
    # write cleaned/formatted data to new csv
    df = clean_wsp_collision_data(input_csv_filepath)
    df.to_csv(cleaned_csv_filepath, sep=',')
    print('cleaned csv file exported!')
