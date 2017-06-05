"""
Functions to combine Washington State Patrol and Weather Underground datasets into single enhanced DF
"""
import pandas as pd
import os
import numpy as np
import copy
import pickle
from geopy.distance import vincenty  # note: had to pip install geopy
from wu_metadata_scraping import subset_stations_by_coords
from wu_cleaning import clean_obs_data


def get_bounding_box(coords, dist_mi):
    """
    Calculate lat/lon bounding box for distance from reference location
    :param coords: 2-tuple
        (latitude, longitude) pair for reference location 
    :param dist_mi: numeric
        length of shortest distance of bounding box, in miles
    :return: lists of bounding box coordinate limits for latitude and longitude
    """
    lon_dist_mi = dist_mi * 1 / vincenty(coords, (coords[0], coords[1] + 1)).miles
    lat_dist_mi = dist_mi * 1 / vincenty(coords, (coords[0] + 1, coords[1])).miles

    lat_bounds_deg = [coords[0] - lat_dist_mi, coords[0] + lat_dist_mi]
    lon_bounds_deg = [coords[1] - lon_dist_mi, coords[1] + lon_dist_mi]

    return lat_bounds_deg, lon_bounds_deg


def enhance_wsp_with_wu_data(wu_metadata_full_filepath, wsp_data_full_filepath, wu_obs_filepath, radius_mi,
                             lat_range=[47.4, 47.8], lon_range=[-122.5, -122.2]):
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
    station_df = subset_stations_by_coords(wu_metadata_full_filepath, lat_range, lon_range)
    wsp_df = pd.read_csv(wsp_data_full_filepath, index_col="Unnamed: 0")
    os.chdir(wu_obs_filepath)

    collision_count = wsp_df.shape[0]

    # TODO: write wrapper function on wu_cleaning.py to clean data and save file as *_cleaned
    # These cleaned files are what we'll call in below (so we don't have to clean them each
    # time they're called)

    wsp_df_new = pd.DataFrame()
    unique_event_id = 1

    for collision_row_id in range(1000):  # TODO: update to range(collision_count):

        print("-------- processing row #" + str(collision_row_id) + " of " + str(collision_count) + " --------")

        # get collision info
        collision_coords = wsp_df["lat"].iloc[collision_row_id], wsp_df["lon"].iloc[collision_row_id]
        collision_date = wsp_df["date"].iloc[collision_row_id]
        collision_time = wsp_df["time_of_day"].iloc[collision_row_id]
        collision_datetime = np.datetime64(collision_date + " " + collision_time)
        collision_datetime_minus_15_mins = collision_datetime - np.timedelta64(15, 'm')
        collision_datetime_minus_60_mins = collision_datetime - np.timedelta64(60, 'm')
        collision_datetime_minus_24hrs = collision_datetime - np.timedelta64(24, 'h')

        # autopopulate wx info if duplicate collision record (i.e. same lat/lon/date/time)
        if collision_row_id > 0:
            dup_record = True
            dup_record = dup_record & (collision_time == wsp_df_new["time_of_day"][collision_row_id - 1])
            dup_record = dup_record & (collision_date == wsp_df_new["date"][collision_row_id - 1])
            dup_record = dup_record & (collision_coords[0] == wsp_df_new["lat"][collision_row_id - 1])
            dup_record = dup_record & (collision_coords[1] == wsp_df_new["lon"][collision_row_id - 1])
            if dup_record:
                print("duplicate event")
                temp_df_dict = dict(wsp_df.iloc[collision_row_id])
                temp_df_dict.update(grouped_station_dict)
                wsp_df_new = wsp_df_new.append(temp_df_dict, ignore_index=True)
                continue
            else:
                unique_event_id += 1
                pass
        else:
            pass

        # subset station DF by lat/lon bbox (to reduce # of distance calculations later)
        station_df_temp = copy.deepcopy(station_df)
        bbox = get_bounding_box(collision_coords, radius_mi)
        station_df_temp = subset_stations_by_coords(station_df, bbox[0], bbox[1])

        # initialize new DF for combined station info
        stations = pd.DataFrame()

        # loop through stations
        for station_row_id in range(station_df_temp.shape[0]):

            # get station info and distance from collision
            station_id = station_df_temp.index[station_row_id]
            station_coords = station_df_temp["Latitude"].iloc[station_row_id], station_df_temp["Longitude"].iloc[
                station_row_id]
            station_dist_mi = vincenty(collision_coords, station_coords).miles

            # proceed if station within max radius
            if station_dist_mi <= radius_mi:

                # import wx obs for single station  # TODO: update to cleaned data when available
                wu_station_data = pickle.load(open(station_id + "_cleaned.p", "rb"))
                # wu_station_data = pickle.load(
                #     open(station_id + ".p", "rb"))  # TODO: remove this line after all data cleaned
                # wu_station_data = clean_obs_data(wu_station_data)  # TODO: remove this line after all data cleaned

                # subset wx obs to pre-collision only
                wu_station_datetime = pd.DatetimeIndex(wu_station_data["DateUTC"])
                wu_station_data = wu_station_data[wu_station_datetime <= collision_datetime]
                wu_station_datetime = wu_station_datetime[wu_station_datetime <= collision_datetime]

                # latest readings (up to 15 minutes prior to collision)
                wu_station_data_latest = wu_station_data[wu_station_datetime >= collision_datetime_minus_15_mins]
                if wu_station_data_latest.shape[0] > 0:
                    TemperatureF_latest = wu_station_data_latest["TemperatureF"].iloc[-1]
                    DewpointF_latest = wu_station_data_latest["DewpointF"].iloc[-1]
                    PressureIn_latest = wu_station_data_latest["PressureIn"].iloc[-1]
                    WindDirection_latest = wu_station_data_latest["WindDirection"].iloc[-1]
                    WindDirectionDegrees_latest = wu_station_data_latest["WindDirectionDegrees"].iloc[-1]
                    WindSpeedMPH_latest = wu_station_data_latest["WindSpeedMPH"].iloc[-1]
                    WindSpeedGustMPH_latest = wu_station_data_latest["WindSpeedGustMPH"].iloc[-1]
                    Humidity_latest = wu_station_data_latest["Humidity"].iloc[-1]
                    # TODO: ADD PRECIP RATE
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
                    # TODO: ADD PRECIP RATE
                    # TODO: ADD WIND DIRECTION

                # last 1 hr summary (note that not all parameters are averaged)
                wu_station_data_last_hr = wu_station_data[wu_station_datetime >= collision_datetime_minus_60_mins]
                nrow_last_1hr = wu_station_data_last_hr.shape[0]
                if nrow_last_1hr > 0:
                    TemperatureF_last_1hr_avg = np.round(np.mean(wu_station_data_last_hr["TemperatureF"]), 1)
                    DewpointF_last_1hr_avg = np.round(np.mean(wu_station_data_last_hr["DewpointF"]), 1)
                    PressureIn_last_1hr_avg =  np.round(np.mean(wu_station_data_last_hr["PressureIn"]), 2)
                    WindSpeedMPH_last_1hr_avg = np.round(np.mean(wu_station_data_last_hr["WindSpeedMPH"]), 1)
                    WindSpeedGustMPH_last_1hr_max = np.round(np.max(wu_station_data_last_hr["WindSpeedGustMPH"]), 1)
                    Humidity_last_1hr_avg = np.round(np.mean(wu_station_data_last_hr["Humidity"]), 1)
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
                    # get time delta in last hr to ensure good spread of data across last hr
                    wu_station_datetime_last_1hr = pd.DatetimeIndex(wu_station_data_last_hr["DateUTC"])
                    last_1hr_time_delta = wu_station_datetime_last_1hr[-1] - wu_station_datetime_last_1hr[0]
                    if last_1hr_time_delta > np.timedelta64(45, "m"):
                        do_last_1hr_calcs = True
                    else:
                        do_last_1hr_calcs = False
                else:
                    do_last_1hr_calcs = False

                # last 1 hr changes
                if do_last_1hr_calcs:
                    # net change beginning to end
                    TemperatureF_last_1hr_change = wu_station_data_last_hr["TemperatureF"].iloc[-1] - \
                                                   wu_station_data_last_hr["TemperatureF"].iloc[-0]
                    DewpointF_last_1hr_change = wu_station_data_last_hr["DewpointF"].iloc[-1] - \
                                                wu_station_data_last_hr["DewpointF"].iloc[-0]
                    PressureIn_last_1hr_change = wu_station_data_last_hr["PressureIn"].iloc[-1] - \
                                                 wu_station_data_last_hr["PressureIn"].iloc[-0]
                    Humidity_last_1hr_change = wu_station_data_last_hr["Humidity"].iloc[-1] - \
                                               wu_station_data_last_hr["Humidity"].iloc[-0]
                    # Avg net increase and decrease beginning to end
                    if nrow_last_1hr > 1:
                        TempF_diff = np.diff(wu_station_data_last_hr["TemperatureF"])
                        TemperatureF_last_1hr_avg_increase = -1 * np.round(np.sum(np.minimum(TempF_diff, 0)) /
                                                                        (nrow_last_1hr - 1), 1)
                        TemperatureF_last_1hr_avg_decrease = np.round(np.sum(np.maximum(TempF_diff, 0)) /
                                                                   (nrow_last_1hr - 1), 1)
                        DpF_diff = np.diff(wu_station_data_last_hr["DewpointF"])
                        DewpointF_last_1hr_avg_increase = -1 * np.round(np.sum(np.minimum(DpF_diff, 0)) /
                                                                     (nrow_last_1hr - 1), 1)
                        DewpointF_last_1hr_avg_decrease = np.round(np.sum(np.maximum(DpF_diff, 0)) /
                                                                (nrow_last_1hr - 1), 1)
                        RH_diff = np.diff(wu_station_data_last_hr["Humidity"])
                        Humidity_last_1hr_avg_increase = -1 * np.round(np.sum(np.minimum(RH_diff, 0)) /
                                                                    (nrow_last_1hr - 1), 1)
                        Humidity_last_1hr_avg_decrease = np.round(np.sum(np.maximum(RH_diff, 0)) /
                                                               (nrow_last_1hr - 1), 1)
                        # TODO: ADD PRECIP RATE
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
                    # TODO: ADD PRECIP RATE
                    # TODO: ADD WIND DIRECTION

                # save data in dataframe
                stations = stations.append({"station_id": station_id,
                                            "station_dist_mi": station_dist_mi,
                                            "TemperatureF_latest": TemperatureF_latest,
                                            "TemperatureF_last_1hr_avg": TemperatureF_last_1hr_avg,
                                            "TemperatureF_last_1hr_change": TemperatureF_last_1hr_change,
                                            "TemperatureF_last_1hr_avg_increase": TemperatureF_last_1hr_avg_increase,
                                            "TemperatureF_last_1hr_avg_decrease": TemperatureF_last_1hr_avg_decrease,
                                            "DewpointF_latest": DewpointF_latest,
                                            "DewpointF_last_1hr_avg": DewpointF_last_1hr_avg,
                                            "DewpointF_last_1hr_change": DewpointF_last_1hr_change,
                                            "DewpointF_last_1hr_avg_increase": DewpointF_last_1hr_avg_increase,
                                            "DewpointF_last_1hr_avg_decrease": DewpointF_last_1hr_avg_decrease,
                                            "PressureIn_latest": PressureIn_latest,
                                            "PressureIn_last_1hr_avg": PressureIn_last_1hr_avg,
                                            "PressureIn_last_1hr_change": PressureIn_last_1hr_change,
                                            "WindSpeedMPH_latest": WindSpeedMPH_latest,
                                            "WindSpeedMPH_last_1hr_avg": WindSpeedMPH_last_1hr_avg,
                                            "WindSpeedGustMPH_latest": WindSpeedGustMPH_latest,
                                            "WindSpeedGustMPH_last_1hr_max": WindSpeedGustMPH_last_1hr_max,
                                            "Humidity_latest": Humidity_latest,
                                            "Humidity_last_1hr_avg": Humidity_last_1hr_avg,
                                            "Humidity_last_1hr_change": Humidity_last_1hr_change,
                                            "Humidity_last_1hr_avg_increase": Humidity_last_1hr_avg_increase,
                                            "Humidity_last_1hr_avg_decrease": Humidity_last_1hr_avg_decrease},
                                           # TODO: ADD PRECIP RATE
                                           # TODO: ADD WIND DIRECTION
                                           ignore_index=True)
                stations = stations.sort_values("station_dist_mi")
            else:
                pass

        station_count = stations.shape[0]

        # duplicate WSP data for current collision
        temp_df_dict = dict(wsp_df.iloc[collision_row_id])

        # gather WU data means and address renamed and non-mean'd parameters
        grouped_station_dict = np.mean(stations)
        grouped_station_dict["mean_station_dist_mi"] = grouped_station_dict.pop("station_dist_mi")
        grouped_station_dict["WindSpeedGustMPH_latest"] = np.max(stations.WindSpeedGustMPH_latest)
        grouped_station_dict["WindSpeedGustMPH_last_1hr_max"] = np.max(stations.WindSpeedGustMPH_last_1hr_max)
        grouped_station_dict["station_count"] = station_count
        grouped_station_dict["unique_event_id"] = unique_event_id

        # combine WSP and WU dictionaries and append to wsp_df_new
        temp_df_dict.update(grouped_station_dict)
        wsp_df_new = wsp_df_new.append(temp_df_dict, ignore_index=True)

    return wsp_df_new
