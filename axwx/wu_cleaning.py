import numpy as np
import pandas as pd

"""
Functions to clean WU PWS observation data
"""


def clean_obs_data(df):
    """
    Clean WU PWS data for a single station.
    Currently just fills missing values w/ NaN's.
    :param df: pandas.DataFrame
        raw data
    :return: cleaned pandas.DataFrame
    """

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    ignore = ["Time", "WindDirection", "SoftwareType",
              "Conditions", "Clouds", "DateUTC"]

    for col in df.columns:
        if col == "TemperatureF":
            df.loc[df[col] < 10, col] = np.nan
            df.loc[df[col] > 125, col] = np.nan
        elif col == "DewpointF":
            df.loc[df[col] == -99.9, col] = np.nan
        elif col == "PressureIn":
            df.loc[df[col] < 25, col] = np.nan
        elif col not in ignore:
            df.loc[df[col] < 0, col] = np.nan

    return df
