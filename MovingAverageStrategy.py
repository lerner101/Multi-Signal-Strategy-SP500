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
    """
    Generate daily signals for all valid tickers using only `ticker_dict`.
      +1 -> BUY when 20-day MA > 50-day MA
      -1 -> SELL when 20-day MA < 50-day MA
       0 -> HOLD otherwise

    Notes:
    - We right-align series and truncate to the shortest length so rows line up
      on the most recent dates.
    - Requires at least `min_points_per_ticker` points per ticker.
    """

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

    # Rolling means
    ma20 = prices.rolling(window=20, min_periods=20).mean()
    ma50 = prices.rolling(window=50, min_periods=50).mean()

    # Signals: +1 (buy) if MA20 > MA50, -1 (sell) if MA20 < MA50, else 0
    signals = pd.DataFrame(0, index=prices.index, columns=prices.columns, dtype=int)
    signals[ma20 > ma50] = 1
    signals[ma20 < ma50] = -1

    # Zero out early rows where MAs aren't defined yet (first 50)
    valid_mask = ma20.notna() & ma50.notna()
    signals = signals.where(valid_mask, 0).astype(int)

    return signals


prices = get_prices()
print(prices)
# print(MovingAverageStrategy().compute_signals(prices))