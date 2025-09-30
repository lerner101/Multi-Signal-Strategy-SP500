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

    def RSI_calc(self,prices: pd.DataFrame) -> int:
        # 10 day RSI 
        data = prices[-10:]
        pcts = data.pct_change()
        up_moves = pcts[pcts > 0]
        down_moves = pcts[pcts > 0]

        RSI = 100 - 100 / (1 - (up_moves.mean()/down_moves.mean()))

        return RSI

    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        x = self.RSI_calc(prices)
        P = 0 
        signals = [0] * 10
        
        if P == 0 and x < 30: # buy
            signals.append(1)
            P = 1
        elif P == 1 and x > 70: # sell
            signals.append(-1)
            P = 0
        elif P == 1 and x < 70: # hold
            signals.append(1)
        else: 
            signals.append(0)

        return signals