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


def get_prices(folder="sp500_adj_close", MIN_TRADING_DAYS= 10 * 252):
    """
    Gets all ticker price data individually from sp_500_adj_close foolder and concats them into a df
    Returns P, df of close prices whereby rows are times series columns are tickers
    They all meet MIN_TRAINING_DAYS req.
    """
    folder = Path(folder) # turn into path

    frames = [] # array to store all df
    kept = [] # array to keep ticker names

    # loop through every file in folder
    for filename in folder.iterdir():
        if filename.suffix == ".csv":
            ticker = filename.stem # get ticker
            path = filename

            # check if csv file exists
            if not path.exists():
                raise FileNotFoundError(f"Missing file: {path}")

            # read csv file
            df = pd.read_csv(path, parse_dates=["Date"], usecols=["Date", "Close"])
            df = df.dropna(subset=["Close"]).set_index("Date").sort_index()

            # Ignore tickers with less than min data
            if len(df) < MIN_TRADING_DAYS:
                continue

            # store valid ticker data into the arrays
            df = df.rename(columns={"Close": ticker})[[ticker]]
            frames.append(df)
            kept.append(ticker)

    # concat price series into one df
    P = pd.concat(frames, axis=1, join="inner").astype(float)

    print("Number of tickers:", P.shape[1])
    print("Total prices collected:", P.shape[0])
    return P




