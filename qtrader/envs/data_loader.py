# scientific computing
import numpy as np
import pandas as pd

import os
import typing

# market data provider
import quandl
quandl.ApiConfig.api_key = os.environ.get('QUANDL_API_KEY')


class Finance:
    """Market Data Wrapper."""
    _col = 'Adj. Close'

    @classmethod
    def _get(cls,
             ticker: str,
             **kwargs):
        """Helper method for `web.DataReader`.

        Parameters
        ----------
        ticker: str
            Ticker name
        **kwargs: dict
            Arguments for `quandl.get`
        Returns
        -------
        df: pandas.DataFrame
            Table of prices for `ticker`
        """
        return quandl.get('WIKI/%s' % ticker, **kwargs)

    @classmethod
    def _csv(cls,
             root: str,
             ticker: str):
        """Helper method for loading prices from csv files.

        Parameters
        ----------
        root: str
            Path of csv file
        ticker: str
            Ticker name
        """
        df = pd.read_csv(root, index_col='Date',
                         parse_dates=True).sort_index(ascending=True)
        return df[ticker]

    @classmethod
    def Returns(cls,
                tickers: typing.List[str],
                start_date: str = None,
                end_date: str = None,
                freq: str = 'B',
                csv: typing.Optional[str] = None):
        """Get daily returns for `tickers`.

        Parameters
        ----------
        tickers: list
            List of ticker names
        freq: str
            Resampling frequency
        Returns
        -------
        df: pandas.DataFrame
            Table of Returns of Adjusted Close prices for `tickers`
        """
        return cls.Prices(tickers,
                          start_date,
                          end_date,
                          freq,
                          csv).pct_change()[1:]

    @classmethod
    def Prices(cls,
               tickers: typing.List[str],
               start_date: str = None,
               end_date: str = None,
               freq: str = 'B',
               csv: typing.Optional[str] = None):
        """Get daily prices for `tickers`.

        Parameters
        ----------
        tickers: list
            List of ticker names
        freq: str
            Resampling frequency
        Returns
        -------
        df: pandas.DataFrame | pandas.Series
            Table of Adjusted Close prices for `tickers`
        """
        if isinstance(csv, str):
            df = pd.DataFrame.from_dict(
                {ticker: cls._csv(csv, ticker)
                 for ticker in tickers}).loc[start_date:end_date]
        else:
            df = pd.DataFrame(
                {ticker: cls._get(ticker, start_date=start_date,
                                  end_date=end_date)[cls._col]
                 for ticker in tickers})
        # if len(df.columns) == 1:
        #     df = df[df.columns[0]]
        return df.sort_index(ascending=True).resample(freq).last()
