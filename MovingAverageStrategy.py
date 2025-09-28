import pandas as pd
from Strategy import Strategy   # or: from .strategy_base import Strategy

class MovingAverageStrategy(Strategy):
    """
    Signals (executed next day by the base runner):
      +1  -> BUY one share when MA20 crosses ABOVE MA50
      -1  -> SELL one share when MA20 crosses BELOW MA50
       0  -> HOLD
    """

    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        # Rolling means; min_periods ensures we don't trade before both MAs exist
        ma20 = prices.rolling(window=20, min_periods=20).mean()
        ma50 = prices.rolling(window=50, min_periods=50).mean()

        # Crossovers
        above_yday = ma20.shift(1) > ma50.shift(1)
        above_today = ma20 > ma50

        cross_up   = (~above_yday) & (above_today)   # 0/1 boolean
        cross_down = (above_yday) & (~above_today)   # 0/1 boolean

        signals = cross_up.astype(int) - cross_down.astype(int)  # in {-1,0,1}

        # Don’t trade where MAs aren’t valid yet
        valid = ma50.notna() & ma20.notna()
        signals = signals.where(valid, 0).astype(int)

        return signals

