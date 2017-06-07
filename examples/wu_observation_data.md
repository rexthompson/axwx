Scrape weather data from a generated list of personal weather stations
-------------------------------------------------------------------------

A given personal weather station's data is available by day at a link such as the following:

https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KWASEATT1735&day=3&month=6&year=2017&graphspan=day&format=1

Use the `scrape_data_one_day()` function to scrape data from a single station for a single day. For example, the following code will retrieve the data shown at the link above:

```
scrape_data_one_day("KWASEATT1735", 2017, 6, 3)
```

The function returns the observation data as a Pandas DataFrame.

---

Since users are typically interested in data for more than a single day, we provide the `scrape_data_multiple_day()` function. This function again takes `station_id` as its first argument. The second and third arguments -- `start_date` and `end_date` -- tell the function over which days you would like to retrieve data. A `delay` argument defaults to pausing 3 seconds between requests, as a courtesy to the Weather Underground servers. Finally, an option is provided to append new observations to an existing dataframe using the `combined_df` argument.

For example, the following will retrieve data from the same station as before, but over a few days' time:

```
scrape_data_multiple_day("KWASEATT1735", 20170603, 20170605)
```

The function returns a Pandas DataFrame with observations from a single station over multiple consecutive days.

---

Users may also wish to scrape data for multiple stations over multiple days. For this, we provide the `scrape_data_multiple_stations_and_days()` function.

The arguments to this function are similar to those in the prior function, except `station_ids` now consists of a list of station IDs. We also provide a `data_dir` argument, as individual station data is exported to this directory with a filename of `<station_id>.p`.

For example, the following will generate data for multiple stations:

```
station_ids = ["KWAWASHI24", "KWASEATT1735"]
scrape_data_multiple_stations_and_days(station_ids, 20170603, 20170605, "./data/")
```

Have fun scraping!