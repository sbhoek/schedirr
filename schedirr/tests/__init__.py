import unittest
from . import test_area_fractions
from . import test_area_time_fractions 

def make_test_suite():
    """Assemble test suite and return it
    """
    allsuites = unittest.TestSuite([test_area_fractions.suite(), test_area_time_fractions.suite()])
    
    return allsuites

def test_all():
    """Assemble test suite and run the test using the TextTestRunner
    """
    allsuites = make_test_suite()
    unittest.TextTestRunner(verbosity=2).run(allsuites)