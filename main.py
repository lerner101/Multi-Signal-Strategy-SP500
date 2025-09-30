


# ticker_dict = get_prices()


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



# SIMPLE TEST CASE JUST AS AN EXAMPLE
# from MovingAverageStrategy import MovingAverageStrategy

# strat = MovingAverageStrategy(name="MA20_50")
# # single ticker
# res = strat.run_strategy()
# print(res[["Cash","TotalAssets"]].tail())

from PriceLoader import get_prices
from MACDStrategy import MACDStrategy

strat = MACDStrategy()
P_all = get_prices()

print(strat.compute_signals(P_all))

# multiple tickers
# res = strat.run_from_tickers(["AAPL", "MSFT", "NVDA"])