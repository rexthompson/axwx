Cleaning Washington State Patrol (WSP) Collision Analysis Tool (CAT) Data
-------------------------------------------------------------------------

Here we will create a cleaned copy of a small subset of the raw WSP collision data that was downloaded during the installation. The data file that will be cleaned is `test_wsp_raw.csv` located in the data directory of the package. The function to clean the data and assign it to a variable is `clean_wsp_collision_data`. Find the package data directory and try entering the following into python:

```
df = axwx.clean_wsp_collision_data('~Anaconda/Lib/site-packages/Ax_Wx-0.1-py3.5.egg/axwx/data/test_wsp_raw.csv')
print(df)
```

If you would like to instead export the cleaned version to a csv file available on your desktop, you may use the following function:

```
axwx.export_cleaned_wsp_file('~Anaconda/Lib/site-packages/Ax_Wx-0.1-py3.5.egg/axwx/data/test_wsp_raw.csv',
                             '~Desktop/my_cleaned_data.csv')
``` 