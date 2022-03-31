import pandas as pd
from pandas.api.types import is_numeric_dtype
from math import sqrt
from DistanceFunctions import DistanceFunctions


def sample_brokerage(shares,trade_value):
    return 0.01*trade_value


class BasicDistanceApproach():
    '''
    This class implements the basic distance approach to a pairs trading signal in 3 steps:
    - normalizes price data
    - Orders proposed pairs according to a distance metric
    - Generates a signal according to a deviation threshold
    - Outputs a backtest according to a brokerage fee template
    '''

    def __init__(self) -> None:
        self.pairs = None
        self.pairsData = pd.DataFrame
        self.tradeData = None
        self.NotEnoughColumnsException = 'Dataframe is missing columns. Check that you have both securities and date columns'
        self.dateTimeException = 'Left-Most Column is not of type datetime64'
        self.nonNumericalException = 'Detected non-numerical data-types to the right of date column'
        self.signals = None


   
    @staticmethod
    def renameDateColumn(data: pd.DataFrame):
        '''
        Renames the first observed column in a pandas series with the type datetime64 to 'Date'
        '''
        for i in data.columns:
        #Makes sure the date column is renamed to 'Date' 
            #Makes later reference easier
            if data[i].dtype == 'datetime64[ns]':
                data.rename(columns={i : 'Date'}, inplace = True)
                break

   
    def setPairsData(self, data: pd.DataFrame) -> bool: 
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
        if self.__isDataWellFormed(data):
            self.renameDateColumn(data) 
            self.data = data
            return True

    
    def setSignalData(self, data: pd.DataFrame) -> bool:
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
        if self.__isDataWellFormed(data):
            #Rename the date column to date for good measure
            self.renameDateColumn(data)
            self.tradeData = data
            return True
   
    @staticmethod
    def __isDataWellFormed(data: pd.DataFrame) -> bool:
        '''
        Private Method: Do not call outside of class
        Checks whether a dataframe conforms to requirements to store in DistanceApproach class
        '''
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


    #Todo: refactor this out of the class later 
    def normalizeSeries(self, priceSeries: pd.Series):
        return (priceSeries - min(priceSeries))/(max(priceSeries-min(priceSeries)))

    
    def __normalizePairs(self):
        '''
        Private Method: Do not call outside of class
        Args:
        takes a dataframe structured as follows:
        Date | security1 | security2
        Reformats as
        Date | security1 | security2 | security1_normalized | security2_normalized | normalized_spread
        '''  
        for pair in self.pairs:
            a = pair.columns[1]
            b = pair.columns[2]
            pair[a + '_norm'] = self.normalizeSeries(pair[a])
            pair[b + '_norm'] = self.normalizeSeries(pair[b])
            pair['Spread'] = pair[a + '__norm'] - pair[b + '__norm']

    def generatePairs(self, distanceFunc: DistanceFunctions.__call__, top: int):
        '''
        Generates Pairs:
        - Build list of all possible pairs
        - Sort list according to distance function
        - Sets the top n best pairs as the pairs field in the class
        Args:
        - distanceFunc: a function that measures the distance (see DistanceFunctions.py)
        - top: the number of pairs to select from the n best candidates

        The pairs field is a list of data frames structured as follows:
        The right-most column is the spread between the two normalized asset prices.

        Date | Asset_Price1 | Asset_Price2 | Asset_Price1_Normalized | Asset_Price2_Normalized | Normalized_Spread
        '''
        allPairs = []
        for i in self.pairsData.columns:
            for j in self.pairsData.columns:
                if i != j:
                    allPairs.append(self.pairsData[['Date',i,j]])

        #Uses a lambda to calculate the distance metric for all pairs
        #
        calcDistance = lambda x: distanceFunc(self.normalizeSeries(x.iloc[1]),self.normalizeSeries(x.iloc[2]))
        allPairs.sort(key=calcDistance)
        if top <= len(allPairs):
            self.pairs = allPairs[0:top]
        self.__normalizePairs()

   
    def getPairs(self):
        '''
        Retrieves the stored pairs in the object. Raises an exception if the pairs have not yet been generated.
        '''
        if self.pairs != None:
            return self.pairs
        else:
            raise Exception('Error: Pairs have not yet been generated.')

    
    def addTradeSignals(threshold: int, brokerage):
        '''
        Performs the following modifications to self.pairs:

        1. Adds a signal column to each data frame within the pairs list (self.pairs).
        A signal  is in the form of an integer:
        1 -> Buy the spread
        -1 -> Sell the spread
        0 -> Close the position

        2. Adds a returns column - The returns generated by trading the signal

        Args:
        threshold - the unit number of standard deviations required to trigger a signal
        brokerage - a function f with f(shares: int, trade_value: int) -> int

        ------------------Trading Strategy----------------------
        If the spread exceeds the threshold of positive standard deviations - buy
        If the spread exceeds the threshold of negative standard deviations - sell
        If the spread crosses 0 - close the position
        '''
        pass
    
   
    def plotEquityCurve():
        '''
        Provided you have already added the trade signals, returns a list of plots of each equity curve for each pair
        '''
        pass
        

    

    
