import pandas as pd
from Strategy import Strategy   # or: from .strategy_base import Strategy
import numpy as np
from PriceLoader import get_prices


class BenchmarkStrategy(Strategy):
  """
  Buy just at beginning
  """
  def __init__(self, buy_index: int = 0, name="Benchmark"):
        """
        min_points_per_ticker: filter tickers that have fewer points.
        buy_index: row index at which to place the '1' (default 0).
        """
        self.buy_index = buy_index
        super().__init__(name=name)

  def compute_signals(self, prices) -> pd.DataFrame:

    
    # Signals: +1 (buy) if MA20 > MA50, -1 (sell) if MA20 < MA50, else 0
    signals = pd.DataFrame(0, index=prices.index, columns=prices.columns, dtype=int)
    signals.iloc[self.buy_index, :] = 1
    return signals

