import pandas as pd
from Strategy import Strategy   # or: from .strategy_base import Strategy
import numpy as np
from PriceLoader import get_prices


class BenchmarkStrategy(Strategy):
  """
  Buy just at beginning
  """
  def __init__(self, min_points_per_ticker: int = 2500, buy_index: int = 0):
        """
        min_points_per_ticker: filter tickers that have fewer points.
        buy_index: row index at which to place the '1' (default 0).
        """
        self.min_points_per_ticker = min_points_per_ticker
        self.buy_index = buy_index
        self.tickers = None  # list[str]
        self.T = None        # time length
        self.N = None        # number of tickers

  def compute_signals(self, prices) -> pd.DataFrame:

    
    # Signals: +1 (buy) if MA20 > MA50, -1 (sell) if MA20 < MA50, else 0
    signals = pd.DataFrame(0, index=prices.index, columns=prices.columns, dtype=int)
    signals.iloc[self.buy_index, :] = 1
    return signals


prices = get_prices()
print(BenchmarkStrategy().compute_signals(prices))