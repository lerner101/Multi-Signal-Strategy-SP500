import pandas as pd
from Strategy import Strategy

class MACDStrategy(Strategy):
    """
    MACD Strategy:
      +1 -> Buy when MACD crosses above Signal
      -1 -> Sell when MACD crosses below Signal
       0 -> Hold
    """
    def __init__(self, name="MACD", fast=12, slow=26, signal=9):
        super().__init__(name=name)
        self.fast = fast    # short EMA window
        self.slow = slow    # long EMA window
        self.signal = signal  # signal line EMA window

    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        # MACD and signal line
        ema_fast = prices.ewm(span=self.fast, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()

        # Crossovers: generate buy/sell signals
        buy = (macd > signal_line) & (macd.shift(1) <= signal_line.shift(1))
        sell = (macd < signal_line) & (macd.shift(1) >= signal_line.shift(1))

        # Signals DataFrame aligned with prices
        signals = pd.DataFrame(0, index=prices.index, columns=prices.columns, dtype=int)
        signals[buy] = 1
        signals[sell] = -1
        return signals
