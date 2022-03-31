import pandas as pd
from pandas.api.types import is_numeric_dtype
from math import sqrt
from DistanceFunctions import DistanceFunctions




'''
This class implements the basic distance approach to a pairs trading signal in 3 steps:
- normalizes price data
- Orders proposed pairs according to a distance metric
- Generates a signal according to a deviation threshold
- Outputs a backtest according to a brokerage fee template
'''
class BasicDistanceApproach():

    def __init__(self) -> None:
        self.pairs = None
        self.pairsData = None
        self.tradeData = None
        self.NotEnoughColumnsException = 'Dataframe is missing columns. Check that you have both securities and date columns'
        self.dateTimeException = 'Left-Most Column is not of type datetime64'
        self.nonNumericalException = 'Detected non-numerical data-types to the right of date column'
        self.signals = None



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
    def setSignalData(self, data: pd.DataFrame) -> bool:
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
    - Build list of all possible pairs
    - Sort list according to distance function
    - Sets the top n best pairs as the pairs field in the class
    Args:
    - distanceFunc: a function that measures the distance (see DistanceFunctions.py)
    - top: the number of pairs to select from the n best candidates

    The pairs field is a list of data frames structured as follows:
    Date | Asset_Price1 | Asset_Price2 | Asset_Price1_Normalized | Asset_Price2_Normalized | Normalized_Spread
    '''
    def generatePairs(self, distanceFunc: DistanceFunctions.__call__, top: int):
        pass

    '''
    Retrieves the stored pairs in the object. Raises an exception if the pairs have not yet been generated.
    '''
    def getPairs(self):
        if self.pairs != None:
            return self.pairs
        else:
            raise Exception('Error: Pairs have not yet been generated.')

    '''
    Adds a signal column to each data frame within the pairs list (self.pairs).
    A signal  is in the form of an integer:
    1 -> Buy the spread
    -1 -> Sell the spread
    0 -> Close the position
    '''
    def addTradeSignals():
        pass
        

    

    
