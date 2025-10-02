
from PriceLoader import get_prices

ticker_dict = get_prices()



# # keep only tickers with at least 2 prices
# valid = {t: [float(x) for x in p if x is not None] 
#          for t, p in ticker_dict.items() if p and len([x for x in p if x is not None]) >= 2500}


# if not valid:
#     raise ValueError("No tickers with >=2 prices.")

# # make all series the same length by truncating to the shortest
# tickers = sorted(valid.keys())
# lengths = {t: len(valid[t]) for t in tickers}

# #print(lengths)
# min_len = min(lengths.values())

# if len(set(lengths.values())) > 1:
#     print(f"Note: truncating to common length {min_len} (shortest series).")

# # shape: (time, tickers)
# P = np.array([valid[t][:min_len] for t in tickers], dtype=float).T

# #print(P)

# # buy 1 share of each at index 1 (act on previous day's signal)
# buy_prices = P[1, :]
# shares_per_stock = 100
# invested = np.nansum(buy_prices * shares_per_stock)

# # holdings: from index 1 onward, hold 1 share each
# holdings = np.zeros_like(P)
# holdings[1:, :] = shares_per_stock

# print(invested)

# portfolio_value = np.nansum(holdings * P, axis=1)
# portfolio_return = (portfolio_value - invested) / invested

# print(f"Tickers used: {len(tickers)}; Invested: {invested:,.2f}")
# print(f"Final portfolio value: {portfolio_value[-1]:,.2f}")
# print(f"Final return: {portfolio_return[-1]*100:.2f}%")


# import matplotlib.pyplot as plt

# import matplotlib.pyplot as plt
# import numpy as np

# equity = portfolio_value  # 1-D array
# x = np.arange(len(equity))

# plt.figure()
# plt.plot(x, equity)
# plt.xlabel("Time step")
# plt.ylabel("Portfolio value ($)")
# plt.title("Equity Curve")
# plt.tight_layout()
# plt.show()



# Example usage with the NEW Simulator

from PriceLoader import get_prices
from MACDStrategy import MACDStrategy
from TradingSimulator import Simulator   # your new Simulator class
import matplotlib.pyplot as plt
import pandas as pd

# load prices
prices = get_prices()

strat = MACDStrategy(name="MACD")

# sim back test
sim = Simulator(strategy=strat, prices=prices, initial_cash=1_000_000)
res = sim.run()   # <-- returns ONE DataFrame with blocks, not a dict

# results
final_cash = res["Cash"].iloc[-1]
final_positions = res["Holdings"].iloc[-1].to_dict()
equity = res[["Cash", "TotalAssets"]]  # analogous to your old 'equity' dict entry


print("Final Cash:", final_cash)
print("Final Positions:", final_positions)
print(equity.tail())

# equity curve plots
plt.figure(figsize=(10, 6))
plt.plot(equity.index, equity["TotalAssets"], label="Total Assets")
plt.plot(equity.index, equity["Cash"], label="Cash", linestyle="--")
plt.title(f"Equity Curve — {res.attrs.get('strategy_name','')}")
plt.xlabel("Date")
plt.ylabel("USD")
plt.legend()
plt.grid(True)
plt.show()

