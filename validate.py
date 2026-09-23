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
# Checked cell by cell. This used to be bare present() on div/eps/gross/net only;
# the valuation-change row was never checked at all, and it carried last week's
# +0.22/+0.42 after QQQ's multiple re-priced to a de-rating. It is the row a
# valuation model is most likely to move.
def _row(label):
    m = re.search(rf'<tr[^>]*><td>{re.escape(label)}</td>((?:<td class="n[^"]*">[^<]*</td>)+)</tr>', html)
    return re.findall(r'<td class="n[^"]*">([^<]*)</td>', m.group(1)) if m else None
def _fmt(x, signed=True):
    if abs(x) < 5e-3: return '—'
    s = f'{abs(x):.2f}'
    return (('+' if x > 0 else '\u2212') + s) if signed else s
for label, fld, signed in (('Dividend yield','div',True), ('Earnings growth','eps',True),
                           ('Valuation change','val',True), ('Currency drag','fx',True),
                           ('Gross CAGR','gross',False), ('Net CAGR','net',False)):
    want = [_fmt(E['components'][k][fld], signed) for k in ('QQQ','IEMG')]
    got  = _row(label)
    ck(f'building block row: {label}', got == want, got, want)
for k in ('QQQ','IEMG'):
    c = E['components'][k]
    ck(f'{k} valuation term is the annualised re-rating to its own 10-yr mean',
       abs(c['val'] - M.r2h(M.annualised(M.OBS[k]['fwd_pe'], M.OBS[k]['pe_end']))) < 1e-9,
       c['val'], M.OBS[k]['fwd_pe'])

# ── price-linked inputs: yield and multiple must come from the same price ────
for k, pr in M.PRICES.items():
    ck(f'{k} dividend yield derives from its price',
       abs(M.OBS[k]['div'] - M.r2h(pr['ttm_div'] / pr['px'] * 100)) < 1e-9,
       M.OBS[k]['div'], round(pr['ttm_div'] / pr['px'] * 100, 3))
    ck(f'{k} forward P/E derives from the same price',
       abs(M.OBS[k]['fwd_pe'] - pr['basis_fwd'] * pr['px'] / pr['basis_px']) < 5e-3,
       M.OBS[k]['fwd_pe'], round(pr['basis_fwd'] * pr['px'] / pr['basis_px'], 3))
    present(f'{k} forward P/E shown on slide',
            f'<span class="k">Forward P/E</span><span class="v">{M.OBS[k]["fwd_pe"]:.1f}×</span>')
present('QQQ price shown with its date',
        f'Price ({int(M.PRICES["QQQ"]["px_asof"][8:])} Sep)</span><span class="v">${M.PRICES["QQQ"]["px"]:.2f}')

# ── the sleeve slides must carry the same weights as the donuts ──────────────
_slides = re.findall(r'<article class="slide">(.*?)</article>', html, re.S)
_seen = {}
for _art in _slides:
    _tk = re.search(r'<div class="sl-tick">(\w+)</div>', _art).group(1)
    _m = re.search(r'<div class="k">Baseline</div><div class="v">(\d+)%</div></div>'
                   r'<div><div class="k">Optimized</div><div class="v"[^>]*>(\d+)%</div>', _art)
    _b, _o = (int(_m.group(1)), int(_m.group(2))) if _m else (None, None)
    _seen[_tk] = (_b, _o)
    ck(f'{_tk} slide weights match the portfolios',
       (_b, _o) == (M.PORTFOLIOS['baseline'][_tk], M.PORTFOLIOS['optimized'][_tk]),
       (_b, _o), (M.PORTFOLIOS['baseline'][_tk], M.PORTFOLIOS['optimized'][_tk]))
for _col, _i in (('baseline', 0), ('optimized', 1)):
    _tot = sum(v[_i] for v in _seen.values() if v[_i] is not None)
    ck(f'slide weights sum to 100: {_col}', _tot == 100, _tot, 100)

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
# the theorem is exact only with riskless cash; SGOV's own volatility leaves a
# residual the page states. Earlier revisions called it "machine precision",
# which was never true of this model.
_cal0 = [r for _, r in M.cal_line(cash_vol=0.0)]
ck('CAL exact with riskless cash', max(_cal0) - min(_cal0) < 1e-12,
   f'{max(_cal0)-min(_cal0):.2e}', '<1e-12')
_m, _e = f'{max(cal) - min(cal):.0e}'.split('e-')
present('CAL residual stated', f'{_m}&thinsp;×&thinsp;10<sup>−{int(_e)}</sup> along the line')
present('CAL residual attributed to SGOV vol',
        f"its {M.REGIME['normalized']['vol']['SGOV']}% volatility leaves a residual")
# the illustration only approximates it, and the page must not claim otherwise
ill = [r for *_, r in M.cash_line()]
ck('illustration drifts', max(ill) - min(ill) > 1e-4, f'{max(ill)-min(ill):.2e}', '>1e-4')

# ── the frontier chart is generated, so the page must carry it verbatim ───────
_on = {n: any(w == M.PORTFOLIOS[n] for _, _, w in M.efficient()[0]) for n in M.PORTFOLIOS}
ck('frontier call-out names the right books as efficient',
   ('Both books now sit on the frontier' in html) == all(_on.values()) and
   ('the baseline, by a hair, is not' in html) == (_on['optimized'] and not _on['baseline']),
   _on, 'prose matches')
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
    sign = lambda x, p: ('\u2212' if x < 0 else '+') + f'{M.r2h(abs(x), p):.{p}f}'
    present(f"sens row {r['label']}",
            f'<td>{r["label"]}</td><td class="n">{r["now"]}</td>'
            f'<td class="n">{sign(r["d_cagr"], 2)}</td><td class="n">{sign(r["d_gap"], 3)}</td>')
_gaps = sorted((abs(r['d_gap']) for r in _rows), reverse=True)
ck('top input doubles every other effect on the gap', abs(_gaps[0] / _gaps[1] - 2) < 0.05 and
   'double any other input&#8217;s effect on the gap' in html, round(_gaps[0] / _gaps[1], 2), 2.0)
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
# J.P. Morgan's EM volatility is a fixed long-run estimate; this page's normalised
# figure moves inversely with spot VIX, so which is larger has flipped three times
# in a fortnight. The check names the relation rather than a side, so the prose has
# to be re-read whenever the relation changes.
_emvol = 20.9   # J.P. Morgan LTCMA 2026 EM equity volatility
_lo, _hi = M.REGIME['calm']['vol']['IEMG'], M.REGIME['normalized']['vol']['IEMG']
_rel = ('exceeds <em>both</em>' if _emvol > max(_lo, _hi)
        else 'below <em>both</em>' if _emvol < min(_lo, _hi)
        else 'falls <em>between</em>')
ck('EM volatility comparison states the right relation', _rel in html,
   (round(_lo, 1), round(_hi, 1), _emvol), _rel)
present('normalized EM vol in the house comparison',
        f"18.0% calm and {M.REGIME['normalized']['vol']['IEMG']:.1f}% normalised")
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

# ── a candidate sleeve must go through the same maths as the four ───────────
_ctx = M.base_ctx()
for _p, _w in M.PORTFOLIOS.items():
    for _r in M.REGIME:
        _a, _b = M.stats(_w, _r), M.stats_n(_w, _r, _ctx)
        ck(f'stats_n reproduces stats: {_p}/{_r}',
           all(abs(_a[k] - _b[k]) < 1e-12 for k in ('cagr','fee','vol','dd','naive','sharpe')),
           {k: round(_b[k], 6) for k in ('cagr','vol','sharpe')}, 'identical')
        ck(f'stats_n risk contribs match: {_p}/{_r}',
           all(abs(_a['rc'][k] - _b['rc'][k]) < 1e-9 for k in _w), _b['rc'], _a['rc'])
ck('stress lift matches the published regimes',
   abs(M.stress_lift() - 0.17) < 5e-3, round(M.stress_lift(), 4), 0.17)
# the bug this guards against: a candidate keeping calm correlations while the
# rest of the book is stressed
_cand = M.with_candidate('TEST', 8.0, 0.30, 22.0, 50.0,
                         {('QQQ','TEST'): 0.50, ('IEMG','TEST'): 0.45, ('BMNR','TEST'): 0.30})
for _pair, _c in ((('QQQ','TEST'), 0.50), (('IEMG','TEST'), 0.45), (('BMNR','TEST'), 0.30)):
    ck(f'candidate {_pair[0]}.{_pair[1]} is stressed in the normalized regime',
       _cand['regime']['normalized']['rho'][_pair] > _cand['regime']['calm']['rho'][_pair],
       (_cand['regime']['calm']['rho'][_pair], _cand['regime']['normalized']['rho'][_pair]),
       'normalized above calm')
ck('candidate volatility is stressed by the same uplift',
   abs(_cand['regime']['normalized']['vol']['TEST'] - 22.0 * M.UPLIFT) < 1e-9,
   _cand['regime']['normalized']['vol']['TEST'], 22.0 * M.UPLIFT)
ck('candidate leaves the four existing sleeves untouched',
   all(_cand['regime'][r]['vol'][k] == M.REGIME[r]['vol'][k]
       for r in M.REGIME for k in M.DD),
   'a sleeve moved', 'unchanged')

# ── the VIX series is data, not a typed number ───────────────────────────────
ck('VIX_SPOT comes from the series', M.VIX_SPOT == M.VIX_SERIES[-1][1],
   M.VIX_SPOT, M.VIX_SERIES[-1])
ck('VIX series is dated in order',
   [d for d, _ in M.VIX_SERIES] == sorted(d for d, _ in M.VIX_SERIES),
   [d for d, _ in M.VIX_SERIES], 'ascending')
ck('VIX series has no duplicate dates',
   len({d for d, _ in M.VIX_SERIES}) == len(M.VIX_SERIES), M.VIX_SERIES, 'unique dates')
for _a, _b in zip(M.VIX_SERIES, M.VIX_SERIES[1:]):
    ck(f'VIX move {_a[0]} to {_b[0]} is plausible', abs(_b[1] - _a[1]) / _a[1] < 0.25,
       f'{(_b[1]-_a[1])/_a[1]*100:+.1f}%', 'under 25% in one session')
present('VIX series printed on the page',
        ', '.join(f'{x:g}' for _, x in M.VIX_SERIES))
ck('page is stamped with the series as-of date',
   f"As of {int(M.VIX_ASOF[8:])} Sep {M.VIX_ASOF[:4]}" in html,
   re.search(r'As of ([^<]+)', html).group(1), M.VIX_ASOF)

# ── the sensitivity spec is derived, so its labels cannot go stale ───────────
for _lab, _now, _key, _val in M.SENS:
    _fld = _key.split('_', 1)[1]
    _cur = (M.OBS[_key.split('_')[0]][_fld] if _key.split('_')[0] in M.OBS
            else M.BMNR[_fld] if _key.startswith('BMNR') else M.SGOV_GROSS)
    ck(f'sens step is one unit: {_lab}', abs(abs(_val - _cur) - 1.0) < 1e-9,
       abs(_val - _cur), 1.0)
ck('SGOV sensitivity row shows the live assumption',
   f'{M.SGOV_GROSS:g}%' in [n for _l, n, _k, _v in M.SENS if _l == 'SGOV gross yield'][0],
   [n for _l, n, _k, _v in M.SENS if _l == 'SGOV gross yield'][0], f'{M.SGOV_GROSS:g}%')

# ── the cash sleeve must follow policy, not a superseded level ───────────────
present('policy range on the page', 'Fed 3.75–4.00%')
ck('SGOV assumption equals the policy midpoint', abs(M.SGOV_GROSS - 3.875) < 1e-9,
   M.SGOV_GROSS, 3.875)
ck('SGOV is still the lowest-return sleeve',
   M.A['SGOV']['net'] == min(a['net'] for a in M.A.values()),
   M.A['SGOV']['net'], 'lowest')

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
# Stated to three decimals because at two the sleeves now print as 0.27 and 0.27.
# The check names the relation the prose must use rather than assuming a winner:
# a hardcoded 'QQQ ahead' here was true for three passes and then was not.
_q = (M.A['QQQ']['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol']['QQQ']
_i = (M.A['IEMG']['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol']['IEMG']
present('QQQ return-per-vol stated', f'{_q:.3f} against {_i:.3f}')
_tie = abs(_q - _i) < 0.01
_word = 'level' if _tie else ('QQQ ahead' if _q > _i else 'IEMG ahead')
ck('prose states the sleeve relation the model implies',
   (_tie and 'are now <b>level</b>' in html) or
   (not _tie and ('QQQ now leads on both measures' in html) == (_q > _i)),
   (round(_q, 4), round(_i, 4)), _word)
ck('raw-return ranking stated correctly',
   ('It still trails QQQ on raw return' in html) == (M.A['QQQ']['net'] > M.A['IEMG']['net']),
   (M.A['QQQ']['net'], M.A['IEMG']['net']), 'QQQ ahead on raw return')

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
_STAKED, _HELD = 5_067_309, 5_983_940          # 21 Sep 2026 holdings release
ck('BMNR staked share matches token counts',
   abs(M.BMNR['stake_share'] - _STAKED/_HELD) < 0.0005,
   M.BMNR['stake_share'], round(_STAKED/_HELD, 4))
present('BMNR treasury count on slide', f'<span class="v">{_HELD:,}</span>')

# ── portfolio VaR table: every cell, both books, from the model ──────────────
# The baseline's calm VaR sat at a superseded CAGR's values for a revision
# because nothing but monotonicity was checked.
def _v1(x): return '−' + str(M.Decimal(repr(abs(x))).quantize(M.Decimal('0.1'), rounding=M.ROUND_HALF_UP)) + '%'
_bc, _oc = (M.stats(M.PORTFOLIOS[n], 'calm') for n in ('baseline', 'optimized'))
for _lab, _h in (('3 months', 0.25), ('6 months', 0.5), ('12 months', 1.0)):
    present(f'VaR table row {_lab}',
            f'<tr><td>{_lab}</td><td class="n">{_bc["vol"]*_h**0.5:.2f}%</td><td class="n neg">{_v1(_bc["var"][_h])}</td>'
            f'<td class="n">{_oc["vol"]*_h**0.5:.2f}%</td><td class="n neg">{_v1(_oc["var"][_h])}</td></tr>')
_bn, _on_ = (M.stats(M.PORTFOLIOS[n], 'normalized') for n in ('baseline', 'optimized'))
present('VaR table 12 mo normalized row',
        f'<tr><td>12 mo, normalized</td><td class="n">{_bn["vol"]:.2f}%</td><td class="n neg">{_v1(_bn["var"][1.0])}</td>'
        f'<td class="n">{_on_["vol"]:.2f}%</td><td class="n neg">{_v1(_on_["var"][1.0])}</td></tr>')

# ── risk-contribution card, scoped: a page-wide search matched BMNR's figure in
# another block and let a stale 23.8% stand here ─────────────────────────────
_rcc = html[html.index('<h3>Risk contribution</h3>'):html.index('<h3>Ten-year regime view</h3>')]
for _k in ('BMNR', 'QQQ', 'IEMG'):
    _x = _on_['rc'][_k]
    ck(f'risk card {_k} figure', f'<div class="drv-s"' in _rcc and
       re.search(r'%s <span class="wt">%d%% weight</span></div><div class="drv-s"[^>]*>%.1f%%</div>\s*'
                 r'<div class="drv-bar"><i style="width:%.1f%%;' % (_k, M.PORTFOLIOS['optimized'][_k], _x, _x), _rcc)
       is not None, _k, f'{_x:.1f}%')
_rat = _on_['rc']['BMNR'] / M.PORTFOLIOS['optimized']['BMNR']
ck('BMNR risk share described correctly',
   ('more than a quarter' in _rcc) == (_on_['rc']['BMNR'] > 25) and
   ('almost a quarter' in _rcc) == (22.5 <= _on_['rc']['BMNR'] < 25), round(_on_['rc']['BMNR'], 2), 'wording matches')
ck('BMNR ratio range includes today', f'<b>{_rat:.1f}× risk-to-weight ratio</b>' in _rcc and
   re.search(r'ranged from ([\d.]+)× to 5\.5×', _rcc) is not None and
   float(re.search(r'ranged from ([\d.]+)× to 5\.5×', _rcc).group(1)) <= round(_rat, 1),
   (re.search(r'ranged from ([\d.]+)×', _rcc) or [None, 'absent'])[1], f'<= {_rat:.1f}')

# ── VIX narrative: every derived figure from the stored series ───────────────
_ser = dict(M.VIX_SERIES); _dd = _ser['2026-09-16']; _lo = M.VIX_2026['low']
def _q(x, p='1'): return str(M.Decimal(repr(x)).quantize(M.Decimal(p), rounding=M.ROUND_HALF_UP))
present('VIX day change', f'down {_q(abs(M.VIX_SPOT/M.VIX_SERIES[-2][1]-1)*100, "0.1")}%, and '
        f'{_q((1-M.VIX_SPOT/_dd)*100)}% below its {_dd:.2f} close on decision day')
present('VIX round trip', f'up {_q(_dd-_lo, "0.01")} points to {_dd:.2f} on decision day, then back to within {_q(M.VIX_SPOT-_lo, "0.01")} of the low')
ck('spot is the lowest close on file', M.VIX_SPOT == min(v for _, v in M.VIX_SERIES), M.VIX_SPOT, 'series min')
present('decision-day discount', f'closed to {_q((1-_dd/M.VIX_MEAN)*100, "0.1")}% on decision day')
ck('VIX low date matches its stated date', M.VIX_2026['low_date'] == '2026-08-28' and '(28 August)' in html,
   M.VIX_2026['low_date'], '28 August on page')

# ── forward multiples quoted in prose track the price-linked model ───────────
_fq, _fi = M.OBS['QQQ']['fwd_pe'], M.OBS['IEMG']['fwd_pe']
_b0 = 1 - M.PRICES['IEMG']['basis_fwd'] / M.PRICES['QQQ']['basis_fwd']
present('valuation driver multiples', f'The Nasdaq-100 trades at {_fq:.1f}× forward earnings against emerging markets at '
        f'{_fi:.1f}× — a {_q((1-_fi/_fq)*100)}% discount, wider than the {_q(_b0*100)}% at the 11 September basis')
present('valuation driver VIX', f'is back to <b>{M.VIX_SPOT:.2f}</b> — {_q(M.VIX_SPOT-_lo, "0.01")} above its 2026 low')
present('IEMG transmission multiples', f'at {_fi:.1f}× forward against the Nasdaq-100&#8217;s {_fq:.1f}×')
present('Asia note multiple', f'Equities trade at {_fi:.1f}× forward — just below EM&#8217;s own 20-year average of 11.7×')
ck('Asia note relation to 20-yr mean', _fi < 11.7, _fi, '< 11.7')
present('US note multiple', f'the richest multiple in the panel at {_fq:.1f}× forward')

# ── the portfolio call-out pairs one book's calm and normalised drawdowns ────
# It had quoted the baseline's normalised figure against the optimized book's
# calm one, under the optimized book's risk-asset share.
_B, _O = M.PORTFOLIOS['baseline'], M.PORTFOLIOS['optimized']
present('trade call-out pairs the same book',
        f"the baseline — {100-_B['SGOV']}% in risk assets — near −{_q(M.stats(_B,'normalized')['dd'])}%, "
        f"not −{_q(M.stats(_B,'calm')['dd'])}%. Giving up {_q(M.stats(_B,'calm')['cagr_d']-M.stats(_O,'calm')['cagr_d'], '0.01')} "
        f"points of CAGR to bring that to −{_q(M.stats(_O,'normalized')['dd'], '0.1')}% is the trade")
ck('vol warnbox pairs the optimized book', f"A {100-_O['SGOV']}%-risk-asset book that looks like a −{_q(M.stats(_O,'calm')['dd'])}% drawdown "
   f"at today&#8217;s volatility is a <b>−{_q(M.stats(_O,'normalized')['dd'])}% drawdown book</b>" in html, '', 'present')

# ── rationale, house comparison and triggers: derived, not typed ────────────
# These sections sit after 'How much to trust this', so the frozen-prose checks
# below scan everything up to the verification log, not body_only.
_pre_log = html[:html.index('<h3>Verification log</h3>')]
_t = lambda w: M.stats(w, 'calm')['terminal']
present('rationale terminal values',
        f"SGOV&#8217;s ${_t({'QQQ':0,'IEMG':0,'SGOV':100,'BMNR':0}):,.0f} terminal value against "
        f"QQQ&#8217;s ${_t({'QQQ':100,'IEMG':0,'SGOV':0,'BMNR':0}):,.0f} on the same $10,000")
_vals = [v for _, v in M.VIX_SERIES]
_side = [M.REGIME['calm']['vol']['IEMG'] * M.VIX_MEAN / v > 20.9 for v in _vals]
_flips = sum(a != b for a, b in zip(_side, _side[1:]))
present('EM-vol comparison flip count',
        f"flipped {({1:'once',2:'twice',3:'three times',4:'four times'})[_flips]} in the {len(_vals)} sessions on file")
present('VIX range over the series', f"covered {_q(max(_vals)-min(_vals), '0.01')} points in those {len(_vals)} sessions")
_oc2, _on2 = M.stats(_O, 'calm'), M.stats(_O, 'normalized')
present('volatility trigger distance', f"That trigger is now {_q(M.VIX_MEAN-M.VIX_SPOT, '0.01')} points away</b>; a week ago it stood "
        f"{_q(M.VIX_MEAN-_ser['2026-09-16'], '0.01')} away")
present('regime gap on the recommended book', f"the two regimes differ by {_q(_on2['dd']-_oc2['dd'], '0.1')} points of drawdown on the recommended book")
for _bad, _why in (('reversed two passes ago', 'relative pass reference'), ('made two passes ago', 'relative pass reference'),
                   ('Three of them fell this pass', 'relative pass reference'), ('a fortnight ago the baseline sat', 'baseline was efficient through Rev. 18'),
                   ('covered four points in ten sessions', 'series range superseded'), ('flipped three times', 'flip count not supported by the series'),
                   ('That second trigger', 'trigger named before it was introduced'), ('differ by 10.3 points', 'baseline gap quoted for the recommended book'),
                   ('70%-risk-asset book near', 'mismatched drawdown pairing')):
    ck(f'no frozen prose ({_why}: {_bad[:24]})', _bad not in _pre_log, _bad, 'absent outside log')

# ── the EM sleeve against the houses: the wording must match the relation ────
# The page said "bracketed by 7.8% and 8.1%" for a forecast above both, and had
# since the comparison was first written.
_H = M.INSTITUTIONAL
_em, _us = M.A['IEMG']['gross'], M.A['QQQ']['gross']
_tem = max(_H, key=lambda k: _H[k]['em']); _tus = max(_H, key=lambda k: _H[k]['us'])
ck('EM sleeve relation to the houses', _em > _H[_tem]['em'] and 'bracketed by' not in _pre_log,
   _em, f'above {_H[_tem]["em"]}')
present('EM margin over the highest house',
        f"by {M.r2h(_em - _H[_tem]['em'], 1):.1f} points over the highest — {_tem}&#8217;s {_H[_tem]['em']:.1f}% — "
        f"against {M.r2h(_us - _H[_tus]['us'], 1):.1f} on the US sleeve")

# ── every slide: gross minus expense ratio equals the net shown ──────────────
for _k in ('SGOV', 'QQQ', 'IEMG'):
    _sl = html[html.index(f'<div class="sl-tick">{_k}</div>'):]
    _sl = _sl[:_sl.index('</article>')]
    _g = re.search(r'Gross forecast</span><span class="v">([\d.]+)%', _sl)
    ck(f'{_k} slide gross matches model', _g is not None and float(_g.group(1)) == M.r2h(M.A[_k]['gross']),
       _g and _g.group(1), M.r2h(M.A[_k]['gross']))

# ── the fee saving quoted in the rationale is the table's difference ─────────
_fd = M.stats(M.PORTFOLIOS['baseline'],'calm')['fee_drag'] - M.stats(M.PORTFOLIOS['optimized'],'calm')['fee_drag']
present('fee saving in rationale', f'${_q(_fd)} per $10,000 over ten years')

# ── typographic minus in prose: an ASCII hyphen before a figure is a leftover ──
_vis = re.sub(r'<style>.*?</style>|<svg.*?</svg>|<script.*?</script>|<[^>]+>', ' ', html, flags=re.S)
_ascii = re.findall(r'(?<![\w/–-])-\d[\d.]*%', _vis)
ck('no ASCII minus on a signed figure', not _ascii, _ascii[:5], 'none')

# ── the forecast-history card: its last entries are live, its arithmetic checked ──
_hist = (8.18, 9.03, 10.19, 9.96)        # QQQ net at Revs 7, 8, 10, 14 (git history)
present('QQQ net history ends at the live forecast',
        ' → '.join(f'{x:.2f}%' for x in _hist) + f" → <b>{M.A['QQQ']['net']:.2f}%</b>")
present('QQQ dividend history ends at the live yield',
        f"0.65% → 0.42% → <b>{M.OBS['QQQ']['div']:.2f}%</b>")
_mv = max(_hist) - min(_hist)
present('one-week move stated', f'<b>+{_mv:.2f} pts</b>')
_dq = (M.PORTFOLIOS['baseline']['QQQ'] - M.PORTFOLIOS['optimized']['QQQ']) / 100
_cb = M.calibration(M.PORTFOLIOS['baseline'], M.PORTFOLIOS['optimized'])
present('history move translated into the gap',
        f"A {_mv:.2f}-point revision to QQQ&#8217;s forecast moves the gap between the two books by "
        f"{M.r2h(_dq*_mv):.2f} points — "
        f"{M.Decimal(repr(_dq*_mv/_cb['gap']*100)).quantize(M.Decimal('1'), rounding=M.ROUND_HALF_UP)}% of the "
        f"{M.r2h(M.r2h(M.stats(M.PORTFOLIOS['baseline'],'calm')['cagr_d']) - M.r2h(M.stats(M.PORTFOLIOS['optimized'],'calm')['cagr_d'])):.2f}-point gap being ranked")
present('warnbox cites the live tracking error', f"Read that against the ±{_cb['se']:.2f}.")

# ── the two correction counts on the page must agree with each other ─────────
_log  = html[html.index('Verification log'):]
_card = _log[_log.index('<div class="card">'):_log.index('<p class="sl-role"')]
_rows = _card.count('<div class="kv">')
def _in_words(n):
    """Hyphenated British style, as the page writes it: One-hundred-and-fifty-seven."""
    ones = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
    tens = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()
    def u100(k):
        return ones[k] if k < 20 else tens[k // 10 - 2] + ('-' + ones[k % 10] if k % 10 else '')
    w = u100(n) if n < 100 else ones[n // 100] + '-hundred' + ('-and-' + u100(n % 100) if n % 100 else '')
    return w[0].upper() + w[1:]
assert _in_words(99) == 'Ninety-nine' and _in_words(100) == 'One-hundred' and _in_words(140) == 'One-hundred-and-forty'
_words = {n: _in_words(n) for n in range(20, 1000)}
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
ck('no machine-precision claim for the CAL', 'invariant to machine precision' not in body_only,
   'claim present outside log', 'absent')
# prose frozen at an earlier date: each was live on the page until this pass
for _bad, _why in (('yesterday as 16.93', 'relative date three revisions old'),
                   ('low of 14.13 in early September', 'VIX low misdated'),
                   ('heading into a 15–16 September FOMC', 'pre-decision tense'),
                   ('touched 4.818%', '10-year high superseded by 5.04%'),
                   ('a 10-year above 5%', '10-year level superseded'),
                   ('more than a quarter of the risk', 'BMNR share below 25%'),
                   ('complacent at 14.13; it is 3.5 points', 'VIX distance superseded'),
                   ('the widest discount of the month', 'unverifiable superlative')):
    ck(f'no frozen prose ({_why})', _bad not in body_only, _bad, 'absent outside log')
ck('no frozen prose (pre-revision fee saving)',
   '$26 per $10,000' not in html[:html.index('<h3>Verification log</h3>')], '$26 per $10,000', 'absent outside log')
# Each pattern is anchored to the markup it used to live in. A bare percentage is
# not safe here: '24.5%' was blacklisted as an old BMNR risk contribution and then
# collided with a legitimate −24.5% VaR when the VIX moved, failing the build on a
# figure that was correct. The meta-check below stops that recurring.
STALE = (('16.00%','old optimized sigma'), ('27.2%','old optimized maxDD'),
         ('7.32%','old optimized CAGR'),  ('36.9%','old normalized maxDD'),
         ('20.39%','pre-fix sigma'),      ('$20,052','pre-fix baseline terminal'),
         ('4.8/10','pre-rescale gauge'),
         ('VIX 15.30','pre-CPI VIX'),     ('Brent $100','pre-settle Brent'),
         ('0.112%','wrong optimized fee'),
         ('width:24.5%;background:var(--bmnr)','pre-fix BMNR risk contrib'),
         ('width:44.3%;background:var(--qqq)','pre-fix QQQ risk contrib'),
         ('staked</span><span class="v">85.9%','pre-filing staked share'),
         ('0.1296','pre-fix CAL ratio'),  ('86 allocations','pre-fix efficient count'),
         ('75%-risk-asset','wrong risk-asset share'),
         ('2.58% staking','pre-filing staking yield'))
for stale, why in STALE:
    ck(f'no superseded value ({why})', stale not in body_only, stale, 'absent outside log')

# meta-check: a blacklist entry must never match something the model currently emits
_live = set()
for _p, _w in M.PORTFOLIOS.items():
    for _r in M.REGIME:
        _s = M.stats(_w, _r)
        _live |= {f"{_s['vol']:.2f}%", f"−{_s['dd']:.1f}%", f"{_s['cagr_d']:.2f}%",
                  f"−${_s['fee_drag']:,.0f}", f"${_s['terminal']:,.0f}", f"{_s['fee']:.3f}%"}
        _live |= {f"−{abs(_v):.1f}%" for _v in _s['var'].values()}
        _live |= {f"{_v:.1f}%" for _v in _s['rc'].values()}
for _k, _a in M.A.items():
    _live |= {f"{_a['net']:.2f}%", f"{_a['gross']:.2f}%"}
_collide = [(s, w) for s, w in STALE if s in _live]
ck('no blacklist entry collides with a live model figure', not _collide, _collide, 'none')

# ── no stale scale or revision markers ───────────────────────────────────────
for bad, why in (('/10</small>', 'gauge must be /5'),):
    ck(f'no stale: {why}', bad not in html, bad, 'absent')
# exactly one revision stamp, and it is the newest one
revs = re.findall(r'<span>Rev\. (\d+) ·', html)
ck('single revision stamp', len(revs) == 1, revs, 'one')
ck('revision stamp is current', revs == [str(M.REVISION)], revs, [str(M.REVISION)])

# ── the page's claim about the mutation harness must match mutate.py ────────
_mut = open('mutate.py').read()
_n_mut = _mut.count('\n ("')
ck('mutation count on page matches mutate.py',
   f'{_n_mut} deliberate corruptions' in html and f'all {_n_mut} were caught' in html,
   (re.search(r'(\d+) deliberate corruptions', html) or [None, 'absent'])[1],
   _n_mut)

# ── last check: the page must state this file's own assertion count ──────────
ck('assertion count on page is current', f'{checks + 1} assertions' in html,
   re.search(r'(\d+) assertions', html).group(1), checks + 1)

print(f'{checks} checks, {len(fails)} failed')
for f in fails: print('  FAIL', f)
sys.exit(1 if fails else 0)
