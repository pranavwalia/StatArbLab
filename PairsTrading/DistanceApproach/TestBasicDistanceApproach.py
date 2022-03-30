from datetime import datetime
from turtle import distance
from BasicDistanceApproach import BasicDistanceApproach
import unittest
import pandas as pd

class TestDistanceApproach(unittest.TestCase):

    '''
    - Tests that the correct exceptions are raised when trying to pass flawed data to setPairsData or setTradeData
    - Tests that a well formed dataframe is excepted by setPairsData and setTradeData
    '''
    def testSetData(self):
        distanceClass = BasicDistanceApproach()
        #Checks that an error exception is returned from a distance class with the appropriate messsage
        def assertExceptionMessage(message: str, data):
            with self.assertRaises(Exception) as cm:
                distanceClass.setPairsData(data)
            self.assertEqual(cm.exception.args[0],message)
            with self.assertRaises(Exception) as cm:
                distanceClass.setTradeData(data)
            self.assertEqual(cm.exception.args[0],message)

        exampleDate = pd.to_datetime(datetime(2020,4,5)) 
        dfNotEnoughColumns = pd.DataFrame({'Dates' : ['date']})
        dfFirstNotDateTime = pd.DataFrame({'Price' : [1], 'Date' : [exampleDate]})
        dfNoneNumericalColumn = pd.DataFrame({'Date' : [exampleDate], 'Price1' : [1], 'Price2' : ['dog']})
        wellFormedDF = pd.DataFrame({'Date': [exampleDate], 'Price1' : [1], 'Price2' : [2.4494]})

        assertExceptionMessage(distanceClass.NotEnoughColumnsException,dfNotEnoughColumns)
        assertExceptionMessage(distanceClass.dateTimeException,dfFirstNotDateTime)
        assertExceptionMessage(distanceClass.nonNumericalException, dfNoneNumericalColumn)
        self.assertEqual(distanceClass.setPairsData(wellFormedDF),True)
        self.assertEqual(distanceClass.setTradeData(wellFormedDF),True)


if __name__ == '__main__':
    unittest.main()