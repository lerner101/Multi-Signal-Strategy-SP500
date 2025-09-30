'''class MovingAverageStrategy(Strategy):
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
'''
from Strategy import Strategy
import pandas as pd

class RSIStrategy(Strategy):
    '''
    Signals:
        +1 -> Buy one share if RSI < 30 and no open position
        -1 -> sell one share when RSI > 70 (overbought) and a open position
        0 -> hold 
    '''
    def __init__(self,name = 'RSI_Strategy'):
        super().__init__(name = name)
        self.tickers = None # list[str]
        self.T = None       # time length
        self.N = None       # no of tickers

    def RSI_calc(self,prices: pd.Series, window: int = 10) -> pd.Series:
        '''
        RSI calculation function to be used in compute_signals method
            10 - day RSI, change in window
        '''
        pcts = prices.pct_change()
        
        ups = pcts.clip(lower = 0)
        down = - pcts.clip(upper = 0)

        avg_up = ups.rolling(window).mean()
        avg_down = down.rolling(window).mean()

        RS = avg_up/avg_down

        RSI = 100 - (100 / (1 + RS))

        return RSI

    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        
        RSI = self.RSI_calc(prices)   

        signals = pd.DataFrame(0, index=prices.index, columns=prices.columns)

        signals[RSI < 30] = 1
        signals[RSI > 70] = -1

        return signals