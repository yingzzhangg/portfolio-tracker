# =============================================================================
# config.py
# Central configuration for the Multi-Asset Portfolio Monitoring System.
#
# Edit this file to change the portfolio, date range, or analytics settings.
# All other modules import from here — nothing is hardcoded elsewhere.
# =============================================================================


# ---------------------------------------------------------------------------
# Model Portfolio — Strategic Asset Allocation (SAA)
# ---------------------------------------------------------------------------
# These are the long-term "policy weights" the portfolio is supposed to hold.
# Every analysis in this project measures performance relative to these targets.

MODEL_PORTFOLIO = {
    "SPY": 0.40,   # US Large-Cap Core Equity        — SPDR S&P 500 ETF
    "QQQ": 0.20,   # US Growth / Technology Equity   — Invesco Nasdaq-100 ETF
    "IWM": 0.10,   # US Small-Cap Equity             — iShares Russell 2000 ETF
    "EFA": 0.10,   # International Developed Markets — iShares MSCI EAFE ETF
    "TLT": 0.10,   # US Long-Duration Fixed Income   — iShares 20+ Yr Treasury ETF
    "GLD": 0.10,   # Real Assets / Inflation Hedge   — SPDR Gold Shares
}

# Maps each ticker to its broad asset class.
# Used to roll up constituent weights into asset-class totals.
ASSET_CLASS_MAP = {
    "SPY": "US Equity",
    "QQQ": "US Equity",
    "IWM": "US Equity",
    "EFA": "International Equity",
    "TLT": "Fixed Income",
    "GLD": "Real Assets",
}


# ---------------------------------------------------------------------------
# Analysis Period
# ---------------------------------------------------------------------------
START_DATE = "2019-01-01"
END_DATE   = "2024-12-31"


# ---------------------------------------------------------------------------
# Performance Analytics
# ---------------------------------------------------------------------------
RISK_FREE_RATE = 0.04   # Annualized risk-free rate used in Sharpe / Sortino
TRADING_DAYS   = 252    # Standard number of trading days per year


# ---------------------------------------------------------------------------
# Drift Monitoring Thresholds
# ---------------------------------------------------------------------------
# Active deviation = sum of |actual weight - policy weight| across all tickers.
# These thresholds mirror common institutional rebalancing policy bands.

DRIFT_WARNING_THRESHOLD   = 0.05   # 500 bps  — monitoring alert level
DRIFT_REBALANCE_THRESHOLD = 0.10   # 1000 bps — rebalancing trigger level


# ---------------------------------------------------------------------------
# Rebalancing Schedules to Compare
# ---------------------------------------------------------------------------
# Keys are human-readable labels used in chart legends and the metrics table.
# Values are pandas date offset aliases (or None for buy-and-hold).

REBALANCE_SCHEDULES = {
    "No Rebalancing": None,
    "Quarterly":      "QS",    # Quarter Start
    "Monthly":        "MS",    # Month Start
}


# ---------------------------------------------------------------------------
# Output Directories
# ---------------------------------------------------------------------------
DATA_DIR   = "data"      # Cached price data lives here
OUTPUT_DIR = "output"    # Charts and CSVs are saved here