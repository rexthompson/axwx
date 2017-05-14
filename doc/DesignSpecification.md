Ax/Wx - Traffic Accident / Weather Analysis - Design Specification
==================================================================


COMPONENTS
----------
_This section should list the components that you expect to have in your project (not necessarily a complete list), what they do, and how their interfaces (e.g., functions with inputs and outputs). If the component is an existing package, then you should point to a documentation for the package. If the component is something that you'll build, then describe (maybe at a high level) the functions and their inputs and outputs._

WU pull
	scrapy/beautifulsoup

**Getting the latitude and longitude from the weather stations.**
Use the data scraped previously from weather underground listing the unique station identification. From these data we created a script to obtain the latitude and longitude from these weather stations. The script runs as follows:

- Load the data into python using a panda dataframe.
- We used the urllib3 package to make each URL request.
- The beautiful soup package was used to parse the XML document that was returned from each URL call. 
- Any missing data was filled in with NA's. 

WU cleanup
	coordinate mapping (lat/lon)

collision pull
collision cleanup
	coordinate mapping (lat/lon)

merge of two datasets

visualization of data
	bokeh
	folium


INTERACTIONS
------------
_You should have a subsection here for each use case in your functional specification (homework 6). In each subsection, you will describe how the components interact to accomplish the use case._

#### Traffic Engineer

<stuff here>

#### Law Enforcement Officer

<stuff here>

#### Insurance Company

<stuff here>

#### Common Driver

<stuff here>


PROJECT PLAN
------------
_Provide details for what you'll accomplish in the next two weeks, and higher level descriptions for the remaining weeks in the quarter so that the end result is that you have implemented and tested a system that accomplishes your use cases._

<stuff here>

