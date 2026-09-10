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

# ── values from superseded revisions must not survive outside the change log ──
log_start = html.index('Verification log')
body_only = html[:log_start]
ck('no exact-invariance claim', 'identical return-per-drawdown ratio' not in body_only,
   'claim present outside log', 'absent')
for stale, why in (('16.00%','old optimized sigma'), ('27.2%','old optimized maxDD'),
                   ('7.32%','old optimized CAGR'),  ('36.9%','old normalized maxDD'),('20.39%','pre-fix sigma'),
                   ('44.3%','pre-fix IEMG rc'),     ('$20,052','pre-fix baseline terminal'),
                   ('4.8/10','pre-rescale gauge')):
    ck(f'no superseded value ({why})', stale not in body_only, stale, 'absent outside log')

# ── no stale scale or revision markers ───────────────────────────────────────
for bad, why in (('/10</small>', 'gauge must be /5'),):
    ck(f'no stale: {why}', bad not in html, bad, 'absent')
# exactly one revision stamp, and it is the newest one
revs = re.findall(r'<span>Rev\. (\d+) ·', html)
ck('single revision stamp', len(revs) == 1, revs, 'one')
ck('revision stamp is current', revs == [str(M.REVISION)], revs, [str(M.REVISION)])

print(f'{checks} checks, {len(fails)} failed')
for f in fails: print('  FAIL', f)
sys.exit(1 if fails else 0)
