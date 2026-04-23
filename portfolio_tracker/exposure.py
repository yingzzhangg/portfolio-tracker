# =============================================================================
# exposure.py
# Portfolio exposure and drift module.
#
# Responsibility: measure how actual portfolio weights evolve over time
# under a buy-and-hold assumption, and compare them to policy targets.
#
# Three public functions are used by main.py:
#   - simulate_drift()         → actual weights over time
#   - compute_drift_magnitude()→ daily total active deviation
#   - build_exposure_snapshot()→ constituent + asset-class summary table
# =============================================================================

import pandas as pd

from portfolio_tracker.config import MODEL_PORTFOLIO, ASSET_CLASS_MAP


def simulate_drift(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Simulate how constituent weights evolve under a buy-and-hold strategy.

    On day 1, each position is sized to match its policy weight exactly.
    After that, no trading occurs — positions just grow or shrink with prices.
    This shows what happens to the allocation if the portfolio is never touched.

    Parameters
    ----------
    prices : pd.DataFrame — adjusted closing prices (rows=days, cols=tickers)

    Returns
    -------
    pd.DataFrame — actual portfolio weights over time (rows=days, cols=tickers)
    """
    # Align policy weights to the column order of the prices DataFrame
    policy = pd.Series(MODEL_PORTFOLIO).reindex(prices.columns)

    # Price relative to day 1: shows how much each position has grown
    price_relatives = prices / prices.iloc[0]

    # Dollar value of each position = initial weight × price growth
    position_values = price_relatives.multiply(policy, axis="columns")

    # Portfolio weight = each position's value ÷ total portfolio value
    total_value    = position_values.sum(axis=1)
    actual_weights = position_values.divide(total_value, axis="index")

    return actual_weights


def compute_drift_magnitude(actual_weights: pd.DataFrame) -> pd.Series:
    """
    Compute the total active deviation on each day.

    Active deviation = sum of |actual weight - policy weight| for every ticker.

    A value of 0.10 means the portfolio has drifted 1000 basis points
    in aggregate from its policy targets — a common institutional trigger
    for initiating a rebalancing review.

    Parameters
    ----------
    actual_weights : pd.DataFrame — actual weights over time (from simulate_drift)

    Returns
    -------
    pd.Series — daily total active deviation, one value per trading day
    """
    policy     = pd.Series(MODEL_PORTFOLIO).reindex(actual_weights.columns)
    deviations = (actual_weights - policy).abs()
    return deviations.sum(axis=1).rename("Total Active Deviation")


def build_exposure_snapshot(actual_weights: pd.DataFrame):
    """
    Build point-in-time exposure tables for the most recent date in the data.

    Returns two DataFrames:
    1. constituent_table — policy, actual, and active weight for each ticker
    2. asset_class_table — same information rolled up to asset class level

    Parameters
    ----------
    actual_weights : pd.DataFrame — actual weights over time (from simulate_drift)

    Returns
    -------
    tuple of (pd.DataFrame, pd.DataFrame)
        constituent_table : indexed by ticker
        asset_class_table : indexed by asset class name
    """
    policy = pd.Series(MODEL_PORTFOLIO)
    latest = actual_weights.iloc[-1]   # Most recent day's weights
    active = latest - policy           # Overweight (+) or underweight (-)

    # --- Constituent-level table ---
    constituent_table = pd.DataFrame({
        "Asset Class":   pd.Series(ASSET_CLASS_MAP),
        "Policy Weight": policy,
        "Actual Weight": latest,
        "Active Weight": active,
    })

    # --- Asset-class rollup ---
    # Group tickers by asset class and sum their weights
    asset_class_table = (
        constituent_table
        .groupby("Asset Class")[["Policy Weight", "Actual Weight", "Active Weight"]]
        .sum()
    )

    return constituent_table, asset_class_table