"""
Functions to clean WU PWS observation data
"""

import copy
import numpy as np
import pandas as pd
import os
import pickle


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
