import unittest
from models import TimeSeries, TimeSeriesCollection
import pandas as pd
import numpy as np

class TestModels(unittest.TestCase):
    """
    Class containing all the tests for the submodule Optimizers
    """
    tickers1 = {
        "asset1": {
          "2024-06-26": 1,
          "2024-06-27": 2,
          "2024-06-28": 3,
        }
    }

    tickers2 = {
        "asset2": {
          "2024-06-26": 10,
          "2024-06-27": 8,
          "2024-06-28": 6,
        }
    }
    
    def test_timeseries(self):
        timeseries = TimeSeries(series=self.tickers1)
        self.assertEqual(type(timeseries.to_pandas_dataframe()),pd.DataFrame)
        self.assertEqual(timeseries.returns, [1, 0.5])
        self.assertEqual(timeseries.variance(),0.125)
        self.assertEqual(timeseries.mean_return(),0.75)


        timeseries = TimeSeries(series=self.tickers2)
        self.assertEqual(type(timeseries.to_pandas_dataframe()),pd.DataFrame)
        self.assertEqual(timeseries.returns, [1, 0.5])
        self.assertEqual(timeseries.variance(),0.125)
        self.assertEqual(timeseries.mean_return(),0.75)
    
    #def test_timeseriescollection(self):
    #    timeseries1 = TimeSeries(series=self.tickers1)
    #    timeseries2 = TimeSeries(series=self.tickers2)
    #    timeseriescollection = TimeSeriesCollection(collection=[timeseries1, timeseries2])
    #    
    #    print(timeseriescollection.variances())
    #    print(timeseriescollection.all_returns())
    #    print(timeseriescollection.covariance())
    #    print(timeseriescollection.to_dataframe())
        
        

if __name__ == "__main__":
    unittest.main()
