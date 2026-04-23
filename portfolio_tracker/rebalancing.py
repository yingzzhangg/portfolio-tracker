# =============================================================================
# rebalancing.py
# Rebalancing simulation module.
#
# Responsibility: simulate how a portfolio performs under different rebalancing
# schedules (monthly, quarterly, or never) and return the resulting daily
# return series for each strategy.
#
# Key concept: on a rebalancing date, all constituent weights are reset back
# to their policy targets. Between rebalancing dates, weights drift naturally
# as asset prices move at different rates.
# =============================================================================

from typing import Optional

import pandas as pd

from portfolio_tracker.config import MODEL_PORTFOLIO, REBALANCE_SCHEDULES


def simulate_strategy(prices: pd.DataFrame, rebalance_freq: Optional[str]) -> pd.Series:
    """
    Simulate one portfolio strategy from start to end.

    On each rebalancing date, weights are reset to policy targets.
    On all other days, weights drift with price movements (no trading).

    Parameters
    ----------
    prices        : pd.DataFrame — adjusted closing prices (rows=days, cols=tickers)
    rebalance_freq: str or None
        A pandas date offset alias such as "QS" (quarter start) or "MS"
        (month start). Pass None to simulate a pure buy-and-hold strategy
        with no rebalancing at all.

    Returns
    -------
    pd.Series — daily portfolio returns, indexed by date
    """
    tickers = list(MODEL_PORTFOLIO.keys())

    # Policy weights as a numpy array, ordered to match the tickers list
    policy_weights  = pd.Series(MODEL_PORTFOLIO).reindex(tickers).values
    current_weights = policy_weights.copy()

    # Pre-build the set of rebalancing dates for fast lookup
    if rebalance_freq is not None:
        rebal_dates = set(
            pd.date_range(start=prices.index[0], end=prices.index[-1], freq=rebalance_freq)
        )
    else:
        rebal_dates = set()

    daily_returns = []

    # Walk forward day by day starting from day 2 (day 1 has no prior price)
    for i in range(1, len(prices)):
        today = prices.index[i]
        prev  = prices.index[i - 1]

        # Daily return for each constituent
        asset_returns = (prices.iloc[i][tickers] / prices.iloc[i - 1][tickers] - 1).values

        # Weighted portfolio return for today
        portfolio_return = (current_weights * asset_returns).sum()
        daily_returns.append(portfolio_return)

        # Rebalance if any scheduled date falls between yesterday and today (inclusive)
        should_rebalance = any(prev <= d <= today for d in rebal_dates)

        if should_rebalance:
            # Reset to policy targets
            current_weights = policy_weights.copy()
        else:
            # Let weights drift: each position grows/shrinks with its asset return
            new_values      = current_weights * (1 + asset_returns)
            current_weights = new_values / new_values.sum()

    return pd.Series(daily_returns, index=prices.index[1:])


def run_all_schedules(prices: pd.DataFrame) -> dict:
    """
    Run every rebalancing schedule defined in config.REBALANCE_SCHEDULES.

    Parameters
    ----------
    prices : pd.DataFrame — adjusted closing prices

    Returns
    -------
    dict — {strategy_name: pd.Series of daily returns}
    """
    results = {}
    for name, freq in REBALANCE_SCHEDULES.items():
        print(f"  Simulating: {name} ...")
        results[name] = simulate_strategy(prices, freq)
    return results


def build_nav_series(returns_dict: dict, base: float = 100.0) -> dict:
    """
    Convert daily return series into NAV (Net Asset Value) series.

    NAV starts at `base` (default 100) and compounds each day.
    This is the standard way institutional portfolios are presented,
    making it easy to compare strategies regardless of absolute dollar size.

    Parameters
    ----------
    returns_dict : dict  — {name: pd.Series of daily returns}
    base         : float — starting NAV level (default 100)

    Returns
    -------
    dict — {name: pd.Series of NAV values}
    """
    return {
        name: base * (1 + rets).cumprod()
        for name, rets in returns_dict.items()
    }