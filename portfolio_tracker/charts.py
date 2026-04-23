# =============================================================================
# charts.py
# Visualization module.
#
# Responsibility: generate all five presentation-ready charts and save them
# as PNG files to the output/ directory.
#
# Charts produced:
#   1. NAV comparison — all rebalancing strategies on one chart
#   2. Exposure snapshot — actual vs. policy weights, current date
#   3. Constituent weight drift — stacked area over time
#   4. Total active deviation — drift magnitude with alert thresholds
#   5. Drawdown comparison — all strategies overlaid
#
# One public function is called from main.py: generate_all_charts()
# =============================================================================

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

from portfolio_tracker.config import (
    MODEL_PORTFOLIO,
    DRIFT_WARNING_THRESHOLD,
    DRIFT_REBALANCE_THRESHOLD,
    OUTPUT_DIR,
)


# ---------------------------------------------------------------------------
# House Style
# ---------------------------------------------------------------------------
# All colors, sizes, and formatting choices are defined here in one place.
# To restyle all charts at once, edit this section only.

PALETTE = {
    "navy":       "#0B2545",
    "blue":       "#1D4E89",
    "teal":       "#1B7F79",
    "amber":      "#C27D38",
    "slate":      "#5C6B73",
    "red":        "#A63D2F",
    "light_gray": "#F0F2F5",
    "mid_gray":   "#C9CDD4",
    "dark_gray":  "#3A3F47",
}

# One color per rebalancing strategy — used consistently across all charts
STRATEGY_COLORS = {
    "No Rebalancing": PALETTE["slate"],
    "Quarterly":      PALETTE["blue"],
    "Monthly":        PALETTE["teal"],
}

# One color per asset/ticker — used in stacked area and bar charts
ASSET_COLORS = [
    PALETTE["navy"],
    PALETTE["blue"],
    PALETTE["teal"],
    PALETTE["amber"],
    PALETTE["slate"],
    PALETTE["red"],
]

FIGSIZE    = (13, 5)    # Wide format for time-series charts
FIGSIZE_SQ = (9, 6)     # Square format for snapshot charts
DPI        = 150

FONT_TITLE = {"fontsize": 13, "fontweight": "bold", "color": PALETTE["dark_gray"]}
FONT_LABEL = {"fontsize": 10, "color": PALETTE["dark_gray"]}
FONT_TICK  = {"labelsize": 9, "labelcolor": PALETTE["slate"]}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _style_axes(ax: plt.Axes) -> None:
    """
    Apply consistent institutional styling to a matplotlib Axes object.
    Removes top/right spines, adds subtle horizontal gridlines.
    """
    ax.set_facecolor("white")
    ax.grid(True, axis="y", color=PALETTE["light_gray"], linewidth=0.8, zorder=0)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(PALETTE["mid_gray"])
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_color(PALETTE["mid_gray"])
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(**FONT_TICK)


def _format_date_axis(ax: plt.Axes) -> None:
    """Format x-axis as readable dates with 6-month intervals."""
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


def _save(fig: plt.Figure, filename: str) -> None:
    """Save a figure to the output directory and close it."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    print(f"  Saved → {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Chart 1: NAV Comparison
# ---------------------------------------------------------------------------

def plot_nav_comparison(nav_dict: dict) -> None:
    """
    Line chart comparing the NAV trajectory of each rebalancing strategy.
    All strategies start at NAV = 100 on day 1.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)

    for name, nav in nav_dict.items():
        color = STRATEGY_COLORS.get(name, PALETTE["slate"])
        # Dashed line for the no-rebalancing baseline; solid for active strategies
        linestyle = "--" if name == "No Rebalancing" else "-"
        linewidth = 1.4 if name == "No Rebalancing" else 2.2
        ax.plot(nav.index, nav.values, label=name,
                color=color, linestyle=linestyle, linewidth=linewidth, zorder=3)

    ax.set_title("NAV Performance by Rebalancing Strategy  (Base = 100)", **FONT_TITLE)
    ax.set_ylabel("NAV (Base 100)", **FONT_LABEL)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    _format_date_axis(ax)
    _style_axes(ax)
    fig.tight_layout()
    _save(fig, "1_nav_comparison.png")


# ---------------------------------------------------------------------------
# Chart 2: Exposure Snapshot
# ---------------------------------------------------------------------------

def plot_exposure_snapshot(actual_weights: pd.DataFrame) -> None:
    """
    Grouped bar chart comparing current actual weights to policy weights.
    Each pair of bars represents one ticker.
    The label above the actual bar shows the active weight (+ = overweight).
    """
    tickers = list(MODEL_PORTFOLIO.keys())
    policy  = pd.Series(MODEL_PORTFOLIO)
    latest  = actual_weights.iloc[-1]
    active  = latest - policy

    x     = np.arange(len(tickers))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIGSIZE_SQ)

    ax.bar(x - width / 2, policy[tickers].values * 100,
           width=width, label="Policy Weight", color=PALETTE["mid_gray"], zorder=3)
    ax.bar(x + width / 2, latest[tickers].values * 100,
           width=width, label="Actual Weight", color=PALETTE["blue"], zorder=3)

    # Annotate active weight above each actual bar
    for i, ticker in enumerate(tickers):
        aw    = active[ticker]
        sign  = "+" if aw >= 0 else ""
        color = PALETTE["teal"] if aw >= 0 else PALETTE["red"]
        ax.text(
            x[i] + width / 2,
            latest[ticker] * 100 + 0.5,
            f"{sign}{aw * 100:.1f} pp",
            ha="center", va="bottom",
            fontsize=8, fontweight="bold", color=color,
        )

    as_of = actual_weights.index[-1].strftime("%d %b %Y")
    ax.set_title(f"Exposure Snapshot: Actual vs. Policy Weight  (as of {as_of})", **FONT_TITLE)
    ax.set_ylabel("Weight (%)", **FONT_LABEL)
    ax.set_xticks(x)
    ax.set_xticklabels(tickers, fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.legend(frameon=False, fontsize=9)
    _style_axes(ax)
    fig.tight_layout()
    _save(fig, "2_exposure_snapshot.png")


# ---------------------------------------------------------------------------
# Chart 3: Constituent Weight Drift Over Time
# ---------------------------------------------------------------------------

def plot_weight_drift(actual_weights: pd.DataFrame) -> None:
    """
    Stacked area chart showing how each constituent's portfolio weight
    changes over time under a buy-and-hold (no rebalancing) assumption.
    White dashed lines mark the policy weight boundaries.
    """
    tickers = list(MODEL_PORTFOLIO.keys())
    policy  = pd.Series(MODEL_PORTFOLIO)

    fig, ax = plt.subplots(figsize=FIGSIZE)

    ax.stackplot(
        actual_weights.index,
        [actual_weights[t].values * 100 for t in tickers],
        labels=tickers,
        colors=ASSET_COLORS[: len(tickers)],
        alpha=0.78,
        zorder=2,
    )

    # Draw horizontal reference lines at the cumulative policy weight boundaries
    cumulative = 0
    for ticker in tickers:
        cumulative += policy[ticker] * 100
        ax.axhline(y=cumulative, color="white", linestyle="--",
                   linewidth=0.9, alpha=0.8, zorder=3)

    ax.set_title("Constituent Weight Drift Over Time  (Buy-and-Hold, No Rebalancing)", **FONT_TITLE)
    ax.set_ylabel("Portfolio Weight (%)", **FONT_LABEL)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.legend(loc="upper left", fontsize=8, ncol=2, frameon=False)
    _format_date_axis(ax)
    _style_axes(ax)
    fig.tight_layout()
    _save(fig, "3_weight_drift.png")


# ---------------------------------------------------------------------------
# Chart 4: Total Active Deviation
# ---------------------------------------------------------------------------

def plot_active_deviation(drift: pd.Series) -> None:
    """
    Area chart showing daily total active deviation over time.
    Horizontal dashed lines mark the warning and rebalancing trigger thresholds.
    """
    # Convert to percentage points for the y-axis
    drift_pp = drift * 100

    # Threshold values in percentage points
    warn_pp  = DRIFT_WARNING_THRESHOLD   * 100   # e.g. 5 pp = 500 bps
    trig_pp  = DRIFT_REBALANCE_THRESHOLD * 100   # e.g. 10 pp = 1000 bps

    fig, ax = plt.subplots(figsize=FIGSIZE)

    ax.fill_between(drift.index, drift_pp, color=PALETTE["blue"], alpha=0.25, zorder=2)
    ax.plot(drift.index, drift_pp, color=PALETTE["blue"], linewidth=1.6, zorder=3)

    ax.axhline(y=warn_pp, color=PALETTE["amber"], linestyle="--", linewidth=1.2, zorder=4,
               label=f"Monitoring alert  ({int(warn_pp * 10)} bps)")
    ax.axhline(y=trig_pp, color=PALETTE["red"],   linestyle="--", linewidth=1.2, zorder=4,
               label=f"Rebalancing trigger  ({int(trig_pp * 10)} bps)")

    ax.set_title("Total Active Deviation from Policy Weights  (Σ |Actual − Policy|)", **FONT_TITLE)
    ax.set_ylabel("Active Deviation (percentage points)", **FONT_LABEL)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f} pp"))
    ax.legend(frameon=False, fontsize=9)
    _format_date_axis(ax)
    _style_axes(ax)
    fig.tight_layout()
    _save(fig, "4_active_deviation.png")


# ---------------------------------------------------------------------------
# Chart 5: Drawdown Comparison
# ---------------------------------------------------------------------------

def plot_drawdown_comparison(nav_dict: dict) -> None:
    """
    Drawdown chart for all strategies on the same axes.
    Shows the depth and duration of losses from each strategy's high-water mark.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)

    for name, nav in nav_dict.items():
        drawdown = (nav - nav.cummax()) / nav.cummax() * 100
        color     = STRATEGY_COLORS.get(name, PALETTE["slate"])
        linewidth = 1.2 if name == "No Rebalancing" else 1.8
        ax.fill_between(drawdown.index, drawdown.values, 0, alpha=0.08, color=color)
        ax.plot(drawdown.index, drawdown.values, label=name,
                color=color, linewidth=linewidth)

    ax.set_title("Drawdown from High-Water Mark by Strategy", **FONT_TITLE)
    ax.set_ylabel("Drawdown (%)", **FONT_LABEL)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.legend(frameon=False, fontsize=9)
    _format_date_axis(ax)
    _style_axes(ax)
    fig.tight_layout()
    _save(fig, "5_drawdown_comparison.png")


# ---------------------------------------------------------------------------
# Orchestrator — called from main.py
# ---------------------------------------------------------------------------

def generate_all_charts(
    nav_dict:       dict,
    actual_weights: pd.DataFrame,
    drift:          pd.Series,
) -> None:
    """
    Generate and save all five charts.

    Parameters
    ----------
    nav_dict       : dict        — {strategy name: NAV series}
    actual_weights : pd.DataFrame — constituent weights over time
    drift          : pd.Series   — daily total active deviation
    """
    print("\nGenerating charts...")
    plot_nav_comparison(nav_dict)
    plot_exposure_snapshot(actual_weights)
    plot_weight_drift(actual_weights)
    plot_active_deviation(drift)
    plot_drawdown_comparison(nav_dict)
    print("All charts saved to output/\n")