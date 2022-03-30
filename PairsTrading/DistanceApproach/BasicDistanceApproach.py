import pandas as pd
from pandas.api.types import is_numeric_dtype

'''
This class stores distance functions that can be passed to the calculate pairs function of the DistanceApproach Class.
'''
class DistanceFunctions():
    def __init(self) -> None:
        pass
    '''
    Simple Euclidean Distance
    '''
    def euclideanDistance(a,b):
        return (b-a)**2

'''
This class implements the distance approach to a pairs trading signal in 3 steps:
- Orders and ranks pairs according to some distance metric
- Generates a signal according to a threshold
- Outputs a backtest according to a brokerage fee template
'''
class BasicDistanceApproach():

    def __init__(self) -> None:
        self.pairsData = None
        self.tradeData = None
        self.NotEnoughColumnsException = 'Dataframe is missing columns. Check that you have both securities and date columns'
        self.dateTimeException = 'Left-Most Column is not of type datetime64'
        self.nonNumericalException = 'Detected non-numerical data-types to the right of date column'



    '''
    This Function sets the data set for generating possible pairs.

    Make sure your data frame is formated according to the following structure
    DateTime | Price Series A | Price Series B | Price Series C |...
    Raises Exception if:
    - Data doesn't have more than two columns
    - Left-Most column is not of type datetime64
    - If there are non-numerical data types 
    Returns true if we can successfully set the pairs data
    '''
    def setPairsData(self, data: pd.DataFrame) -> bool: 
        if self.isDataWellFormed(data):
            self.data = data
            return True

    '''
     This Function sets the data set for simulating trade data.

    Make sure your data frame is formated according to the following structure
    DateTime | Price Series A | Price Series B | Price Series C |...
    Raises Exception if:
    - Data doesn't have more than two columns
    - Left-Most column is not of type datetime64
    - If there are non-numerical data types 
    Returns true if we can successfully set the pairs data
    '''
    def setTradeData(self, data: pd.DataFrame) -> bool:
        if self.isDataWellFormed(data):
            self.tradeData = data
            return True
    '''
    Checks whether a dataframe conforms to requirements to store in DistanceApproach class
    '''
    @staticmethod
    def isDataWellFormed(data: pd.DataFrame) -> bool:

        t = lambda x: is_numeric_dtype(x) 
        if len(data.columns) <= 1:
            raise Exception('Dataframe is missing columns. Check that you have both securities and date columns')
        elif data.dtypes[0] != 'datetime64[ns]':
           raise Exception('Left-Most Column is not of type datetime64')
        #Check if there is a non-numerical column to the right of date column
        elif False in list(data.apply(t)[1:]):
            raise Exception('Detected non-numerical data-types to the right of date column')
        else:
            return True

    '''
    Generates Pairs:
    Returns a dataframe with all the pair names and their distance values
    '''
    def generatePairs(self,distanceFunc):
        pass
        

    

    
