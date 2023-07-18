import unittest
from .. cropstage import CropStage # type: ignore
from array import array

__author__ = "Steven B. Hoek"

class TestAreaFractions(unittest.TestCase):
    test_class = None
    
    def test_sum_of_fractions_per_stage(self):
        # Constant
        eps: float = 0.0000001
        
        # Test for different values of the spreading period
        print("Testing area time fractions\n")
        print("sp month sum_of_fractions")
        for x in range(3, 10, 1):
            sp = x / 4
            for month in range(1,13):
                arr = array('f', 5 * [0.0])
    
                # Let's calculate things for a crop stage starting in the current month
                mycropstage = CropStage(startperiod=month, time=0.5, duration=0.5, sp=sp)
                for period in range(month, month+5):
                    arr[period - mycropstage.start] = mycropstage.area_fraction(period)
                print(sp, month, sum(arr))
                testmsg = "Sum of area fractions for month %s and sp %s not close enough to 1.0!"
                #self.assertLess(abs(sum(arr) - 1.0), eps, testmsg % (month, sp))
                
        # Close
        print("\n")
        
def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAreaFractions))
    return suite