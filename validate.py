#!/usr/bin/env python3
"""
Checks allocation.html against portfolio_model.py. Every figure the page
asserts must match what the model computes. Exits non-zero on any mismatch.
"""
import re, sys, math
import portfolio_model as M

html = open('allocation.html').read()
fails, checks = [], 0

def ck(label, ok, got=None, want=None):
    global checks
    checks += 1
    if not ok:
        fails.append(f'{label}: page={got!r} model={want!r}')

def present(label, needle):
    ck(label, needle in html, needle[:70], 'present')

E = M.export()

# ── model self-consistency, independent of the page ──────────────────────────
for pname, w in M.PORTFOLIOS.items():
    ck(f'{pname} weights sum to 100', sum(w.values()) == 100, sum(w.values()), 100)
    for reg in M.REGIME:
        st = M.stats(w, reg)
        ck(f'{pname}/{reg} risk contribs sum to 100',
           abs(sum(st['rc'].values()) - 100) < 1e-6, sum(st['rc'].values()), 100)
        ck(f'{pname}/{reg} sigma within sleeve bounds',
           min(M.REGIME[reg]['vol'].values()) < st['vol'] < max(M.REGIME[reg]['vol'].values()),
           st['vol'], 'between min and max sleeve sigma')
        ck(f'{pname}/{reg} VaR worsens with horizon',
           st['var'][0.25] > st['var'][0.5] > st['var'][1.0], list(st['var'].values()), 'monotone')
    ck(f'{pname} normalized sigma exceeds calm',
       M.stats(w,'normalized')['vol'] > M.stats(w,'calm')['vol'], '', 'norm > calm')
for k, c in E['components'].items():
    ck(f'{k} components sum to gross',
       abs(c['div']+c['eps']+c['val']+c['fx']-c['gross']) < 0.005, c, 'sums')
    ck(f'{k} gross minus fee equals net', abs(c['gross']-c['er']-c['net']) < 0.005, c, 'nets')
ck('driver weights sum to 1', abs(sum(x for _,_,x in M.DRIVERS) - 1) < 1e-9)
for k, v_ in E['regions'].items():
    ck(f'{k} mean matches its scores',
       abs(sum(M.to5(x) for x in M.REGIONS[k])/4 - v_['mean']) < 0.05, v_['mean'], 'mean')
ck('optimized drawdown beats baseline in both regimes',
   all(M.stats(M.PORTFOLIOS['optimized'],r)['dd'] < M.stats(M.PORTFOLIOS['baseline'],r)['dd']
       for r in M.REGIME), '', 'optimized lower')

# ── structure ────────────────────────────────────────────────────────────────
for tag in ('section','div','table','article','svg','nav','script','style',
            'p','tr','td','th','span','button','a','circle','text','path','line'):
    o = len(re.findall(r'<%s[\s/>]' % tag, html)); c = len(re.findall(r'</%s>' % tag, html))
    if tag in ('circle','path','line'):        # void-ish in our usage: self-closed
        continue
    ck(f'tags <{tag}>', o == c, o, c)
ids = re.findall(r'\bid="([^"]+)"', html)
ck('unique ids', len(ids) == len(set(ids)), len(ids), len(set(ids)))
panes = set(re.findall(r'<section class="pane[^"]*" id="([^"]+)"', html))
tabs  = set(re.findall(r'data-p="([^"]+)"', html))
ck('tabs match panes', panes == tabs, sorted(panes), sorted(tabs))
for p in panes:
    ck(f'pane {p} has tabpanel role', f'id="{p}" role="tabpanel"' in html or
       f'<section class="pane on" id="{p}" role="tabpanel"' in html, p, 'role')

# ── sleeve figures ───────────────────────────────────────────────────────────
for k, v in E['sleeves'].items():
    present(f'{k} net CAGR', f"{v['net']:.2f}%")
for k in ('QQQ','IEMG','SGOV'):
    present(f'{k} terminal', f"${E['sleeves'][k]['terminal']:,}")

# ── building blocks ──────────────────────────────────────────────────────────
for k in ('QQQ','IEMG'):
    c = E['components'][k]
    for fld, sign in (('div','+'), ('eps','+'), ('gross',''), ('net','')):
        present(f'{k} {fld}', f"{sign if sign and c[fld]>0 else ''}{c[fld]:.2f}")

# ── portfolios ───────────────────────────────────────────────────────────────
for name, w in E['weights'].items():
    calm, norm = E['portfolios'][name]['calm'], E['portfolios'][name]['normalized']
    present(f'{name} CAGR',        f"{calm['cagr_d']:.2f}%")
    present(f'{name} fee',         f"{calm['fee']:.3f}%")
    present(f'{name} sigma calm',  f"{calm['vol']:.2f}%")
    present(f'{name} sigma norm',  f"{norm['vol']:.2f}%")
    present(f'{name} maxDD calm',  f"−{calm['dd']:.1f}%")
    present(f'{name} maxDD norm',  f"−{norm['dd']:.1f}%")
    present(f'{name} naive stress',f"−{calm['naive']:.1f}%")
    present(f'{name} terminal',    f"${calm['terminal']:,.0f}")
    present(f'{name} fee drag',    f"−${calm['fee_drag']:,.0f}")
    for tk, pct in w.items():
        present(f'{name} weight {tk}', f'{tk}<em>{pct}%</em>')

# optimized-only: Sharpe and risk contributions shown on the page
present('optimized Sharpe calm', f"{E['portfolios']['optimized']['calm']['sharpe']:.3f}")
present('baseline Sharpe calm',  f"{E['portfolios']['baseline']['calm']['sharpe']:.3f}")
for k, v in E['portfolios']['optimized']['normalized']['rc'].items():
    present(f'risk contrib {k}', f"{v:.1f}%")

# ── the comparison table's own cells, not merely 'value appears somewhere' ────
cmp_rows = {
 'Net 10-yr CAGR':      (f"{E['portfolios']['baseline']['calm']['cagr_d']:.2f}%",
                         f"{E['portfolios']['optimized']['calm']['cagr_d']:.2f}%"),
 'σ — calm (today)':    (f"{E['portfolios']['baseline']['calm']['vol']:.2f}%",
                         f"{E['portfolios']['optimized']['calm']['vol']:.2f}%"),
 'σ — vol normalized':  (f"{E['portfolios']['baseline']['normalized']['vol']:.2f}%",
                         f"{E['portfolios']['optimized']['normalized']['vol']:.2f}%"),
 'Max DD — calm':       (f"−{E['portfolios']['baseline']['calm']['dd']:.1f}%",
                         f"−{E['portfolios']['optimized']['calm']['dd']:.1f}%"),
 'Max DD — normalized': (f"−{E['portfolios']['baseline']['normalized']['dd']:.1f}%",
                         f"−{E['portfolios']['optimized']['normalized']['dd']:.1f}%"),
}
for label, (b_want, o_want) in cmp_rows.items():
    m = re.search(r'<td>%s</td>((?:<td class="n[^"]*">[^<]+</td>){2})' % re.escape(label), html)
    ck(f'cmp row present: {label}', m is not None, bool(m), True)
    if m:
        cells = re.findall(r'<td class="n[^"]*">([^<]+)</td>', m.group(1))
        ck(f'cmp row {label}', cells == [b_want, o_want], cells, [b_want, o_want])

# ── gauge ────────────────────────────────────────────────────────────────────
g = E['gauge']
present('gauge display', f'>{g["display"]}<small>/5</small>')
present('gauge arc',     f'stroke-dasharray="{g["arc_dash"]} 251.4"')
present('gauge needle',  f'x2="{g["needle"][0]}" y2="{g["needle"][1]}"')
for nm, sc, fl in g['drivers']:
    present(f'driver {nm} score', f'>{sc}</div>')
    present(f'driver {nm} bar',   f'width:{fl}%')
ck('gauge rescale commutes', abs(g['score5'] - round(M.to5(g['score10']), 4)) < 1e-9,
   g['score5'], round(M.to5(g['score10']), 4))

# ── regions ──────────────────────────────────────────────────────────────────
seg = html[html.index('============ REGIONS'):html.index('============ VOLATILITY')]
pv = [float(x) for x in re.findall(r'hz-v">([\d.]+)<', seg)]
pw = [float(x) for x in re.findall(r'hz-t"><i style="width:([\d.]+)%', seg)]
mv = sum((E['regions'][k]['scores'] for k in ('Asia / EM','United States','Europe')), [])
mw = sum((E['regions'][k]['fills']  for k in ('Asia / EM','United States','Europe')), [])
ck('region scores', pv == mv, pv, mv)
ck('region fills',  pw == mw, pw, mw)
for k, v in E['regions'].items():
    row = re.search(r'<td>%s</td>((?:<td class="n">[\d.]+</td>)+)' % re.escape(k), seg)
    ck(f'matrix row {k}', row is not None, bool(row), True)
    if row:
        n = [float(x) for x in re.findall(r'([\d.]+)', row.group(1))]
        ck(f'matrix {k}', n == v['scores'] + [v['mean']], n, v['scores'] + [v['mean']])
# ordering must survive the rescale
for h in range(4):
    ck(f'ordering @h{h}',
       E['regions']['Asia / EM']['scores'][h] > E['regions']['United States']['scores'][h]
       > E['regions']['Europe']['scores'][h], 'order', 'Asia>US>Europe')

# ── donuts ───────────────────────────────────────────────────────────────────
C = 2 * math.pi * 64
for name, segs in E['donuts'].items():
    for tk, seg_, gap, off in segs:
        present(f'donut {name} {tk}',
                f'stroke-dasharray="{seg_:.2f} {gap:.2f}" stroke-dashoffset="{off:.2f}"'
                .replace('-0.00', '0'))
    ck(f'donut {name} closes', abs(sum(s[1] for s in segs) - C) < 0.02,
       round(sum(s[1] for s in segs), 2), round(C, 2))

# ── VIX term structure ───────────────────────────────────────────────────────
for h, lab in ((0.25, '3 months'), (0.5, '6 months'), (1.0, '12 months')):
    present(f'vix sigma {lab}', f"{E['vix']['term'][h]:.2f}%")
    present(f'vix band {lab}',  f"±{1.645*E['vix']['term'][h]:.1f}%")

# ── weight constraints from the brief ────────────────────────────────────────
for name, w in E['weights'].items():
    ck(f'{name} sums to 100', sum(w.values()) == 100, sum(w.values()), 100)
    ck(f'{name} ends in 5 or 0', all(v % 5 == 0 for v in w.values()), w, 'multiples of 5')
    ck(f'{name} holds all four', set(w) == {'QQQ','IEMG','SGOV','BMNR'}, set(w), 'all four')
    ck(f'{name} BMNR capped 5%', w['BMNR'] == 5, w['BMNR'], 5)

# ── claims the prose makes must match the model ──────────────────────────────
for reg in ('calm','normalized'):
    w, st = M.frontier(reg, sgov_min=5)[0]
    ck(f'frontier winner {reg} sums to 100', sum(w.values()) == 100, sum(w.values()), 100)
wc, _ = M.frontier('calm', sgov_min=5)[0]
present('frontier stated in prose',
        f"QQQ {wc['QQQ']} / IEMG {wc['IEMG']} / SGOV {wc['SGOV']} / BMNR {wc['BMNR']}")
present('frontier Sharpe stated', f"{M.frontier('calm', sgov_min=5)[0][1]['sharpe']:.3f}")
# the theorem: a true CAL (risky mix fixed, scaled against cash) is invariant
cal = [r for _, r in M.cal_line()]
ck('CAL invariant', max(cal) - min(cal) < 1e-4, f'{max(cal)-min(cal):.2e}', '<1e-4')
present('CAL ratio stated', f'{cal[0]:.4f}')
# the illustration only approximates it, and the page must not claim otherwise
ill = [r for *_, r in M.cash_line()]
ck('illustration drifts', max(ill) - min(ill) > 1e-4, f'{max(ill)-min(ill):.2e}', '>1e-4')

# ── the frontier chart is generated, so the page must carry it verbatim ───────
present('frontier svg matches model', M.frontier_svg())
eff, _ = M.efficient()
present('efficient count stated', f'{len(eff)} allocations are efficient')
present('frontier local slope', f"{M.fr_slope():.2f} points of CAGR")

# ── calibration: every figure in "How much to trust this" ────────────────────
O, B = M.PORTFOLIOS['optimized'], M.PORTFOLIOS['baseline']
cal = M.calibration(B, O)
sep, _ = M.separable()
for reg in ('calm', 'normalized'):
    se = M.se_level('optimized', reg); c = M.stats(O, reg)['cagr_d']
    present(f'SE stated {reg}', f'±{se:.2f}')
    present(f'68% band {reg}', f'{c-se:.1f} to {c+se:.1f}')
    present(f'95% band {reg}', f'\u2212{abs(c-1.96*se):.1f} to {c+1.96*se:.1f}')
    z = lambda x: 0.5*(1+math.erf(((x-c)/se)/math.sqrt(2)))*100
    col = 2 if reg == 'calm' else 3
    for lab, val in (('P(CAGR &lt; 0)', z(0)), ('P(&lt; T-bills)', z(M.A['SGOV']['net']))):
        row = re.search(rf'<td>{re.escape(lab)}</td>((?:<td class="n">[^<]*</td>)+)', html)
        cells = re.findall(r'<td class="n">([^<]*)</td>', row.group(1)) if row else []
        ck(f'{lab} {reg}', len(cells) >= col - 1 and cells[col-2] == f'{val:.1f}%',
           cells[col-2] if len(cells) >= col - 1 else None, f'{val:.1f}%')
present('separable count stated', f'at 95% over ten years is <b>{sep}</b>')
present('information ratio stated', f"information ratio of {cal['ir']:.2f}")
present('z at ten years stated', f"z = {cal['z']:.2f}")
present('years to prove stated', f"<b>{cal['years95']:.0f} years</b>")
present('years vs T-bills stated',
        f"<b>{(1.96/M.stats(O,'calm')['sharpe'])**2:.0f}</b>")
present('tracking sigma stated', f"just {cal['te']:.2f}%/yr")
present('tracking SE stated', f"±{cal['se']:.2f} pts")
present('ranking probability stated', f"{cal['p']*100:.0f}% chance the baseline ends ahead")
best = max((M.calibration(w, O) | {'w': w} for w in M.admissible() if M.tracking(w, O) > 1e-9),
           key=lambda d: d['ir'])
present('most separable alternative',
        f"QQQ {best['w']['QQQ']} / IEMG {best['w']['IEMG']} / SGOV {best['w']['SGOV']} "
        f"/ BMNR {best['w']['BMNR']} — would still need {best['years95']:.0f}")
ck('ranking is likelier than a coin flip', cal['p'] > 0.5, cal['p'], '>0.5')
ck('comparison SE beats level SE', cal['se'] < M.se_level('optimized'),
   cal['se'], f"< {M.se_level('optimized'):.2f}")
ck('nothing is separable inside the horizon', sep == 0, sep, 0)

# ── the sensitivity table is computed, so every cell must match ──────────────
_rows, _o0, _g0 = M.sensitivity()
for r in _rows:
    sign = lambda x, p: ('\u2212' if x < 0 else '+') + f'{abs(x):.{p}f}'
    present(f"sens row {r['label']}",
            f'<td>{r["label"]}</td><td class="n">{r["now"]}</td>'
            f'<td class="n">{sign(r["d_cagr"], 2)}</td><td class="n">{sign(r["d_gap"], 3)}</td>')
ck('sensitivity rows ordered by effect',
   _rows == sorted(_rows, key=lambda r: -abs(r['d_cagr'])), 'unsorted', 'descending')
ck('QQQ earnings growth is the most sensitive input',
   _rows[0]['label'] == 'QQQ earnings growth', _rows[0]['label'], 'QQQ earnings growth')
ck('BMNR cannot move the choice',
   all(abs(r['d_gap']) < 5e-4 for r in _rows if r['label'].startswith('BMNR')),
   [r['d_gap'] for r in _rows if r['label'].startswith('BMNR')], 'zero')
present('most sensitive input named', f"{_rows[0]['now']} earnings-growth assumption")
ck('baseline sensitivity run reproduces the model',
   abs(_o0 - M.stats(M.PORTFOLIOS['optimized'], 'calm')['cagr']) < 1e-9, _o0, 'same CAGR')

# ── the outside check: published forecasts, and the scenario they imply ──────
for _name, _d in M.INSTITUTIONAL.items():
    present(f'house row {_name}',
            f'<td>{_name}</td><td class="n">{_d["us"]:.1f}%</td><td class="n">{_d["em"]:.1f}%</td>')
_jpm  = M.scenario(M.alt_nets())
_mine = M.scenario({k: M.A[k]['net'] for k in M.A})
ck('scenario reproduces the model on the model\'s own inputs',
   abs(_mine['rows']['optimized']['cagr'] - M.stats(M.PORTFOLIOS['optimized'], 'calm')['cagr']) < 1e-9,
   _mine['rows']['optimized']['cagr'], 'same CAGR')
for _k, _r in (('baseline', 'Baseline CAGR'), ('optimized', 'Optimized CAGR')):
    present(f'scenario row {_r}',
            f'<td>{_r}</td><td class="n">{_mine["rows"][_k]["cagr"]:.2f}%</td>'
            f'<td class="n">{_jpm["rows"][_k]["cagr"]:.2f}%</td>')
present('scenario gap row',
        f'<td class="n">+{_mine["gap"]:.2f}</td><td class="n">+{_jpm["gap"]:.2f}</td>')
present('scenario best-Sharpe row',
        f'<td class="n">{_mine["best_w"]["QQQ"]}/{_mine["best_w"]["IEMG"]}/{_mine["best_w"]["SGOV"]}/'
        f'{_mine["best_w"]["BMNR"]}</td><td class="n">{_jpm["best_w"]["QQQ"]}/{_jpm["best_w"]["IEMG"]}/'
        f'{_jpm["best_w"]["SGOV"]}/{_jpm["best_w"]["BMNR"]}</td>')
present('scenario efficient counts',
        f'<td class="n">{_mine["n_eff"]}</td><td class="n">{_jpm["n_eff"]}</td>')
present('this page\'s own row in the house table',
        f'<td>This page</td><td class="n">{M.A["QQQ"]["gross"]:.2f}%</td>'
        f'<td class="n">{M.A["IEMG"]["gross"]:.2f}%</td>')
present('gap to J.P. Morgan stated',
        f'{M.A["QQQ"]["gross"] - M.INSTITUTIONAL[M.ALT_SOURCE]["us"]:.1f} points above')
# the disagreement the page reports must actually be there
# count the houses rather than assert a number: an earlier revision wrote this
# check to exclude the one house that disagreed, which made it prove the claim
# instead of testing it, and the page said "all four" when the answer was three.
_above = [n for n, d in M.INSTITUTIONAL.items() if d['em'] > d['us']]
ck('the page states the right number of dissenting houses',
   f'{len(_above)} of the {len(M.INSTITUTIONAL)} rank emerging markets' in html,
   len(_above), 'stated on the page')
ck('at least one house is quoted on each side',
   0 < len(_above) < len(M.INSTITUTIONAL),
   {n: (d['us'], d['em']) for n, d in M.INSTITUTIONAL.items()}, 'a real split')
ck('this page ranks them the other way',
   M.A['QQQ']['net'] > M.A['IEMG']['net'], (M.A['QQQ']['net'], M.A['IEMG']['net']), 'QQQ ahead')
ck('the alternative inputs really do flip the best book',
   _jpm['best_w']['IEMG'] > _mine['best_w']['IEMG'],
   (_mine['best_w'], _jpm['best_w']), 'EM weight rises')
ck('neither book is efficient under the alternative inputs',
   not any(_jpm['on_frontier'].values()), _jpm['on_frontier'], 'both False')
ck('the baseline still leads under both input sets',
   _mine['gap'] > 0 and _jpm['gap'] > 0, (_mine['gap'], _jpm['gap']), 'both positive')

# ── the CAL must follow the book the page recommends, not a stale mix ────────
ck('CAL uses the recommended risky mix',
   M.risky_mix() == tuple(M.PORTFOLIOS['optimized'][k] for k in ('QQQ','IEMG','BMNR')),
   M.risky_mix(), 'optimized QQQ/IEMG/BMNR')
_ill = M.cash_line()
ck('illustration holds IEMG at the recommended weight',
   all(w['IEMG'] == M.PORTFOLIOS['optimized']['IEMG'] for w, *_ in _ill),
   sorted({w['IEMG'] for w, *_ in _ill}), M.PORTFOLIOS['optimized']['IEMG'])
ck('illustration brackets the recommendation',
   any(w == M.PORTFOLIOS['optimized'] for w, *_ in _ill), 'absent', 'present')
present('cash-line drift stated',
        f"drifts from {[x for *_, x in _ill][0]:.3f} to {[x for *_, x in _ill][-1]:.3f}")

# ── dividend yields are trailing distributions, and the page must show them ──
for k in ('QQQ', 'IEMG'):
    present(f'{k} dividend yield shown', f'<span class="v">{M.OBS[k]["div"]:.2f}%</span>')
    sv = (M.A[k]['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol'][k]
    ck(f'{k} return-per-vol is positive', sv > 0, sv, '>0')
_q = (M.A['QQQ']['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol']['QQQ']
_i = (M.A['IEMG']['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol']['IEMG']
present('QQQ return-per-vol stated', f'{_q:.2f} per unit of volatility against {_i:.2f}')
ck('prose ranks the sleeves the way the model does', _q > _i, (_q, _i), 'QQQ ahead')

# ── the frontier chart must fit inside the axes it draws ─────────────────────
_eff, _ = M.efficient()
ck('frontier fits its own axes',
   all(M.FR_X[0] <= d <= M.FR_X[1] and M.FR_Y[0] <= c <= M.FR_Y[1] for d, c, _w in _eff),
   (min(d for d, *_ in _eff), max(d for d, *_ in _eff),
    min(c for _, c, _w in _eff), max(c for _, c, _w in _eff)), (M.FR_X[:2], M.FR_Y[:2]))

# ── BMNR is built from its filing, not from assumptions ──────────────────────
b = M.A['BMNR']
present('BMNR staking contribution', f"+{b['stake']:.2f}% staking")
present('BMNR mNAV normalisation', f"\u2212{abs(b['mnav']):.2f}% mNAV")
ck('BMNR components sum to net',
   abs(b['eth'] + b['stake'] + b['mnav'] + b['drag'] - b['net']) < 0.005, b, 'sums')
ck('BMNR staked share matches token counts',
   abs(M.BMNR['stake_share'] - 5_067_309/5_929_198) < 0.0005,
   M.BMNR['stake_share'], round(5_067_309/5_929_198, 4))

# ── the two correction counts on the page must agree with each other ─────────
_log  = html[html.index('Verification log'):]
_card = _log[_log.index('<div class="card">'):_log.index('<p class="sl-role"')]
_rows = _card.count('<div class="kv">')
_words = dict(zip(range(70, 100),
    'Seventy Seventy-one Seventy-two Seventy-three Seventy-four Seventy-five Seventy-six '
    'Seventy-seven Seventy-eight Seventy-nine Eighty Eighty-one Eighty-two Eighty-three '
    'Eighty-four Eighty-five Eighty-six Eighty-seven Eighty-eight Eighty-nine Ninety '
    'Ninety-one Ninety-two Ninety-three Ninety-four Ninety-five Ninety-six Ninety-seven '
    'Ninety-eight Ninety-nine'.split()))
ck('log count in words matches rows', f'{_words.get(_rows, "?")} corrections recorded' in html,
   _rows, _words.get(_rows))
ck('calibration card quotes the same count',
   f'<span class="k">Corrections that changed a number</span><span class="v"><b>{_rows}</b></span>' in html,
   _rows, 'same figure in both places')

# ── values from superseded revisions must not survive outside the self-audit ──
# Everything from 'How much to trust this' on is where the page quotes its own
# superseded figures deliberately, so the blacklist stops there.
body_only = html[:html.index('How much to trust this')]
ck('no exact-invariance claim', 'identical return-per-drawdown ratio' not in body_only,
   'claim present outside log', 'absent')
for stale, why in (('16.00%','old optimized sigma'), ('27.2%','old optimized maxDD'),
                   ('7.32%','old optimized CAGR'),  ('36.9%','old normalized maxDD'),('20.39%','pre-fix sigma'),
                   ('$20,052','pre-fix baseline terminal'),
                   ('4.8/10','pre-rescale gauge'),
                   ('VIX 15.30','pre-CPI VIX'),      ('Brent $100','pre-settle Brent'),
                   ('0.112%','wrong optimized fee'), ('24.5%','pre-fix BMNR risk contrib'),
                   ('44.3%','pre-fix QQQ risk contrib'), ('85.9%','pre-filing staked share'),
                   ('0.1296','pre-fix CAL ratio'),   ('86 allocations','pre-fix efficient count'),
                   ('75%-risk-asset','wrong risk-asset share'),
                   ('2.58% staking','pre-filing staking yield')):
    ck(f'no superseded value ({why})', stale not in body_only, stale, 'absent outside log')

# ── no stale scale or revision markers ───────────────────────────────────────
for bad, why in (('/10</small>', 'gauge must be /5'),):
    ck(f'no stale: {why}', bad not in html, bad, 'absent')
# exactly one revision stamp, and it is the newest one
revs = re.findall(r'<span>Rev\. (\d+) ·', html)
ck('single revision stamp', len(revs) == 1, revs, 'one')
ck('revision stamp is current', revs == [str(M.REVISION)], revs, [str(M.REVISION)])

# ── last check: the page must state this file's own assertion count ──────────
ck('assertion count on page is current', f'{checks + 1} assertions' in html,
   re.search(r'(\d+) assertions', html).group(1), checks + 1)

print(f'{checks} checks, {len(fails)} failed')
for f in fails: print('  FAIL', f)
sys.exit(1 if fails else 0)
