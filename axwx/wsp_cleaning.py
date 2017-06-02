'''
WSP Cleaning:
Takes a csv file from WSP's collision analysis tool and returns a new csv file
in a format that can be merged with Weather Underground data, ultimately being
used in a visualization tool
'''

import numpy as np
import pandas as pd

from IPython.core.interactiveshell import InteractiveShell
from pyproj import Proj, transform

InteractiveShell.ast_node_interactivity = "all"


def convert_stateplane_to_latlon(state_x, state_y, proj_in=2286,
                                 proj_out=4326):
    '''
    This funtion takes the state plane coordinates used by the state patrol
    and converts them to latitudes and longitudes to be plotted on a map
    '''
    inProj = Proj(init='epsg:' + str(proj_in), preserve_units=True)
    outProj = Proj(init='epsg:' + str(proj_out))
    x2, y2 = transform(inProj, outProj, state_x, state_y)
    return y2, x2


# read in raw data from WSP's collision analysis tool
print('\nreading csv file...')
df = pd.read_csv('~/Desktop/WA_Crash_Data.csv', sep=',', low_memory=False)

# drop any collision records with no state plane coordinates
print('dropping records with no state plane coordinates...')
df = df.drop(df[np.isnan(df.Colli_Dtl_Info_State_Plane_X)].index)
df = df.drop(df[np.isnan(df.Colli_Dtl_Info_State_Plane_Y)].index)
df = df.reset_index(drop=True)

# convert state plane coordinates to latitudes and longitudes
print('converting state plane coordinates/dropping records not in range...')
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
    'MV_Drvr_Ctrb_Circums_Typ_Cd_2': 'contributing_factor_3',
    'MV_Drvr_Alch_Test_Cd': 'alcohol_test_given',
    'MV_Drvr_Air_Bag_Typ_Cd': 'airbag'})

# write cleaned/formatted data to new csv
df.to_csv('~/Desktop/WSP_Crash_Data_Cleaned.csv', sep=',')
print('cleaned csv file exported!')
