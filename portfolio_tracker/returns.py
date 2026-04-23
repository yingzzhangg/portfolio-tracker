# =============================================================================
# returns.py
# Performance analytics module.
#
# Responsibility: compute risk-adjusted performance metrics for any return
# series, and produce a formatted comparison table across all strategies.
#
# Two public functions are called from main.py:
#   - compute_performance_table() → formatted DataFrame of metrics
#   - compute_drawdown()          → drawdown series (also used in charts.py)
# =============================================================================

import numpy as np
import pandas as pd

from portfolio_tracker.config import RISK_FREE_RATE, TRADING_DAYS


def compute_drawdown(nav: pd.Series) -> pd.Series:
    """
    Compute the rolling drawdown from the portfolio's high-water mark.

    Drawdown measures how far below its peak the portfolio is at each point.
    A value of -0.20 means the portfolio is 20% below its previous high.

    Parameters
    ----------
    nav : pd.Series — NAV series (e.g., starting at 100)

    Returns
    -------
    pd.Series — drawdown as a negative decimal on each day
    """
    high_water_mark = nav.cummax()
    return (nav - high_water_mark) / high_water_mark


def _compute_metrics(rets: pd.Series) -> dict:
    """
    Compute the full set of performance and risk metrics for one return series.

    Metrics computed:
        Cumulative Return  — total growth over the full period
        CAGR               — annualized compound growth rate
        Ann. Volatility    — annualized standard deviation of daily returns
        Sharpe Ratio       — excess return per unit of total risk
        Sortino Ratio      — excess return per unit of downside risk only
        Max Drawdown       — largest peak-to-trough decline
        Calmar Ratio       — CAGR divided by Max Drawdown (tail-risk-adjusted)
        Daily Hit Rate     — percentage of days with a positive return

    Parameters
    ----------
    rets : pd.Series — daily returns (e.g., 0.01 means +1% that day)

    Returns
    -------
    dict — {metric name: formatted string value}
    """
    n_days  = len(rets)
    n_years = n_days / TRADING_DAYS

    # --- Return metrics ---
    cumulative_return = (1 + rets).prod() - 1
    cagr              = (1 + cumulative_return) ** (1 / n_years) - 1

    # --- Risk metrics ---
    ann_volatility = rets.std() * np.sqrt(TRADING_DAYS)

    # Sharpe: annualized excess return / annualized total volatility
    daily_rf = RISK_FREE_RATE / TRADING_DAYS
    sharpe   = ((rets - daily_rf).mean() / rets.std()) * np.sqrt(TRADING_DAYS)

    # Sortino: uses only negative-return days in the denominator
    downside_std = rets[rets < 0].std() * np.sqrt(TRADING_DAYS)
    sortino      = (cagr - RISK_FREE_RATE) / downside_std if downside_std > 0 else float("nan")

    # Drawdown metrics
    nav     = 100 * (1 + rets).cumprod()
    max_dd  = compute_drawdown(nav).min()   # Most negative value = worst drawdown
    calmar  = cagr / abs(max_dd) if max_dd != 0 else float("nan")

    # Hit rate: fraction of days with a gain
    hit_rate = (rets > 0).mean()

    return {
        "Cumulative Return": f"{cumulative_return:.2%}",
        "CAGR":              f"{cagr:.2%}",
        "Ann. Volatility":   f"{ann_volatility:.2%}",
        "Sharpe Ratio":      f"{sharpe:.2f}",
        "Sortino Ratio":     f"{sortino:.2f}",
        "Max Drawdown":      f"{max_dd:.2%}",
        "Calmar Ratio":      f"{calmar:.2f}",
        "Daily Hit Rate":    f"{hit_rate:.2%}",
        "Period (Years)":    f"{n_years:.1f}",
    }


def compute_performance_table(returns_dict: dict) -> pd.DataFrame:
    """
    Build a side-by-side performance table for all strategies.

    Calls _compute_metrics() once per strategy and assembles the results
    into a single DataFrame suitable for printing or exporting to CSV.

    Parameters
    ----------
    returns_dict : dict — {strategy_name: pd.Series of daily returns}

    Returns
    -------
    pd.DataFrame — rows = strategies, columns = metrics
    """
    records = {name: _compute_metrics(rets) for name, rets in returns_dict.items()}
    return pd.DataFrame(records).T