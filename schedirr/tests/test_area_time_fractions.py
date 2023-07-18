import unittest
from .. cropstage import CropStage # type: ignore
from math import floor
from array import array

__author__ = "Steven B. Hoek"

class TestAreaTimeFractions(unittest.TestCase):
    test_class = None
    
    def test_sum_of_fractions_per_month(self):
        # Constants
        eps: float = 0.0000001
        N = 2 # number of stages per month
        duration = 0.5
        
        # Test for different values of the spreading period
        print("Testing area time fractions\n")
        print("sp month sum_of_fractions")
        for x in range(3, 10, 1):
            sp = x / 4
            L: int = floor(sp - eps) + 1
            M: int = (L + 1) * N
            
            # Loop over the months
            arr = array('f', M * [0.0])
            for month in range(1,13):
                # Reset array
                for k in range(M): arr[k] = 0.0
                
                # Loop over the months of which the stages continue into the current month
                for k in range(L + 1):
                    # Loop over the stages belonging to those months
                    for i in range(N):
                        mycropstage = CropStage(startperiod=month, time=i*duration, duration=duration, sp=sp)
                        atf = mycropstage.area_time_fraction(month)
                        arr[i*N + k] = atf
                print(sp, month, sum(arr))
                testmsg = "Sum of area fractions for month %s and sp %s not close enough to 1.0!"
                #self.assertLess(abs(sum(arr) - 1.0), eps, testmsg % (month, sp))
            
        # Close
        print("\n")
    
def suite():
    """ This defines all the tests of a module"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAreaTimeFractions))
    return suite    