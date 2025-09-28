import os
from pathlib import Path
import time
import pandas as pd
import yfinance as yf
import requests



class PriceLoader:
    def __init__(self):
        pass


    def get_tickers(self):
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text
        df = pd.read_html(html, attrs={"id": "constituents"}, header=0)[0]
        tickers = df["Symbol"].str.replace('.', '-', regex=False).tolist()
        return tickers

    def chunked(self,seq, n):
        for i in range(0, len(seq), n):
            yield seq[i:i+n]

    def download_per_ticker_csv_simple(
        self,
        start="2005-01-01",
        end="2025-12-31",
        out_dir="prices",
        batch_size=40,
        adjusted=True,
        pause=1.0,
    ):
        tickers = self.get_tickers()
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        auto_adjust = bool(adjusted)

        for batch in self.chunked(tickers, batch_size):
            df = yf.download(batch, start=start, end=end, auto_adjust=auto_adjust, progress=False)
            if df.empty:
                time.sleep(pause)
                continue

            # Handle single vs multi-ticker return
            if isinstance(df.columns, pd.MultiIndex):
                close_wide = df["Close"]
            else:
                close_wide = df[["Close"]]
                close_wide.columns = batch  # name the single column as the ticker

            # Write one CSV per ticker
            for t in close_wide.columns:
                s = close_wide[t].dropna()
                if s.empty:
                    continue
                out = s.reset_index()
                out.columns = ["Date", "Close"]
                out.to_csv(Path(out_dir) / f"{t}.csv", index=False)

            time.sleep(pause)


# sp500 = PriceLoader()
# sp500.download_per_ticker_csv_simple(start="2005-01-01", end="2025-09-27",
#                                out_dir="sp500_adj_close", batch_size=40, adjusted=True)


def get_prices():
    folder = "sp500_adj_close"

    all_prices = []       # master list of all prices
    ticker_dict = {}      # ticker -> list of prices

    # loop through every file in folder
    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            ticker = filename.replace(".csv", "")  # assume filename = "AAPL.csv"
            filepath = os.path.join(folder, filename)

            df = pd.read_csv(filepath)

            # check if there's an "Adj Close" column
            if "Close" in df.columns:
                prices = df["Close"].dropna().tolist()
            else:
                raise ValueError(f"No 'Close' column found in {filename}")

            ticker_dict[ticker] = prices
            all_prices.extend(prices)
    

    print("Number of tickers:", len(ticker_dict))
    print("Total prices collected:", len(all_prices))
    return ticker_dict




