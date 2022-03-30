from datetime import datetime
from re import I
from turtle import distance
from DistanceApproach import DistanceApproach
import unittest
import pandas as pd

class TestDistanceApproach(unittest.TestCase):

    def testSetPairsData(self):
        distanceClass = DistanceApproach()
        #Not Enough Columns in DF
        dfNotEnoughColumns = pd.DataFrame({'Dates' : ['date']})
        self.assertRaises(Exception,distanceClass.setPairsData,dfNotEnoughColumns) 
        #First column not datetime
        dfFirstNotDateTime = pd.DataFrame({'Price' : [1], 'Date' : [datetime(2020,4,5)]})
        self.assertRaises(Exception, distanceClass.setPairsData, dfFirstNotDateTime)
        #Non-numerical column
        dfNoneNumericalColumn = pd.DataFrame({'Date' : [datetime(2020,1,2)], 'Price1' : [1], 'Price2' : ['dog']})
        self.assertRaises(Exception, distanceClass.setPairsData, dfNoneNumericalColumn)
        print('SetPairsData Test Passed')


    def testSetTradeData(self):
        pass
        
         

if __name__ == '__main__':
    unittest.main()