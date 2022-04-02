import pandas as pd

'''
This class stores distance functions that can be passed to the calculate pairs function of the DistanceApproach Class.
'''
class DistanceFunctions():
    def __init__(self) -> None:
        pass
    '''
    The sum of the squared distances between two securities
    '''
    @staticmethod
    def sumSquaredDistance(priceSeriesA: pd.Series, priceSeriesB: pd.Series) -> float:
        squaredDifferenceSum = ((priceSeriesB-priceSeriesA)**2)
        return sum(squaredDifferenceSum)