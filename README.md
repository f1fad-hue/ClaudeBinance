# Four-Sleeve Allocation Desk

A mobile-first (Android) portfolio dashboard for a mandated four-holding universe:
**SGOV**, **QQQ**, **IEMG**, **BMNR** — built on a 10-year investment horizon.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

Market data to the **23 September 2026** close (Rev. 20). Fund prices carry their own
dates — QQQ 22 September, IEMG 18 September — and move when newer closes are verified.

## Contents

| File | Purpose |
|---|---|
| `allocation.html` | The dashboard. Bottom tab bar, light theme, five sections. |
| `portfolio_model.py` | Single source of truth for every figure on the page. |
| `validate.py` | Asserts the page matches the model, plus model self-consistency. 424 checks. |
| `checklist.py` | Runs the original brief as an acceptance test. PASS / FAIL / CONFLICT per requirement. |
| `mutate.py` | Mutation-tests the validator: corrupts one model input at a time and checks validate.py fails. 62 mutations. |
| `VERIFICATION.md` | Every recorded correction, newest first, with what caught it. |
| `sync-artifact.sh` | Validates, then copies the page one-way to the publish path. |

```bash
python3 portfolio_model.py   # readable report of every figure
python3 validate.py          # verify allocation.html against it
./checklist.py --live <file> # audit against the brief; <file> is the live page saved via Artifact read
python3 mutate.py            # prove validate.py actually fails when the model changes
./sync-artifact.sh <path>    # validate, then copy to the publish path
```

`checklist.py` encodes each requirement from the brief as a check, so the deliverable is
re-auditable rather than eyeballed. It currently reports **15 pass, 0 fail, 1 conflict**.
With `--live` it also compares the page the HTTPS link actually serves against the validated
file and checks the host shell sets a device-width viewport — the published file is a
fragment, so that shell is what makes Android lay it out at phone width. The last recheck
(24 September) found the live page byte-identical and passed a Pixel 7 emulation run: 412px
layout, fixed bottom tabs, all five panes, swipeable slides, light background, no errors.

Item 6 reads the gauge requirement as 1–5: the brief first asked for 1–10, later
instructions asked for 1–5 and then for the regional rankings to match, and the user
confirmed 1–5. Item 15 tests Pareto efficiency over all 969 admissible allocations rather
than "beats the baseline on Sharpe" — the earlier criterion, which the brief never asked
for and which QQQ's correction broke. The old criterion is kept in a comment so the change
reads as a fix, not as moved goalposts.

Item 9 is the conflict. The brief asks for data only from authoritative sources; every
observable figure here has one, but three inputs are extrapolations rather than
observations — QQQ's 9.5%/yr earnings growth, the 1.70 × σ drawdown multiplier, and BMNR's
9%/yr ETH assumption — and the first is the most load-bearing number on the page. The
check used to count source domains, which tested whether the page *cites* authorities
rather than whether its numbers come from them, and passed. It now reports CONFLICT, which
is surfaced for the user to settle and does not set the exit code.

This repo is the source of truth. `sync-artifact.sh` copies one way only —
copying back from the publish path once silently reverted a fix that had
already passed validation.

If a number changes in the model, the page is wrong until it changes there too.
`validate.py` covers sleeve figures, building blocks cell by cell, both portfolios in both
volatility regimes, the VaR table cell by cell, risk contributions (scoped to their own
card), gauge and regional scores with their bar fills, donut geometry, the VIX series and
every figure derived from it, the frontier and cash-line claims made in the prose, the
forward multiples quoted in prose, the rationale and recommendation figures, the masthead's
market levels (each reconciled against the change its source reported), the comparison
table's Δ column, and the brief's own weight constraints. It also asserts the model is internally coherent regardless
of the page: risk contributions sum to 100, portfolio sigma sits between the min and max
sleeve sigma, VaR worsens monotonically with horizon, normalized sigma exceeds calm,
forecast components sum to their gross, and driver weights sum to one. The frontier chart
and the sensitivity table are regenerated and must appear verbatim, and a list of phrases
that were once true — relative dates, superseded levels, superlatives the data cannot back —
must not reappear outside the verification log.

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
| QQQ  | 45% | 35% |
| IEMG | 25% | 30% |
| SGOV | 25% | 30% |
| BMNR |  5% |  5% |

| Metric | Baseline | Optimized |
|---|---|---|
| Net 10-yr CAGR | **7.86%** | 7.54% |
| Weighted fee | 0.126% | 0.117% |
| σ — calm (today) | 16.44% | 15.22% |
| σ — vol normalized | 21.23% | 19.74% |
| Max drawdown — calm | −27.9% | −25.9% |
| Max drawdown — normalized | −36.1% | **−33.6%** |
| Correlated-stress drawdown | −32.1% | −30.0% |
| Return / risk (calm) | 0.248 | 0.246 |

The optimized book is driven by macro sentiment, regional rankings **and** volatility
analysis across 3, 6 and 12 months. It does not dominate the baseline on every axis:
it gives up 0.32 points of CAGR to buy 2.5 points of normalized drawdown, at a return per
unit of risk two thousandths lower. It is the lower-drawdown choice, not the better book.

## Is the recommendation efficient?

Exhaustively: all 969 allocations the brief permits (four sleeves, multiples of 5, none
below 5%) plotted by net CAGR against normalised drawdown. **The optimized book is on the
efficient frontier; the baseline, by a hair, is not.** It is beaten by exactly one allocation
— QQQ 15 / IEMG 60 / SGOV 20 / BMNR 5 — by +0.01 points of CAGR and 0.1 of drawdown, which
is a technicality rather than a verdict. The baseline had sat on the frontier from Rev. 10
through Rev. 18; tying both forward multiples to price in Rev. 19 moved the curve back
toward emerging markets.

Two limits are stated rather than glossed. "Best" is a curve, not a point — 107
allocations are efficient and the right one depends on the drawdown actually tolerated.
And the curve is nearly straight: at the recommendation, one more point of drawdown buys
about 0.09 points of CAGR, and that ratio barely changes along it — which is the frontier
telling you the same thing the capital-allocation line does. Beyond BMNR 45% the frontier
returns drawdowns worse than −100%, which is impossible — the variance model fails exactly
where this repo already documents it failing, so the curve is drawn only where BMNR stays
at 5%.

## Method

Equity forecasts are built from observable components rather than asserted. Components
are rounded to displayed precision before summing, so every figure on the page can be
reproduced by hand from the components shown. Rounding is half-up on the decimal value,
with float dust snapped off first (`r2h()`), since a difference that is exactly −0.0395
arrives from floating point as −0.03949… and would otherwise round the wrong way.

| Component | QQQ | IEMG |
|---|---|---|
| Dividend yield | +0.41 | +2.20 |
| Earnings growth | +9.50 | +7.50 |
| Valuation change | −0.22 | +0.62 |
| Currency drag | — | −1.50 |
| **Gross** | **9.69** | **8.82** |
| Expense ratio | −0.18 | −0.09 |
| **Net** | **9.51** | **8.73** |

Both price-sensitive inputs are tied to one price per fund (`PRICES`). The dividend yield
is the trailing-twelve-month distribution over the latest close — QQQ $3.03 / $747.46 on
22 September, IEMG $1.80 / $81.66 on 18 September. The forward multiple is the 11 September
basis scaled by the same price move: QQQ 22.4× → **23.42×** (+4.6%), IEMG 11.7× → **11.47×**
(−2.0%). Until Rev. 19 neither input was tied to price: both sat at the 11 September basis
while the page's stamp moved on, so a 4.6% QQQ rally left its forecast untouched.

Valuation change annualises the forward multiple moving from that level to **the index's
own 10-year average** (NDX 22.9×, MSCI EM 12.2×) over ten years. One rule governs both
sleeves. QQQ now sits above its average and carries a de-rating; IEMG sits below both its
10-year and 20-year (11.7×) means.

BMNR is modelled separately: 9.0% ETH appreciation, +2.22% staking (84.7% of the treasury
staked at the company's reported 2.62% seven-day yield), −0.77% mNAV normalisation from
1.08× on crypto holdings, −1.40% corporate and dilution drag — **9.05%**.

## Sentiment scales

Both the composite gauge and the regional rankings use 1–5, where 3 is neutral.
Converting a 1–10 score is `1 + (x-1) * 4/9`, not division by two, since both scales
floor at 1. Arcs and bars fill on `(score-1)/4` so the scale's floor sits at the left
stop rather than at zero.

Composite reads **2.4/5**. Regional means: Asia/EM 3.5, US 3.2, Europe 2.3 — ordering
preserved at every horizon, which is the check that the rescale is presentational only.

## Volatility regime

Weights are sized to *normalized* volatility, not today's level. Spot VIX of **15.35**
(23 September, up 8.0% on the day) sits 18.8% below its 2016–2023 average of 18.9, so sleeve
volatilities are scaled by 1.23 and correlations stressed toward crisis levels (QQQ·IEMG
0.66 → 0.85). A session earlier the VIX closed at 14.21, a 21-session low and 0.08 above the
2026 low of 14.13 (14 August). The revisit trigger, a sustained VIX above 18.9, is 3.55 points
away; on decision day it was 1.19.

The VIX is stored as a dated series (`VIX_SERIES`), not a single typed number, and
`VIX_SPOT` is read from its last entry. A level published from a source whose own stated
change will not reconcile with the close already on file is a build failure, because
that is exactly how a wrong one got through — twice now. The masthead's Brent and 10-year
levels follow the same rule through `MARKET`.

| Sleeve | σ calm | σ normalized |
|---|---|---|
| QQQ | 21.0% | 25.9% |
| IEMG | 18.0% | 22.2% |
| SGOV | 0.5% | 0.5% |
| BMNR | 95% | 109% |

Two findings constrained the answer:

- **The cash line is straight — to within SGOV's own volatility.** Scaling a fixed risky
  mix against cash holds return-per-drawdown at **0.1117** regardless of the cash weight.
  With truly riskless cash that is exact (`cal_line(cash_vol=0)` holds to 5.6e-17), since
  excess return and risk both scale by the risky weight. SGOV carries 0.5% volatility in
  this model, which leaves a residual of **6.7e-6** along the line. Earlier revisions of
  this README and the page called it "invariant to machine precision", which was never true
  of the model; both now state the residual, and `validate.py` tests the theorem and the
  residual separately. The optimizer cannot pick the cash weight; 30% is a stated drawdown
  budget, not a model output. The QQQ-against-SGOV illustration with IEMG pinned is *not* a
  pure CAL (the risky mix changes, not just its scale) and drifts 0.114 → 0.108.
- **Variance math breaks on BMNR.** Under a lognormal model a +10% compound return at 109%
  volatility implies a 69.6% arithmetic mean, which nobody would forecast. A Booth-Fama
  rebalancing premium worth an apparent +2.9%/yr was computed, traced to this artefact,
  and discarded rather than published.

Subject only to the brief's floor of 5% per sleeve, the highest return-per-unit-risk mix
is QQQ 40 / IEMG 50 / SGOV 5 / BMNR 5 (Sharpe 0.260 vs the recommended book's 0.246). It
is rejected — and a search over every BMNR weight, not just 5%, returns the same book. It over-fits the two least reliable inputs and holds only 5% in reserve, which
is not a drawdown budget anyone would choose. The same search has wanted 85% in emerging
markets and 60% in the Nasdaq-100 in earlier revisions; that instability is the subject of
the calibration section below.

## How much to trust it

Every figure above is a point estimate, so the page carries the distribution around it.

| Optimized book, 10 yr | Calm | Normalized |
|---|---|---|
| Net CAGR | 7.54% | 7.54% |
| Standard error, σ/√10 | ±4.81 | ±6.24 |
| 95% band | −1.9 to 17.0 | −4.7 to 19.8 |

**Of the 969 admissible allocations, 0 are statistically distinguishable from the
recommendation at 95% over ten years.** For two books drawn from the same four sleeves,
`z ≈ IR × √T`; an information ratio of 0.20 gives `z = 0.62` where 1.96 is needed. Proving
the baseline out-returns the recommendation would take **99 years**; proving the
recommended book beats T-bills would take **63**; the most separable alternative in the
whole set (QQQ 40 / IEMG 35 / SGOV 20 / BMNR 5) still needs 43.

A *comparison* is far better determined than a *level*. The two books share three of four
sleeves, so their difference is a 10-point switch with a tracking volatility of 1.65%/yr —
a standard error of 0.52 points against ±4.81 on either book alone. The 0.32-point gap is
0.62 SE, a **73% chance the baseline ends ahead on return**.

`calibration()`, `separable()`, `tracking()` and `se_level()` in the model compute all of it;
`validate.py` asserts the page's figures against them.

### Which input to argue with first

Each input moved one unit and rebuilt through the same code path as `build()`.

| Input | Now | Δ CAGR | Δ gap |
|---|---|---|---|
| QQQ earnings growth | 9.5% | −0.35 | −0.100 |
| IEMG earnings growth | 7.5% | −0.30 | +0.050 |
| SGOV gross yield | 3.875% | +0.30 | −0.050 |
| IEMG currency drag | −1.50% | +0.30 | −0.050 |
| IEMG forward P/E | 11.47× | −0.25 | +0.042 |
| IEMG terminal P/E | 12.2× | +0.24 | −0.040 |
| QQQ terminal P/E | 22.9× | −0.16 | −0.045 |
| QQQ forward P/E | 23.42× | −0.15 | −0.042 |
| BMNR ETH return | 9.0% | −0.05 | +0.000 |
| BMNR staking yield | 2.62% | −0.04 | +0.000 |

The most load-bearing input is **QQQ's 9.5% earnings-growth assumption** — 0.35 of CAGR
and 0.100 of the gap per point, double any other input's effect on the gap — and it is the
one number on the page that extrapolates a cycle across a decade rather than observing it.
A point off IEMG's currency drag moves the gap by 0.05; closing the 0.32-point gap that way
would take more than six points of it. BMNR's inputs move the level and nothing about the
choice, since both books hold exactly 5%.

### Against the professionals

Ten-to-fifteen-year, USD, total return, gross of fund fees — the same basis as this repo's
figures.

| Source | US | EM | Note |
|---|---|---|---|
| J.P. Morgan LTCMA 2026 | 6.7% | 7.8% | US large cap; EM vol 20.9% |
| Fidelity | 4.4% | 8.1% | US large cap midpoint 3.4-5.4; US growth 2.3-4.3 |
| Vanguard | 5.2% | 4.3% | midpoints of 4.2-6.2 and 3.3-5.3 |
| BlackRock | 5.0% | 7.1% | EM figure is non-US broadly |
| **This page** | **9.69%** | **8.82%** | building blocks, see Method |

The US figure is 3.0 points above the highest of them, J.P. Morgan's US large cap, and
Fidelity puts US *growth* stocks, the closest published proxy for the Nasdaq-100, at
2.3–4.3%. The EM figure is above every house too, but by 0.7 points over the highest,
Fidelity's 8.1% — the page previously called it "bracketed by" 7.8% and 8.1%, which it
never was. Three of the four rank emerging markets *above* the US, the ranking this repo
reversed in Rev. 8; Vanguard is the exception. J.P. Morgan's 20.9% EM volatility currently
falls between this page's two regimes (18.0% calm, 22.2% normalised); the comparison has
flipped twice in the nine sessions on file, because the uplift factor moves inversely with
spot VIX, and the reason both regimes are reported rather than one.

`scenario()` re-runs the whole comparison on a different set of sleeve returns with every
risk input untouched, so it isolates how much of the answer rests on this repo's own
forecasts:

| | This page | J.P. Morgan inputs |
|---|---|---|
| Baseline CAGR | 7.86% | 6.26% |
| Optimized CAGR | 7.54% | 6.18% |
| Baseline's lead | +0.32 | +0.08 |
| Best-Sharpe book | 40/50/5/5 | 5/85/5/5 |
| Efficient allocations | 107 | 17 |
| Both books efficient | optimized only | neither |

The sizing survives and the baseline still leads, but the margin collapses from 0.32 to 0.08
and the best risk-adjusted book moves to the largest EM tilt the brief allows. So "QQQ leads
and the EM overweight costs return" is a consequence of one assumption — 9.5%/yr of
Nasdaq-100 earnings growth for a decade — that three of four houses implicitly reject. The
repo keeps its own arithmetic, because a building-block forecast can be checked line by line
and a house forecast cannot, but a reader who trusts J.P. Morgan over this page should hold
*more* emerging markets, not less.

## Verification

One hundred and seventy-seven corrections have been recorded across nineteen verification
passes; [VERIFICATION.md](VERIFICATION.md) has every one, newest first. This pass (Rev. 20):

- **Two closes the page already held were wrong, and the next day's quotes proved it.** The
  23 September VIX close was reported as 15.35, +1.14 / +8.02% — which reconciles only from
  **14.21**, the figure the 22nd's own report gives ("fell 4.44% to 14.21, a 21-session low").
  The page carried 14.25. The 10-year's +16bp to 5.12% on the 23rd is quoted from **4.96%**;
  the page carried 4.93% for the 22nd. The masthead levels now live in `MARKET` with their
  reported changes, and a level that does not reconcile fails at import.
- **The 2026 VIX low was misdated.** 14.13 was set on Friday **14 August** ("fell to 14.13 on
  Friday, its lowest level of 2026", reported 17 August); Rev. 19 gave 28 August, which the
  21-session low on 22 September rules out.
- **A safety check that could never fire.** The blacklist meta-check compared whole strings
  against bare figures, but every entry is anchored to markup, so it could never match. When
  BMNR's risk share returned to 24.5% the build failed on a correct figure — the case it was
  written for. It now compares the figures inside each entry.
- **Checks that were missing.** The term-structure 1-day row, the comparison table's Δ column,
  the masthead levels, the volatility hero card, the slide hero figures and the rationale's
  CAL ratio were unchecked or checked only page-wide; the best-Sharpe claim ("subject only to
  the 5% floor") was tested with BMNR pinned; the term σ used `round()`, so an exact 7.675
  printed 7.67. All asserted now; `mutate.py` 46 → **62** mutations, 0 survived.
- **Code review.** `build()` and `build_with()` now share one core; the model report printed
  "IEMG fixed at 40" for a cash line pinned at 30; `checklist.py` typed the three assumed
  inputs instead of reading them; `sync-artifact.sh` defaulted to one session's scratch path.
- **Market data to 23 September.** Hot flash PMIs (services 58.7, composite 58.4, output
  growth fastest in over five years) sent the 10-year to **5.12%**, its highest since 2007;
  Brent settled **$103.08**; the VIX rose to **15.35**. Sleeve forecasts are unchanged — fund
  prices are held at their last verified closes — and the higher VIX eases the normalized
  drawdowns to −36.1% / **−33.6%**. The optimized book is still efficient, the baseline still
  off the frontier by 0.01 of CAGR, and the weights are unchanged.

## Disclaimer

Not investment advice. Forward figures are modelled estimates that depend on earnings
growth, terminal valuation, currency, volatility and correlation assumptions which will not
hold exactly. Market data is to the 23 September 2026 close. BMNR carries single-issuer, dilution
and crypto-price risk that can result in total loss of that position.
