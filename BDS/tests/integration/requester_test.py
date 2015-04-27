import unittest
import os
import requests
import xml.etree.ElementTree as ET
import random
import boto
from BDS.requester import BDSRequest
from BDS.coverage import Coverage, CoverageList

request = BDSRequest(api_key=os.environ['API_KEY'])

def random_item(lst):
    if len(lst) == 0:
        return None
    else:
        indx = random.randint(0, (len(lst) - 1))
        return lst[indx]

def create_random_paramDict(coverage):
    format    = random_item(coverage.formats)
    elevation = random_item(coverage.elevations)
    # Currently, some "available" CRSs return errors.
    crs       = "EPSG:4326" #random_item(coverage.CRSs)

    return request.getParameterDictionary(format, crs, elevation)

class Test_BDSRequest(unittest.TestCase):

    def test_requests(self):
        ##### Test getCapabilities #####
        getCap_path = "/tmp/testGetCap.xml"
        coverages   = request.getCapabilities(show=False, savepath=getCap_path)

        # Test returned type.
        self.assertEqual(type(coverages), CoverageList)

        # Test returned data.
        for cov in coverages:
            self.assertIsNotNone(cov.name)
            self.assertIsNotNone(cov.label)
            self.assertIsNotNone(cov.bbox)

        # Test saved XML. Element tree will only parse valid xml.
        ET.parse(getCap_path)


        ##### Test describeCoverage #####
        desCov_path = "/tmp/testDesCov.xml"
        # Choose random coverage as example.
        cov_name = random_item(coverages).name
        coverage = request.describeCoverage(cov_name, show=False,
                                            savepath=desCov_path)
        self.assertEqual(type(coverage), Coverage)

        # Test returned data.
        self.assertIsNotNone(coverage.name)
        self.assertIsNotNone(coverage.label)
        self.assertIsNotNone(coverage.bbox)
        self.assertIsNotNone(coverage.dim_runs)
        self.assertIsNotNone(coverage.times)
        self.assertIsNotNone(coverage.dim_forecasts)
        self.assertIsNotNone(coverage.formats)
        self.assertIsNotNone(coverage.CRSs)
        self.assertIsNotNone(coverage.elevations)
        self.assertIsNotNone(coverage.interpolations)

        # Test saved XML.
        ET.parse(desCov_path)


        ##### Test getCoverage #####
        param_dict = create_random_paramDict(coverage)
        response = request.getCoverage(cov_name, param_dict)

        self.assertEqual(type(response), requests.Response)
        self.assertNotEqual(response.headers['content-type'], 'text/xml')


        ##### Test createCoverageCube #####
        cube = request.createCoverageCube(cov_name, param_dict)
        # Assert a valid cube has been created.
        self.assertEqual(cube.name(), cov_name)


        # ##### Test streamCoverageToAWS #####
        aws_bucket_name = "simons-test-bucket-2345"
        aws_filepath    = "test_data.nc"

        try:
            request.streamCoverageToAWS(cov_name, param_dict,
                                        aws_bucket_name,
                                        aws_filepath)
        except:
            raise UserWarning("streamCoverageToAWS failed")
        else:
            # Delete test data
            bucket = s3_conn.get_bucket(aws_bucket_name)
            key    = bucket.new_key(aws_filepath)
            bucket.delete_key(key)


if __name__ == '__main__':
    unittest.main()
