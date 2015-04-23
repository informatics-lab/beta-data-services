import unittest
import os
import xml.etree.ElementTree as ET
from BDS.requester import BDSRequest
from BDS.coverage import Coverage, CoverageList

class Test_BDSRequest(unittest.TestCase):
    def setUp(self):
        self.req = BDSRequest(api_key=os.environ['API_KEY'])


class Test__check_model_feed(Test_BDSRequest):
    def test_bad_model_feed(self):
        self.assertRaises(UserWarning, self.req._check_model_feed, "bad_feed")


class Test__check_service(Test_BDSRequest):
    def test_bad_service(self):
        self.assertRaises(UserWarning, self.req._check_service, "bad_service",
                          "1.0")

    def test_bad_version(self):
        self.assertRaises(UserWarning, self.req._check_service, "WCS",
                          "99.12345")


class Test_response_functions(Test_BDSRequest):
    def setUp(self):
        super(Test_response_functions, self).setUp()
        # Create dummy response class.
        class Response(object):
            def __init__(self, status_code, url, headers, text):
                self.status_code = status_code
                self.url = url
                self.headers = headers
                self.text = text

        self.response = Response(200, "www.test.com", {}, "text")


class Test__check_response_status(Test_response_functions):
    def test_403_error(self):
        self.response.status_code = 403
        self.assertRaises(UserWarning, self.req._check_response_status,
                          self.response)

    def test_404_error(self):
        self.response.status_code = 404
        self.assertRaises(UserWarning, self.req._check_response_status,
                          self.response)

    def test_other_error(self):
        # Any status_code not 200 is considered an error.
        self.response.status_code = 101
        self.assertRaises(UserWarning, self.req._check_response_status,
                          self.response)


class Test__check_getCoverage_response(Test_response_functions):
    def test_xml_response(self):
        # If getCoverage returns an XML response, an error has occured. The
        # response header specifies the type of response. Check XML raises an
        # error.
        self.response.headers["content-type"] = "text/xml"
        # Added dummy xml string.
        self.response.text = '<?xml version="1.0" encoding="UTF-8"?>'\
        '<ExceptionReport version="1.0" xmlns="http://www.opengis.net/ows">'\
          '<Exception exceptionCode="CoverageNotDefined">'\
            '<ExceptionText>Test error</ExceptionText>'\
          '</Exception>'\
        '</ExceptionReport>'
        self.assertRaises(UserWarning, self.req._check_getCoverage_response,
                          self.response)


class Test__check_bbox(Test_BDSRequest):
    def test_bad_type(self):
        # Must be a list (or tuple).
        self.assertRaises(UserWarning, self.req._check_bbox, "not a list")

    def test_bad_length(self):
        # Must have four items.
        self.assertRaises(UserWarning, self.req._check_bbox, [1,2,3])

    def test_bad_value(self):
        # Values must be numeric.
        self.assertRaises(UserWarning, self.req._check_bbox, [1,2,3,"d"])

    def test_mix_type_values(self):
        # The type does not matter so long as values are numeric.
        self.req._check_bbox(["1",2.3,4,"5.5"])

    def test_bad_format(self):
        # Must have format [x-min, y-min, x-max, y-max].
        self.assertRaises(UserWarning, self.req._check_bbox, [10,20,1,2])


class Test__sort_time(Test_BDSRequest):
    def test_bad_dates(self):
        self.assertRaises(UserWarning, self.req._sort_time, "bad_date")

    def test_valid_dates(self):
        vaild_date = "2015-04-21T00:00:00Z"
        self.assertEqual(vaild_date, self.req._sort_time("2015-04-21T"))
        self.assertEqual(vaild_date, self.req._sort_time("21/4/2015"))
        self.assertEqual(vaild_date, self.req._sort_time("21st April 2015"))


class Test__sort_bbox(Test_BDSRequest):
    def test_return_str(self):
        self.assertEqual("1,2,3,4", self.req._sort_bbox([1,2,3,4]))


class Test__send_request(Test_BDSRequest):
    def setUp(self):
        pass


class Test_getCapabilities(Test_BDSRequest):
    def test_return_type(self):
        coverages = self.req.getCapabilities(show=False)
        self.assertEqual(type(coverages), CoverageList)

    def test_save_xml(self):
        # Check XML response is saved properly.
        self.req.getCapabilities(show=False, savepath="/tmp/testGetCap.xml")
        root = ET.parse("/tmp/testGetCap.xml")


class Test_describeCoverage(Test_BDSRequest):
    def setUp(self):
        # Integration test
        pass


class Test_getCoverage(Test_BDSRequest):
    def setUp(self):
        # Integration test
        pass


class Test_streamCoverageToAWS(Test_BDSRequest):
    def setUp(self):
        # Integration test
        pass


class Test_createCoverageCubes(Test_BDSRequest):
    def setUp(self):
        # Integration test
        pass


class Test_getParameterDictionary(Test_BDSRequest):
    def setUp(self):
        super(Test_getParameterDictionary, self).setUp()
        self.bbox          = [-14.0, 7.0, 47.5, 61.0]
        self.dim_run       = "2015-04-22T03:00:00Z"
        self.time          = "2015-04-23T03:00:00Z"
        self.dim_forecast  = "PT12H"
        self.format        = "NetCDF3"
        self.crs           = "EPSG:4326"
        self.width         = 100
        self.height        = 100
        self.resx          = 0.5
        self.resy          = 0.5
        self.resz          = 1.0
        self.elevation     = "0-1500m"
        self.interpolation = "bilinear"

    def test_params_in_dict(self):
        params = self.req.getParameterDictionary(bbox=self.bbox,
                                                 format=self.format,
                                                 crs=self.crs)

if __name__ == '__main__':
    unittest.main()
