# Setup module for Ax/Wx


import os
from setuptools import setup, find_packages
PACKAGES = find_packages()

# Get version and release info, which is all stored in shablona/version.py
# ver_file = os.path.join('shablona', 'version.py')
# with open(ver_file) as f:
#     exec(f.read())

# packages = ['csv', 'os', 'time', 'pandas', 'pickle', 'requests',
#             'urllib3', 'bs4.BeautifulSoup', 'numpy']

opts = dict(name='Ax/Wx',
            maintainer='Rex Thompson',
            maintainer_email='rexs.thompson@gmail.com',
            description='Accident-Weather Analysis Tool',
            long_description=('AxWx - Accident-Weather Analysis Tool for data'
                              ' scraping, cleaning, merging and analysis'),
            url='https://github.com/rexthompson/axwx',
            # download_url="DOWNLOAD_URL",
            license='MIT',
            # classifiers="CLASSIFIERS",
            author='Ax/Wx"',
            author_email='axwx@googlegroups.com',
            version='0.1',
            packages=PACKAGES
            package_data="PACKAGE_DATA",
            # install_requires="REQUIRES",
            # requires="REQUIRES"
            )

if __name__ == '__main__':
    setup(**opts)
