# data-manager

Repository for all data handling.

### BDS
Python wrapper for sending and recieving requests to Beta Data Services (BDS).
Includes methods for main requests:

* getCapabilities()
* describeCoverage()
* getCoverage()

As well as wrapper methods:

* createCoverageCubes() - For returning getCoverage() data in an iris.cube.Cube
* streamCoverageToAWS() - For streaming getCoverage() data straight to Amazon Web Sevices S3 server

Example use:

```python
req = BDSRequest(api_key="1234-your-api-key-5678")
req.getCapabilities() # Prints out all avaiable coverages.
```

_UKPPBEST_Cloud_base  
UKPPBEST_Critical_snow_rate  
UKPPBEST_Falling_Snow_Level  
UKPPBEST_High_cloud_cover  
UKPPBEST_Lightning_Rate  
UKPPBEST_Low_cloud_cover  
UKPPBEST_Medium_cloud_cover  
UKPPBEST_Precipitation_rate  
etc.._

```python
req.describeCoverage("UKPPBEST_Low_cloud_cover") # Takes a coverage and prints out available parameters.
```

_*** NAME ***_  
_UKPPBEST_Low_cloud_cover_  

_*** LABEL ***_  
_Low cloud cover_  

_*** BBOX ***_  
_-14.0, 7.0, 47.5, 61.0_  

_*** DIM_RUNS ***_  
_2015-04-16T00:00:00Z_  
_2015-04-16T03:00:00Z_  
_2015-04-16T06:00:00Z_  
_2015-04-16T09:00:00Z_  
_etc.._  

_*** DIM_FORECASTS ***_  
_PT1H_  
_PT2H_  
_PT3H_  
_PT4H_  
_PT5H_  
_etc.._  

_*** TIMES ***_  
_2015-04-21T18:00:00Z_  
_2015-04-21T21:00:00Z_  
_2015-04-22T00:00:00Z_  
_2015-04-22T03:00:00Z_  
_etc.._  

_*** ELEVATIONS ***_  
_0-300m_  
_0-1500m_  

_*** CRSS ***_  
_CRS:84_  
_EPSG:54004_  
_EPSG:27700_  
_EPSG:4326_  

_*** FORMATS ***_  
_GRIB1_  
_GRIB2_  
_NetCDF3_  
_GeoTIFF_  
_GeoTIFFfloat_  
_KML_  
_JSON_  

_*** INTERPOLATIONS ***_  
_nearest-neighbour_  
_bilinear_  
_high-order_

```python
# Use the built in method to build parameter dictionary (needed for getCoverage) properly.
param_dict = req.getParameterDictionary(bbox=[-14.0, 7.0, 47.5, 61.0], format="NetCDF3", etc..)

# Return a requests.Response instance (returned data content is stored as response.content).
response = req.getCoverage("UKPPBEST_Low_cloud_cover", param_dict)

# Return an iris.cube.CubeList instance.
cubes = req.createCoverageCubes("UKPPBEST_Low_cloud_cover", param_dict)

# Stream returned data straight to AWS S3 server.
req.streamCoverageToAWS("UKPPBEST_Low_cloud_cover", param_dict, "bucket-name", "path/to/file.nc")
```
