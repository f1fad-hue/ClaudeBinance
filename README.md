# Four-Sleeve Allocation Desk

A mobile-first (Android) portfolio dashboard for a mandated four-holding universe:
**SGOV**, **QQQ**, **IEMG**, **BMNR** — built on a 10-year investment horizon.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

## Contents

| File | Purpose |
|---|---|
| `allocation.html` | The dashboard. Bottom tab bar, light theme, five sections. |
| `portfolio_model.py` | Reproduces every number on the page: CAGR, volatility, VaR, drawdown, risk contribution. |
| `vol_regime.py` | Two-regime volatility analysis and the frontier search behind the optimized weights. |

## Sections

1. **Macro** — composite driver gauge (1–10) over six weighted inputs, plus correlated transmission into each sleeve.
2. **Regions** — US / Europe / Asia-EM ranked at 3, 6, 12 months and 10 years.
3. **Volatility** — VIX term-structure math, portfolio σ and VaR by horizon, risk decomposition, 10-year regime view.
4. **Sleeves** — one swipeable slide per holding with net-of-fee 10-year CAGR and expected drawdown.
5. **Portfolios** — baseline vs optimized donuts, forecast comparison, rationale.

## Allocations

Weights are constrained to increments of 5.

| Sleeve | Baseline | Optimized |
|---|---|---|
| QQQ  | 45% | 25% |
| IEMG | 25% | 40% |
| SGOV | 25% | 30% |
| BMNR |  5% |  5% |

| Metric | Baseline | Optimized |
|---|---|---|
| Net 10-yr CAGR | 7.21% | 7.07% |
| Weighted fee | 0.126% | 0.108% |
| σ — calm (today) | 16.59% | 15.05% |
| σ — vol normalized | 22.41% | 20.39% |
| Max drawdown — calm | −28.2% | −25.6% |
| Max drawdown — normalized | −38.1% | −34.7% |
| Correlated-stress drawdown | −30.6% | −27.5% |

The optimized book is driven by macro sentiment, regional rankings **and** volatility
analysis across 3, 6 and 12 months. Unlike earlier revisions it does not dominate the
baseline on every axis: it gives up 0.14 points of CAGR to buy 3.4 points of drawdown.

## Method

Equity forecasts are built from observable components rather than asserted:

| Component | QQQ | IEMG |
|---|---|---|
| Dividend yield | +0.65 | +2.29 |
| Earnings growth | +9.50 | +7.50 |
| Valuation change | −1.79 | +0.74 |
| Currency drag | — | −1.50 |
| **Gross** | **8.36** | **9.03** |
| Expense ratio | −0.18 | −0.09 |
| **Net** | **8.18** | **8.94** |

Valuation change annualises the forward multiple moving from its observed level
(QQQ 25.2×, IEMG 11.6×) to an assumed terminal level (21×, 12.5×) over ten years.
BMNR is modelled separately: 9.0% ETH appreciation, +2.6% staking on 85.9% of the
treasury, −0.2% mNAV normalisation, −1.4% corporate and dilution drag. Portfolio
volatility is computed from a correlation matrix (QQQ·IEMG 0.72, QQQ·BMNR 0.65,
IEMG·BMNR 0.55, SGOV uncorrelated). Horizon volatility scales as σ√(h/12); VaR is the
drift-adjusted 5th percentile. Ten-year expected maximum drawdown uses the
≈1.65–1.75 × σ approximation for a positively-drifting portfolio, cross-checked against
correlation-weighted sleeve drawdowns.

Market data is as of 4 September 2026 and sourced from fund issuers (iShares, Invesco),
Siblis Research and MSCI for valuations, the Federal Reserve, BLS, ECB, IMF, FRED, Cboe
and SEC filings. Sources are linked on the page.

The unconstrained max-Sharpe allocation over 5% increments is QQQ 5 / IEMG 70 / SGOV 20 /
BMNR 5. It is deliberately rejected: it over-fits the two least reliable inputs (EM
valuation reversion and currency drag) and concentrates a dollar investor in a bloc where
China alone is roughly a quarter of the index. The 40% cap keeps most of the benefit while
staying robust to those assumptions being wrong.

## Volatility regime

Weights are sized to *normalized* volatility, not today's calm. Spot VIX of 14.32 sits
roughly 24% below its 2016–2023 average of 18.9, so sleeve volatilities are scaled by
1.32 and correlations stressed toward crisis levels (QQQ·IEMG 0.72 → 0.85):

| Sleeve | σ calm | σ normalized |
|---|---|---|
| QQQ | 21.0% | 27.7% |
| IEMG | 18.0% | 23.8% |
| SGOV | 0.5% | 0.5% |
| BMNR | 95% | 109% |

Two findings constrained the answer:

- **The cash line is straight.** Substituting QQQ for SGOV from 35/20 through 15/40 gives
  an identical return-per-drawdown ratio of 0.113 at every step, because an uncorrelated
  near-zero-volatility asset traces a capital-allocation line. The optimizer cannot pick
  the cash weight; 30% is a stated drawdown budget, not a model output.
- **Variance math breaks on BMNR.** Under a lognormal model a +10% compound return at 109%
  volatility implies a 69.6% arithmetic mean, which nobody would forecast. A Booth-Fama
  rebalancing premium worth an apparent +2.9%/yr was computed, traced to this artefact,
  and discarded rather than published.

The equity tilt is unchanged across both regimes — the Sharpe ordering of every candidate
allocation survives — so volatility analysis altered how much to hold, not what to hold.

## Verification

Rev 2 re-checked every figure against primary sources. Fourteen corrections were recorded;
the two most consequential:

- The page asserted both that the VIX "sits near its 10-year average" and that the average
  was near 19 — a direct self-contradiction. The 2016–2023 mean is 18.9, so spot at 14.32
  is ~24% below it.
- QQQ trailing returns were carried from a 30 June factsheet without being marked stale,
  overstating the twelve-month run-up by 8 points (34.4% vs an actual 26.0%).

Others: SGOV yield 3.66→3.63%, BMNR mNAV 1.10→1.02× (total NAV, not crypto alone), China
GDP ~5→4.4% and India 6.4→6.3% (IMF), 3→5 FOMC officials favouring a hike, QQQ drawdown
history restated as ranges, severe-stress drawdown changed from asserted to derived, and
the QQQ fee-cut value corrected from $25 to $41 per $10,000.

A swipe-indicator bug was also fixed: dot tracking divided `scrollWidth` by slide count,
ignoring gap and padding, so the active dot drifted. It now selects the slide whose centre
is nearest the viewport centre.

## Disclaimer

Not investment advice. Forward figures are modelled estimates that depend on volatility,
correlation and terminal-valuation assumptions which will not hold exactly. BMNR carries
single-issuer, dilution and crypto-price risk that can result in total loss of that position.
