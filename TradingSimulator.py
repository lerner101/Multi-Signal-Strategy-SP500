import pandas as pd
import numpy as np
from dataclasses import dataclass
from BenchmarkStrategy import BenchmarkStrategy
from MovingAverageStrategy import MovingAverageStrategy
from MACDStrategy import MACDStrategy
from PriceLoader import get_prices

import pandas as pd
from dataclasses import dataclass
import math

class Simulator:
    """
    Execute a backtest using the exact logic that was in Strategy.run(),
    but with hard-coded rules:
      - act on previous day's signal
      - max 1 share per ticker per day (buy/sell)
      - no shorts
    """

    def __init__(self, strategy, prices: pd.DataFrame, initial_cash: float = 1_000_000):
        self.strategy = strategy
        self.prices = prices
        self.initial_cash = float(initial_cash)

    def run(self) -> pd.DataFrame:
        """
        Backtesting. This is hella long, so tl;dr steps are
        clean prices, get signals from `compute_signals()`, act on prev day signal, allocate holdings trades cash arrays,
         execute daily loop, mark-to-market it, and combine the df and return
        """
        # Clean data
        # sort dates, drop duplicate dates, ensure float
        P = (self.prices.sort_index()
                         .loc[~self.prices.index.duplicated()]
                         .astype(float))

        # child compute signals, basically 0 or 1
        S_raw = (self.strategy.compute_signals(P)
                               .reindex_like(P)
                               .fillna(0)
                               .clip(lower=-1, upper=1)
                               .astype(int))

        # Act on previous day's signal if requested  (hard-coded: yes)
        S_exec = S_raw.shift(1).fillna(0).astype(int)

        T, N = P.shape
        Px = P.values
        Sig = S_exec.values

        holdings = np.zeros((T, N), dtype=int)
        trades   = np.zeros((T, N), dtype=int)
        cash     = np.zeros(T, dtype=float)

        cash_t = float(self.initial_cash)
        h_prev = np.zeros(N, dtype=int)

        # Loop over each day, so we can check cash constraints, holding constraints,per day caps,
        # executions, mark-to-market
        for t in range(T):
            # desired change per ticker for day t in {-1,0,1}
            desire = Sig[t].clip(-1, 1)

            # cap per-day size  (hard-coded: 1 share per buy/sell)
            pos = desire > 0
            neg = desire < 0
            desire[pos] = 1
            desire[neg] = -1

            # lower-bound desire by -h_prev for the negative side, dont let holdings go negative NO SHORTS
            desire = np.maximum(desire, -h_prev)

            px = Px[t].astype(float)

            # Sells first (IN CASE WE NEED TO FREE UP CASH FOR OTHER BUYS)
            sell_idx = np.flatnonzero(desire < 0)
            if sell_idx.size:
                qty = -desire[sell_idx]  # positive integers (only 0 or 1)
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
                "Price":     P,
                "RawSignal": pd.DataFrame(S_raw.values,  index=P.index, columns=P.columns),
                "ExecSignal":pd.DataFrame(S_exec.values, index=P.index, columns=P.columns),
                "Trades":    pd.DataFrame(trades,        index=P.index, columns=P.columns),
                "Holdings":  pd.DataFrame(holdings,      index=P.index, columns=P.columns),
            },
            axis=1
        )
        out["Cash"] = cash
        out["TotalAssets"] = total_assets
        out.attrs["strategy_name"] = getattr(self.strategy, "name", type(self.strategy).__name__)
        return out
