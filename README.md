# Four-Sleeve Allocation Desk

A mobile-first (Android) dashboard for a mandated four-holding universe — **SGOV**, **QQQ**,
**IEMG**, **BMNR** — on a 10-year horizon: macro sentiment gauge (1–5), regional rankings,
volatility analysis at 3/6/12 months, a slide per holding, and baseline vs optimized
portfolios as donuts, each with net-of-fee CAGR and expected drawdown.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

This README deliberately carries no market figures. Every number lives in one place — the
model — and reaches the page through the generator; copies of those numbers in prose were
the single most common defect in this repo's history (see VERIFICATION.md).

## Files

| File | Role |
|---|---|
| `portfolio_model.py` | Single source of truth: inputs, forecasts, risk, frontier, calibration. |
| `build.py` | Generates `allocation.html` from the model. Only dated facts (`FACTS`) are literal. |
| `page.css` | The page's stylesheet, inlined by `build.py`. |
| `allocation.html` | The generated page. Never edit by hand. |
| `validate.py` | Re-derives every figure on the page without importing `build.py`, checks the model's own consistency, and requires the page to be exactly what `build.py` writes. |
| `checklist.py` | The original brief as an acceptance test: PASS / FAIL / CONFLICT per requirement. |
| `mutate.py` | Mutation-tests `validate.py`: corrupts the model (the page must read as stale) and plants bugs in the generator (the independent checks must catch them). |
| `sync-artifact.sh` | Validates, then copies the page one way to the publish path. |
| `VERIFICATION.md` | Every recorded correction, newest first, and what caught it. |

## Workflow

```bash
# 1. change inputs in portfolio_model.py (bump REVISION, record the change in VERIFICATION.md)
python3 build.py                      # regenerate allocation.html
python3 validate.py                   # every figure, re-derived; exit 1 on any mismatch
python3 checklist.py --live <file>    # the brief; <file> = live page saved via Artifact read
python3 mutate.py                     # prove the checks bite
./sync-artifact.sh <publish-path>     # validate, then copy
```

## Data rules

- Market closes come from **history tables**, not live coverage. Each level is stored with the
  change its source reported and must reconcile with the close already on file; a level that
  does not reconcile fails at import. Two different snapshots can both reconcile from the same
  prior close, which is why the source must be the official close.
- Price-dependent inputs (dividend yield, forward P/E) derive from one price per fund.
- A day whose closes still conflict across sources is held back rather than averaged.
- Figures the model cannot compute (a CPI print, a PMI reading) go in `build.py`'s `FACTS`,
  each dated in the sentence that uses it, with sources linked on the page.

## Method, in brief

- **Forecasts** are building blocks: dividend yield + earnings growth + valuation change (the
  forward multiple annualised back to the index's own 10-year average) + currency − fee.
  BMNR is ETH return + staking − premium normalisation − dilution drag. SGOV is the policy
  midpoint held flat.
- **Risk** uses two regimes: today's volatility, and volatility mean-reverted to the VIX's
  2016–2023 mean with crisis correlations. Weights are sized to the second. Ten-year expected
  drawdown ≈ 1.70 × σ.
- **Allocation**: every 5%-step book holding all four sleeves at 5% or more is searched. The
  recommendation must sit on the return/drawdown efficient frontier; SGOV's weight is a stated
  drawdown budget (the capital-allocation line cannot choose it); BMNR is capped at 5% because
  of its share of risk.
- **Confidence**: standard errors, the probability the ranking holds, a sensitivity table and
  published house forecasts are shown with the answer, and three inputs are flagged as
  assumptions rather than observations.

## Checklist status

`checklist.py` reports 15 pass, 0 fail, 1 conflict. The conflict is item 9 — "data only from
authoritative sources" — because three inputs are extrapolations (QQQ's earnings growth, the
drawdown multiplier, BMNR's ETH return). The page discloses them; only the user can decide
whether that meets the brief.

## Disclaimer

Not investment advice. Forecasts are modelled estimates that will not hold exactly. BMNR carries
single-issuer, dilution and crypto-price risk, including total loss of that position.
