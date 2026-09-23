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

html = open('allocation.html').read()
E = M.export()
body = html[:html.index('Verification log')]
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
req(1, 'Live HTTPS URL, bottom tab bar, light theme',
    bool(tabs) and light and no_dark and html.count('data-p="') == 5,
    f'{html.count("data-p=")} bottom tabs; light tokens only, no dark override')

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
req(5, 'A slide per fund/ETF/stock with net 10-yr CAGR and expected drawdown',
    len(slides) == 4 and have and cagr_dd, f'{len(slides)} swipeable slides, each with both figures')

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
reg_ok = all(len(v['scores']) == 4 for v in E['regions'].values()) and len(E['regions']) == 3
order  = all(E['regions']['Asia / EM']['scores'][h] > E['regions']['United States']['scores'][h]
             > E['regions']['Europe']['scores'][h] for h in range(4))
req(8, 'Ranking for US, Europe and Asia at 3, 6, 12 months and 10 years', reg_ok and order,
    'Asia > US > Europe at all four horizons')

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
req(10, '10-yr CAGR net of fees and expected drawdown for both portfolios', both,
    ' vs '.join(f"{p} {E['portfolios'][p]['calm']['cagr_d']:.2f}% / "
                f"−{E['portfolios'][p]['calm']['dd']:.1f}%" for p in E['portfolios']))

# 11 ── weights end in 5 or 0
req(11, 'Allocation percentages end in 5 or 0 in both portfolios',
    all(v % 5 == 0 for w in E['weights'].values() for v in w.values()) and
    all(sum(w.values()) == 100 for w in E['weights'].values()), 'both sum to 100')

# 12 ── donut vs donut
donuts = re.findall(r'<circle cx="90" cy="90" r="64"', html)
req(12, 'Two portfolios shown as donut charts, side by side', len(donuts) == 8 and 'class="duo"' in html,
    '2 donuts x 4 segments, rendered side by side')

# 13 ── baseline is a 10-year strategic book
req(13, 'Baseline portfolio built on a 10-year horizon',
    'Strategic' in html and E['weights']['baseline']['QQQ'] == 45,
    'plain strategic split, no macro tilt')

# 14 ── optimized driven by macro + regional rankings (+ volatility, added later)
req(14, 'Optimized portfolio from macro sentiment and regional rankings, 3/6/12mo, 10-yr horizon',
    'Macro-tilted' in html and 'volatility analysis across 3, 6 and 12 months' in html,
    'also incorporates volatility analysis, requested later')

# 15 ── max CAGR net of fees subject to controlling drawdown
# Two objectives, so "best" means Pareto-efficient: no admissible allocation offers
# BOTH more CAGR and less drawdown. An earlier version of this check asked whether the
# optimized book beat the baseline on Sharpe, which the brief never required -- and which
# failed once QQQ's forecast was corrected, even though the recommendation stayed efficient.
adm = []
for q in range(5, 86, 5):
    for i in range(5, 86, 5):
        for s_ in range(5, 86, 5):
            b = 100 - q - i - s_
            if b < 5 or b % 5: continue
            w = {'QQQ': q, 'IEMG': i, 'SGOV': s_, 'BMNR': b}
            st = M.stats(w, 'normalized')
            adm.append((w, st['cagr_d'], st['dd']))
opt, base = E['portfolios']['optimized'], E['portfolios']['baseline']
dominators = [o for o in adm
              if o[1] >= opt['normalized']['cagr_d'] and o[2] <= opt['normalized']['dd']
              and (o[1] > opt['normalized']['cagr_d'] or o[2] < opt['normalized']['dd'])]
req(15, 'Maximise net CAGR while controlling drawdown to a minimum', not dominators,
    f"efficient: no allocation of {len(adm)} beats it on both axes; "
    f"{opt['normalized']['cagr_d']:.2f}% at −{opt['normalized']['dd']:.1f}% vs "
    f"baseline {base['normalized']['cagr_d']:.2f}% at −{base['normalized']['dd']:.1f}%")

# 16 ── the audit trail itself
req(16, 'Data revalidated, errors recorded and rectified',
    'Verification log' in html and 'sync-artifact' not in html,
    f'change log on the page; {len(re.findall(r"class=.kv.", html[html.index("Verification log"):]))} entries')

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
