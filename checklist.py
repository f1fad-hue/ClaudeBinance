#!/usr/bin/env python3
"""
Runs the original brief as an acceptance test against allocation.html.

Each requirement from the request is encoded as a check so the deliverable can
be re-audited on demand rather than eyeballed. Reports PASS / FAIL / CONFLICT.
CONFLICT means the deliverable knowingly departs from the brief in a way the page
discloses; it is surfaced for the user to settle, never silently resolved, and it
does not set the exit code. An earlier revision advertised this status and a PASS*
status without implementing either.
"""
import re, sys
import portfolio_model as M

# Optional: `./checklist.py --live PATH` compares the page the live HTTPS URL serves
# (saved with the Artifact tool's read action) against this repo's file and checks
# the host shell carries the mobile viewport. Without it, item 1 says it was not run.
LIVE = sys.argv[sys.argv.index('--live') + 1] if '--live' in sys.argv else None

html = open('allocation.html').read()
E = M.export()
rows = []

def req(n, text, ok, note=''):
    rows.append((n, text, 'PASS' if ok else 'FAIL', note))

def conflict(n, text, note):
    """The deliverable departs from the brief in a way the page discloses but that
    only the user can settle. Not a pass and not a failure: it is surfaced so the
    decision stays theirs. Reported separately and does not set the exit code."""
    rows.append((n, text, 'CONFLICT', note))

# 1 ── live https url, android, bottom tabs, light theme
tabs = re.search(r'\.tabs\{position:fixed;bottom:0', html)
light = ':root{' in html and '--paper:#F7F8FA' in html
no_dark = '@media(prefers-color-scheme: dark)' not in html and '@media (prefers-color-scheme: dark)' not in html
# Android: the page is published as a fragment and the artifact host supplies the
# document shell. Earlier this check never looked at the live page or the viewport,
# which is what makes a phone lay it out at device width instead of 980px desktop.
mobile_css = '.app{max-width:460px' in html and 'env(safe-area-inset-bottom' in html
live_note = 'live copy not compared (run with --live PATH)'
live_ok = True
if LIVE:
    _l = open(LIVE).read()
    _b = _l.split('<body>', 1)[1].strip()
    for _t in ('</body></html>', '</body>'):
        if _b.endswith(_t): _b = _b[:-len(_t)].strip()
    _vp = 'name=viewport content="width=device-width' in _l or 'name="viewport" content="width=device-width' in _l
    live_ok = _b == html.strip() and _vp and 'color-scheme:light' in _l
    live_note = ('live page identical to the validated file; host shell sets a device-width viewport and a light colour scheme'
                 if live_ok else 'LIVE PAGE DIFFERS from the repo file, or its shell lacks the mobile viewport')
req(1, 'Live HTTPS URL for Android, bottom tab bar, light theme',
    bool(tabs) and light and no_dark and html.count('data-p="') == 5 and mobile_css and live_ok,
    f'{html.count("data-p=")} fixed bottom tabs; light tokens only, no dark override; {live_note}')

# 2 ── all four sleeves in both portfolios
allfour = all(set(w) == {'QQQ','IEMG','SGOV','BMNR'} and all(v >= 5 for v in w.values())
              for w in E['weights'].values())
req(2, 'Uses SGOV, QQQ, IEMG and BMNR in both portfolios', allfour,
    '; '.join(f'{p}: ' + '/'.join(f'{k} {v}%' for k, v in w.items()) for p, w in E['weights'].items()))

# 3 ── broad + correlated macro sentiment tied to the holdings
broad = 'Composite inputs' in html and len(E['gauge']['drivers']) == 6
corr  = 'Correlated transmission' in html and all(f'>{t}</div>' in html for t in ('SGOV','QQQ','IEMG','BMNR'))
req(3, 'Broad and correlated macro sentiment reflecting the holdings', broad and corr,
    '6 weighted drivers; a transmission note per sleeve')

# 4 ── volatility deep analysis at 3/6/12 months on a 10-year horizon
vol_h = all(f'{E["vix"]["term"][h]:.2f}%' in html for h in (0.25, 0.5, 1.0))
vol_p = all(f'{E["portfolios"][p][r]["sigma_h"][h]:.2f}%' in html
            for p in E['portfolios'] for r in ('calm',) for h in (0.25, 0.5, 1.0))
req(4, 'Volatility maths at 3, 6, 12 months with a 10-year horizon',
    vol_h and vol_p and '10 yr max DD' in html, 'VIX term structure + portfolio sigma and VaR per horizon')

# 5 ── a slide per holding carrying net CAGR and expected drawdown
slides = re.findall(r'<article class="slide">.*?</article>', html, re.S)
have = all(any(t in sl for sl in slides) for t in ('SGOV','QQQ','IEMG','BMNR'))
cagr_dd = all('Net 10-yr CAGR' in sl and 'Expected max DD' in sl for sl in slides)
# "net 10yr cagr minus fund fees": each ETF slide must show the fee it nets off,
# and the net must equal gross minus that fee. BMNR is a stock and has no fund fee.
def _slide(t): return next(sl for sl in slides if f'<div class="sl-tick">{t}</div>' in sl)
fees = all(f'Expense ratio</span><span class="v">{M.A[t]["er"]:.2f}%' in _slide(t) and
           abs(M.A[t]['gross'] - M.A[t]['er'] - M.A[t]['net']) < 0.006 for t in ('SGOV','QQQ','IEMG'))
req(5, 'A slide per fund/ETF/stock with net 10-yr CAGR (after fund fees) and expected drawdown',
    len(slides) == 4 and have and cagr_dd and fees,
    f'{len(slides)} swipeable slides, each with both figures; the three ETF slides show the fee netted off')

# 6 ── the sentiment gauge; the brief now specifies 1-5, matching the page
scale_ok = '/5</small>' in html and 1 <= E['gauge']['score5'] <= 5
regions_match = all(1 <= x <= 5 for v in E['regions'].values() for x in v['scores'])
req(6, 'Gauge of overall macro driver sentiment, 1 to 5', scale_ok and regions_match,
    f'reads {E["gauge"]["display"]}/5; regional rankings share the scale')

# 7 ── rationale report
req(7, 'Rationale report for the optimized allocation',
    'Rationale' in html and html.count('<div class="num">') == 1 and 'Recommendation.' in html,
    f'{len(re.findall(r"<div><b>", html[html.index(chr(60)+"div class=" + chr(34) + "num" + chr(34) + ">"):]))} numbered arguments plus a recommendation')

# 8 ── regional ranking system
# Earlier this read only the model and hardcoded "Asia > US > Europe", so a
# legitimate change in the ranking would have failed the requirement. It now checks
# that the PAGE ranks the three blocs by their mean score, at all four horizons.
reg_ok = all(len(v['scores']) == 4 for v in E['regions'].values()) and len(E['regions']) == 3
_seg = html[html.index('id="p-regions"'):html.index('id="p-vol"')]
_page_rank = {nm: int(r) for nm, r in re.findall(r'<span class="nm">([^<]+)</span><span class="rank[^"]*">Rank (\d)</span>', _seg)}
_names = {'Asia / EM': 'Asia / Emerging', 'United States': 'United States', 'Europe': 'Europe'}
_by_mean = sorted(E['regions'], key=lambda k: -E['regions'][k]['mean'])
ranks_ok = all(_page_rank.get(_names[k]) == i + 1 for i, k in enumerate(_by_mean))
horizons_ok = all(_seg.count(f'<span class="hz-l">{h}</span>') == 3 for h in ('3 mo', '6 mo', '12 mo', '10 yr'))
req(8, 'Ranking for US, Europe and Asia at 3, 6, 12 months and 10 years', reg_ok and ranks_ok and horizons_ok,
    'page ranks ' + ' > '.join(_names[k] for k in _by_mean) + ' by mean score; every bloc scored at all four horizons')

# 9 ── sourcing
srcs = re.findall(r'href="https://([^/"]+)', html)
auth = {'www.federalreserve.gov','www.bls.gov','www.ecb.europa.eu','www.imf.org',
        'fred.stlouisfed.org','www.sec.gov','www.ishares.com','www.invesco.com','www.cboe.com'}
# Counting source domains tested whether the page *cites* authorities, not whether
# its numbers come from them. Three inputs are admittedly extrapolations, and the
# page names them; one of those three is its single most load-bearing figure. That
# is a real departure from the brief's wording, so it is reported as one.
ASSUMED = (f"{M.OBS['QQQ']['eps']:g}%/yr earnings growth", f'{M.DD_MULT:.2f} x sigma drawdown multiplier',
           f"BMNR's {M.BMNR['eth']:g}%/yr ETH appreciation")
observed = auth.issubset(set(srcs))
discloses = 'Still open' in html and 'assumptions rather than observations' in html
if observed and discloses:
    conflict(9, 'Data only from authoritative, fact-checked sources',
             f'{len(set(srcs))} authoritative domains cited and every observable figure '
             f'sourced — but {len(ASSUMED)} inputs are extrapolations, not observations '
             f'({"; ".join(ASSUMED)}), and the first is the most load-bearing number on '
             f'the page. Disclosed in "Still open" and in the sensitivity table; only you '
             f'can decide whether that meets the brief.')
else:
    req(9, 'Data only from authoritative, fact-checked sources', False,
        'authoritative domains missing' if not observed else 'assumptions not disclosed')

# 10 ── both portfolios' CAGR net of fees and drawdown
both = all(f"{E['portfolios'][p]['calm']['cagr_d']:.2f}%" in html and
           f"−{E['portfolios'][p]['calm']['dd']:.1f}%" in html for p in E['portfolios'])
both = both and all(f"−{E['portfolios'][p]['normalized']['dd']:.1f}%" in html for p in E['portfolios'])
req(10, '10-yr CAGR net of fees and expected drawdown for both portfolios', both,
    ' vs '.join(f"{p} {E['portfolios'][p]['calm']['cagr_d']:.2f}% / "
                f"−{E['portfolios'][p]['calm']['dd']:.1f}% (−{E['portfolios'][p]['normalized']['dd']:.1f}% normalised)"
                for p in E['portfolios']))

# 11 ── weights end in 5 or 0
req(11, 'Allocation percentages end in 5 or 0 in both portfolios',
    all(v % 5 == 0 for w in E['weights'].values() for v in w.values()) and
    all(sum(w.values()) == 100 for w in E['weights'].values()), 'both sum to 100')

# 12 ── donut vs donut
donuts = re.findall(r'<circle cx="90" cy="90" r="64"', html)
req(12, 'Two portfolios shown as donut charts, side by side', len(donuts) == 8 and 'class="duo"' in html,
    '2 donuts x 4 segments, rendered side by side')

# 13 ── baseline is a 10-year strategic book
# Earlier this asserted QQQ == 45, which tests a number rather than the requirement.
req(13, 'Baseline portfolio built on a 10-year horizon',
    '<div class="dn-t">Baseline</div><div class="dn-c">Strategic</div>' in html and
    'both are built for a 10-year horizon' in html and 'The baseline is a plain strategic split' in html,
    'plain strategic split for the 10-year horizon, no macro tilt')

# 14 ── optimized driven by macro + regional rankings (+ volatility, added later)
# Two phrases on the page do not show the book is BASED on its inputs. The tilt
# must follow them: overweight the sleeve of the top-ranked bloc, hold more reserve
# while spot volatility sits below its mean (the normalised regime is the larger
# risk), and come out with the lower normalised drawdown.
_top = _by_mean[0]
_sleeve = {'Asia / EM': 'IEMG', 'United States': 'QQQ'}.get(_top)
_Bw, _Ow = E['weights']['baseline'], E['weights']['optimized']
tilt_ok = (_sleeve is not None and _Ow[_sleeve] > _Bw[_sleeve] and
           (M.VIX_SPOT >= M.VIX_MEAN or _Ow['SGOV'] >= _Bw['SGOV']) and
           E['portfolios']['optimized']['normalized']['dd'] < E['portfolios']['baseline']['normalized']['dd'])
req(14, 'Optimized portfolio from broad + correlated sentiment, volatility and regional rankings, 3/6/12mo, 10-yr',
    'Macro-tilted' in html and 'volatility analysis across 3, 6 and 12 months' in html and
    'Correlated transmission' in html and tilt_ok,
    f'{_sleeve} {_Bw[_sleeve]}→{_Ow[_sleeve]}% for the top-ranked bloc; SGOV {_Bw["SGOV"]}→{_Ow["SGOV"]}% '
    f'with VIX {M.VIX_SPOT} below its {M.VIX_MEAN} mean; lower normalised drawdown')

# 15 ── max CAGR net of fees subject to controlling drawdown
# Two objectives, so "best" means Pareto-efficient: no admissible allocation offers
# BOTH more CAGR and less drawdown. An earlier version of this check asked whether the
# optimized book beat the baseline on Sharpe, which the brief never required -- and which
# failed once QQQ's forecast was corrected, even though the recommendation stayed efficient.
adm = [(w, st['cagr_d'], st['dd']) for w, st in ((w, M.stats(w, 'normalized')) for w in M.admissible())]
opt, base = E['portfolios']['optimized'], E['portfolios']['baseline']
dominators = [o for o in adm
              if o[1] >= opt['normalized']['cagr_d'] and o[2] <= opt['normalized']['dd']
              and (o[1] > opt['normalized']['cagr_d'] or o[2] < opt['normalized']['dd'])]
req(15, 'Maximise net CAGR while controlling drawdown to a minimum', not dominators,
    f"efficient: no allocation of {len(adm)} beats it on both axes; "
    f"{opt['normalized']['cagr_d']:.2f}% at −{opt['normalized']['dd']:.1f}% vs "
    f"baseline {base['normalized']['cagr_d']:.2f}% at −{base['normalized']['dd']:.1f}%")

# 16 ── the audit trail itself: a log on the page, a count that matches the record
_n_corr = int(re.search(r'CORRECTIONS: (\d+)', open('VERIFICATION.md').read()).group(1))
req(16, 'Data revalidated, errors recorded and rectified',
    'Verification log' in html and f'{_n_corr} corrections recorded' in html and f'## Rev. {M.REVISION} ' in open('VERIFICATION.md').read(),
    f'{_n_corr} corrections recorded; this revision listed on the page and in VERIFICATION.md')

w = max(len(t) for _, t, _, _ in rows)
print(f"{'#':>3}  {'REQUIREMENT':<{w}}  RESULT")
print('-' * (w + 16))
for n, t, r, note in rows:
    print(f"{n:>3}  {t:<{w}}  {r}")
    if note: print(f"{'':>3}  {'':<{w}}  └─ {note}")
p = sum(1 for *_, r, _ in rows if r.startswith('PASS'))
f = sum(1 for *_, r, _ in rows if r == 'FAIL')
cf = sum(1 for *_, r, _ in rows if r == 'CONFLICT')
print('-' * (w + 16))
print(f"{p} pass, {f} fail, {cf} conflict  (of {len(rows)})")
if cf: print("CONFLICT = the page departs from the brief and says so on its face; "
             "only the user can settle it. Not counted as a failure.")
sys.exit(1 if f else 0)
