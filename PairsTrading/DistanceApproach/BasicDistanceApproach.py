import pandas as pd
from pandas.api.types import is_numeric_dtype
from math import sqrt
from DistanceFunctions import DistanceFunctions
from typing import List

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
        self.trainPairs = List[pd.DataFrame]
        self.testPairs = List[pd.DataFrame]
        self.pairsData = pd.DataFrame
        self.tradeData = pd.DataFrame
        self.NotEnoughColumnsException = 'Dataframe is missing columns. Check that you have both securities and date columns'
        self.dateTimeException = 'Left-Most Column is not of type datetime64'
        self.nonNumericalException = 'Detected non-numerical data-types to the right of date column'
        self.signals = List[pd.DataFrame]


   
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
    def normalizeSeries(self, priceSeries: pd.Series, min1 = None, max1 = None):
        min1 = min(priceSeries) if min1 == None else min1
        max1 = max(priceSeries) if max1 == None else max1
        return (priceSeries - min1)/(max1 - min1)

    
    def __normalizePairs(self):
        '''
        Private Method: Do not call outside of class
        Args:
        Takes trainpairs and test pairs structured below and reformats:
        Date | security1 | security2
        Reformats as
        Date | security1 | security2 | security1_normalized | security2_normalized | normalized_spread
        '''  
        for trainPair, testPair in self.trainPairs, self.testPairs:
            a = trainPair.columns[1]
            b = trainPair.columns[2]
            trainPair[a + '_norm'] = self.normalizeSeries(trainPair[a])
            trainPair[b + '_norm'] = self.normalizeSeries(trainPair[b])
            trainPair['Spread'] = trainPair[a + '__norm'] - trainPair[b + '__norm']
            #Save the min and max from the train dataset to normalize the test dataset
            mina = min(trainPair[a])
            maxa = max(trainPair[a])
            minb = min(trainPair[b])
            maxb = max(trainPair[b])

            a = testPair.columns[1]
            b = testPair.columns[2]
            testPair[a + '_norm'] = self.normalizeSeries(testPair[a], mina, maxa)
            testPair[b + '_norm'] = self.normalizeSeries(testPair[b], minb, maxb)
            testPair['Spread'] = testPair[a + '__norm'] - testPair[b + '__norm']


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
        allPairs = List[pd.DataFrame]
        tradePairs = List[pd.DataFrame]
        for i in self.pairsData.columns:
            for j in self.pairsData.columns:
                if i != j:
                    allPairs.append(self.pairsData[['Date', i, j]])

        #Uses a lambda to calculate the distance metric for all pairs
        calcDistance = lambda x: distanceFunc(self.normalizeSeries(x.iloc[1]),self.normalizeSeries(x.iloc[2]))
        allPairs.sort(key=calcDistance)
        if top <= len(allPairs):
            allPairs = allPairs[0:top]
            self.trainPairs = allPairs 
        #Select the pairs from the test dataset for the backtest later
        for pair in allPairs:
            tradePairs.append(self.tradeData[pair.columns])
        self.testPairs = tradePairs     
        self.__normalizePairs()

   
    def getPairs(self):
        '''
        Retrieves the stored pairs in the object. Raises an exception if the pairs have not yet been generated.
        '''
        if self.trainPairs != None:
            return self.trainPairs
        else:
            raise Exception('Error: Pairs have not yet been generated.')

    
    def addTradeSignals(self, threshold: int, brokerage):
        '''
        Performs the following modifications to self.pairs:

        1. Adds a signal column to each data frame within the pairs list (self.pairs).
        A signal  is in the form of an integer:
        1 -> Long A Short B
        -1 -> Short A Long B
        0 -> Flat

        2. Adds a returns column - The returns generated by trading the signal

        Args:
        threshold - the unit number of standard deviations required to trigger a signal
        brokerage - a function f with f(shares: int, trade_value: int) -> int

        ------------------Trading Strategy----------------------
        If the spread exceeds the threshold of positive standard deviations - buy
        If the spread exceeds the threshold of negative standard deviations - sell
        If the spread crosses 0 - close the position
        '''
        for pair in self.trainPairs:
            sigma = int
            mu = pair['Spread'].mean
            squaredDiff = (pair['Spread'] - mu)**2
            min1 = min(pair.iloc[1])
            max1 = min(pair.iloc[1])
            min2 = min(pair.iloc[2])
            max2 = max(pair.iloc[2])
            if len(pair.index > 0):
                sigma = sqrt(sum(squaredDiff)/(len(pair.index) - 1))
            else:
                raise Exception('Cannot calculate signals: price rows missing')
            
            signalTracker = List[int]
            def signalLogic(val):
                f = lambda x: 1 if val >= threshold*sigma else (-1 if val <= -threshold*sigma else 0)
                if len(signalTracker) == 0:
                    signal = f(val)
                    signalTracker.append(signal)
                    return signal 
                else:
                    if val < 0 and signalTracker[-1] == 1 or val > 0 and signalTracker[-1] == -1:
                        signalTracker.append(0)
                        return 0
                    else:
                        signal = f(val)
                        signalTracker.append(signal)
                        return signal

                
         
    def plotEquityCurve():
        '''
        Provided you have already added the trade signals, returns a list of plots of each equity curve for each pair
        '''
        pass
        

    

    
