# data-manager

Repository for all data handling.

BDS
Python wrapper for sending and recieving requests to Beta Data Services (BDS).
Includes methods for main requests: 

getCapabilities()
describeCoverage()
getCoverage()

As well as wrapper methods:

createCoverageCubes() - For returning getCoverage() data in an iris.cube.Cube
streamCoverageToAWS() - For streaming getCoverage() data straight to Amazon Web Sevices S3 server

Example use:

>>> req = BDSRequest(api_key="1234-your-api-key-5678")
>>> req.getCapabilities() # Prints out all avaiable coverages.
UKPPBEST_Cloud_base
UKPPBEST_Critical_snow_rate
UKPPBEST_Falling_Snow_Level
UKPPBEST_High_cloud_cover
UKPPBEST_Lightning_Rate
UKPPBEST_Low_cloud_cover
UKPPBEST_Medium_cloud_cover
UKPPBEST_Precipitation_rate

>>> req.describeCoverage("UKPPBEST_Low_cloud_cover") # Takes a coverage and prints out available parameters.
*** NAME ***
UKPPBEST_Low_cloud_cover

*** LABEL ***
Low cloud cover

*** BBOX ***
-14.0, 7.0, 47.5, 61.0

*** DIM_RUNS ***
2015-04-16T00:00:00Z
2015-04-16T03:00:00Z
2015-04-16T06:00:00Z
2015-04-16T09:00:00Z
etc..

*** DIM_FORECASTS ***
PT1H
PT2H
PT3H
PT4H
PT5H
etc..

*** TIMES ***
2015-04-21T18:00:00Z
2015-04-21T21:00:00Z
2015-04-22T00:00:00Z
2015-04-22T03:00:00Z
etc..

*** ELEVATIONS ***
0-300m
0-1500m

*** CRSS ***
CRS:84
EPSG:54004
EPSG:27700
EPSG:4326

*** FORMATS ***
GRIB1
GRIB2
NetCDF3
GeoTIFF
GeoTIFFfloat
KML
JSON

*** INTERPOLATIONS ***
nearest-neighbour
bilinear
high-order

>>> # Use the built in method to build parameter dictionary (needed for getCoverage) properly.
>>> param_dict = req.getParameterDictionary(bbox=[-14.0, 7.0, 47.5, 61.0], format="NetCDF3", etc..)

>>> # Return a requests.Response instance (returned data content is stored as response.content).
>>> response = req.getCoverage("UKPPBEST_Low_cloud_cover", param_dict)

>>> # Return an iris.cube.CubeList instance.
>>> cubes = req.createCoverageCubes("UKPPBEST_Low_cloud_cover", param_dict)

>>> # Stream returned data straight to AWS S3 server.
>>> req.streamCoverageToAWS("UKPPBEST_Low_cloud_cover", param_dict, "bucket-name", "path/to/file.nc")


