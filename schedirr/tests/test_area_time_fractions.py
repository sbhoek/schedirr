import unittest
from .. cropstage import CropStage

__author__ = "Steven B. Hoek"

class TestAreaTimeFractions(unittest.TestCase):
    test_class = None
    
    def test_sum_of_fractions_per_month(self):
        pass
    
def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAreaTimeFractions))
    return suite    