# Four-Sleeve Allocation Desk

A mobile-first (Android) dashboard for a mandated four-holding universe — **SGOV**, **QQQ**,
**IEMG**, **BMNR** — on a 10-year horizon: macro sentiment gauge (1–5), regional rankings,
market trend and volatility analysis at 3/6/12 months, a slide per holding, and baseline vs
optimized portfolios as donuts, each with net-of-fee CAGR and expected drawdown. The optimized
book is derived from the baseline by a stated rule, one step per pillar, not typed.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

This README deliberately carries no market figures. Every number lives in one place — the
model — and reaches the page through the generator; copies of those numbers in prose were
the single most common defect in this repo's history (see VERIFICATION.md).

## Files

| File | Role |
|---|---|
| `portfolio_model.py` | Single source of truth: inputs, forecasts, risk, frontier, calibration, the 3/6/12-month trend table and the allocation rule (`tilt_book`). |
| `build.py` | Generates `allocation.html` from the model. Only dated facts (`FACTS`) are literal. |
| `page.css` | The page's stylesheet, inlined by `build.py`. |
| `allocation.html` | The generated page. Never edit by hand. |
| `validate.py` | Re-derives every figure on the page without importing `build.py`, checks the model's own consistency, and requires the page to be exactly what `build.py` writes. Re-implements the allocation rule independently and runs it under counterfactual inputs. |
| `checklist.py` | The original brief as an acceptance test: PASS / FAIL / CONFLICT per requirement. |
| `mutate.py` | Mutation-tests `validate.py`: corrupts the model (the page must read as stale) and plants bugs in the generator (the independent checks must catch them). Refuses to run unless the unmutated repo passes, since a failing baseline would make every mutant look caught. |
| `phone.mjs` | Renders the page as an Android phone (412px and 360px) in Chromium and fails on what string checks cannot see: a tab that does not switch, anything off-screen, a table that hides columns, a malformed pill, text under 9px. |
| `sync-artifact.sh` | Validates, then copies the page one way to the publish path. |
| `VERIFICATION.md` | Every recorded correction, newest first, and what caught it. |

## Workflow

```bash
# 1. change inputs in portfolio_model.py (bump REVISION, record the change in VERIFICATION.md)
python3 build.py                      # regenerate allocation.html
python3 validate.py                   # every figure, re-derived; exit 1 on any mismatch
python3 checklist.py --live <file>    # the brief; <file> = live page saved via Artifact read
python3 mutate.py                     # prove the checks bite
NODE_PATH=$(npm root -g) node phone.mjs 412 && NODE_PATH=$(npm root -g) node phone.mjs 360
./sync-artifact.sh <publish-path>     # validate, then copy
```

## Data rules

- Market closes come from **history tables**, not live coverage. Each level is stored with the
  change its source reported (`VIX_REPORTED`, the `*_prev` fields in `MARKET`) and must
  reconcile with the close already on file; a level that does not reconcile fails at import. Two different snapshots can both reconcile from the same
  prior close, which is why the source must be the official close.
- A new VIX close needs **two independent sources** (`VIX_SOURCES`, asserted at import). A
  source's own reported change is not a second source: a wrong close posted with its matching
  change reconciles perfectly, which is how Rev. 25's 2 October error got through.
- Trend returns are **total returns to the last quarter end** (`TREND_ASOF`) from the fund
  sponsors' and index providers' own tables. Where only parts are published, the parts are
  stored (`TREND_CHAIN`, `TREND_LEVELS`) and `validate.py` rebuilds the figure from them.
- Price-dependent inputs (dividend yield, forward P/E) derive from one price per fund.
- A close that still conflicts across sources is held back rather than averaged. The model
  records the held date and the range reported (`VIX_HELD`), and every sentence that quotes the
  held series says which close it uses.
- Before a value is held as "conflicting", check whether the other reading is the same item a
  period earlier. Both of Rev. 26's dividend "conflicts" were last year's payouts, and one hold
  left QQQ's trailing dividend a quarter stale.
- Trailing dividends are the sum of the dated payouts at the precision paid, not rounded to
  the cent; `validate.py` re-sums its own transcription of them. Rev. 28's cent-rounded $1.80
  for IEMG moved its yield by 0.01 point.
- Any fund price, dividend or house forecast is used only from a dated source, with the
  latest close two sources agree on. A later close with one source, or two that disagree, is
  held back and recorded with the sensitivity it would carry.
- A level whose close lags the market date keeps its own date (`MARKET['ust10_asof']`), and
  every sentence and the masthead that quote it say so.
- BMNR's price is the close of the first session after the holdings date of the release it
  is paired with, never a later close against older holdings; `validate.py` enforces it.
- Figures the model cannot compute (a CPI print, a PMI reading) go in `build.py`'s `FACTS`,
  each dated in the sentence that uses it, with sources linked on the page.

## Method, in brief

- **Forecasts** are building blocks: dividend yield + earnings growth + valuation change (the
  forward multiple annualised back to the index's own 10-year average) + currency − fee.
  BMNR is ETH return + staking ± the move of its mNAV to 1.0× (a cost above 1.0×, a gain
  below it) − dilution drag. SGOV is the policy
  midpoint held flat.
- **Risk** uses two regimes: today's volatility, which scales with the spot VIX, and the
  volatility at the VIX's 2016–2023 mean, which does not depend on spot, with crisis
  correlations. Weights are sized to the second. Ten-year expected drawdown ≈ 2.00 × σ, the
  mean of a daily-step simulation of each book; `validate.py` re-runs a seeded version.
  `validate.py` re-runs the model at a different VIX to prove that independence.
- **Trend**: each market's 3-, 6- and 12-month total return scores +1, 0 or −1 (a move inside
  ±2% is flat), 12 months counted double; +2 or more is an uptrend, −2 or less a downtrend.
- **Allocation**: every 5%-step book holding all four sleeves at 5% or more is searched. The
  optimized book starts from the strategic baseline and each pillar may move one 5-point step:
  regional rankings (the leader must lead at 3 months *and* 10 years), broad and correlated
  sentiment (a gauge below 2.6 grows the reserve, funded by the worst-rated equity sleeve on
  the transmission map that is above its 5% floor), volatility (a five-session average VIX at
  or above its mean spends the reserve; one close does not), market trend (a
  downtrend cuts a sleeve; a QQQ–IEMG trend net of ±2 moves a step), then drawdown control
  (if a book one step away beats the result on both net CAGR and normalized drawdown, move to
  the one with the least drawdown; a dominating book further away is reported, not taken). The page lists each step and what would change it. The result must sit on the
  return/drawdown efficient frontier; SGOV's weight is a stated drawdown budget (the
  capital-allocation line cannot choose it); BMNR is capped at 5% because of its share of risk.
- **Confidence**: standard errors, the probability the ranking holds, a sensitivity table and
  published house forecasts are shown with the answer, and every input the model cannot
  observe is tagged `ASSUMED` in the model and listed on the page.

## Checklist status

`checklist.py` reports 16 pass, 0 fail, 1 conflict. The conflict is item 9 — "data only from
authoritative sources" — because some forecast inputs are assumptions rather than
observations. They are tagged in the model (`ASSUMED`), listed on the page from that tag, and
QQQ's earnings growth is the most load-bearing. Only the user can decide whether that meets
the brief. Portfolio CAGR is a weight-average of sleeve CAGRs, which omits the rebalancing
(diversification) return, so the headline figures are conservative; the page states by how much.

## Disclaimer

Not investment advice. Forecasts are modelled estimates that will not hold exactly. BMNR carries
single-issuer, dilution and crypto-price risk, including total loss of that position.
