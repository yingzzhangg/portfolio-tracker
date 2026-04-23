print("starting")
# =============================================================================
# main.py
# Multi-Asset Portfolio Monitoring System — Entry Point
#
# Run this file to execute the full analytics pipeline:
#
#   Step 1 — Load price data
#   Step 2 — Simulate all rebalancing strategies
#   Step 3 — Compute exposure vs. policy weights
#   Step 4 — Report drift monitoring statistics
#   Step 5 — Compute and print performance metrics
#   Step 6 — Generate all five charts
#   Step 7 — Export results to CSV
#
# Usage:
#   python main.py
#
# Output:
#   output/1_nav_comparison.png
#   output/2_exposure_snapshot.png
#   output/3_weight_drift.png
#   output/4_active_deviation.png
#   output/5_drawdown_comparison.png
#   output/portfolio_analytics_summary.csv
#   output/performance_metrics.csv
# =============================================================================

import os
import pandas as pd

from portfolio_tracker.config       import (
    MODEL_PORTFOLIO,
    OUTPUT_DIR,
    DRIFT_WARNING_THRESHOLD,
    DRIFT_REBALANCE_THRESHOLD,
)
from portfolio_tracker.data_loader  import load_prices
from portfolio_tracker.rebalancing  import run_all_schedules, build_nav_series
from portfolio_tracker.exposure     import (
    simulate_drift,
    compute_drift_magnitude,
    build_exposure_snapshot,
)
from portfolio_tracker.returns      import compute_performance_table
from portfolio_tracker.charts       import generate_all_charts


# ---------------------------------------------------------------------------
# Helper: print a section header to the console
# ---------------------------------------------------------------------------

def _section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:

    print("=" * 60)
    print("  Multi-Asset Portfolio Monitoring System")
    print("  Strategic Asset Allocation — Analytics Report")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Load price data
    # ------------------------------------------------------------------
    _section("Step 1 / Market Data")

    all_prices  = load_prices(use_cache=True)
    prices      = all_prices[list(MODEL_PORTFOLIO.keys())]   # Keep only portfolio tickers

    print(f"  Tickers      : {list(prices.columns)}")
    print(f"  Trading days : {len(prices):,}")
    print(f"  Period       : {prices.index[0].date()} → {prices.index[-1].date()}")

    # ------------------------------------------------------------------
    # Step 2: Simulate rebalancing strategies
    # ------------------------------------------------------------------
    _section("Step 2 / Rebalancing Simulation")

    returns_dict = run_all_schedules(prices)   # {name: daily return series}
    nav_dict     = build_nav_series(returns_dict)  # {name: NAV series, base 100}

    # ------------------------------------------------------------------
    # Step 3: Exposure attribution
    # ------------------------------------------------------------------
    _section("Step 3 / Exposure Attribution")

    actual_weights                       = simulate_drift(prices)
    drift                                = compute_drift_magnitude(actual_weights)
    constituent_table, asset_class_table = build_exposure_snapshot(actual_weights)

    # Print constituent-level snapshot
    print("\n  Constituent Exposure (most recent date):")
    print(f"  {'Ticker':<6}  {'Asset Class':<24}  {'Policy':>7}  {'Actual':>7}  {'Active':>7}")
    print(f"  {'─'*6}  {'─'*24}  {'─'*7}  {'─'*7}  {'─'*7}")
    for ticker, row in constituent_table.iterrows():
        aw   = row["Active Weight"]
        flag = " ▲" if aw > 0.03 else (" ▼" if aw < -0.03 else "  ")
        print(
            f"  {ticker:<6}  {row['Asset Class']:<24}  "
            f"{row['Policy Weight']:>6.1%}  "
            f"{row['Actual Weight']:>6.1%}  "
            f"{aw:>+6.1%}{flag}"
        )

    # Print asset-class rollup
    print("\n  Asset-Class Rollup:")
    print(f"  {'Class':<24}  {'Policy':>7}  {'Actual':>7}  {'Active':>7}")
    print(f"  {'─'*24}  {'─'*7}  {'─'*7}  {'─'*7}")
    for cls, row in asset_class_table.iterrows():
        print(
            f"  {cls:<24}  "
            f"{row['Policy Weight']:>6.1%}  "
            f"{row['Actual Weight']:>6.1%}  "
            f"{row['Active Weight']:>+6.1%}"
        )

    # ------------------------------------------------------------------
    # Step 4: Drift monitoring statistics
    # ------------------------------------------------------------------
    _section("Step 4 / Drift Monitoring")

    peak_drift = drift.max()
    avg_drift  = drift.mean()
    days_warn  = int((drift > DRIFT_WARNING_THRESHOLD).sum())
    days_trig  = int((drift > DRIFT_REBALANCE_THRESHOLD).sum())

    print(f"  Peak active deviation   : {peak_drift:.2%}")
    print(f"  Avg  active deviation   : {avg_drift:.2%}")
    print(f"  Days above 500  bps     : {days_warn:,}  ← monitoring alert threshold")
    print(f"  Days above 1000 bps     : {days_trig:,}  ← rebalancing trigger threshold")

    # ------------------------------------------------------------------
    # Step 5: Performance metrics
    # ------------------------------------------------------------------
    _section("Step 5 / Performance Metrics")

    metrics = compute_performance_table(returns_dict)
    print()
    print(metrics.to_string())
    print()

    # ------------------------------------------------------------------
    # Step 6: Generate charts
    # ------------------------------------------------------------------
    _section("Step 6 / Chart Generation")

    generate_all_charts(nav_dict, actual_weights, drift)

    # ------------------------------------------------------------------
    # Step 7: Export to CSV
    # ------------------------------------------------------------------
    _section("Step 7 / Export")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Master summary: NAV series + daily weights + daily drift, all aligned by date
    nav_df  = pd.DataFrame(nav_dict).add_prefix("NAV_")
    wt_df   = actual_weights.add_prefix("Weight_")
    summary = nav_df.join(wt_df, how="inner").join(drift, how="inner")
    summary_path = os.path.join(OUTPUT_DIR, "portfolio_analytics_summary.csv")
    summary.to_csv(summary_path)
    print(f"  Summary CSV      → {summary_path}")

    # Performance metrics table
    metrics_path = os.path.join(OUTPUT_DIR, "performance_metrics.csv")
    metrics.to_csv(metrics_path)
    print(f"  Performance CSV  → {metrics_path}")

    print("\n" + "=" * 60)
    print("  Pipeline complete. All output saved to output/")
    print("=" * 60)


if __name__ == "__main__":
    main()