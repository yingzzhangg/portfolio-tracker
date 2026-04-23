# =============================================================================
# data_loader.py
# Market data ingestion module.
#
# Responsibility: download adjusted closing prices from Yahoo Finance
# and cache them locally so the project does not re-download on every run.
#
# Only one function is called from outside this file: load_prices().
# =============================================================================

import os
import pandas as pd
import yfinance as yf

from portfolio_tracker.config import MODEL_PORTFOLIO, START_DATE, END_DATE, DATA_DIR


def _download_prices(tickers: list, start: str, end: str) -> pd.DataFrame:
    """
    Pull adjusted closing prices from Yahoo Finance.

    This is a private helper — call load_prices() instead.

    Parameters
    ----------
    tickers : list of str   — e.g. ["SPY", "QQQ", "IWM"]
    start   : str           — start date, "YYYY-MM-DD"
    end     : str           — end date,   "YYYY-MM-DD"

    Returns
    -------
    pd.DataFrame — rows = trading days, columns = tickers, values = adj. close prices
    """
    print(f"  Downloading price data for: {tickers}")
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)

    # yfinance returns MultiIndex columns when fetching multiple tickers.
    # We only need the "Close" level.
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        # Single ticker edge case: raw is a flat DataFrame
        prices = raw[["Close"]]
        prices.columns = tickers

    # Remove any days where every ticker is missing (e.g., market holidays)
    prices.dropna(how="all", inplace=True)

    # Forward-fill isolated missing values (e.g., one ETF not yet listed)
    prices.ffill(inplace=True)

    return prices


def load_prices(use_cache: bool = True) -> pd.DataFrame:
    """
    Load adjusted closing prices for all model portfolio constituents.

    On the first run, prices are downloaded from Yahoo Finance and saved
    to data/prices.csv. On subsequent runs, the CSV is loaded directly
    to avoid unnecessary API calls.

    Parameters
    ----------
    use_cache : bool
        If True (default), load from CSV when it exists.
        Set to False to force a fresh download.

    Returns
    -------
    pd.DataFrame — rows = trading days, columns = tickers
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    cache_path = os.path.join(DATA_DIR, "prices.csv")

    if use_cache and os.path.exists(cache_path):
        print(f"  Loading cached prices from: {cache_path}")
        prices = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        return prices

    tickers = list(MODEL_PORTFOLIO.keys())
    prices  = _download_prices(tickers, START_DATE, END_DATE)

    prices.to_csv(cache_path)
    print(f"  Prices saved to: {cache_path}")

    return prices