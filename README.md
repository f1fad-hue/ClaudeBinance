# Four-Sleeve Allocation Desk

A mobile-first (Android) portfolio dashboard for a mandated four-holding universe:
**SGOV**, **QQQ**, **IEMG**, **BMNR** — built on a 10-year investment horizon.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

## Contents

| File | Purpose |
|---|---|
| `allocation.html` | The dashboard. Bottom tab bar, light theme, five sections. |
| `portfolio_model.py` | Single source of truth for every figure on the page. |
| `validate.py` | Asserts the page matches the model. 151 checks, exits non-zero on drift. |
| `checklist.py` | Runs the original brief as an acceptance test. PASS / PASS* / FAIL / CONFLICT per requirement. |
| `sync-artifact.sh` | Validates, then copies the page one-way to the publish path. |

```bash
python3 portfolio_model.py   # readable report of every figure
python3 validate.py          # verify allocation.html against it
./checklist.py               # audit the deliverable against the original brief
./sync-artifact.sh           # validate, then push to the publish path
```

`checklist.py` encodes each requirement from the brief as a check, so the deliverable is
re-auditable rather than eyeballed. It currently reports **16 pass, 0 fail**.

One item carries `PASS*`: the brief asked for a 1–10 gauge, while later instructions asked
for 1–5 and then for the regional rankings to match. The user confirmed 1–5, so the item
passes but is marked as deviating from the brief's literal wording. Unresolved conflicts are
surfaced as `CONFLICT` and never silently settled.

This repo is the source of truth. `sync-artifact.sh` copies one way only —
copying back from the publish path once silently reverted a fix that had
already passed validation.

If a number changes in the model, the page is wrong until it changes there too.
`validate.py` covers sleeve figures, building blocks, both portfolios in both
volatility regimes, risk contributions, gauge and regional scores with their bar
fills, donut geometry, VIX term structure, the frontier and cash-line claims made
in the prose, and the brief's own weight constraints.

## Sections

1. **Macro** — composite driver gauge (1–5) over six weighted inputs, plus correlated
   transmission into each sleeve.
2. **Regions** — US / Europe / Asia-EM ranked 1–5 at 3, 6, 12 months and 10 years.
3. **Volatility** — VIX term structure, two-regime sizing, risk decomposition, 10-year
   regime view.
4. **Sleeves** — one swipeable slide per holding with net-of-fee CAGR and expected drawdown.
5. **Portfolios** — baseline vs optimized donuts, forecast comparison, rationale,
   verification log.

## Allocations

Weights are constrained to increments of 5, and all four sleeves must be held.

| Sleeve | Baseline | Optimized |
|---|---|---|
| QQQ  | 45% | 30% |
| IEMG | 25% | 35% |
| SGOV | 25% | 30% |
| BMNR |  5% |  5% |

| Metric | Baseline | Optimized |
|---|---|---|
| Net 10-yr CAGR | 7.50% | 7.16% |
| Weighted fee | 0.126% | 0.112% |
| σ — calm (today) | 16.59% | 15.20% |
| σ — vol normalized | 21.29% | 19.58% |
| Max drawdown — calm | −28.2% | −25.8% |
| Max drawdown — normalized | −36.2% | −33.3% |
| Correlated-stress drawdown | −30.6% | −27.9% |

The optimized book is driven by macro sentiment, regional rankings **and** volatility
analysis across 3, 6 and 12 months. It does not dominate the baseline on every axis:
it gives up 0.34 points of CAGR to buy 2.9 points of drawdown, and the risk-adjusted
margin is now thin (0.263 against 0.262).

## Method

Equity forecasts are built from observable components rather than asserted. Components
are rounded to displayed precision before summing, so every figure on the page can be
reproduced by hand from the components shown.

| Component | QQQ | IEMG |
|---|---|---|
| Dividend yield | +0.65 | +2.26 |
| Earnings growth | +9.50 | +7.50 |
| Valuation change | −0.94 | +0.42 |
| Currency drag | — | −1.50 |
| **Gross** | **9.21** | **8.68** |
| Expense ratio | −0.18 | −0.09 |
| **Net** | **9.03** | **8.59** |

Valuation change annualises the forward multiple moving from its observed level
(QQQ 25.2×, IEMG 11.7×) to **that index's own 10-year average** (NDX 22.9×, MSCI EM 12.2×)
over ten years. One rule governs both sleeves. An earlier revision used a hand-picked 21×
for QQQ — below its own average — while holding IEMG only to its average; that asymmetry
favoured the EM sleeve and has been removed.
BMNR is modelled separately: 9.0% ETH appreciation, +2.58% staking on 85.9% of the
treasury, −0.20% mNAV normalisation, −1.40% corporate and dilution drag.

## Sentiment scales

Both the composite gauge and the regional rankings use 1–5, where 3 is neutral.
Converting a 1–10 score is `1 + (x-1) * 4/9`, not division by two, since both scales
floor at 1. Arcs and bars fill on `(score-1)/4` so the scale's floor sits at the left
stop rather than at zero.

Composite reads **2.5/5**. Regional means: Asia/EM 3.5, US 3.2, Europe 2.3 — ordering
preserved at every horizon, which is the check that the rescale is presentational only.

## Volatility regime

Weights are sized to *normalized* volatility, not today's level. Spot VIX of 15.30 sits
~19% below its 2016–2023 average of 18.9, so sleeve volatilities are scaled by 1.24 and
correlations stressed toward crisis levels (QQQ·IEMG 0.72 → 0.85):

| Sleeve | σ calm | σ normalized |
|---|---|---|
| QQQ | 21.0% | 25.9% |
| IEMG | 18.0% | 22.2% |
| SGOV | 0.5% | 0.5% |
| BMNR | 95% | 109% |

Two findings constrained the answer:

- **The cash line is straight.** Scaling a fixed risky mix against cash holds
  return-per-drawdown at 0.1208 regardless of the cash weight — invariant to 2.8e-17,
  since an uncorrelated zero-variance sleeve scales return and risk by the same factor.
  The optimizer cannot pick the cash weight; 30% is a stated drawdown budget, not a model
  output. Earlier revisions demonstrated this with QQQ traded against SGOV at a pinned
  IEMG; that is *not* a pure CAL (the risky mix changes, not just its scale) and drifts
  0.115 → 0.114. `cal_line()` now carries the theorem, `cash_line()` the illustration.
- **Variance math breaks on BMNR.** Under a lognormal model a +10% compound return at 109%
  volatility implies a 69.6% arithmetic mean, which nobody would forecast. A Booth-Fama
  rebalancing premium worth an apparent +2.9%/yr was computed, traced to this artefact,
  and discarded rather than published.

Subject only to the brief's floor of 5% per sleeve, the highest return-per-unit-risk mix
is QQQ 5 / IEMG 85 / SGOV 5 / BMNR 5 (Sharpe 0.273 vs the recommended book's 0.251). It is
rejected: it over-fits the two least reliable inputs and carries a −43.6% normalised
drawdown. The 40% cap keeps most of the benefit while staying robust to those assumptions
being wrong.

## Verification

Forty-two corrections have been recorded across six verification passes. The most
consequential:

- **The terminal multiples were asymmetric — the largest error found.** IEMG's terminal
  multiple was anchored to its own 10-year average (12.2×); QQQ's was hand-set at 21×,
  *below* its own 10-year average of 22.9×. One sleeve was held to its history and the
  other marked down past it, and the asymmetry favoured the EM tilt, which is the page's
  central recommendation. Applying one rule to both adds 0.85 points to QQQ and reverses
  the ranking: QQQ now out-earns IEMG, 9.03% vs 8.59%. The claim that IEMG improved return
  and risk together is withdrawn; the tilt survives on risk-adjusted grounds only and was
  trimmed 40% → 35%.
- September hike odds of 68% were an outlier. CME FedWatch read 58.7% on 7 September and
  ~59% on 9 September, swinging 55–68% inside a week.

- An energy supply shock arrived. Iran-aligned strikes halted Saudi output, Brent reached
  $99.16, and September hike odds rose to 68%. Four of six drivers fell and the composite
  moved 2.7 → **2.5**, its first real move in four passes. It cuts against the EM tilt from
  a new direction — Asia imports most of its energy — so the 3-, 6- and 12-month Asia
  scores were cut; only the 10-year score stands.
- The cash-line claim was overstated. The page asserted an identical return-per-drawdown
  ratio at every step of the QQQ↔SGOV substitution. Pinning IEMG changes the risky mix, not
  merely its scale, so it drifts 0.115 → 0.114. The underlying theorem holds exactly for a
  true CAL, and the demonstration was replaced with one that shows it.

- A premise had gone stale. The page rested the EM sleeve partly on a Fed that *held*
  rather than hiked, capping dollar strength. The 4 September payrolls print — 162,000
  against a 53,000 consensus — moved futures to a ~58–62% chance of a September hike, so
  that premise no longer holds. The overweight now stands on the ten-year valuation gap
  alone, the Asia 3-month score was cut, and one of the page's own stated revisit triggers
  is marked as fired.
- The EM terminal multiple was too aggressive. 11.7× forward sits below the 10-year average
  of 12.2× but level with the 20-year average of 11.7×, so the assumed 12.5× exceeded both
  anchors. Re-anchoring to 12.2× cuts IEMG's forecast by 0.32 points and narrows its edge
  over QQQ from 0.76 to 0.44. The 40% tilt survives — a sensitivity sweep shows IEMG still
  improving return and drawdown together from 25% to 50% — but on a thinner margin.
- BMNR's capital policy reversed. The company authorised a $4B buyback and repurchased ~3M
  shares while its weekly ETH purchase fell to the smallest of 2026, so the page's
  "severe dilution as equity is issued to buy ETH" narrative was out of date. The −1.40%/yr
  corporate drag is unchanged, since less issuance is offset by a slower ETH-per-share
  engine.

- The page asserted both that the VIX "sits near its 10-year average" and that the average
  was near 19 — a direct self-contradiction. The 2016–2023 mean is 18.9, so spot at 14.32
  is ~24% below it.
- QQQ trailing returns were carried from a 30 June factsheet without being marked stale,
  overstating the twelve-month run-up by 8 points (34.4% vs an actual 26.0%).
- The stated unconstrained frontier optimum was an artefact of a 20% cash floor left over
  from an earlier run and never stated as an assumption. Against the brief's actual floor
  the optimizer wants 85% in emerging markets.
- The gauge arc filled `value/10` when the scale's floor is 1, overstating the needle by
  ~6 points of arc.
- A stale mid-band drawdown reference of −27.2% survived from when the optimized book was
  30/40/25/5. It was fixed, then silently reverted by copying the published file back over
  the repo copy — which is why `sync-artifact.sh` now exists and only copies one way.

Data corrections: SGOV yield 3.66→3.63%, BMNR mNAV 1.10→1.02× (total NAV, not crypto
alone), China GDP ~5→4.4% and India 6.4→6.3% (IMF), three→five FOMC officials favouring a
hike, QQQ drawdown history restated as ranges, severe-stress drawdown changed from asserted
to derived, QQQ fee-cut value $25→$41 per $10,000, and the August payrolls print (162,000,
beating consensus) added.

Arithmetic corrections found by `validate.py`: optimized σ normalized 20.39→20.38%, max
drawdown −34.7→−34.6%, risk contributions IEMG 44.3→44.2% and BMNR 23.4→23.5%, and the
baseline terminal value $20,052→$20,061 (it had been computed from an unrounded CAGR while
the page displayed a rounded one).

## Disclaimer

Not investment advice. Forward figures are modelled estimates that depend on earnings
growth, terminal valuation, currency, volatility and correlation assumptions which will not
hold exactly. Market data is as of 4 September 2026. BMNR carries single-issuer, dilution
and crypto-price risk that can result in total loss of that position.
