# Verification history

CORRECTIONS: 254

Every correction recorded against this repo, newest first. The dashboard's own
verification log (Portfolios tab) carries the same record as a table; this file keeps
the reasoning — what was wrong, how it was caught, and what now stops it recurring.
The current state of the model is in [README.md](README.md).

## Rev. 27 — 10 October 2026 (data to the 9 October close)

Thirteen corrections, all in what Rev. 26 or earlier published or wrote down. Every market
close below was cross-checked across at least two independent sources. A few figures rest on
their publisher's own page, the primary source: SGOV's SEC yield (iShares), the spread
(FRED), Vanguard's ranges and the Morningstar survey. The page fetcher could not resolve
hosts this session, so every read came through web search.

- **QQQ's trailing dividend was a quarter stale.** Rev. 25 and 26 held it at $3.03 because
  the September payout was "quoted as $0.7514 and $0.69". The $0.69 was **September 2025's**
  payout ($0.69395), not a second reading of 2026's. Once QQQ went ex on 21 Sep, the four
  quarters on file should have been Dec-25 0.79408 + Mar-26 0.73282 + Jun-26 0.81349 +
  Sep-26 0.75143 = **$3.09** (StockAnalysis's dated history; Investing.com and Dividend.com
  agree). The yield moves 0.40% → **0.41%**.
- **IEMG's held dividend had the same misreading.** Its "$0.71 June figure" was June 2025's
  payout. The $1.80 on file was right (Dec-25 1.1389 + Jun-26 0.6584); the hold was not
  needed.
- **QQQ's 2020 drawdown was understated.** The Volatility tab said ≈−27%. Peak to trough it
  was about **−28.6%** (Portfolioslab; "close to 30%" in Advisor Perspectives' Bloomberg
  data).
- **QQQ's 2007–09 drawdown was understated at the deep end.** The tab said "−50 to −53%";
  Bloomberg data puts it at about **−53.5%**. The 2000–02 (≈−83%) and 2022 (now
  "−35 to −36%": −35.1% Portfolioslab, −35.6% for QQQM) figures stand.
- **Vanguard's EM forecast was wrong.** The house table used 4.3% (midpoint of "3.3–5.3").
  Vanguard's June 2026 model run gives **2.0–4.0%** (midpoint 3.0%); its Q1 run gave
  3.6–5.6%. Neither matches the old range. The US range (4.2–6.2) was right.
- **Fidelity's US figure could not be traced.** The 4.4% ("midpoint 3.4–5.4") matches no
  source found. The survey that carries Fidelity's 8.1% EM figure (Morningstar, 20-year
  2025–44, nominal) gives **5.8%** for US equities, so both now come from that one dated
  source.
- **BlackRock's US figure was 5.2%, not 5.0%,** in the survey it came from (as of 30 Sep
  2025). Each house row now carries its vintage. The page's US forecast is now 2.9 points
  above the highest house, and 3 of 4 houses still rank EM above the US.
- **The dollar claim was typed into the generator, undated.** "The dollar sits at a 16-month
  high" was a literal in `build.py`, not a dated fact. By 5 Oct the index had touched an
  **18-month high** (two sources; CNBC lists 102.54 as its 52-week high that day), so the
  sentence had gone stale with nothing to flag it. It is now a dated fact.
- **The Michigan label was typed too.** "(Michigan, final September)" was a literal beside
  the figure, so updating the figure alone would have mislabeled it. The label now travels
  with the figure: **46.3**, preliminary October, near the 44.8 record low of May.
- **"High-yield spreads widened" was typed.** The verb is now read from the two dated levels
  (3.15% on 8 Oct against 2.80% on 24 Sep), and a helper test runs it on a narrowing.
- **The macro headline was keyed on the day's sign.** "The bond sell-off extended" printed
  for any rise. On 9 Oct the 10-year rose 2bp to 5.24%, 7bp under its 5.31% high, in a week
  it fell. It now says "extended" only of a rise to a close at the high, and today reads
  "Yields edged up". The validator derives the headline itself and tests both cases.
- **The VIX mean's description was wrong.** The model called 18.9 the "2016–2023 mean of
  annual closes". Year-end closes average about 17.3; 18.9 is close to the mean of the
  yearly averages of daily closes. FRED re-confirms 2022 (25.64) and 2023 (16.85), but
  2016–2021 could not be retrieved this session, and the commonly quoted averages give
  **18.8**. That is left as an open item rather than changed from memory: 0.1 of a VIX
  point, about 0.2 points of normalized drawdown, and no effect on the rule at a 14.84 VIX.
- **MSCI EM was labeled "IEMG's market" without saying IEMG tracks the broader MSCI EM IMI.**
  The trend note now says MSCI EM stands in for that benchmark. The IMI's own 3/6/12-month
  returns to 30 Sep were not retrievable this session.

**Market data to 9 October.**

- VIX 15.08 (7 Oct, +0.47%), 15.41 (8 Oct), **14.84** (9 Oct, −3.70%). There were two or
  three sources each, among them FRED and Cboe's own page. One aggregator printed 14.88
  "down 3.4%", which matches an intraday level, not the close.
- Brent settled **$104.72** on 9 Oct (+0.42% from $104.28; Yahoo, Investing.com). It rose
  4.1% on 8 Oct as Iran stepped up attacks on tankers in the Strait of Hormuz and Hurricane
  Isaias shut in most US Gulf of Mexico output; President Trump then ruled out striking Iran
  before the 3 Nov midterms. Sources disagree on 7 Oct, so the chain is anchored on 8–9 Oct.
- 10-year: 5.28% (7 Oct, after touching its highest level since April 2002 intraday), 5.22% (8 Oct)
  and **5.24%** (9 Oct; FRED, Treasury, Investing.com 5.244). The highest close is still
  5.31% on 5 Oct. The 30-year closed at 5.60%.
- QQQ **$751.27** (9 Oct; Yahoo, Twelve Data), after the 8 Oct chip sell-off.
- IEMG **$82.04** (7 Oct; the iShares page's dated closing price and StockAnalysis).
- HY OAS **3.15%** (8 Oct, FRED; 3.09% on 7 Oct).
- SGOV's 30-day SEC yield **3.71%** (7 Oct, iShares).
- New facts:
  - jobless claims 197,000, the lowest since July;
  - Michigan's one-year inflation expectations 4.7%;
  - October hold odds of about 78% before the minutes;
  - the ECB's account showing September's hike was unanimous.
- Not yet out: the IMF's October WEO (13 Oct) and September CPI (14 Oct).
- BitMine's chairman confirmed on 7 Oct (TOKEN2049; CoinDesk, Decrypt) that buying stops at
  5% of supply; BMNR fell 6% that day.

**Gauge and regions re-read, held.** Claims at a three-month low and strong ISM surveys
offset Michigan's slide; firmer oil and inflation expectations sit against an inflation
score that is already low. The hawkish minutes leave October odds where they were, and
spreads a touch wider plus a firmer dollar sit against a 10-year below its high. The gauge
stays **2.3**. The regional order and margins are unchanged, and the trend window (30 Sep)
is unchanged.

**Forecasts.**

| Figure | Rev. 26 | Rev. 27 | Why |
|---|---|---|---|
| QQQ net CAGR | 9.34% | **9.45%** | Re-prices to 23.54× forward; the trailing dividend is corrected |
| IEMG net CAGR | 8.45% | **8.68%** | Re-prices to 11.52× at $82.04; yield 2.19% |
| Baseline | 7.76% | **7.87%** | |
| Optimized | 7.44% | **7.55%** | |

- The gap is still 0.32 points, for 2.9 points less normalized drawdown (−38.9% vs −41.8%).
- Calm drawdowns ease to −31.5% and −29.2% with the VIX at 14.84.
- The rule's five steps are unchanged, and it returns **QQQ 35 / IEMG 30 / SGOV 30 /
  BMNR 5**. The optimized book stays efficient. The baseline is now beaten, by a hair, by
  QQQ 15 / IEMG 60 / SGOV 20 / BMNR 5 (+0.01 points of CAGR, 0.1 of normalized drawdown),
  and the page says so; 106 of 153 allocations are efficient.
- With the baseline off the frontier, only one branch of the frontier call-out renders. Two
  mutants on the other branch then survived the first mutation run. The validator now
  renders every branch on hypothetical frontier memberships.
- The best-Sharpe book is now QQQ 40 / IEMG 50 / SGOV 5 / BMNR 5, still rejected for its
  5% reserve.
- **Allocations unchanged.**

**Held back, not averaged.**

1. IEMG after 7 Oct: 8 Oct is quoted as $80.50 and $80.35, and 9 Oct's $81.40 has one
   source. At $81.40, IEMG's net forecast would be about 8.77%.
2. BMNR stays on its 5 Oct close, paired with the 5 Oct holdings release. Its 9 Oct close
   is quoted as $24.03 and $24.04, and ether's 9 Oct close (near $2,490) is unconfirmed. At
   those levels the mNAV would be about 0.97×. The next release is due 12 Oct.
3. Brent's 7 Oct settlement ($101.90, $100.92 and $100.20 in three sources).
4. BlackRock's reported August 2026 update (9.0% US / 8.8% EM), from one tracker.

**Mutation harness: 140 (88 model, 52 generator), all caught.**

- The first run left two survivors and three skips. The survivors were on the frontier
  call-out's inactive branch (fixed above). The skips were mutants whose targets were Rev.
  26's values (Brent, the 10-year, the typed spread verb). Skips already failed the run, but
  the summary line counted them as "run"; it now reports them.
- New mutants cover:
  - the stale QQQ dividend;
  - the understated 2020 drawdown;
  - the typed spread verb and dollar claim;
  - the headline keyed back on the day's sign.

**Phone check.** `phone.mjs` at 412px and 360px: six tabs, nothing off-screen, no table
hiding columns, text ≥ 9px.

## Rev. 26 — 7 October 2026 (data to the 6 October close)

Seventeen corrections: ten in what Rev. 25 published or tested, seven caught in this pass
before publishing.

- **Rev. 25 published the 2 October VIX close as 15.40; it was 15.31.** The figure came from
  one social-media post that also gave its own day-on-day change (−6.03%), and that change
  reconciled with 1 Oct's 16.39. So the reconciliation rule passed a wrong close because its
  only evidence came from the same source. Three independent sources give **15.31** (−6.59%,
  low 15.30), and 5 Oct's "+1.4% to 15.52" reconciles only from 15.31. A close now needs two
  independent sources (`VIX_SOURCES`, asserted at import), and a change counts as evidence
  only when it comes from a second source. Rev. 25's calm volatilities were scaled from a
  spot 0.6% too high; that is superseded by this revision's 15.01.
- **The optimized book was typed, not derived.** The page said it was "based on" sentiment,
  volatility and regional rankings, and the checklist tested phrases and the direction of the
  tilt, but the weights were entered by hand. They now come from `tilt_book()`, which starts
  from the strategic baseline and lets each pillar move one 5-point step: regional rankings,
  broad and correlated sentiment, volatility, market trend, then drawdown control. The Portfolios
  tab lists each step with its reading and the book after it, and says what would change it.
  `validate.py` re-implements the rule without calling the model's version, checks the step
  log, and runs five counterfactuals (VIX above its mean, a QQQ trend lead, a constructive
  gauge, a US lead and an EM downtrend). The rule returns **QQQ 35 / IEMG 30 / SGOV 30 /
  BMNR 5**, the book Rev. 25 had typed. **Allocations unchanged.**
- **The BMNR slide said "premium normalisation" whatever the mNAV.** The 5 Oct release
  puts the stock at **0.98×** its holdings, a discount, so the build-up term is now a small
  tailwind ("discount closing"). The wording follows the sign of the term, and the validator
  checks it.
- **The transmission map's labels were typed twice.** The macro pane's Tailwind / Two-sided /
  Headwind labels were literals in `build.py`, separate from the scores the rule uses. Both now
  read `CORRELATED` in the model, and a mutant that retypes one label is caught.
- **Checklist item 7 counted the wrong list.** It counted arguments from the page's first
  numbered list. Once the rule's steps appeared above the rationale, it credited the rationale
  with 11 arguments instead of 6. It now reads only the Rationale section.
- **Checklist item 14 tested phrases.** It now requires that the published book is the rule's
  output, that every pillar named in the brief is a step shown on the page, and that the trend
  tab exists. A new item, 14b, checks the trend table cell by cell against the model.
- **Four layout defects had shipped, found by testing the page at phone widths.** A Pixel 7
  (412px) and a 360px screen, the narrowest common Android width, were emulated in Chromium.
  1. **BMNR's "Headwind" tag rendered as a padded, bordered box.** The signal pill's class
     (`dn`) was also the donut card's class, and the card's rule came later in the stylesheet.
     The pill class is now `down`. The validator refuses a pill class that any other rule
     styles.
  2. **Two volatility headers printed σ as Σ.** Table headers are uppercased, and the capital
     of σ (standard deviation) is Σ (summation). The headers now opt out (`.sym`), and the
     validator refuses a Greek letter in an uppercased header.
  3. **Chart labels rendered at 8.1–8.3px.** These were the frontier chart's axis labels and
     the donuts' "NET CAGR %". They are now 9.5–12 viewBox units, at least 9.6px on screen at
     both widths.
  4. **Three tables hid columns behind a sideways scroll.** At 360px these were the
     volatility, comparison and score tables. Narrow screens now get tighter cell padding and
     wrapping row labels; no table overflows at 360px.
- Caught before publishing:
  1. A precedence error in `build_steps()` dropped the downtrend sentence from the trend step
     (`a + b if c else d`); now parenthesized.
  2. "Asia / Emerging leads United States" now reads "leads the United States".
  3. The relative-trend note printed an ASCII hyphen ("0.6 vs -0.4"); the hygiene check caught
     it, and `mf()` now formats it.
  4. **Drawdown control could undo the signals on noise.** The first version jumped to any
     admissible book that beat the result on both axes. In the US-lead counterfactual the
     signals produce QQQ 45 / IEMG 20 / SGOV 30 / BMNR 5, and the step then leapt 60 points
     to QQQ 20 / IEMG 50 / SGOV 25 / BMNR 5 — overweighting the bloc that had just lost the
     ranking — for **0.01 points** of CAGR and **0.002 points** of drawdown. Choosing the
     nearest dominating book instead did not help, because it was the only one. The step now
     moves one 5-point step like every other pillar: to the neighbour that beats the book on
     both axes with the least drawdown. A dominating book further away is counted and
     reported, not taken. No book has such a neighbour on live inputs. So the validator also
     re-runs the step on all 153 books with QQQ set to earn less than cash, which exercises
     the move and its tie-break, and it checks that a US lead now stays a QQQ overweight.
  5. One new mutant ("transmission labels typed") retyped the same label it removed, so it
     changed nothing and could not be caught. It now plants a different label.
  6. **The new trend table's verdict ran off a phone screen.** As a fifth column, "Uptrend
     (+4)" sat 81px past the edge at 412px and showed as "Upt…". The verdict is now a pill
     under each market's name, and the table is four columns wide. The Android test had
     skipped anything inside a horizontal scroller, so it passed this; it now fails any table
     that overflows.
  7. The first mutation run left one survivor: a rule that picks the sentiment step's funder by
     weight alone. On live inputs the map and the weights both pick QQQ, so the validator could
     not tell them apart. A counterfactual now turns the map against IEMG and requires IEMG to
     fund the step.

**New this revision.**

- **Market trend tab.** It shows 3-, 6- and 12-month total returns to 30 Sep for the market
  each sleeve and region trades in, from the sponsors' and index providers' own tables:
  - S&P 500 **+2.30 / +17.85 / +15.74%** (iShares IVV benchmark row; Evercore's Q2 chain);
  - Nasdaq-100 **+0.58 / +28.42 / +24.00%** (Nasdaq monthly total returns and the XNDX
    factsheet; QQQ's NAV 23.75% over 12 months);
  - MSCI EM **−0.37 / +23.59 / +29.22%** (iShares EEM benchmark row; two Q3 reviews);
  - STOXX Europe 600 **−0.70 / +10.64 / +16.56%** in euros (iShares fact sheet);
  - Ether **+70.6 / +27.5 / −35.3%** (CoinGecko and CoinGlass quarters; 30 Sep 2025 at about
    4,150 from two sources).

  A move inside ±2% is flat, and 12 months counts double. Every equity market is in an
  uptrend (+3 or +4), and ether is mixed (0). Where a figure was built from parts
  (`TREND_CHAIN`, `TREND_LEVELS`), the validator rebuilds it. QQQ against EM nets **−1** (US
  ahead at 6 months, EM at 12, level at 3), short of the ±2 that would move a step. The trend
  agrees with the regional ranking at 6 and 12 months and disagrees at 3 months (the S&P 500
  led). The page says so instead of hiding it.
- **Why the rule lands on 35/30/30/5:**
  - Asia / Emerging leads at 3 months (3.0 vs 2.8) and at 10 years (3.9 vs 3.7), so QQQ −5,
    IEMG +5.
  - The gauge reads 2.3, below 2.6. The reserve grows, funded by QQQ, the equity sleeve the
    map rates two-sided.
  - The VIX at 15.01 sits below its 18.9 mean, so the reserve is held.
  - No downtrend, and the trend net is −1, so no trend move.
  - Nothing admissible beats the result on both net CAGR and normalized drawdown.
  - The page names the triggers: the gauge reaching 2.6, the VIX reaching 18.9, the trend net
    reaching ±2, or Asia losing its 3-month or 10-year lead.
- **Market data to 6 October.**
  - VIX 15.31 (2 Oct), 15.52 (5 Oct, +1.4%), **15.01** (6 Oct, −3.29%), three sources each.
  - Brent settled $100.32 (5 Oct), then **$100.58** (6 Oct, +0.26%), after Saudi Arabia's
    price cut and the G7 reserve release.
  - 10-year **5.31%** on 5 Oct (Treasury par curve; the highest close since April 2002), then
    **5.27%** on 6 Oct. The 30-year closed at 5.66% and then 5.64%.
  - QQQ **$759.66** (6 Oct, +$3.46 from $756.20; a record close, with the S&P 500 and Nasdaq
    at records).
  - IEMG **$83.58** (5 Oct, iShares fund page).
  - BMNR **$26.79** (5 Oct), paired with the 5 Oct release (6,016,414 ETH held as of 4 Oct,
    5,067,309 staked, $17.4 billion in total).
  - ICE BofA HY OAS **3.12%** (5 Oct, FRED), back from 3.24% but still above 24 Sep's 2.80%.
  - New facts:
    - ISM services 54.9, with prices paid 74.0, the highest since July 2022;
    - the 7 Oct FOMC minutes, where most officials see another hike as likely by year end, with
      about 80% odds of an October hold;
    - BitMine's chairman saying on 7 Oct that it will stop buying ETH at 5% of supply.
- **Gauge re-read, unchanged at 2.3.** Narrower spreads are offset by a 2002-high 10-year;
  services strength is offset by payrolls and the minutes. The six drivers keep their scores.
  The regional scores keep their order and margins.
- **Forecasts.**
  - QQQ re-prices to 23.80× forward; net CAGR 9.47% → **9.34%**.
  - IEMG 8.64% → **8.45%**.
  - BMNR 9.51% → **10.01%** (the mNAV moved from a premium to 0.98×; the dilution drag is held
    at 1.40%/yr pending the end of issuance).
  - Baseline 7.84% → **7.76%** and optimized 7.52% → **7.44%**: a 0.32-point gap for 2.9
    points less normalized drawdown (−38.9% vs −41.8%).
  - Both books stay efficient (106 of 153 with BMNR at 5%). The best-Sharpe book, QQQ 45 /
    IEMG 45 / SGOV 5 / BMNR 5, is still rejected for its 5% reserve.
- **Held back, not averaged.**
  1. IEMG's 6 Oct close ($83.04 vs $83.05).
  2. BMNR's 6 Oct close ($26.20 vs $26.23).
  3. QQQ's September distribution ($0.7514 vs $0.69).
  4. IEMG's June distribution ($0.66 vs $0.71).
  5. BMNR's share count, while buybacks run and issuance ends.
- **Mutation harness: 135 (87 model, 48 generator), all caught.** New
  mutants cover:
  - the book typed over the rule;
  - each rule threshold;
  - the funder chosen by weight only;
  - transmission labels and signs;
  - one trend return per market;
  - a chain part, the deadband, the weights, the window and the quarter-end close;
  - drawdown control leaping past one step, and its tie-break taken by return;
  - in the generator, the trend verdict, signs, net, step books, leader horizon,
    since-quarter base, trigger VIX and typed labels;
  - the four layout fixes: the pill class, the σ header, the verdict column and the verdict's
    colour.

## Rev. 25 — 4 October 2026 (data to the 2 October close)

- **The ten-year drawdown rule understated every drawdown by about 15%.** The model carried
  expected max drawdown = 1.70 × σ with a "1.65–1.75" band. Neither was ever derived. A
  seeded simulation of the model's own books (GBM at each book's CAGR and σ, daily steps,
  ten years) gives a mean of **2.01–2.04×** and a median of 1.89–1.95×. Monthly steps give
  1.83–1.90× because they skip intra-month troughs. The rule is now **2.00×** with a 1.90–2.05
  band, and `validate.py` re-runs a 400-path simulation of the recommended book (2.01×).
  Normalized drawdowns move from −35.5% / −33.0% to **−41.8% / −38.9%**. The ranking and the
  frontier do not change, because one multiple scales every book. Normal returns understate
  fat tails, so 2.0× is still a floor. The frontier chart's x-axis was widened to 60% after
  its own range assertion caught the overflow.
- **"Highest since 2007" was overtaken.** The 10-year closed at 5.29% on 30 Sep (Treasury par
  curve). That passes the 2007 peak, and several outlets report the move as the highest since
  2002. The fact now reads "highest close since 2002" and attaches only to the 30 Sep close.
  The 30-year's "highest since 2004" is likewise now "since 2002": it touched 5.61% on
  29 Sep (CNBC, Bloomberg).
- **"High-yield spreads … stay tight" was no longer true.** The ICE BofA HY OAS widened
  from 2.80% (24 Sep) to **3.24%** (1 Oct). The note now states both dated levels, and the
  validator refuses "tight" next to a wider spread. With the dollar at a 16-month high and
  the 10-year at a 2002 high, Liquidity & credit is re-scored 4.5 → **4.0**.
- **The gauge note said "Strong growth" as a constant.** The September payrolls print
  (+29,000 against 84,000 expected, unemployment 4.2%, July–August revised down 60,000) took
  Growth momentum from 7.0 to **6.0** (3.7 → 3.2 of 5). The note now names growth by its
  score.
- **Monetary policy re-scored 2.0 → 2.5.** October-hike odds fell from about 36% to about
  17% after the jobs report (CME FedWatch; Kalshi 18%), with December still priced. The
  composite gauge moves **2.4 → 2.3**. Inflation stays at 3.0. August PCE came in at 3.4%
  (core 3.0%), both below forecast, but a BEA method change trims about 0.2 point of that,
  and ISM prices paid jumped to 77.9.
- **The metamorphic VIX test could silently do nothing.** It looked up the last close by
  printing the float (`15.4`), but the source says `15.40`, so the replacement found
  nothing. The test then compared the model with itself and reported "calm vol does not
  scale". It now matches the entry as written, and it checks that the copy changed and runs
  at the new spot. `mutate.py` had the same float lookup in two mutants, now fixed.
- **The VIX reconciliation evidence lived only in comments.** Each close's reported change is
  now data (`VIX_REPORTED`), and the model refuses any close that does not reproduce it. That
  check would have caught Rev. 20's 15.35 and Rev. 24's candidate 16.37 at import.
- **Rev. 24's held-VIX branches went untested once the hold lifted.** The three mutants
  that exercised them became equivalent. The validator now runs `vix_lead`, the masthead and
  the revisit trigger on a hypothetical held close.
- **The VIX hold is lifted.** The 29 Sep report ("down 0.2% to 16.04") reconciles only with a
  28 Sep close of **16.07**; 16.37 would have been −2.0%. The chain then runs:
  - 30 Sep **16.34** (+1.87%);
  - 1 Oct **16.39** (open 16.33, high 17.59);
  - 2 Oct **15.40** (−0.99, −6.03%, exact).
- **Market data to 2 October.**
  - Brent settled $102.25 (−$0.06, from $102.31, which settled +4.4% on 1 Oct; EnergyNow).
  - 10-year 5.28% on Treasury's par curve (5.24, 5.26, 5.29, 5.24 on the four sessions
    before), so 1bp below the high.
  - QQQ $749.58 (+1.02% from $742.03; a 52-week high, with the Nasdaq Composite at a
    record).
  - IEMG $82.36 (+$1.14, +1.40% from $81.22, exact).
  - New facts:
    - eurozone flash September HICP 3.8% (energy 18.8%, core 2.5%; Eurostat);
    - China's official manufacturing PMI 50.1 (NBS);
    - ISM manufacturing 54.5;
    - the G7's 2 Oct agreement to release up to 100 million barrels.
- **Forecasts.** QQQ re-prices to 23.49× forward; net CAGR 9.65% → **9.47%**. IEMG 8.75% →
  **8.64%**. Baseline 7.95% → **7.84%**, optimized 7.62% → **7.52%**; the gap is 0.32 points
  for 2.9 points less normalized drawdown. Both books stay efficient (106 of 153). The
  unrestricted best-Sharpe book is QQQ 40 / IEMG 50 / SGOV 5 / BMNR 5, still rejected.
  `audit.py`, which uses no model functions, matches every sleeve and portfolio figure.
  **Allocations unchanged.**
- **Held back, not averaged.**
  1. BMNR stays on its 25 Sep close ($27.56), paired with the 27 Sep holdings. The 2 Oct
     close ($26.27, −1.72%) has one source, and pairing it with a week-old ETH valuation
     would mix dates. The next holdings release is due 5 Oct.
  2. QQQ's 21 Sep distribution ($0.7514 vs $0.69).
  3. IEMG's June distribution ($0.66 vs $0.71).
- **Judgements flagged, not changed.** With the corrected rule, QQQ's history-anchored −40%
  sleeve drawdown now sits below the σ model's calm reading (−41.3%). The "correlated-stress"
  row (every sleeve at its judged drawdown at once, −32.1% / −30.0%) is also shallower than
  the normalized σ drawdown. Both say the sleeve judgements are mild beside the corrected
  rule. They are listed as assumptions. Regional scores were re-read against the euro-area
  inflation jump, China's PMI and the dollar, and the order and margins are unchanged.
- **Mutation harness: 106 (70 model, 36 generator), all caught.** New mutants cover:
  - the band typed instead of read from the model;
  - spreads called tight;
  - growth called strong regardless of its score;
  - the rejected 28 Sep snapshot;
  - a wrong reported change;
  - the DD band itself.

  The held-range mutant was retired with the hold.

## Rev. 24 — 29 September 2026 (data to the 28 September close)

- **The term-structure "95% band" was a 90% band.** It printed ±1.645σ, the one-sided z,
  while the same page's other 95% band (the CAGR range) correctly used 1.96. `validate.py`
  re-derived the band with the same 1.645, so the two agreed on the error. The band is now
  ±1.96σ, and the validator takes its z from the normal distribution (erf(z/√2) = 0.95)
  rather than from the generator. The 12-month band widens from ±24.5% to **±29.1%**.
- **The mutation harness could pass vacuously.** `mutate.py` never ran the unmutated repo.
  With one baseline failure (this revision not yet recorded) every mutant made `validate.py`
  exit 1 and was counted as caught: the first run of this pass reported 94 of 94 caught on
  exactly that basis. It now refuses to run unless the baseline passes. The Rev. 23 run was
  valid (its baseline passed); the guard makes that a precondition instead of luck.
- **Three stale facts, all from authoritative sources that had moved on.** The ECB's
  September staff projections put 2026 growth at **0.9%**, not 0.8% (ECB projections page;
  Morningstar agrees). The IMF's July update has world growth at **3.0%**, not 3.1%, and
  China at **4.6%** and India at **6.4%**, where the page carried 4.4% and 6.3% next to a
  43.6% share of world growth taken from the January figures. The vintages are now stated.
  SGOV's 30-day SEC yield was an undated 3.74% labelled "pre-hike". The latest dated figure
  is **3.65%** as of 22 Sep (etf.com; 12-month trailing 3.69%).
- **"Its highest since 2007" was keyed on the sign of the day's change.** Rev. 23 fixed the
  down-day case, but a rise that stops short of the high would still have been called the
  high. The model now carries the high close and its date (`ust10_high`), and the phrase is
  printed only of a close that equals it. `validate.py` runs the helper on a hypothetical
  close 2bp under the high.
- **A stale cause would have been attached to any later day's move.** The lead said yields
  rose "after hot flash PMIs on 23 Sep", a cause of an earlier session. The cause is now a
  dated fact (`move_cause`), printed only when its date is the market date. Today's: the US
  rejected Iran's peace proposal.
- **BMNR was called "levered ETH exposure".** It carries no leverage to speak of: mNAV is
  1.03× and the premium is not debt. It is high-beta (95% volatility against ETH's lower
  figure), and now says so.
- **Six sentences were true only on one side of a threshold**, and the validator had copied
  each of them word for word:
  - the VIX "below" its mean, in two places;
  - "above the highest house";
  - "ranks first at every horizon";
  - "almost the same return per unit of risk";
  - a VIX trigger distance that would have gone negative;
  - "sits inside both" for a drawdown below both readings.

  Each is now computed, and the validator derives the word itself.
- **The revision rows' prior figures were typed twice** (generator and validator). They now
  live once in `PRIOR` and must appear in bold in the previous revision's entry here.
- **The VIX's 28 September close is held back.** Sources give 16.07 (+8.07%), 16.10, 16.30,
  16.34 and 16.37 (+1.50, +10.08%). Two of them reconcile exactly with 14.87, the Rev. 20
  trap. FRED's last observation is 22 Sep and no Cboe history table has the day. The model
  records the held date and range (`VIX_HELD`) and keeps VIX_SPOT at 14.87 (25 Sep). The
  masthead, the lead, the valuation driver and the revisit trigger each say which close
  they use. Calm-regime risk stays at the 25 Sep level; on any of the reported closes, today's
  optimized drawdown would be about 2 points deeper, and the normalized figures would not
  move.
- **Market data to 28 September.**
  - Brent settled $105.28 (+$0.96 from $104.32, exact); WTI $92.60 (+$0.19 from $92.41,
    exact).
  - 10-year 5.24%, from Treasury's par curve (5.17% on 25 Sep, which is the level held),
    +7bp and its highest since 2007. Press reports of "+6bp" and "5.23%" differ by one
    snapshot. The 30-year closed at 5.56%, its highest since 2004.
  - QQQ $736.53 (−$7.97, −1.07% from $744.50, exact); IEMG $81.62 (−$0.93, −1.13% from
    $82.55, exact).
  - BMNR's 28 Sep close is not yet published (range $26.90–27.43), so it stays at $27.56
    (25 Sep), alongside the 27 Sep holdings.
- **Forecasts.** QQQ's forward multiple re-prices 23.33× → 23.08× and its net CAGR rises
  9.54% → **9.65%**. IEMG 8.60% → **8.75%** (dividend yield 2.21%, forward 11.46×). Baseline
  7.87% → **7.95%**, optimized 7.53% → **7.62%**. Normalized drawdowns are unchanged (−35.5% /
  −33.0%) because they no longer depend on the spot VIX. Both books are efficient (106 of
  153), and the unrestricted best-Sharpe book is QQQ 45 / IEMG 45 / SGOV 5 / BMNR 5, still
  rejected. `audit.py`, which uses no model functions, matches every sleeve and portfolio
  figure. Allocations unchanged.
- **Held back, not averaged.**
  1. The VIX's 28 Sep close (above).
  2. BMNR's 28 Sep close.
  3. QQQ's 21 Sep distribution: $0.7514 vs $0.69.
  4. IEMG's June distribution: $0.66 (the $1.80 trailing held) vs $0.71 ($1.85), 0.06 of a
     point of yield.
  5. A 21.95× Nasdaq-100 forward multiple, recorded in Rev. 23.
- **Judgement scores re-read, not changed.** The US rejected Iran's proposal on 26 Sep and oil
  rose, but Geopolitical risk is already 1.4 of 5. The 10-year's new high and a 5.56% 30-year
  sit inside Liquidity & credit's 2.6, and high-yield spreads near 2.8% argue against going
  lower. Regional order and margins are unchanged.
- **House cleanup.**
  - Removed an unused fact (`em_ann_mean`) and a dead variable in the macro pane.
  - Deleted four stale scratch files, among them a coverage scan written for the
    hand-written page, which no longer ran.
  - The README states the hold-back rule and the harness precondition.
- **Mutation harness: 101 (68 model, 33 generator).** One old mutant, a band built on the
  unrounded σ, became equivalent once z changed, because the two round alike at every
  horizon. It was replaced by one that uses the 12-month σ in every row. New mutants cover:
  - a band built on the one-sided z;
  - the high keyed on the day's sign;
  - VIX distance words reversed;
  - a held VIX narrated as a move;
  - the masthead VIX undated while held;
  - the revisit trigger undated while held;
  - a prior figure absent from the record;
  - a close short of the high;
  - a changed held range.

## Rev. 23 — 28 September 2026 (data to the 25 September close)

- **The stress-volatility regime moved the wrong way with the VIX — a structural error
  carried since the regimes were introduced.** The calm vols were fixed constants while the
  "normalized" regime was those constants times VIX_MEAN / VIX_SPOT. So a *rising* VIX made
  stress risk *fall* (at a VIX of 25, QQQ's mean-reverted vol would have been 15.9%, below
  today's) and a 5% fall in the VIX on 25 Sep moved the recommended book's normalized
  drawdown by 1.4 points with nothing else changed. Every earlier check re-derived
  the page from the model, so none could see it; the history even records the drawdown
  "improving" as the uplift collapsed. Fixed: the calm regime is today's volatility and
  scales with the spot VIX; the normalized regime is the volatility at the long-run mean and
  ignores spot; they differ by the uplift, as the page says. The equity vols are unchanged
  from Rev. 22 (struck at the 15.67 close), so normalized drawdowns are unchanged
  (−35.5% / −33.0%) while today's fall with the VIX (optimized −25.9% → −24.9%).
  `validate.py` now runs a metamorphic test — re-execute the model with the spot VIX 20%
  higher — and requires normalized vol and drawdown to be identical, equity calm vol to scale
  in proportion, and today's risk to rise. Planting the old design fails five of those checks.
- **Volatilities and stress correlations were missing from the assumptions list.** Only
  calm correlations were tagged observed; the vol levels (21 / 18 / 95%), the BMNR ×1.15 stress
  multiplier and the stress correlations are estimates. Added as an eighth assumed input,
  which the page lists from the tag.
- **BMNR's release date and holdings date were one field.** The disclaimer said holdings were
  "from its 21 September release" using the date the holdings were struck. Holdings are as of
  a Sunday and released the Monday after (27 and 28 Sep); the model now carries both and the
  page states both.
- **"Its highest since 2007" would have been printed against a down-day close, and the
  30-year was said to have "closed at" its highest since 2004** with only a live quote for
  support. The 10-year note is now computed (on a lower close it names the prior 5.20% as the
  high); the 30-year is stated as what a dated source supports, that it hit the level on 24 Sep.
- **The verification rows on the Portfolios tab were hard-coded and unchecked** — the same
  stale-prose class as the rest of this file: "Fund prices 22/18 Sep → 24 Sep" would have
  stayed after this roll. The current figures are computed and `validate.py` re-derives each.
- **Four driver and region notes gave only one side of their own score.** Europe's card cited
  the ECB's 0.8% growth projection and omitted the 23 Sep flash composite PMI of 53.1 (52.0 in
  August, a poll of 51.7; the highest since April 2023). Liquidity & credit, scored 4.5,
  cited only yields, not high-yield spreads near 2.8% (FRED series, 24 Sep). Growth omitted
  Michigan sentiment of 48.1 and said "flash PMIs" without saying they were the US ones.
  Inflation omitted July PCE of 3.7% (core 3.3%), the Fed's gauge. All four added; no score
  changed, because none of the new facts moves a driver across a level a note already implied.
- **README stale**: it said three inputs were assumptions and described a one-regime uplift.
  Both corrected.
- **Market data to 25 September.** VIX 14.87 (−5.11% from 15.67), Brent settled $104.32
  (−$2.28, −2.14% from $106.60, which reconciles exactly), 10-year 5.17% (−3bp; Trading
  Economics and Advisor Perspectives' Treasury snapshot agree), QQQ $744.50 (+$3.40; a 28 Sep
  quote repeats it as the previous close), IEMG $82.55 (its quoted previous close, $81.70,
  is exactly the 24 Sep close held), BMNR $27.56 (−$0.47, −1.68%, two outlets). BMNR's 28 Sep
  release: 6,001,302 ETH at $2,698 as of 27 Sep (17,362 bought; 5,983,940 + 17,362
  reconciles), 5,067,309 staked (unchanged for the third release, so the staked share falls to
  84.4%), $17.2B total. The premium to crypto narrows 1.08× → **1.03×** — the stock fell 4.1%
  while holdings rose — which lifts BMNR's net CAGR 9.05% → **9.51%**. QQQ 9.59% → **9.54%**
  (its forward multiple re-prices 23.23× → 23.33×), IEMG 8.73% → **8.60%**. Baseline
  7.90% → **7.87%**, optimized 7.57% → **7.53%**; both books stay on the frontier, allocations
  unchanged, and the independent recomputation (`audit.py`, no model functions) matches every
  sleeve and portfolio figure.
- **Held back, not averaged.** (1) QQQ's 21 Sep distribution, $0.7514 vs $0.69 — the trailing
  $3.03 stays; the yield moves at most 0.01 either way. (2) QQQ's 24 Sep close appears as
  741.10 (implied by the 25 Sep change), 741.21 (held) and 741.32; the 0.03% spread moves its
  net CAGR by under 0.01. (3) CNBC's live 10-year quote read 5.163% "up less than 1bp" while
  two sources say 5.17% and a fall; the level is used, the disagreement is recorded.
  (4) BMNR's premium sits on a rounding edge (1.025×): $0.02B of crypto either way moves it a
  cent, and 0.3% more shares from the week's purchases are not yet in the share count.
  (5) A 21.95× Nasdaq-100 forward multiple (MacroMicro / GuruFocus, September) against the
  22.4× basis: it lies inside the 20.8–22.4× range that set the basis, would lift QQQ's net
  CAGR to 10.15% and the baseline to 8.14% (optimized 7.74%), widening the gap between the
  books from 0.34 to 0.40. The recommendation does not change, but vendor definitions of
  forward earnings differ and this input stays the page's weakest.
- **Judgement scores re-read, not changed.** Regional margins: Europe would need +2.1 points
  across all four horizons (of 10) to overtake the US; Asia / EM leads the US by only 0.6, so
  that ordering is the fragile one — the US–China outcome (tariff cuts on $30B of goods each
  way, the truce extended two months, few breakthroughs) does not move it. Fed speakers pushed
  October-hike odds to 64–77%; Monetary policy is already the lowest-scored driver.
- **Mutation harness: 94 (67 model, 27 generator), all caught.** New: the old inverted uplift,
  the vols with no spot dependence, the strike level, BMNR's calm vol, a high claimed on a
  down day, a revision row on the wrong figure, a disclaimer without the holdings date. One
  older mutant became equivalent — BMNR's price date now equals the market date, so "dated to
  BMNR's price" changed nothing — and was replaced by one dated to the holdings.

## Rev. 22 — 25 September 2026 (data to the 24 September close)

- **The "still open" list understated the assumptions.** It named three inputs as assumed —
  QQQ's earnings growth, the drawdown rule, BMNR's ETH return — and omitted IEMG's earnings
  growth and currency drag, BMNR's dilution drag and the sleeve drawdowns, which are no more
  observed. Every input is now tagged observed or assumed in the model (`ASSUMED`,
  `OBSERVED`) and the page lists seven, generated from that tag.
- **An undisclosed simplification in the headline figures.** Portfolio CAGR is the
  weight-average of the sleeve CAGRs, which omits the diversification return a rebalanced book
  earns, ½(Σwσ² − σₚ²). Excluding BMNR it is about 0.55–0.57%/yr, near-identical for both
  books, so the ranking is unaffected; with BMNR's 95% volatility the formula gives about
  2.4%, which is not credible. The page now states it; the CAGRs shown are conservative.
- **Fund prices rolled to 24 September.** QQQ $741.21 (reconciled with the Nasdaq-100's
  +0.03% from $740.93), IEMG $81.70. QQQ's forward multiple re-prices 23.42× → 23.23×, its
  de-rating eases −0.22 → −0.14, and its net CAGR rises **9.51% → 9.59%**. Baseline 7.90%,
  optimized 7.57%.
- **The baseline returns to the efficient frontier.** With QQQ's forecast up, both books are
  efficient (106 allocations): two points on one curve, not a better and a worse book. Weights
  are unchanged.
- **Market data to 24 September:** VIX 15.67 (+3.23% from 15.18, history table), Brent settled
  $106.60 (+3.4%), 10-year 5.20% (+8bp; the three-session +23bp reported reconciles with the
  closes on file), 30-year at its highest close since 2004.
- **Held back:** QQQ's 21 September distribution ($0.7514 vs $0.69 across sources) — the
  trailing dividend stays at the verified $3.03, a difference of at most 0.01 in the yield;
  BMNR's 24 September close and that day's ETH price, so BMNR stays on its 22 September price
  and 21 September holdings, a matched pair.
- **A neutral score beside a tightening note.** Liquidity & credit scored 3.0 of 5 while its
  own note said conditions were tightening, with the 10-year at a 19-year high and the 30-year
  at a 22-year high. It now scores 2.6 (4.5 of 10). The composite gauge still reads 2.4.
- **Three mutations went silent on the new data.** With QQQ and IEMG both priced on 24
  September, the disclaimer date equal to QQQ's price date, and the rounded and unrounded CAGR
  gaps both 0.33, three planted bugs produced identical pages — equivalent mutants, not holes
  in the validator. They were replaced with bugs that change the output whatever the data.
- An independent recomputation of every net CAGR, σ and drawdown from raw inputs, without the
  model's functions, matched the model to machine precision.

## Rev. 21 — 24 September 2026 (data to the 23 September close)

- **A VIX close published here was a pre-settlement snapshot.** Rev. 20 carried 15.35 for
  23 September, from a live blog written at the bell ("+1.14 / +8.02%"). The official 4:15pm
  close is **15.18** (+0.97 / +6.83%) in the history tables. Both reconcile from 14.21, so the
  change test could not separate them; closes now come from history tables only.
- **The disclaimer was twelve days stale.** It gave the data date as 11 September, called
  QQQ's 22.4× multiple "the stalest input" (price-linked since Rev. 19), dated BMNR's balance
  sheet to an 8 September 8-K (the 21 September release is used), and said a point of QQQ
  growth moves "a quarter" of the gap between the books (0.100 of 0.32, nearly a third).
- **Three source links were superseded:** the July FOMC statement (the September decision is
  cited), a June ECB decision (September), and the 5.93M-ETH BMNR release (5.98M).
- **The page is now generated.** `build.py` writes every figure and every comparison word
  from the model; `validate.py` re-derives them without importing it and requires the file to
  be exactly what `build.py` writes. Twenty revisions of stale-prose corrections were one
  defect: numbers typed into sentences. The page is also about a third of its former length.
- 24 September closes were researched and held back: VIX and 10-year figures conflicted
  across sources hours after the close.
- **The validator was rewritten for the generated page** (305 checks): model consistency,
  derived inputs, analytics, freshness, structure, then every pane re-derived without
  importing `build.py`. `mutate.py` now runs in throwaway copies, in parallel, and adds 21
  **generator mutations** — realistic bugs planted in `build.py`, the page rebuilt from them —
  which only the independent checks can catch. 83 run, 0 survived.
- **Five model inputs had gone dead.** The first concise draft dropped the house-forecast
  table and the FOMC date, so mutating Vanguard, Fidelity, BlackRock, J.P. Morgan's EM
  volatility or the decision day changed nothing on the page. Five survivors exposed it; the
  table (five rows) and the dated policy note are back.
- **The generator and the validator agreed on a wrong number.** Both counted mutations with
  the same regex, which missed the generator rows: the page said 62 while `mutate.py` ran 83.
  The validator now counts the two tables separately.
- House cleanup: `cash_line()` and an unused export field removed; the README no longer
  repeats model figures (they went stale in it every pass); `sync-artifact.sh` refuses a page
  `build.py` would not write.

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
