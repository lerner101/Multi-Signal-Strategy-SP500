import pandas as pd
from Strategy import Strategy   # or: from .strategy_base import Strategy
import numpy as np
from PriceLoader import get_prices


class MovingAverageStrategy(Strategy):
  """
  Signals (executed next day by the base runner):
    +1  -> BUY one share when MA20 crosses ABOVE MA50
    -1  -> SELL one share when MA20 crosses BELOW MA50
      0  -> HOLD
  """
  def __init__(self, name="MovingAverage"):
        """
        min_points_per_ticker: filter tickers that have fewer points.
        """
        super().__init__(name=name)
        self.tickers = None  # list[str]
        self.T = None        # time length
        self.N = None        # number of tickers

  def compute_signals(self, prices) -> pd.DataFrame:
    """
    Generate daily signals for all valid tickers using only `ticker_dict`.
      +1 -> BUY when 20-day MA > 50-day MA
      -1 -> SELL when 20-day MA < 50-day MA
       0 -> HOLD otherwise
    Input: Prices is a dataframe from get_prices()
    NOTE: IT IS ALREADY CLEANED UP, WITH DATES ALIGNED.
    """

    # Rolling means
    ma20 = prices.rolling(window=20, min_periods=20).mean() #MA20
    ma50 = prices.rolling(window=50, min_periods=50).mean() # MA50

    # check signals
    # if == then this gives 0, do nth
    signals = (ma20 > ma50).astype(int) - (ma20 < ma50).astype(int)

    # make sure non-nan
    signals = signals.where(ma20.notna() & ma50.notna(), 0).astype(int)

    return signals