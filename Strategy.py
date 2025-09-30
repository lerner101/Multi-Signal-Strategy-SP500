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


@dataclass
class StrategyConfig:
    """
    To ensure all strategies follows the same constraint
    """
    initial_cash: float = 1000000
    act_on_prev_signal: bool = True  # so WE NEED to shift(1)
    max_sell_per_tick: int = 1
    max_buy_per_tick: int = 1  # “Only 1 share per buy signal”
    price_col: str = "Close"

    data_dir: str = "sp500_adj_close" # for us to pull data later

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
        self.config = config or StrategyConfig()

    # Abstract methods for child to implement
    @abstractmethod
    def compute_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Return a (T×N) DataFrame of signals, aligned to `prices` df
        with integer values in {-1, 0,1}. 1 means buy share next day, 0 means do nothing, -1 sell
        """
        ...

    # METHODS
    def run_strategy(self):
        """
        Method to pull all clean and avail SP500 data and then run backtest
        """
        P = get_prices()
        return self.run(P)

    def run(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Backtesting. This is hella long, so tl;dr steps are
        clean prices, get signals from `compute_signals()`, act on prev day signal, allocate holdings trades cash arrays,
         execute daily loop, mark-to-market it, and combine the df and return

        """
        # Clean data
        # sort dates, drop duplicate dates, ensure float
        P = (prices.sort_index()
                   .loc[~prices.index.duplicated()]
                   .astype(float))

        # child compute signals, basically 0 or 1
        S_raw = (self.compute_signals(P)
                   .reindex_like(P)
                   .fillna(0)
                   .clip(lower=-1, upper=1)
                   .astype(int))

        # Act on previous day's signal if requested
        S_exec = (S_raw.shift(1).fillna(0).astype(int)
                  if self.config.act_on_prev_signal else S_raw)

        T, N = P.shape
        Px = P.values
        Sig = S_exec.values

        holdings = np.zeros((T, N), dtype=int)
        trades = np.zeros((T, N), dtype=int)
        cash = np.zeros(T, dtype=float)

        cash_t = float(self.config.initial_cash)
        h_prev = np.zeros(N, dtype=int)

        # Loop over each day, so we can check cash constraints, holding constraints,per day caps,
        # executions, mark-to-market
        for t in range(T):
            # desired change per ticker for day t in {-1,0,1}
            desire = Sig[t].clip(-1, 1)

            # cap per-day size
            pos = desire > 0
            neg = desire < 0
            desire[pos] = np.minimum(desire[pos], self.config.max_buy_per_tick)  # 0 or 1
            desire[neg] = -np.minimum(-desire[neg], self.config.max_sell_per_tick)  # 0 or -1

            # lower-bound desire by -h_prev for the negative side, dont let holdings go negative NO SHORTS
            desire = np.maximum(desire, -h_prev)

            px = Px[t].astype(float)

            # Sells first (IN CASE WE NEED TO FREE UP CASH FOR OTHER BUYS)
            sell_idx = np.flatnonzero(desire < 0)
            if sell_idx.size:
                qty = -desire[sell_idx]  # positive integers
                proceeds = (qty * px[sell_idx]).sum()
                cash_t += proceeds
                h_prev[sell_idx] -= qty
                trades[t, sell_idx] = -qty  # negative trades recorded

            #  Then buys
            buy_idx = np.flatnonzero(desire > 0)
            for j in buy_idx:
                cost = px[j]
                if cost <= cash_t:
                    cash_t -= cost
                    h_prev[j] += 1
                    trades[t, j] = 1

            holdings[t] = h_prev
            cash[t] = cash_t

        total_assets = cash + (holdings * Px).sum(axis=1)

        out = pd.concat(
            {
                "Price": P,
                "RawSignal": pd.DataFrame(S_raw.values, index=P.index, columns=P.columns),
                "ExecSignal": pd.DataFrame(S_exec.values, index=P.index, columns=P.columns),
                "Trades": pd.DataFrame(trades, index=P.index, columns=P.columns),
                "Holdings": pd.DataFrame(holdings, index=P.index, columns=P.columns),
            },
            axis=1
        )
        out["Cash"] = cash
        out["TotalAssets"] = total_assets
        out.attrs["strategy_name"] = self.name
        out.attrs["config"] = self.config
        return out
