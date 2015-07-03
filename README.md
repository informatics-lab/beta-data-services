# betadataservices

Python wrapper for sending and receiving requests to Met Office Beta Data
Services (BDS).

To validate the requests an API key is needed, which must be registered with
BDS. A key can be received by registering with
[Met Office DataPoint](www.metoffice.gov.uk/datapoint/) and following the
link to "Your DataPoint API key". Currently, this gives you access to DataPoint
data only. Contact the BDS team at the Met Office to have this key registered
to get access the BDS data.

Requests can be made through WCS1 or WCS2 requests with the _WCS1Requester_
and _WCS2Requester_ classes.
These classes both include methods for the basic request types:

* getCapabilities()
* describeCoverage()
* getCoverage() - _Note, arguments differ between WCS1 and WCS2._

_WCS2Requester_ also includes:

* describeCoverageCollection()

**Example use:**

```python
import betadataservices as bds

bds.available_model_feeds()
```
_EGloEGRR
UKPPBEST
UKPPNOW
EURO4
GlobEGRR_
```python
req = bds.WCS2Requester(api_key="your-datapoint-api-key-1234",
                        model_feed="UKPPBEST")
# Print out all available coverages.
req.getCapabilities()
```

_UKPPBEST_2015-06-23T03.00.00Z_AGL  
UKPPBEST_2015-06-23T03.00.00Z_Atmosphere  
UKPPBEST_2015-06-23T03.00.00Z_CloudBase  
UKPPBEST_2015-06-23T03.00.00Z_Ground  
UKPPBEST_2015-06-23T06.00.00Z_AGL  
UKPPBEST_2015-06-23T06.00.00Z_Atmosphere  
UKPPBEST_2015-06-23T06.00.00Z_CloudBase  
UKPPBEST_2015-06-23T06.00.00Z_Ground  
etc.._  

```python
# Take a coverage name and print out available parameters for it.
req.describeCoverage("UKPPBEST_2015-06-23T06.00.00Z_AGL")
```

_*** NAME ***_  
_UKPPBEST_2015-06-23T06.00.00Z_AGL_  

_*** COMPONENTS ***_  
_Temperature_  
_Visibility_  
_Wind_Direction_  
_Wind_Gust_Speed_  
_Wind_Speed_  

_*** BBOX ***_  
_-14.0, 47.5, 7.0, 61.0_  

_*** DIM_RUNS ***_  
_2015-06-23T06:00:00Z_  

```python
# Get a the coverage data and save to file.
req.getCoverage(coverage_id="UKPPBEST_2015-06-23T06.00.00Z_AGL",
                components="Temperature",
                format="NetCDF3",
                elevation=10,
                bbox=[-14.0, 47.5, 7.0, 61.0],
                time="2015-06-23T06:00:00Z",
                savepath="path/to/save.nc")

```
