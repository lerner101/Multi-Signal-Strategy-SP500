from Strategy import Strategy
import pandas as pd

class Volatility_Breakout_Strategy(Strategy):
  """
  Signals (executed next day by the base runner):
    +1  -> BUY one share when daily return > roll 20d STD
    -1  -> SELL one share when daily return < roll 20d STD
    0  -> No action
  """
  def __init__(self,name = 'Volatility_Breakout'):
    super().__init__(name = name)
    self.tickers = None # list[str]
    self.T = None       # time length
    self.N = None       # no of tickers

  def compute_signals(self, prices) -> pd.DataFrame:
    std20 = prices.rolling(window = 20, min_periods=20).std()
    rets = prices.pct_change()
    signals = pd.DataFrame(0,index = prices.index, columns= prices.columns)
    signals[rets > std20] = 1
    signals[rets < -std20] = -1

    return signals