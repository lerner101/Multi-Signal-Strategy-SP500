import numpy as np
from PriceLoader import get_prices

class Benchmark:
    """
    For each ticker: emit a column vector [1, 0, 0, 0, ...] of length T.
    - No sells are generated here.
    """
    def __init__(self, min_points_per_ticker: int = 2500, buy_index: int = 0):
        """
        min_points_per_ticker: filter tickers that have fewer points.
        buy_index: row index at which to place the '1' (default 0).
        """
        self.min_points_per_ticker = min_points_per_ticker
        self.buy_index = buy_index
        self.tickers = None  # list[str]
        self.T = None        # time length
        self.N = None        # number of tickers

    def _build_price_matrix(self, ticker_dict: dict):
        """
        Truncate all series to the shortest length so they align by index.
        Returns (tickers, T, N) but NOT the prices (kept out for simplicity).
        """
        # Clean & filter
        valid = {}
        for t, p in ticker_dict.items():
            if p:  # skip empty lists
                cleaned = []
                for x in p:
                    if x is not None:
                        cleaned.append(float(x))
                if len(cleaned) >= self.min_points_per_ticker:
                    valid[t] = cleaned

        if not valid:
            raise ValueError(f"No tickers with >= {self.min_points_per_ticker} prices.")

        tickers = sorted(valid.keys())
        min_len = min(len(valid[t]) for t in tickers)  # common T
        return tickers, min_len, len(tickers)

    def generate_signals(self, ticker_dict: dict) -> np.ndarray:
        """
        Returns S with shape (T, N): for every column (ticker), S[buy_index, j] = 1, else 0.
        """
        self.tickers, self.T, self.N = self._build_price_matrix(ticker_dict)
        if not (0 <= self.buy_index < self.T):
            raise ValueError(f"buy_index {self.buy_index} out of range for T={self.T}")

        S = np.zeros((self.T, self.N), dtype=int)
        S[self.buy_index, :] = 1
        return S
