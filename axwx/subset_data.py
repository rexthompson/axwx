rain_vals = [0.05,0.25]
time_vals = [9,21]
def subset_day_night(time_vals, data):
    """
    Function to subset the data by day and night based on the values
    inputted by time_vals.

    :param time_vals: list
        two values used to split the data into day and night subsets
    :param data: DataFrame
        The data to be subsetted. This data must contain a column of hours
        taken from the time values using some form of time parsing, i.e.
        pd.Datetimeindex(blah).hour
    """

    tmp_day = data[(data['hour'] >= time_vals[0])]
    day_data = tmp_day[tmp_day['hour'] < time_vals[1]]

    tmp_night1 = data[data['hour'] < time_vals[0]]
    tmp_night2 = data[data['hour'] >= time_vals[1]]
    night_data = pd.DataFrame.append(tmp_night1, tmp_night2)

    return(day_data, night_data)

def subset_rain(rain_vals, data):
    """
    Function to subset the amount that it was raining in the past 60 minutes.
    This comes from the values of the rain_vals list inputted into the function.

    :param rain_vals: list
        Past 60 minute rain values to subset the data by. The data would be
        subsetted from 0 to the first value, the first to the second value,
        and the second value up to the maximum value in the data.
    :param data: DataFrame
        The data to be subsetted. This data must contain a column of hours
        taken from the time values using some form of time parsing, i.e.
        pd.Datetimeindex(blah).hour
    """
    norain_data = data[data['rolling60_precip_in'] < rain_vals[0]]

    tmp_lightrain = data[data['rolling60_precip_in'] >= rain_vals[0]]
    lightrain_data = tmp_lightrain[tmp_lightrain['rolling60_precip_in'] <
    rain_vals[1]]

    heavyrain_data = data[data['rolling60_precip_in'] >= rain_vals[1]]

    return(norain_data, lightrain_data, heavyrain_data)

def subset_all(data, time_vals, rain_vals):
    """
    Function that leverages the previous subset functions to take a single
    dataframe and subset each one by day and night and the rain values. Takes
    as input the rain values and the hours to subset the data by.

    :param data: DataFrame
        The data to be subsetted. This data must contain a column of hours
        taken from the time values using some form of time parsing, i.e.
        pd.Datetimeindex(blah).hour
    :param time_vals: list
        Two values used to split the data into day and night subsets. 
    :param rain_vals: list
        Past 60 minute rain values to subset the data by. The data would be
        subsetted from 0 to the first value, the first to the second value,
        and the second value up to the maximum value in the data.
    """
    day, night = subset_day_night(time_vals, data)
    day_norain, day_lightrain, day_heavyrain = subset_rain(rain_vals, day)
    night_norain, night_lightrain, night_heavyrain = subset_rain(rain_vals,
    night)
    return(day_norain, day_lightrain, day_heavyrain, night_norain,
    night_lightrain, night_heavyrain)
