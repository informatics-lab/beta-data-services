"""
Python wrapper for getting data from BDS.

To do:

Which parameters are esstential - Is that request dependant, how would this be handled?

Practise with 3D sets/mutilple time steps.


"""
import requests
import dateutil.parser
import iris
from boto.s3.connection import S3Connection, Location
from xml_reader import read_getCapabilities_xml, read_describeCoverage_xml, \
                       read_xml

valid_model_feeds = ["UKPPBEST"]
valid_services = {"WCS" : ["1.0"]}

class BDSRequest(object):
    """
    Send requests and handle responses to BDS.

    Args:

    * api_key: string
        BDS requires an api key to access the data. This is can received by
        signing up to Met Office DataPoint. www.metoffice.gov.uk/datapoint/

    Kwargs:

    * model_feed: string
        The model feed from which you wish to pull data.

    * service/version: string
        The OGC protocol. (currently only support for WCS1.0)

    * validate_api: boolean
        If True a dummy request is made during intialisation to check the api
        key is valid. This is not entirely necessary as the same check is done
        with all requests.

    """
    def __init__(self, api_key,  model_feed="UKPPBEST", service="WCS",
                 version="1.0", validate_api=False):

        self._check_model_feed(model_feed)
        self._check_service(service, version)

        self.model_feed = model_feed
        self.service    = service
        self.version    = version

        self.BDS_url = "https://dataservices-beta.metoffice.gov.uk/services/"
        self.url     = self.BDS_url + self.model_feed

        self.params = {"key"     : api_key,
                       "SERVICE" : self.service,
                       "VERSION" : self.version}

        if validate_api:
            # Uses self.params (which contains the api_key) to send a dummy
            # request.
            self._check_api_key()
        self.api_key = api_key

        # Define the root xml namespace. Can this be done by python? It is an
        # attribute of the root
        self.xmlns = "{http://www.opengis.net/wcs}"

    @staticmethod
    def _check_model_feed(model_feed):
        if model_feed not in valid_model_feeds:
            raise UserWarning("%s is an invalid model feed. Valid model feeds"\
                              " are %s" % (model_feed, valid_model_feeds))

    @staticmethod
    def _check_service(service, version):
        valid_versions = valid_services.get(service)
        if valid_versions is None:
            raise UserWarning("%s is an invalid service. Valid services"\
                              " are %s" % (service, valid_services.keys()))
        else:
            if version not in valid_versions:
                raise UserWarning("%s is an invalid version for %s service. "\
                                  "Valid versions are %s"\
                                   % (version, service, valid_versions))

    def _check_api_key(self, api_key):
        """
        Send dummy request to BDS and check response.

        """
        response = requests.get(self.url, params=self.params)
        self._check_response_status(response)

    @staticmethod
    def _check_response_status(response):
        """
        Check the status code returned by the request.

        """
        status = response.status_code
        if status != 200:
            url_message = "Here's the url that was sent:\n", response.url
            if status == 403:
                raise UserWarning("403 Error, request forbidden. This is "\
                                  "likely due to an incorrect API key, but "\
                                  "sometimes the service is temporarily "\
                                  "down. If you know your key is fine, try "\
                                  "again.\n%s") % url_message
            elif status == 404:
                raise UserWarning("404 Error, server not found.\n%s"\
                                  % url_message)
            else:
                raise UserWarning("%s Error\n%s" % (status, url_message))

    @staticmethod
    def _check_getCoverage_response(response):
        """
        Check if response is an XML file, if it is there has been an error.

        """
        if response.headers["content-type"] == 'text/xml':
            xml_str = response.text
            # This function checks for an error XML response.
            read_xml(xml_str)
            # If read_xml does not detect an error XML something has gone
            # wrong.

            raise UserWarning("getCoverage has returned an XML file (not what"\
                              " we want) but the format is not recognised. "\
                              "Here it is to look at:\n%s" % xml_str)

    @staticmethod
    def _check_bbox(bbox):
        """
        Check bbox is valid.

        """
        if type(bbox) not in [list, tuple]:
            raise UserWarning("bbox argument must be a list.")
        if len(bbox) != 4:
            raise UserWarning("bbox must contain 4 values, %s found."\
                              % len(bbox))
        bbox_flts = []
        for val in bbox:
            try:
                bbox_flts.append(float(val))
            except:
                raise UserWarning("All bbox values must be numbers.")
        # Check min and max values are sensible.
        if bbox_flts[0] > bbox_flts[2] or bbox_flts[1] > bbox_flts[3]:
            raise UserWarning("bbox min value larger than max. Format must be"\
                              " [x-min, y-min, x-max, y-max]")

    @staticmethod
    def _check_time(time):
        """
        Check time string is valid.

        """
        try:
            dateutil.parser.parse(time)
        except:
            raise UserWarning("Invalid time argument given: %s. Times must "\
                              "be strings in ISO format; '{year}-{month}-"\
                              "{day}T{hour}:{minute}:{second}Z'" % time)

    @staticmethod
    def _sort_bbox(bbox):
        """
        Convert to string format requires for BDS request.

        """
        return ",".join([str(val) for val in bbox])

    def getCapabilities(self, show=True, savepath=None):
        """
        Send a request to BDS to get an XML file containing all available
        coverages. Coverages are returned as Coverage objects in a
        CoverageList. The coverage names (seen when a coverage is printed) are
        all that are needed to send a describeCoverage request, but there are
        more attributes available and can be seen using the print_info() method
        on any coverage.

        Kwargs:

        * show: boolean
            If True, print out all the returned coverage names.

        * savepath: string or None
            If a filepath (and name) is provided, save the the returned XML
            (unless it is an XML error response).

        returns:
            CoverageList

        """
        payload = {"REQUEST" : "GetCapabilities"}
        payload.update(self.params)
        response = requests.get(self.url, params=payload)
        self._check_response_status(response)

        xml_str   = response.text
        coverages = read_getCapabilities_xml(xml_str, namespace=self.xmlns)

        if show:
            for cov in coverages:
                print cov

        if savepath:
            with open(savepath, "w") as outfile:
                outfile.write(xml_str)

        return coverages

    def describeCoverage(self, coverage_name, show=True, savepath=None):
        """
        Send a request to BDS to get an XML file containing details of a
        particular coverage. The coverage is returned as a Coverage object.
        Use the print_info() method to print out all available parameters for
        a coverage.

        Args:

        * coverage_name: string
            Available coverage names are printed by getCapabilities method.

        Kwargs:

        * show: boolean
            If True, print out all the coverage information.

        * savepath: string or None
            If a filepath (and name) is provided, save the the returned XML
            (unless it is an XML error response).

        returns:
            Coverage

        """
        payload = {"REQUEST"  : "DescribeCoverage",
                   "COVERAGE" : coverage_name}
        payload.update(self.params)
        response = requests.get(self.url, params=payload)
        self._check_response_status(response)

        xml_str  = response.text
        coverage = read_describeCoverage_xml(xml_str, namespace=self.xmlns)

        if show:
            print coverage.print_info()

        if savepath:
            with open(savepath, "w") as outfile:
                outfile.write(xml_str)

        return coverage

    def getCoverage(self, coverage_name, param_dict, stream=False):
        """
        Send a request to BDS for data specified by the coverage name and a
        parameter dictionary.

        Args:

        * coverage_name: string
            Available coverage names are printed by getCapabilities method.

        * param_dict: dictionary
            Use describeCoverage method to see available parameters and
            getParameterDictionary method to help build the param_dict
            correctly.

        Kwargs:

        * stream: boolean
            If False (default), the response content will be immediately
            downloaded.

        returns
            requests.Response

        """
        payload = {"REQUEST"  : "GetCoverage",
                   "COVERAGE" : coverage_name}
        payload.update(param_dict)
        payload.update(self.params)

        response = requests.get(self.url, params=payload, stream=stream)
        self._check_response_status(response)
        self._check_getCoverage_response(response)

        return response

    def streamCoverageToAWS(self, coverage_name, param_dict, aws_bucket_name,
                            aws_filepath, aws_access_key_id=None,
                            aws_secret_access_key=None, create_bucket=False,
                            location=Location.EU):
        """
        Make a getCoverage request and stream the response straight to AWS
        (Amazon Web Services) S3 server.

        Args:

        * coverage_name: string
            Available coverage names are printed by getCapabilities method.

        * param_dict: dictionary
            Use describeCoverage method to see available parameters and
            getParameterDictionary method to help build the param_dict
            correctly.

        * aws_bucket_name: string
            AWS groups data in buckets (easily thought of as a top level
            directory).

        * aws_filepath: string
            The filepath (including filename). Note, file extensions have no
            effect on the file content streamed so this is left to the user to
            match extentions and formats.

        Kwargs:

        * aws_access_key_id/aws_secret_access_key: string
            These are provided with an AWS account (then downloading your
            credentials). These set as environment variables these do not need
            to be given.

        * create_bucket: boolean
            If True, create a new bucket in the AWS S3 server. Note, new
            buckets much have an entierly unique name. Default is False, where
            a pre existig bucket must be specified.

        * location: Location (from boto.s3.connection)
            The location of the aws_bucket. Default is EU, also available (at
            time of writing); APNortheast, APSoutheast, APSoutheast2, SAEast,
            USWest, USWest2

        """
        response = self.getCoverage(coverage_name, param_dict, stream=True)

        s3_conn = S3Connection(aws_access_key_id, aws_secret_access_key)
        if create_bucket:
            bucket  = s3_conn.create_bucket(aws_bucket_name)
        else:
            bucket  = s3_conn.get_bucket(aws_bucket_name)
        key = bucket.new_key(aws_filepath)
        key.set_contents_from_string(response.content)

    def createCoverageCubes(self, coverage_name, param_dict):
        """
        Make a getCoverage request and load the response into an iris CubeList.

        Args:

        * coverage_name: string
            Available coverage names are printed by getCapabilities method.

        * param_dict: dictionary
            Use describeCoverage method to see available parameters and
            getParameterDictionary method to help build the param_dict
            correctly.

        """
        # Make sure the returned data is in a format iris can read.
        param_dict["FORMAT"] = "NetCDF3"

        response = self.getCoverage(coverage_name, param_dict)

        iris_filename = "_temp_iris_data.nc"
        with open(iris_filename, "w") as outfile:
            outfile.write(response.content)

        cubes = iris.load(iris_filename)

        return cubes

    def getParameterDictionary(self, format=None, crs=None, elevation=None, bbox=None, dim_run=None, time=None, dim_forecast=None,  width=None, height=None, resx=None, resy=None, resz=None, interpolation=None):
        """
        Create a dictionary of valid parameters for getCoverage method.

        Kwargs:

        * bbox: list
            Must contain 4 values in the format [x-min, y-min, x-max, y-max].
            Values can be given as integers, floats or strings.

        * dim_run: string (ISO format)
            The model run time.

        * time: string (ISO format)
            The forecast time

        * dim_forecast: string
            The time releative to the dim_run e.g. PT36H is 36 hours from the
            model run time.

        * format: string
            The format for the data to be returned in, e.g. NetCDF3

        * crs: string
            The coordinate reference system, e.g. EPSG:4326

        * width/height: integer
            The number of gridpoints in the x (width) and y (height) within
            the bounding box. Interpolation is used.

        * resx/resy/resz: float
            The size of a gridpoint in the x/y/z direction. This is an
            alternative method to specifing the width/height. Interpolation is
            used.

        * elevation: string
            The veritcal level.

        * interpolation: string
            The interpolation method used if data is re-gridded.

        returns:
            dictionary

        """
        param_dict = {}
        if bbox:
            self._check_bbox(bbox)
            bbox_str = self._sort_bbox(bbox)
            param_dict["BBOX"] = bbox_str
        if dim_run:
            self._check_time(dim_run)
            param_dict["DIM_RUN"] = dim_run
        if time:
            self._check_time(time)
            param_dict["TIME"] = time
        if dim_forecast:
            param_dict["DIM_FORECAST"] = dim_forecast
        if format:
            param_dict["FORMAT"] = format
        if crs:
            param_dict["CRS"] = crs
        if width:
            param_dict["WIDTH"] = width
        if height:
            param_dict["HEIGHT"] = height
        if resx:
            param_dict["RESX"] = resx
        if resy:
            param_dict["RESY"] = resy
        if resz:
            param_dict["RESZ"] = resz
        if elevation:
            param_dict["ELEVATION"] = elevation
        if interpolation:
            param_dict["INTERPOLATION"] = interpolation
        return param_dict
