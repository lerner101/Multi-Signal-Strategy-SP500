from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd
from pathlib import Path
from PriceLoader import get_prices

# NOTE: My thoughts
# I wanna standardise 3 things,
# 1. Input/outputs (we using dataframe)
# 2. hooks that each child must defineto add indiciators, basically just strategy computation and computation of
# signals in {-1, 0, 1} or {0, 1} shaped df, aligned to the prices
# 3. All folow same constraints given in assignment, but I write here for easy ref
# No shorts, only 1 share per buy signal, act on prev days signal, starting 1m cash, track holdings, cash and total assets

"""
@dataclass
class StrategyConfig:
    # To ensure all strategies follows the same constraint

    initial_cash: float = 1000000
    act_on_prev_signal: bool = True  # so WE NEED to shift(1)
    max_sell_per_tick: int = 1
    max_buy_per_tick: int = 1  # “Only 1 share per buy signal”
    price_col: str = "Close"

    data_dir: str = "sp500_adj_close" # for us to pull data later
"""

class Strategy(ABC):
    """
    Base class. child strategies only need to implement `compute_signals(prices)`.
    - prices is a (T×N) DataFrame: index=Date, columns=tickers, values=Close.
    - signals in {-1, 0, 1} but we can never go short
    """

    def __init__(self, name: str, config: Optional[StrategyConfig] = None):
        """
        Name: name of strategy so easy to keep track ltr
        config autoamtically set using dataclass
        """
        self.name = name
        # self.config = config or StrategyConfig()

    # Abstract methods for child to implement
    @abstractmethod
    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Return a (T×N) DataFrame of signals, aligned to `prices` df
        with integer values in {-1, 0,1}. 1 means buy share next day, 0 means do nothing, -1 sell
        """
        ...
