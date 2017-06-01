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
  |- doc/
     |- CAT-DataDictionary.xlsx
     |- CAT-LookUp.accdb
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

Using the Accident-Weather Analysis Tool (`Ax/Wx`)
--------------------------------------------------