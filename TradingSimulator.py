import pandas as pd
from dataclasses import dataclass
from BenchmarkStrategy import BenchmarkStrategy
from MovingAverageStrategy import MovingAverageStrategy
from PriceLoader import get_prices

import pandas as pd
from dataclasses import dataclass
import math

@dataclass
class Trade:
    date: pd.Timestamp
    ticker: str
    side: str    # 'BUY' or 'SELL'
    qty: int
    price: float
    cash_after: float

class Simulator:
    def __init__(self, cash, strategy: str, prices: pd.DataFrame, signals: pd.DataFrame):
        """
        prices: DataFrame indexed by date, columns = tickers, values = prices
        signals: DataFrame aligned with prices (same index/columns), values in {-1,0,1}
        """
        self.cash = float(cash)
        self.strategy = strategy.lower()
        self.prices = prices.sort_index()
        self.signals = signals.reindex_like(self.prices).fillna(0).astype(int)

    def run(self):
        tickers = list(self.prices.columns)
        positions = {t: 0 for t in tickers}
        trades = []
        cash_series = []
        value_series = []

        for dt in self.prices.index:
            px_row = self.prices.loc[dt]
            sig_row = self.signals.loc[dt]

            # --- 1) Execute sells first (close all on -1)
            for t in tickers:
                sig, px = sig_row[t], px_row[t]
                if sig == -1 and positions[t] > 0 and pd.notna(px):
                    qty = positions[t]
                    self.cash += qty * px
                    positions[t] = 0
                    trades.append(Trade(dt, t, "SELL", qty, float(px), self.cash))

            # --- 2) Execute buys using shared cash
            # Benchmark: allocate today's available cash equally across all +1 signals
            if self.strategy == "benchmark":
                to_buy = [t for t in tickers if sig_row[t] == 1 and pd.notna(px_row[t])]
                n = len(to_buy)
                if n > 0 and self.cash > 0:
                    per_name_budget = self.cash / n
                    # buy floor(per_name_budget / price) shares for each (>=0)
                    # do it in two passes to ensure cash doesn’t drift negative due to rounding
                    for t in to_buy:
                        px = px_row[t]
                        if px > 0:
                            qty = int(math.floor(per_name_budget / px))
                            if qty > 0:
                                cost = qty * px
                                if self.cash >= cost:
                                    self.cash -= cost
                                    positions[t] += qty
                                    trades.append(Trade(dt, t, "BUY", qty, float(px), self.cash))
                                # if a single name gets too expensive after other buys, it just skips
            else:
                # Non-benchmark: buy 1 share per +1 signal, if cash allows
                for t in tickers:
                    sig, px = sig_row[t], px_row[t]
                    if sig == 1 and pd.notna(px) and px > 0:
                        cost = px
                        if self.cash >= cost:
                            self.cash -= cost
                            positions[t] += 1
                            trades.append(Trade(dt, t, "BUY", 1, float(px), self.cash))

            # --- 3) Mark-to-market total portfolio value (single equity curve)
            port_val = self.cash + sum(
                positions[t] * px_row[t] for t in tickers if positions[t] > 0 and pd.notna(px_row[t])
            )
            cash_series.append(self.cash)
            value_series.append(port_val)

        equity = pd.DataFrame(
            {"cash": cash_series, "portfolio_value": value_series},
            index=self.prices.index
        )
        trade_log = pd.DataFrame([t.__dict__ for t in trades])

        return {
            "equity": equity,           # <-- this is your total-portfolio equity curve
            "trade_log": trade_log,
            "final_cash": self.cash,
            "final_positions": positions
        }



# Example usage
prices = get_prices()
sim = Simulator(
    cash=1_000_000,          # starting cash
    strategy="movingaverage",    # choose benchmark strategy
    prices=prices,           # your price DataFrame
    signals=MovingAverageStrategy().compute_signals(prices)          # your signal DataFrame
)

results = sim.run()

# Inspect results
print("Final Cash:", results["final_cash"])
print("Final Positions:", results["final_positions"])
print(results["equity"].tail())       # portfolio value over time
print(results["trade_log"].head())    # first few trades


import matplotlib.pyplot as plt

# results["equity"] has columns ["cash", "portfolio_value"]
equity = results["equity"]

plt.figure(figsize=(10, 6))
plt.plot(equity.index, equity["portfolio_value"], label="Portfolio Value")
plt.plot(equity.index, equity["cash"], label="Cash", linestyle="--")

plt.title("Equity Curve")
plt.xlabel("Date")
plt.ylabel("Value ($)")
plt.legend()
plt.grid(True)
plt.show()
