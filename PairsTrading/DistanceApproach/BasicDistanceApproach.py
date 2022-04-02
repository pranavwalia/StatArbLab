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
        #Training Pairs
        self.trainPairs = List[pd.DataFrame]
        #Testing Pairs
        self.testPairs = List[pd.DataFrame]
        #Training Data
        self.dataTrain = pd.DataFrame
        #Testing Data
        self.dataTest = pd.DataFrame
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
            self.dataTrain = data
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
            self.dataTest = data
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
        for i in range(len(self.trainPairs)):
            trainPair: pd.DataFrame = self.trainPairs[i]
            testPair: pd.DataFrame = self.testPairs[i]
            a = trainPair.columns[1]
            b = trainPair.columns[2]
            anorm = a + '_norm'
            bnorm = b + '_norm'
            trainPair[anorm] = self.normalizeSeries(trainPair[a])
            trainPair[bnorm] = self.normalizeSeries(trainPair[b])
            trainPair['Spread'] = trainPair[anorm] - trainPair[bnorm]
            #Save the min and max from the train dataset to normalize the test dataset
            mina = min(trainPair[a])
            maxa = max(trainPair[a])
            minb = min(trainPair[b])
            maxb = max(trainPair[b])

            a = testPair.columns[1]
            b = testPair.columns[2]
            testPair[anorm] = self.normalizeSeries(testPair[a], mina, maxa)
            testPair[bnorm] = self.normalizeSeries(testPair[b], minb, maxb)
            testPair['Spread'] = testPair[anorm] - testPair[bnorm]


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
        tradePairs = []
        for i in self.dataTrain.columns[1:]:
            for j in self.dataTrain.columns[1:]:
                if i != j:
                    allPairs.append(self.dataTrain[['Date', i, j]])

        #Uses a lambda to calculate the distance metric for all pairs
        calcDistance = lambda x: distanceFunc(self.normalizeSeries(x.iloc[:,1]),self.normalizeSeries(x.iloc[:,2]))
        allPairs.sort(key=calcDistance)
        if top <= len(allPairs):
            allPairs = allPairs[0:top]
            self.trainPairs = allPairs 
        #Select the pairs from the test dataset for the backtest later
        for pair in allPairs:
            tradePairs.append(self.dataTest[pair.columns])
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

    
    def addTradeSignals(self, threshold: int):
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
        for i in range(len(self.trainPairs)):
            trainPair: pd.DataFrame = self.trainPairs[i]
            testPair: pd.DataFrame = self.testPairs[i]
            sigma = int
            mu = trainPair['Spread'].mean()
            squaredDiff = (trainPair['Spread'] - mu).pow(2)
            if len(trainPair.index > 0):
                sigma = sqrt(sum(squaredDiff)/(len(trainPair.index) - 1))
            else:
                raise Exception('Cannot calculate signals: price rows missing')
            
            signalTracker = [0]
            #Helper function which adds the signals to the signal tracker
            def signalLogic(val):
                f = lambda x: -1 if val >= threshold*sigma else (1 if val <= -threshold*sigma else signalTracker[-1])
                if val < 0 and signalTracker[-1] == 1 or val > 0 and signalTracker[-1] == -1:
                    signalTracker.append(0)
                    return 0
                else:
                    signal = f(val)
                    signalTracker.append(signal)
                    return signal
            #Map the signal logic onto the spread and create a new column called signal
            testPair["Signal"] = testPair["Spread"].map(signalLogic) 
    
    def computeReturns(self):
        '''
        Adds the following new columns
        - Returns Series of both Securities
        - Returns of the spread
        - Series of the equity curve
        '''
        for pair in self.testPairs:
            if not "Signal" in pair.columns:
                raise Exception("Signals have not yet been generated")
            a = pair.columns[1] + '_Returns'
            b = pair.columns[2] + '_Returns'
            pair[a] = pair.iloc[:,1].pct_change().fillna(0)
            pair[b] = pair.iloc[:,1].pct_change().fillna(0)
            pair["Returns"] = (pair.iloc[:,1] - pair.iloc[:,2]).pct_change().fillna(0) * pair["Signal"]
            #Tracks the previous values of the equity curve as we map through the returns series
            equity = [1]
            #Function to be mapped onto the returns series which  determines current value of equity curve
            def equityCurve(x):
                prev = equity[-1]
                if prev >= 0:
                    curr = prev + x*prev
                    equity.append(curr)
                    return curr
                elif prev < 0:
                    curr = prev - x*prev
                    equity.append(curr)
                    return curr

            pair['Equity_Curve'] = pair['Returns'].map(equityCurve)

    def portfolioPerformance(self):
        '''
        Only call after running computeReturns
        Returns data on the performance of the portfolio
        '''
        for pair in self.testPairs:
            print(pair.columns[1] + '_' + pair.columns[2] + ' Sharpe:',pair['Returns'].std())

    def export_backtests_to_excel(self):
        '''
        Exports finished backtests to excel and adds a chart of the equity curve
        '''
        for pair in self.testPairs:
            excel_file = pair.columns[1] + '_' +  pair.columns[2] + '.xlsx'
            sheet_name = 'Sheet1'
            writer = pd.ExcelWriter(excel_file,engine='xlsxwriter')
            pair.to_excel(writer,sheet_name=sheet_name)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:L',15)
            chart = workbook.add_chart({'type': 'line'})
            max_row = len(pair) + 1
            chart.add_series({
                'categories': ['Sheet1', 0,1,max_row,1],
                'name': ['Sheet1',0,11],
                'values': ['Sheet1', 0, 11, max_row, 11],
                'line': {'width': 1.00},
            })
            chart.set_x_axis({'name': 'Date', 'date_axis': True})
            chart.set_y_axis({'name': 'Equity_Curve', 'major_gridlines': {'visible': False}})
            chart.set_legend({'position': 'top'})
            worksheet.insert_chart('H2', chart)
            writer.save()
                 
    def plotEquityCurve():
        '''
        Provided you have already added the trade signals, returns a list of plots of each equity curve for each pair
        '''
        pass
        

    

    
