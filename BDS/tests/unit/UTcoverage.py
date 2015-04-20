import unittest
from BDS.coverage import Coverage, CoverageList

class Test_Coverage(unittest.TestCase):
    def test_print_info(self):
        cov1 = Coverage(name="name1", formats="NetCDF3")
        cov1 = Coverage(name="name2", bbox=[1,2,3,4])
