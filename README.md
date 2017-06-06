<img src=https://raw.githubusercontent.com/rexthompson/axwx/master/images/axwx-logo.jpg alt="Logo3" width="200" height="200" />



Ax/Wx
=====
Ax/Wx is a collision and weather analysis tool that can enhance the WSP collision database with objective observations from nearby personal weather stations. Most weather observations come from major weather stations that may not be able to detect the weather as accurately as a closer weather station at a particular location.

To use Ax/Wx, you will need to clone this repository onto your computer and follow the instructions at the bottom of this page.



Organization of the Project
---------------------------
The project has the following structure:
```
axwx/
  |- README.md
  |- axwx/
     |- __init__.py
     |- axwx_dashboard.py
     |- wsp_cleaning.py
     |- wu_metadata_scraping.py
     |- wu_observation_scraping.py
     |- wu_cleaning.py
     |- merge_wsp_wu.py
     |- tests/
        |- dashboard_unit_tests.py
        |- merge_unit_tests.py
        |- wsp_unit_tests.py
        |- wu_unit_tests.py
  |- data/
     |- station_data.csv
     |- station_data.xlsx
     |- station_info-1.csv
     |- CAT-DataDictionary.xlsx
     |- CAT-LookUp.accdb
  |- doc/
     |- DesignSpecification.md
     |- FunctionalSpecification.md
  |- examples/
     |- ...
  |- images/
     |- Logo.png
     |- WhiteboardMockup.JPG
     |- axwx-log0.jpg
     |- mockup2.jpg
  |- setup.py
  |- LICENSE
  |- requirements.txt
```



Examples (How to use Ax/Wx)
---------------------------
To understand how to use Ax/Wx, please refer to 
the [examples](https://github.com/rexthompson/axwx/tree/master/examples) section of this GitHub page where you can find 
examples for doing the following:
    
- How to generate a list of active personal weather stations in a region of interest
- Scraping weather data from a generated list of personal weather stations
- Cleaning the scraped weather data
- Cleaning the Washington State Patrol collision data
- Merging weather data with collision data from the Washington State patrol
- Creating visualizations with the merged dataset



Project History
---------------
The idea for Ax/Wx was developed in May 2017 in the University of Washington's DATA 515 course for Software Development.
Seeing the potential benefit of personal weather station data (sourced from Weather Underground) combined with collision
records from the Washington State Patrol, we decided build the infrastructure to help easily scrape and combine these 
two data sources.  The first objective we had set was to perform an analysis within the Seattle area to see what 
insights could be uncovered in respect to weather impacts on collision occurrence.  Going forward, we hope to explore 
integrating interactive visualization tools and perhaps even mobile application creation.

Station List function to scrape can be easily customized to scrape weather data for state in the U.S. and can be further
subset based off lat/long inputs.



Limitations
-----------
In its current form, the Ax/Wx package serves as a very efficient and customizable weather station and data scraping 
tool, with the ability for local users in Washington State to merge the data with Washington State Patrol's [collision data](http://www.wsp.wa.gov/publications/collision.htm).

The package also does not support ad hoc interactive visualization but can create an analysis
report for weather impacts on accidents in Washington State for a given time frame.



Acknowledgements
----------------
A thanks to our DATA 515 course professors, Joe Hellerstein and Dave Beck, of the University of Washington eScience
Institute, for instructing us on the best practices of software development.

As mentioned, Weather Underground and Washington State Patrol were the resources used for the sourcing of weather 
station and collision data respectively.



Installation
------------
To install `axwx` you will need to begin by cloning `axwx` on your own computer by using the following `git` command:

```
git clone https://github.com/uwescience
```

Next, to install the package you will need to go into the `axwx` directory and run the `setup.py` file:

```
cd axwx/
python setup.py install
```

To ensure that the dependencies to run `axwx` are installed on your computer you will want to run the following command:

```
pip install -r requirements.txt
```

You should now be ready to import and use `axwx` on your computer.



Contact
-------
Questions? Comments? Drop us a line at [axwx@googlegroups.com](https://groups.google.com/forum/#!forum/axwx)