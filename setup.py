# placeholder for file that initializes project after it has been cloned

import os
from setuptools import setup, find_packages
PACKAGES = find_packages()

# Get version and release info, which is all stored in shablona/version.py
# ver_file = os.path.join('shablona', 'version.py')
# with open(ver_file) as f:
#     exec(f.read())

packages = ['csv', 'os', 'time', 'pandas', 'pickle', 'requests',
            'urllib3', 'bs4.BeautifulSoup', 'numpy']

opts = dict(name="NAME",
            #maintainer="MAINTAINER",  # TODO
            #maintainer_email="MAINTAINER_EMAIL",  # TODO
            #description="DESCRIPTION",  # TODO
            #long_description="LONG_DESCRIPTION",
            #url="URL",
            #download_url="DOWNLOAD_URL",
            #license="LICENSE",
            #classifiers="CLASSIFIERS",
            #author="AUTHOR",  # TODO
            #author_email="AUTHOR_EMAIL",  # TODO
            #platforms="PLATFORMS",
            #version="VERSION",  # TODO
            packages=packages)#,
            #package_data="PACKAGE_DATA",
            #install_requires="REQUIRES",
            #requires="REQUIRES")

if __name__ == '__main__':
    setup(**opts)
