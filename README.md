# Four-Sleeve Allocation Desk

A mobile-first (Android) portfolio dashboard for a mandated four-holding universe:
**SGOV**, **QQQ**, **IEMG**, **BMNR** — built on a 10-year investment horizon.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

## Contents

| File | Purpose |
|---|---|
| `allocation.html` | The dashboard. Bottom tab bar, light theme, five sections. |
| `portfolio_model.py` | Reproduces every number on the page: CAGR, volatility, VaR, drawdown, risk contribution. |

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
| QQQ  | 45% | 35% |
| IEMG | 25% | 35% |
| SGOV | 25% | 25% |
| BMNR |  5% |  5% |

| Metric | Baseline | Optimized |
|---|---|---|
| Net 10-yr CAGR | 7.21% | 7.24% |
| Weighted fee | 0.126% | 0.117% |
| Annualised σ | 16.59% | 16.16% |
| Expected max drawdown | −28.3% | −26.7% |

## Method

Forward CAGR is a gross forecast per sleeve less its stated expense ratio. Portfolio
volatility is computed from a correlation matrix (QQQ·IEMG 0.72, QQQ·BMNR 0.65,
IEMG·BMNR 0.55, SGOV uncorrelated). Horizon volatility scales as σ√(h/12); VaR is the
drift-adjusted 5th percentile. Ten-year expected maximum drawdown uses the
≈1.65–1.75 × σ approximation for a positively-drifting portfolio, cross-checked against
correlation-weighted sleeve drawdowns.

Market data is as of 4 September 2026 and sourced from fund issuers (iShares, Invesco),
the Federal Reserve, BLS, ECB, IMF, FRED, Cboe and SEC filings. Sources are linked on
the page.

## Disclaimer

Not investment advice. Forward figures are modelled estimates that depend on volatility,
correlation and terminal-valuation assumptions which will not hold exactly. BMNR carries
single-issuer, dilution and crypto-price risk that can result in total loss of that position.
