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

  def compute_signals(self, ticker_dict: dict) -> pd.DataFrame:

    # Clean & filter (mirrors _build_price_matrix but we also keep cleaned data)
    valid = {}
    for t, p in ticker_dict.items():
        if not p:
            continue
        cleaned = [float(x) for x in p if x is not None]
        if len(cleaned) >= self.min_points_per_ticker:
            valid[t] = cleaned

    if not valid:
        raise ValueError(f"No tickers with >= {self.min_points_per_ticker} prices.")

    tickers = sorted(valid.keys())
    # Common time length (right-aligned on most recent data)
    T = min(len(valid[t]) for t in tickers)

    # Build aligned price matrix (most recent T points for each ticker)
    data = {}
    for t in tickers:
        arr = valid[t]
        data[t] = arr[-T:]  #most recent

    prices = pd.DataFrame(data, columns=tickers)  # shape (T, N)
    #print(prices)

    # Save metadata
    self.tickers = tickers
    self.T = T
    self.N = len(tickers)

    
    # Signals: +1 (buy) if MA20 > MA50, -1 (sell) if MA20 < MA50, else 0
    signals = pd.DataFrame(0, index=prices.index, columns=prices.columns, dtype=int)
    signals.iloc[self.buy_index, :] = 1
    return signals


prices = get_prices()
print(BenchmarkStrategy().compute_signals(prices))