# Four-Sleeve Allocation Desk

A mobile-first (Android) portfolio dashboard for a mandated four-holding universe:
**SGOV**, **QQQ**, **IEMG**, **BMNR** — built on a 10-year investment horizon.

Live page: https://claude.ai/code/artifact/ae9d19e3-750e-4ca8-aec9-e4ba6a8d6f7f

## Contents

| File | Purpose |
|---|---|
| `allocation.html` | The dashboard. Bottom tab bar, light theme, five sections. |
| `portfolio_model.py` | Single source of truth for every figure on the page. |
| `validate.py` | Asserts the page matches the model, plus model self-consistency. 303 checks. |
| `checklist.py` | Runs the original brief as an acceptance test. PASS / FAIL / CONFLICT per requirement. |
| `mutate.py` | Mutation-tests the validator: corrupts one model input at a time and checks validate.py fails. |
| `sync-artifact.sh` | Validates, then copies the page one-way to the publish path. |

```bash
python3 portfolio_model.py   # readable report of every figure
python3 validate.py          # verify allocation.html against it
./checklist.py               # audit the deliverable against the original brief
python3 mutate.py            # prove validate.py actually fails when the model changes
./sync-artifact.sh           # validate, then push to the publish path
```

`checklist.py` encodes each requirement from the brief as a check, so the deliverable is
re-auditable rather than eyeballed. It currently reports **15 pass, 0 fail, 1 conflict**.

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
`validate.py` covers sleeve figures, building blocks, both portfolios in both
volatility regimes, risk contributions, gauge and regional scores with their bar
fills, donut geometry, VIX term structure, the frontier and cash-line claims made
in the prose, and the brief's own weight constraints. It also asserts the model is
internally coherent regardless of the page: risk contributions sum to 100, portfolio
sigma sits between the min and max sleeve sigma, VaR worsens monotonically with
horizon, normalized sigma exceeds calm, forecast components sum to their gross, and
driver weights sum to one. Since this pass it also regenerates the frontier chart and
the sensitivity table and requires the page to carry them verbatim, so neither can drift.

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
| Net 10-yr CAGR | 8.02% | 7.64% |
| Weighted fee | 0.126% | 0.117% |
| σ — calm (today) | 16.44% | 15.22% |
| σ — vol normalized | 21.83% | 20.28% |
| Max drawdown — calm | −27.9% | −25.9% |
| Max drawdown — normalized | −37.1% | −34.5% |
| Correlated-stress drawdown | −32.1% | −30.0% |
| Return / risk (calm) | **0.258** | 0.253 |

The optimized book is driven by macro sentiment, regional rankings **and** volatility
analysis across 3, 6 and 12 months. It does not dominate the baseline on every axis:
it gives up 0.38 points of CAGR to buy 2.6 points of drawdown, and it no longer leads on
risk-adjusted return either. It is the lower-drawdown point on the frontier, not the
better book.

## Is the recommendation efficient?

Exhaustively: all 969 allocations the brief permits (four sleeves, multiples of 5, none
below 5%) plotted by net CAGR against normalised drawdown. **Both** books sit on the efficient frontier — nothing beats either on both axes at once.
The baseline moved onto the frontier this pass when QQQ's stale multiple was corrected; it
had been dominated. The optimized book is therefore no longer an improvement on the
baseline, only a lower-drawdown point on the same curve.

Two limits are stated rather than glossed. "Best" is a curve, not a point — 90
allocations are efficient and the right one depends on the drawdown actually tolerated.
And the curve is nearly straight: at the recommendation, one more point of drawdown buys
0.14 points of CAGR, and that ratio barely changes along it — which is the
frontier telling you the same thing the capital-allocation line does. Beyond BMNR 45% the frontier returns drawdowns
worse than −100%, which is impossible — the variance model fails exactly where this repo
already documents it failing, so the curve is drawn only where BMNR stays at 5%.

## Method

Equity forecasts are built from observable components rather than asserted. Components
are rounded to displayed precision before summing, so every figure on the page can be
reproduced by hand from the components shown.

| Component | QQQ | IEMG |
|---|---|---|
| Dividend yield | +0.42 | +2.16 |
| Earnings growth | +9.50 | +7.50 |
| Valuation change | +0.22 | +0.42 |
| Currency drag | — | -1.50 |
| **Gross** | **10.14** | **8.58** |
| Expense ratio | −0.18 | −0.09 |
| **Net** | **9.96** | **8.49** |

The dividend yield is the trailing-twelve-month distribution over the 11 September close —
QQQ $3.03 / $714.88, IEMG $1.80 on a price near $83 — not an estimate. Both had been carried
at yields struck against lower share prices and were never re-derived as the funds rose.

Valuation change annualises the forward multiple moving from its observed level
(QQQ 22.4×, IEMG 11.7×) to **that index's own 10-year average** (NDX 22.9×, MSCI EM 12.2×)
over ten years. One rule governs both sleeves. An earlier revision used a hand-picked 21×
for QQQ — below its own average — while holding IEMG only to its average; that asymmetry
favoured the EM sleeve and has been removed.
BMNR is modelled separately: 9.0% ETH appreciation, +2.23% staking on 85.5% of the
treasury, −0.39% mNAV normalisation, −1.40% corporate and dilution drag. The staking
figure is the company's own reported 2.61% seven-day annualised yield ($330M on $12.6B
staked, 8-K of 8 September), replacing a 3.00% assumption carried for four revisions.

## Sentiment scales

Both the composite gauge and the regional rankings use 1–5, where 3 is neutral.
Converting a 1–10 score is `1 + (x-1) * 4/9`, not division by two, since both scales
floor at 1. Arcs and bars fill on `(score-1)/4` so the scale's floor sits at the left
stop rather than at zero.

Composite reads **2.4/5**. Regional means: Asia/EM 3.5, US 3.2, Europe 2.3 — ordering
preserved at every horizon, which is the check that the rescale is presentational only.

## Volatility regime

Weights are sized to *normalized* volatility, not today's level. Spot VIX of 14.81
sits 21.6% below its 2016–2023 average of 18.9, so sleeve volatilities are scaled
by 1.28 and correlations stressed toward crisis levels (QQQ·IEMG 0.66 → 0.85). That uplift has
fallen from 1.24 in early September as the VIX rose: most of the premise is spent, and the
repo's own revisit trigger — a sustained VIX above 18.9 — is 4.09 points away, at which
point 30% cash becomes a candidate to spend toward 25%. That distance closed to 1.19 points on the eve of
the FOMC and then re-opened entirely once the decision removed the event premium.

The VIX is stored as a dated series (`VIX_SERIES`), not a single typed number, and
`VIX_SPOT` is read from its last entry. A level published from a source whose own stated
change will not reconcile with the close already on file is now a build failure, because
that is exactly how a wrong one got through.

| Sleeve | σ calm | σ normalized |
|---|---|---|
| QQQ | 21.0% | 26.8% |
| IEMG | 18.0% | 23.0% |
| SGOV | 0.5% | 0.5% |
| BMNR | 95% | 109% |

Two findings constrained the answer:

- **The cash line is straight.** Scaling a fixed risky mix against cash holds
  return-per-drawdown at 0.1117 regardless of the cash weight — invariant to 2.8e-17,
  since an uncorrelated zero-variance sleeve scales return and risk by the same factor.
  The optimizer cannot pick the cash weight; 30% is a stated drawdown budget, not a model
  output. Earlier revisions demonstrated this with QQQ traded against SGOV at a pinned
  IEMG; that is *not* a pure CAL (the risky mix changes, not just its scale) and drifts
  0.115 → 0.108. `cal_line()` now carries the theorem, `cash_line()` the illustration.
- **Variance math breaks on BMNR.** Under a lognormal model a +10% compound return at 109%
  volatility implies a 69.6% arithmetic mean, which nobody would forecast. A Booth-Fama
  rebalancing premium worth an apparent +2.9%/yr was computed, traced to this artefact,
  and discarded rather than published.

Subject only to the brief's floor of 5% per sleeve, the highest return-per-unit-risk mix
is QQQ 60 / IEMG 30 / SGOV 5 / BMNR 5 (Sharpe 0.268 vs the recommended book's
0.253). It is rejected: it over-fits the two least reliable inputs and holds only 5% in
reserve, which is not a drawdown budget anyone would choose. Note which way this has moved —
the same search wanted 85% in emerging markets two passes ago and wants 60% in the
Nasdaq-100 now. That instability is the subject of the calibration section below.

## How much to trust it

Every figure above is a point estimate, so the page now carries the distribution around it.

| Optimized book, 10 yr | Calm | Normalized |
|---|---|---|
| Net CAGR | 7.64% | 7.64% |
| Standard error, σ/√10 | ±4.81 | ±6.41 |
| 95% band | −1.8 to 17.1 | −4.9 to 20.2 |

The headline result is uncomfortable and worth stating plainly: **of the 969 admissible
allocations, 0 are statistically distinguishable from the recommendation at 95% over ten
years.** For two books drawn from the same four sleeves, `z ≈ IR × √T`; an information ratio
of 0.23 gives `z = 0.73` where 1.96 is needed. Proving the baseline out-returns the
recommendation would take **72 years**; proving the recommended book beats T-bills would
take **60**; the most separable alternative in the whole set still needs 41.

What saves the exercise from being pointless is that a *comparison* is far better determined
than a *level*. The two books share three of four sleeves, so their difference is a 10-point
switch with a tracking volatility of 1.65%/yr — a standard error of 0.52 points against
±4.81 on either book alone. The 0.38-point gap is 0.73 SE, a **77% chance the baseline ends
ahead on return**. An earlier pass reported that as 53% by dividing the gap by the error on
the level; that is the wrong denominator, since errors common to both books cancel.

`calibration()`, `separable()`, `tracking()` and `se_level()` in the model compute all of it;
`validate.py` asserts the page's figures against them.

### Which input to argue with first

Each input moved one unit and rebuilt through the same code path as `build()`.

| Input | Now | Δ CAGR | Δ gap |
|---|---|---|---|
| QQQ earnings growth | 9.5% | -0.35 | -0.100 |
| IEMG currency drag | −1.50% | +0.30 | -0.050 |
| SGOV gross yield | 3.875% | +0.30 | -0.050 |
| IEMG earnings growth | 7.5% | -0.30 | +0.050 |
| IEMG forward P/E | 11.7× | -0.25 | +0.041 |
| IEMG terminal P/E | 12.2× | +0.24 | -0.040 |
| QQQ terminal P/E | 22.9× | -0.16 | -0.045 |
| QQQ forward P/E | 22.4× | -0.15 | -0.044 |
| BMNR ETH return | 9.0% | -0.05 | +0.000 |
| BMNR staking yield | 2.61% | -0.04 | +0.000 |

This corrected a claim the page had backwards. The disclaimer named IEMG's valuation
reversion and currency drag as the most sensitive inputs and said a one-point change in
either would move the recommended tilt. The most load-bearing input is in fact **QQQ's 9.5%
earnings-growth assumption** — 0.35 of CAGR and 0.100 of the gap per point, roughly
double anything else — and it is the one number on the page that extrapolates a cycle across
a decade rather than observing it. A point off IEMG's currency drag moves the gap by 0.05;
closing the 0.41-point gap that way would take more than eight points of it. BMNR's inputs
move the level and nothing about the choice, since both books hold exactly 5%.

### Against the professionals

The sensitivity table says QQQ's earnings-growth assumption carries the page, so this pass
put it against the firms that publish ten-year forecasts for a living. Ten-to-fifteen-year,
USD, total return, gross of fund fees — the same basis as this repo's figures.

| Source | US | EM | Note |
|---|---|---|---|
| J.P. Morgan LTCMA 2026 | 6.7% | 7.8% | US large cap; EM vol 20.9% |
| Fidelity | 4.4% | 8.1% | US large cap midpoint 3.4-5.4; US growth 2.3-4.3 |
| Vanguard | 5.2% | 4.3% | midpoints of 4.2-6.2 and 3.3-5.3 |
| BlackRock | 5.0% | 7.1% | EM figure is non-US broadly |
| **This page** | **10.14%** | **8.58%** | building blocks, see Method |

The US figure is above every one of them — 3.4 points above J.P. Morgan's US large cap, and
Fidelity puts US *growth* stocks, the closest published proxy for the Nasdaq-100, at
2.3–4.3%. Three of the four rank emerging markets *above* the US, which is the ranking this
repo reversed two passes ago; Vanguard is the exception and sits on this page's side. The EM
sleeve is unremarkable by comparison, bracketed by J.P. Morgan's 7.8% and Fidelity's 8.1%.
J.P. Morgan also puts EM volatility at 20.9%, which as of the 14 September VIX exceeds *both*
two regimes used here — 18.0% calm and 23.0% normalised. That comparison has flipped
three times in a fortnight with no assumption changing, because the uplift factor moves
inversely with spot VIX; it is a fair criticism of the method, and the reason both regimes
are reported rather than one. When this comparison was first written the
normalised figure was 21.5% and sat above theirs; the VIX rising pulled the uplift factor down and
took it below. On their number the EM sleeve is under-risked here either way.

`scenario()` re-runs the whole comparison on a different set of sleeve returns with every
risk input untouched, so it isolates how much of the answer rests on this repo's own
forecasts:

| | This page | J.P. Morgan inputs |
|---|---|---|
| Baseline CAGR | 8.02% | 6.28% |
| Optimized CAGR | 7.64% | 6.20% |
| Baseline's lead | +0.38 | +0.08 |
| Best-Sharpe book | 60/30/5/5 | 5/85/5/5 |
| Efficient allocations | 90 | 17 |
| Both books efficient | yes | neither |

The sizing survives and the baseline still leads, but the margin collapses from 0.38 to 0.08
and the best risk-adjusted book flips from QQQ 55 / IEMG 35 to the largest EM tilt the brief
allows. So "QQQ leads and the EM overweight costs return" is not a finding about the market;
it is a consequence of one assumption — 9.5%/yr of Nasdaq-100 earnings growth for a decade —
that three of four houses implicitly reject. The repo keeps its own arithmetic, because a
building-block forecast can be checked line by line and a house forecast cannot, but a reader
who trusts J.P. Morgan over this page should hold *more* emerging markets, not less.

## Verification

One hundred and twenty-six corrections have been recorded across seventeen verification
passes. The most consequential:

- **A fifth sleeve was tested off-page, and the test was wrong.** Asked what adding an
  aerospace-and-defence ETF would do, this model was extended in a throwaway script that
  reimplemented `stats()`. It got the regime wrong: the page stresses *every* correlation
  when it normalises volatility — QQQ·IEMG 0.66→0.85, QQQ·BMNR 0.65→0.80, IEMG·BMNR
  0.55→0.72, a mean lift of +0.17 — and the ad-hoc version left the candidate's correlations
  at their calm values while stressing everyone else's. That flattered the newcomer's
  diversification in precisely the regime that sets the weights. Corrected, the number of
  five-sleeve books beating the recommended one on both return and drawdown fell from **two
  to zero**, and the allocation offered on that basis was withdrawn.

  The fix is structural, not a patch. `with_candidate()` extends the regime with the same
  stress rule the page applies to every other pair; `stats_n()` runs the shared arithmetic
  over an arbitrary sleeve set; and `validate.py` asserts the two reproduce `stats()` exactly
  on every existing book and regime, that the stress lift matches the published regimes, and
  that a candidate's correlations really are lifted. Nothing reimplements `stats()` now.

- **The reconciliation rule added last pass earned its place within the week.** Monday
  21 September was deliberately left off the page: one widely-syndicated figure put the
  10-year at 4.37% against 4.94% at Friday's close, on a day described as a 5bp fall. A level
  whose stated change will not reconcile with the close already on file does not get
  published, so the stamp stays at 18 September.

- **The market unwound the hike it spent a fortnight pricing, and the volatility premise came
  back.** In the two sessions after the 16 September decision the VIX fell **17.71 → 15.42 →
  14.81**, the 10-year retreated from a 19-year high of 5.04% to **4.94%** as oil softened,
  and Brent gave up four dollars to **$103.21**. Spot volatility now sits **21.6% below** its
  2016–2023 average — almost exactly the discount of a fortnight ago, after a week in which
  this repo reported it closing to 6% and the premise nearly spent. The recommended book's
  normalised drawdown widens back out from −30.2% to **−34.5%**, and the revisit trigger
  moves from 1.19 points away to 4.09.

- **A comparison the page makes has now flipped three times without anyone changing an
  assumption.** J.P. Morgan's 20.9% EM volatility is a fixed long-run estimate; this repo's
  normalised figure is anchored to a spot VIX that has covered four points in ten sessions,
  so which is larger keeps reversing. The prose said "exceeds both regimes" and was wrong
  again this pass. Both the sentence and the check are rewritten to state the *relation*
  (below both / between / above both) rather than a side, so the prose has to be re-read
  whenever the relation changes. It is also a fair criticism of the method, and the page now
  says so where the comparison is made.

- Geometry audited directly against the model this pass rather than through the page's own
  assertions: the gauge arc length and needle endpoint, the donut segment lengths implied
  weights back to 45/25/25/5 and 35/30/30/5 to four decimals, and the 1–10 → 1–5 conversion
  and bar fill hit their endpoints exactly and stay monotone. No defects found.

- **The Fed hiked, and two of this repo's assumptions moved with it.** On 16 September the
  FOMC voted **12-0** to raise the range to **3.75-4.00%** — the first increase since July
  2023, and unanimous where July's hold had split 9-3 with three dissenting *for* a hike.
  The dot plot has 16 of 18 participants expecting at least one more this year. `SGOV_GROSS`
  moves from 3.25% to **3.875%**, the midpoint of the new range held flat: neutral by
  construction, neither extrapolating the hiking path futures price (~4.1% by December) nor
  assuming a return to a level that had fallen below both spot and the curve. SGOV's net
  forecast rises 3.16% → **3.79%**, which lifts both books and, because it is also the
  risk-free rate, lowers every Sharpe on the page.

- **A VIX close published here yesterday was wrong, and the arithmetic said so at the time.**
  Rev. 16 carried 16.93 for 15 September, from a source whose own stated change (−0.27,
  −1.57%) implied a prior close of 17.20 — not the 17.62 this repo already held for
  14 September, itself verified against 11 September's 15.84 at +11.24%. The correct series
  is 15.84 / 17.62 / 17.20 / 17.71. The VIX is now a dated series in the model rather than a
  typed scalar, `VIX_SPOT` reads its last entry, and `validate.py` checks ordering, unique
  dates, the page's as-of stamp and that no single session moves more than 25%. A quoted
  level whose change will not reconcile with the close already on file is the tell.

- **The sensitivity table's spec was hardcoded and had gone stale.** Both the displayed
  level and the perturbed value were literals. When SGOV's assumed yield moved, the row went
  on claiming 3.25% and its "one unit" step quietly shrank to 0.375, understating that
  input's influence by two thirds. `SENS` is now built from the live constants, and
  `validate.py` asserts every step is exactly one unit and that the displayed level matches.

- `mutate.py` broke loudly when `VIX_SPOT` stopped being a literal — the right failure mode,
  since a silently skipped mutation is a blind spot. Repaired to perturb the series instead,
  plus a date mutation and a live-derived `SGOV_GROSS` step: **42 run, 0 survived.**

- **`checklist.py` advertised two statuses it could not produce.** Its docstring and this
  README both promised a `CONFLICT` result for requirements the deliverable departs from,
  and a `PASS*` for ones a later instruction superseded. Neither existed in the code: there
  was no `CONFLICT` path at all, and the `superseded()` helper that emitted `PASS*` was
  never called. `PASS*` is removed and `CONFLICT` is implemented — and it has a real
  occupant.

- **Item 9 was testing the wrong thing, and passing.** The brief asks for data only from
  authoritative, fact-checked sources. The check counted how many authoritative domains the
  page links to, which measures whether the page *cites* authorities, not whether its
  numbers come from them. Three inputs are admitted extrapolations — QQQ's 9.5%/yr earnings
  growth, the 1.70 × σ drawdown multiplier, BMNR's 9%/yr ETH assumption — and the first is
  the single most load-bearing figure here, contradicted by three of four published house
  forecasts. Item 9 now reports **CONFLICT** with those three named. Only the user can
  decide whether it meets the brief; the checklist's job was to stop pretending the
  question had been settled.

- **A blacklist entry collided with a correct figure.** `validate.py` forbids superseded
  values from surviving outside the self-audit, and `24.5%` was on that list as an old BMNR
  risk contribution. When the VIX moved, the baseline's 12-month normalised VaR became
  −24.5% and the build failed on a number that was right. Bare percentages are not safe
  patterns: the risk-contribution entries are now anchored to the markup they live in
  (`width:24.5%;background:var(--bmnr)`), and a meta-check asserts that no blacklist entry
  matches any figure the model currently emits, so this cannot recur silently.

- Market data to the 15 September close, published hours before the decision it describes.
  VIX **16.93** after Monday's 11.24% spike to 17.62 and Friday's identically-sized fall to
  15.84. The 10-year touched **5.04%**, a 19-year high above even the October 2023 peak,
  closing near 5.01% — the repo had called it "the first print above 5% since October
  2023", which the new high supersedes. Brent **$107.46**. Hike odds **84–91%** across
  venues into the meeting. The page now carries a standing notice that it closes before the
  FOMC announcement and has not been written with knowledge of the outcome.

- **The validator is now mutation-tested, and it holds.** More than half its checks are
  `present()`, which only asserts that a string appears somewhere in the page — weak by
  construction, and last pass one of them passed on a false statement. `mutate.py` corrupts
  one model input at a time (42 of them: every return component, every volatility and
  correlation, both portfolios' weights, the drawdown multiplier, the driver and regional
  scores, the published house forecasts, the revision stamp) and re-runs `validate.py`,
  restoring the file afterwards. **42 run, 0 survived.** Every figure the model produces is
  genuinely policed. The page states that count and `validate.py` checks the claim against
  `mutate.py` itself, so the two cannot drift apart.

- **Market data re-verified to the 14 September close, and the volatility premise has nearly
  run out.** The VIX rose 11.24% to **17.62**, reversing Friday's identically-sized 11.21%
  fall, as AI stocks sold off, Brent hit a four-month high of **$108.24** on a Saudi pipeline
  shutdown, and the 10-year Treasury broke **5.01%** — its first print above 5% since October
  2023. The repo had carried 4.80%. The uplift factor separating the two volatility regimes
  has collapsed from 1.24 in early September to **1.07**: the normalised drawdown on the
  recommended book improves from −32.8% to **−30.3%**, and the gap between regimes is now 4.4
  points rather than 7.3. The revisit trigger this repo wrote for itself is 1.28 points away.

- BMNR's risk contribution rose 25.2% → **27.4%** without any of its inputs changing: equity
  volatility fell toward its average while a 109% crypto vol did not, so the same 5% weight
  now carries a 5.5× risk-to-weight ratio. The mechanism the page cites for the 5% cap,
  showing up unprompted.

- **The page's central conclusion is one assumption deep.** Measured against four published
  ten-year forecasts, this repo's US sleeve sits above every one of them and its US-over-EM
  ranking is the opposite of three. Substituting J.P. Morgan's figures — risk inputs
  untouched — cuts the baseline's lead from 0.41 points to 0.11, flips the best risk-adjusted
  book from QQQ 55 / IEMG 35 to QQQ 5 / IEMG 85, and leaves neither of this repo's books
  efficient. Published in full on the page rather than noted here, with the 1–10 confidence
  scores cut to match: the level 3 → 2, overall 5 → 4, and a new line for the sleeve ranking
  at 3.

- **A validator check that proved a claim instead of testing it.** The page said "all four
  houses rank emerging markets at or above the US". Three do; Vanguard does not. The check
  written alongside it excluded Vanguard by name, so it passed on a false statement — the
  worst failure mode available to this repo, since the harness exists precisely to catch
  that. Both the sentence and the check are corrected, and the check now counts the houses
  rather than asserting a number.

- House cleanup: `portfolio_model.py` had two `if __name__ == '__main__'` blocks left
  interleaved with function definitions, and an empty `_ = {}` dict stranded by an earlier
  edit. One runnable report now sits at the bottom of the file, after every definition, and
  it prints the outside-forecast comparison. The `SGOV_GROSS` comment still quoted the old
  3.63% spot yield.

- **Both dividend yields were priced against stale share prices.** QQQ's income term carried
  0.65% and IEMG's 2.26%. Against the 11 September closes they are **0.42%** ($3.03 trailing
  on $714.88) and **2.16%** ($1.80 trailing on a price near $83; secondary sources spread
  2.13–2.16%). Both had been set when the funds traded lower and neither was re-derived as
  prices rose — the same failure mode as the stale forward multiple, in the one input nobody
  re-checks because it looks like a constant. QQQ's forecast falls 0.23 points to **9.96%**
  and IEMG's 0.10 to **8.49%**, narrowing QQQ's risk-adjusted lead from four hundredths to
  two without reversing it. Both portfolios lose about 0.11 points of CAGR.

- **The capital-allocation line was computed for a book the page no longer recommends.**
  `cal_line()` hardcoded a risky mix of QQQ 25 / IEMG 40 / BMNR 5 — the recommendation from
  three revisions earlier — so the invariant ratio the page quoted belonged to the wrong
  portfolio. The logic was unaffected (invariance holds for any fixed mix) but the number
  was not the reader's. Both `cal_line()` and `cash_line()` now derive the mix from
  `PORTFOLIOS['optimized']`, and `validate.py` asserts they track it.

- **The frontier chart would have drawn outside its own axes.** The assertion added to
  `frontier_svg()` this pass caught it on the first run: the corrected yields pushed the
  low-drawdown end of the curve to −12.5%, past the −15% axis floor. Axes widened to
  −10…−50% with an adaptive label step. Without the guard this ships as a line running off
  the plot.

- **`build_with()` ignored the field name for SGOV**, so `SGOV_er=x` would have silently set
  the *gross yield* to x. It is only reached by the sensitivity table, which never passes
  that key, so nothing published was wrong — but it was one keyword away from being wrong.
  Both branches now assert the field exists.

- Rate expectations re-checked: the 90% on CME FedWatch was an intraday spike on the CPI
  release, and prediction markets settled near **80%** over the weekend. The page had carried
  90% in seven places as though it were the level. August PPI — **5.4% year-on-year**,
  released 10 September, well above the 3.4% consumer figure — was missing from the page
  entirely and is now in the monetary-policy driver. SGOV's SEC yield re-read at **3.74%**
  from 3.63%, lifting the reserve's real return to +0.3%. `fr_slope()` and `calibration()`
  gained guards against the degenerate inputs that would raise IndexError and
  ZeroDivisionError, and the model docstring still claimed 4 September data.

- **BMNR was modelled on an assumption where a filed number existed.** The staking yield had
  been set at 3.00% by judgement. BitMine's 8-K of 8 September reports $330M annualised
  staking revenue on $12.6B staked — a 2.61% seven-day annualised yield — and gives exact
  token counts, so the staked share is 5,067,309 / 5,929,198 = 85.5%, not the 85.9% carried.
  The sleeve's staking contribution falls from +2.58% to +2.23%. mNAV also moved: at the
  11 September close the stock trades at 0.98× total NAV of $15.7B and 1.04× against crypto
  alone, against 1.02× / 1.10× before. Taking the conservative crypto-only reading turns the
  mNAV term from −0.20% to −0.39%. Net effect: BMNR's forecast drops 9.98% → **9.44%**, and
  both portfolios lose 0.03 points of CAGR.

- **The forecast had no error bar, which for a ten-year projection is itself a defect.** Added
  a calibration section: ±4.81 points of standard error on the level, a 95% band of −1.9% to
  17.0%, and the finding that none of the 969 admissible allocations is separable from the
  recommendation inside ten years. Also corrected this page's own arithmetic — the
  baseline-versus-optimized ranking had been quoted at 53% confidence using the error on the
  level instead of the tracking error of the difference; it is 80%.

- **The most-sensitive-input claim was wrong in both directions.** The disclaimer named IEMG's
  valuation reversion and currency drag. Measured, the answer is QQQ's earnings-growth
  assumption, at roughly double the effect of anything else, and a one-point move in IEMG's
  currency drag shifts the decision gap by 0.05 — not enough to move the tilt as claimed.
  A `sensitivity()` function now computes the whole table and the validator asserts every
  cell of it.

- **The verification log contradicted itself.** Its "Still open" note carried QQQ's 25.2×
  multiple as an unresolved question in the same card that recorded it resolved to 22.4×.
  Rewritten to name what is genuinely open: BMNR's 9%/yr ETH assumption, the 1.70 × σ
  drawdown multiplier, and QQQ's decade of 9.5% earnings growth.

- **Market data re-verified to the 11 September close.** VIX 15.30 → **15.84** (−11.21% on the
  day, after the week's highest close and first above 17 in 28 sessions). Brent $100 →
  **$104.61** settle, −2.8% on the day but +8.7% on the week. August CPI landed at 3.4%
  headline and 2.4% core year-on-year — the lowest core since March 2021 — while core rose
  0.3% on the month against 0.2% expected; CME FedWatch moved from 70% to 90% priced for a
  hike on the release. The page had described this as simply "a hot core CPI print", which
  misses that the annual core rate fell to a five-year low and that equities read it as
  relief. Both readings are now stated.

- The frontier chart is now generated by the model rather than hand-maintained, after its
  axes were found to be too narrow for the recalculated curve. `frontier_svg()` emits the
  whole SVG and `validate.py` requires the page to carry it verbatim. The efficient count
  also disagreed between page (86) and README (103); both are now derived, and the answer
  is 90.

- **Two unsourced risk assumptions, replaced with data.** The QQQ·IEMG correlation was set
  at 0.72 by judgement; the pair's actual figure is 0.66 all-time (0.82 over one year,
  which supports the 0.85 stressed case). And IEMG's maximum drawdown was assumed at −33%
  when its realised worst since inception is −38.71%. Over the window both funds have
  existed, IEMG drew down *more* than QQQ, not seven points less — the same asymmetry as
  the terminal multiples, favouring the same sleeve. Corrected to −39%, IEMG's "shallower
  drawdown" advantage shrinks from seven points to one.

- **QQQ's forward P/E was stale, and fixing it reversed the recommendation's rationale.**
  25.2× (Siblis, 1 July) was flagged as the weakest input for three passes. Three routes
  agree it is wrong: two secondary sources put the Nasdaq-100 at 20.8–22.4× in late August,
  and the trailing multiple fell 19% over the same window (35.24 → 28.55), which drags the
  forward figure to ~20.4× on its own. Corrected to 22.4×, QQQ's forecast rises 1.16 points
  to 10.19% — ahead of IEMG on raw *and* risk-adjusted return. The EM tilt's last
  justification is gone; it is now a drawdown-reduction lever that costs return.

- **The terminal multiples were asymmetric — the largest error found.** IEMG's terminal
  multiple was anchored to its own 10-year average (12.2×); QQQ's was hand-set at 21×,
  *below* its own 10-year average of 22.9×. One sleeve was held to its history and the
  other marked down past it, and the asymmetry favoured the EM tilt, which is the page's
  central recommendation. Applying one rule to both adds 0.85 points to QQQ and reverses
  the ranking: QQQ now out-earns IEMG, 9.03% vs 8.59%. The claim that IEMG improved return
  and risk together is withdrawn; the tilt survives on risk-adjusted grounds only and was
  trimmed 40% → 35%.
- Two forward-looking claims resolved. August CPI landed 11 September at 3.4% headline and
  2.4% core, but core rose 0.3% m/m against 0.2% expected and hike odds jumped from ~70% to
  **90%** — the figure has swung 55–90% inside a fortnight. The ECB hiked to 2.50%
  unanimously on 10 September, and the "terminal hike" expectation this page had recorded
  was overtaken within the week: investors now price further increases. Worth noting the
  August CPI window closes *before* the 8 September Saudi strikes, so the sharpest part of
  the energy shock is not in that data at all.

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
hold exactly. Market data is as of 11 September 2026. BMNR carries single-issuer, dilution
and crypto-price risk that can result in total loss of that position.
