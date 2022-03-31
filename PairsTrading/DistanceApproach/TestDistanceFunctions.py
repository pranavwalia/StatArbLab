from datetime import date, datetime
import unittest
from DistanceFunctions import DistanceFunctions
import pandas as pd
'''
Tests the distance functions
'''
class TestDistanceFunctions(unittest.TestCase):
    '''
    Tests the sum of squared difference function
    '''
    def testSumSquaredDifference(self):
        d = DistanceFunctions()
        exampleDate1 = pd.to_datetime(datetime(2019,1,1))
        exampleDate2 = pd.to_datetime(datetime(2019,1,2))
        exampleDate3 = pd.to_datetime(datetime(2019,1,3))
        exampleDate4 = pd.to_datetime(datetime(2019,1,4))
        priceDF = pd.DataFrame({'Date' : [exampleDate1, exampleDate2, exampleDate3, exampleDate4], 'Price1' : [1, 2, 1, 3],'Price2' : [1, 3, 4, 1]}) 

        sumSquares = d.sumSquaredDistance(priceDF["Price1"],priceDF["Price2"])
        self.assertEqual(sumSquares,14)


if __name__ == '__main__':
    unittest.main()
        
