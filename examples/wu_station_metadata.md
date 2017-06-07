
Retrieve Weather Underground Personal Weather Station Metadata
-------------------------------------------------------------------------

Use the `axwx.scrape_station_info()` to generate a list of active personal weather stations in a region of interest. Simply specify a US state as an argument to the function (e.g. `state="WA"`), and basic station metadata will be scraped from a URL such as this:

https://www.wunderground.com/weatherstation/ListStations.asp?selectedState=WA&selectedCountry=United+States

The function then retrieves additional metadata for each station. Note that this can take some time, as the function has to scrape from a differnet URL for every station, such as the following:

https://api.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KWASEATT1735&format=XML

The end results is a Pandas DataFrame with the following fields for all active stations in the state of interest:

* Statin ID
* Neighborhood
* City
* Station Type
* Latitude
* Longitude
* Elevation

The function automatically exports the DataFrame as a .csv file to `'./data/station_data_from_FUN.csv'`.

----------

Stay tuned for future functionality, including:

* scraping metadata for all active stations (rather than by state), from https://www.wunderground.com/weatherstation/ListStations.asp
* argument to skip Latitude/Longitude/Elevation (which is the time consuming part)
* argument to skip writing to .csv, and just return the Pandas DataFrame with basic metadata
* arguments for additional metadata (e.g. zip code)
* ability to update existing station list with new stations
