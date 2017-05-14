Ax/Wx - Traffic Accident / Weather Analysis - Design Specification
==================================================================


COMPONENTS
----------
_This section should list the components that you expect to have in your project (not necessarily a complete list), what they do, and how their interfaces (e.g., functions with inputs and outputs). If the component is an existing package, then you should point to a documentation for the package. If the component is something that you'll build, then describe (maybe at a high level) the functions and their inputs and outputs._

WU pull
	scrapy/beautifulsoup
WU cleanup
	coordinate mapping (lat/lon)

collision pull
collision cleanup
	coordinate mapping (lat/lon)

merge of two datasets

Visualization of Data:

	The visualization will consist of a GUI with several plots of the collision/weather data.  There will be descriptive text aids for how to use the tool's interactive features at the top.  Once familiar with the tool, the user can look directly below at applying filters for precip rate, temperature, and date-time and then draw inferences based on their business need

	These interactions can help the user hone in on areas of interest and will update the plots in the GUI.  These will be plots of the following:

		(1) A primary visualization of a city map of Seattle with collisions marked by color based off of collision type (fatality, distraction, impairment, weather induced or pedestrian involvement).  

		(2) A smaller supplementary time-series plot of collision frequency (per hour).

		(3) A smaller supplementary pareto of the number of collisions (per hour) by collision type.

	The Python packages that will be utilized for the visualization are listed as follows:

	bokeh - http://bokeh.pydata.org/en/latest/docs/dev_guide/documentation.html

		The package "bokeh" is a interactive visualization library to help aid presentation by use of advanced custom graphics (such as interactive plots, dashboards, and data applications) in the style of D3.js.   

	folium - https://folium.readthedocs.io/en/latest/

		The package "folium" is a library with built-in tilesets from OpenStreetMap, Mapbox, and Stamen, supporting   GeoJSON and TopoJSON overlays.  Overall, it has a strength in map overlays.


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
