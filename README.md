# Multi-Asset Portfolio Monitoring System

A Python analytics pipeline that tracks portfolio exposure, measures drift from target allocations, and compares rebalancing strategies across a six-constituent multi-asset model portfolio.

Built to demonstrate quantitative investment research skills — data ingestion, performance analytics, exposure attribution, and institutional-quality visualization.

---

## What This Project Does

Starting from a defined Strategic Asset Allocation (policy weights), this system:

1. Downloads six years of historical ETF price data via Yahoo Finance
2. Simulates how the portfolio's actual weights drift over time without rebalancing
3. Measures active deviation from policy targets on each trading day
4. Compares monthly rebalancing vs. quarterly rebalancing vs. no rebalancing
5. Computes institutional performance metrics: CAGR, Sharpe, Sortino, Calmar ratio, max drawdown
6. Generates five presentation-ready charts
7. Exports full results to CSV for further analysis

---

## Model Portfolio — Strategic Asset Allocation

| Ticker | Description                       | Asset Class           | Policy Weight |
|--------|-----------------------------------|-----------------------|---------------|
| SPY    | SPDR S&P 500 ETF                  | US Equity             | 40%           |
| QQQ    | Invesco Nasdaq-100 ETF            | US Equity             | 20%           |
| IWM    | iShares Russell 2000 ETF          | US Equity             | 10%           |
| EFA    | iShares MSCI EAFE ETF             | International Equity  | 10%           |
| TLT    | iShares 20+ Year Treasury ETF     | Fixed Income          | 10%           |
| GLD    | SPDR Gold Shares                  | Real Assets           | 10%           |

---

## Project Structure

```
portfolio_tracker/
│
├── data/                              # Auto-generated: cached price CSV
├── output/                            # Auto-generated: charts + exports
│
├── portfolio_tracker/
│   ├── __init__.py
│   ├── config.py                      # All settings in one place
│   ├── data_loader.py                 # Download and cache price data
│   ├── rebalancing.py                 # Simulate monthly / quarterly / no rebalancing
│   ├── exposure.py                    # Actual vs. policy weight attribution
│   ├── returns.py                     # Performance and risk metrics
│   └── charts.py                      # Generate all five charts
│
├── main.py                            # Run the full pipeline
├── requirements.txt
└── README.md
```

Each file has exactly one responsibility. No file imports from another except through `config.py` constants — making the code easy to test, explain, and extend.

---

## How to Run

```bash
# 1. Install dependencies (only needed once)
pip install -r requirements.txt

# 2. Run the pipeline
python main.py
```

On the first run, prices are downloaded and saved to `data/prices.csv`.
All subsequent runs load from the cache — no internet connection needed.

---

## Output

### Charts (saved to `output/`)

| File | What It Shows |
|------|---------------|
| `1_nav_comparison.png` | NAV growth for all three strategies, base 100 |
| `2_exposure_snapshot.png` | Actual vs. policy weights at period end |
| `3_weight_drift.png` | How constituent weights shift over time (buy-and-hold) |
| `4_active_deviation.png` | Daily drift magnitude with 500 bps and 1000 bps alert bands |
| `5_drawdown_comparison.png` | Peak-to-trough losses for all strategies |

### CSVs (saved to `output/`)

| File | Contents |
|------|----------|
| `portfolio_analytics_summary.csv` | Daily NAV, weights, and drift for all strategies |
| `performance_metrics.csv` | CAGR, Sharpe, Sortino, Calmar, max drawdown by strategy |

---

## Key Concepts

**Portfolio drift** — When assets grow at different rates, their share of the portfolio shifts away from the intended target. If equities rally strongly, SPY might grow from 40% to 50% of the portfolio, adding unintended equity concentration. This project measures that drift daily as the sum of absolute deviations across all constituents.

**Active deviation** — The total signed or unsigned difference between actual and policy weights. Institutional teams typically monitor this against defined tolerance bands: a warning at 500 basis points and a rebalancing trigger at 1000 basis points.

**Rebalancing trade-off** — More frequent rebalancing keeps the portfolio closer to its risk target but incurs higher transaction costs. The three-way comparison in this project quantifies the risk-adjusted performance difference between monthly, quarterly, and no rebalancing across metrics that penalize different types of risk.

**Calmar ratio** — CAGR divided by maximum drawdown. Preferred in institutional contexts because it penalizes strategies with large peak-to-trough losses, making it more conservative than Sharpe alone.

---

## Relevance to Investment Research

Portfolio analytics teams at asset managers, pension funds, and wealth management firms regularly:

- Track active exposures against model portfolios and benchmarks
- Flag drift that exceeds internal tolerance bands and prepare rebalancing proposals
- Evaluate rebalancing schedules against transaction cost budgets
- Report risk-adjusted performance across strategies to investment committees

This project replicates that workflow end-to-end using real market data over a period that includes COVID-19 (2020), the equity recovery (2021), and the Fed rate shock (2022).

---

## Resume Bullet Points

> Built a Python portfolio monitoring system that tracks active deviation, exposure attribution, and rebalancing impact across a six-constituent multi-asset mandate using six years of real ETF price data.

> Designed a modular analytics pipeline — data ingestion, drift simulation, multi-schedule rebalancing engine, risk-adjusted performance reporting (CAGR, Sharpe, Sortino, Calmar) — producing five institutional-quality charts and structured CSV exports.

---

## 30-Second Interview Explanation

*"I built a portfolio analytics system in Python that tracks how a multi-asset portfolio drifts away from its target allocation over time. Starting from a defined strategic allocation — 40% S&P 500, 20% Nasdaq, bonds, gold, and international equities — I simulate what happens to the weights if you never rebalance, and compare that to monthly and quarterly rebalancing. The system computes the full set of institutional metrics including Sharpe, Sortino, and Calmar ratio, generates five charts, and exports everything to CSV. I structured it as a proper Python package so each module has one clear job: data loading, drift simulation, performance analytics, and visualization are all separate. It covers six years of real data including COVID and the 2022 rate shock, which makes the results meaningful."*

---

## Configuration

All settings are in `portfolio_tracker/config.py`:

- `MODEL_PORTFOLIO` — tickers and policy weights (must sum to 1.0)
- `START_DATE` / `END_DATE` — analysis period
- `RISK_FREE_RATE` — used in Sharpe and Sortino calculations
- `DRIFT_WARNING_THRESHOLD` / `DRIFT_REBALANCE_THRESHOLD` — alert bands
- `REBALANCE_SCHEDULES` — add or remove strategies to compare