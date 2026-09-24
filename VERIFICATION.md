# Verification history

Every correction recorded against this repo, newest first. The dashboard's own
verification log (Portfolios tab) carries the same record as a table; this file keeps
the reasoning — what was wrong, how it was caught, and what now stops it recurring.
The current state of the model is in [README.md](README.md).

## Checklist recheck — 24 September 2026

The page did not change; the acceptance test did. Every item passed, but six passed for
the wrong reason:

- **Item 1** never looked at the live URL or at the viewport that makes Android render at
  phone width. It now takes `--live`, compares the served page to the validated file
  (identical) and checks the host shell's viewport and colour scheme.
- **Item 8** read only the model and hardcoded "Asia > US > Europe", so a legitimate change
  in the ranking would have failed the requirement. It now checks the page's rank badges
  against the blocs' mean scores, and that every bloc is scored at all four horizons.
- **Item 13** asserted QQQ = 45% — a value, not "built on a 10-year horizon".
- **Item 14** looked for two phrases. It now requires the tilt to follow its inputs: the
  top-ranked bloc's sleeve overweighted, more reserve while the VIX sits below its mean, and
  a lower normalised drawdown.
- **Item 5** did not check that the ETF slides show the fund fee the net figure is taken after.
- **Item 15** re-implemented the admissible set instead of using `M.admissible()`.

Each new check was broken deliberately and went red. Result unchanged: 15 pass, 0 fail,
1 conflict (item 9, the three extrapolated inputs).

## Rev. 20 — 23 September 2026

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

## Earlier revisions

- **A coverage scan found the prose the validator never read.** Every string `validate.py`
  asserts was mapped onto the page, and every number no assertion touched was listed. That
  turned up figures the model had moved past while the prose stayed put: the SGOV slide's
  pre-hike **3.25%** gross (the model is 3.875%, so gross minus fee no longer equalled the
  3.79% net beside it); the baseline's calm VaR at a superseded CAGR's values on all three
  horizons (−11.5/−15.1/−19.0 → **−11.6/−15.2/−19.2**); BMNR's risk card at Rev. 18's 23.8%,
  described as "more than a quarter" of risk (it is **23.1%**) — its check searched the whole
  page and matched the right figure in another block; the valuation driver's 11 September
  multiples and a VIX distance from 14 September; a liquidity driver still citing the
  10-year's 4.818% after its 5.04% high; the rationale's QQQ terminal value ($25,843 →
  **$24,805**) and fee saving ($26 → **$24**); a call-out that paired the baseline's normalised
  drawdown with the optimized book's calm one; and six relative dates ("yesterday", "two
  passes ago", "a fortnight ago") pointing at revisions that had moved. Each is now generated
  from the model and asserted, the risk-card check is scoped to its card, and a frozen-prose
  list stops each phrase returning. Every new check was run against the unfixed page and
  confirmed to fail. **321 → 383 checks.**

- **A theorem was stated more strongly than the model supports.** The cash line was called
  invariant "to machine precision" because cash is a zero-variance sleeve; SGOV has 0.5%
  volatility here, so the spread is ~1e-5 and has been in every revision (the README's
  "2.8e-17" was never produced by this code). `cal_line()` now takes `cash_vol`, the theorem
  is tested at zero, and the residual is stated. `mutate.py` gains an SGOV-volatility
  mutation to police it: **46 run, 0 survived.**

- **Two history claims the data does not support.** The J.P. Morgan EM-volatility comparison
  was said to have "flipped three times"; the stored VIX series crosses the 16.28 threshold
  twice, and the count is now computed. "Covered four points in ten sessions" was 3.46 points
  in eight.

- **One cell broke the page's own rounding rule.** IEMG's terminal-P/E effect on the gap is
  exactly −0.0395 and rounds half-up to −0.040; floating-point subtraction delivered
  −0.03949… and the page printed −0.039. `r2h()` now snaps float dust before rounding.

- **The valuation model stopped responding to price (Rev. 19).** Dividend yields and forward
  multiples were both typed at the 11 September basis and held there while the page's stamp
  advanced, so a 4.6% QQQ rally and a 2.0% IEMG fall moved nothing in the forecast. Tying both to
  `PRICES` moves QQQ to 23.4× (a de-rating, now) and IEMG to 11.5×: QQQ **9.96% → 9.51%**,
  IEMG **8.49% → 8.73%**, the two level on risk-adjusted return (0.272 vs 0.274). The weights
  are held — chasing a two-thousandths Sharpe difference is what the calibration section says
  the evidence cannot support. The same pass found three of four sleeve slides showing the
  wrong optimized weight (summing to 95%), the valuation-change row never checked, and
  `mutate.py` silently skipping seven mutations; skips now fail the run.

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
