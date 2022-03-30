from re import I
from DistanceApproach import DistanceApproach
import unittest
import pandas as pd

class TestDistanceApproach(unittest.TestCase):

    def testSetPairsData(self):
        distanceClass = DistanceApproach()
        pass
        #Not enough columns
        
        #First column not datetime

        #Non-numerical column

    def testSetTradeData(self):
        distanceClass = DistanceApproach()
        self.assertEqual(1,1)
         
         

if __name__ == '__main__':
    unittest.main()