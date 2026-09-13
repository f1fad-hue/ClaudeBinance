#!/usr/bin/env python3
"""
Single source of truth for every figure in allocation.html.

Run directly for a readable report; `python3 validate.py` checks the published
page against whatever this file computes. If a number changes here, the page is
wrong until it is changed there too.

Market data as of 11 September 2026. Sources are linked on the page itself.
"""
import math, json
from decimal import Decimal, ROUND_HALF_UP

def r2h(x):
    """Round half away from zero, the convention a reader applies by hand.
    Python's round() is banker's rounding, which makes 7.205 -> 7.20."""
    return float(Decimal(repr(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

# ── observed inputs ──────────────────────────────────────────────────────────
# Terminal multiples are each index's OWN 10-year average forward P/E (NDX 22.9x,
# MSCI EM 12.2x). Applying one rule to both keeps the comparison symmetric; an
# earlier revision marked QQQ down to a hand-picked 21.0x, below its own average,
# while marking IEMG up only as far as its average -- an asymmetry that favoured
# the EM sleeve, which is the page's central recommendation.
OBS = {
    'QQQ' : dict(er=0.18, fwd_pe=22.40, div=0.42, eps=9.50, pe_end=22.9,  fx=0.0),
    'IEMG': dict(er=0.09, fwd_pe=11.70, div=2.16, eps=7.50, pe_end=12.2,  fx=-1.50),
}
# div is the trailing-12-month distribution over the 11 Sep 2026 close, not an
# estimate: QQQ $3.03 / $714.88 = 0.42%, IEMG $1.80 over a price near $83 = 2.16%
# (secondary sources spread 2.13-2.16%). QQQ had carried 0.65% and IEMG 2.26%,
# both of which priced the distribution against a lower share price than today's.
_ = {
}
SGOV_GROSS = 3.25          # assumed 10yr average bill yield (spot SEC yield 3.63%)
SGOV_ER    = 0.09
BMNR = dict(eth=9.00, stake_share=0.855, stake_yield=2.61, mnav=1.04, drag=1.40)
# stake_share 5,067,309 / 5,929,198 staked tokens; stake_yield is the company's own
# reported 7-day annualised figure (8-K 8 Sep 2026: $330M on $12.6B staked = 2.62%),
# not an assumption. mnav uses the crypto-only reading (mkt cap $15.39B / ETH $14.79B),
# the conservative one: against total NAV of $15.7B the stock trades at 0.98x.

REVISION = 14                          # bump when publishing; validate.py enforces it
VIX_SPOT, VIX_MEAN = 15.84, 18.9      # 2016-2023 mean of annual closes
DD_MULT = 1.70                        # 10yr E[maxDD] ~= 1.65-1.75 x sigma
RF_LABEL = 'SGOV'

def annualised(p_now, p_end, yrs=10):
    return ((p_end / p_now) ** (1 / yrs) - 1) * 100

# ── forecasts ────────────────────────────────────────────────────────────────
def build():
    """Components are rounded to the precision the page displays, then summed, so
    every figure on the page can be reproduced by hand from the components shown."""
    r2 = r2h
    a = {}
    for k, o in OBS.items():
        val   = r2(annualised(o['fwd_pe'], o['pe_end']))
        gross = r2(o['div'] + o['eps'] + val + o['fx'])
        a[k] = dict(div=o['div'], eps=o['eps'], val=val, fx=o['fx'],
                    gross=gross, er=o['er'], net=r2(gross - o['er']))
    a['SGOV'] = dict(gross=SGOV_GROSS, er=SGOV_ER, net=r2(SGOV_GROSS - SGOV_ER))
    b = BMNR
    mnav  = r2(annualised(b['mnav'], 1.00))
    stake = r2(b['stake_share'] * b['stake_yield'])
    net   = r2(b['eth'] + stake + mnav - b['drag'])
    a['BMNR'] = dict(eth=b['eth'], stake=stake, mnav=mnav, drag=-b['drag'],
                     er=0.0, net=net, gross=net)
    return a

A = build()
DD  = {'QQQ': 40.0, 'IEMG': 39.0, 'SGOV': 0.3, 'BMNR': 85.0}
UPLIFT = VIX_MEAN / VIX_SPOT

REGIME = {
 'calm':       dict(vol={'QQQ':21.0,'IEMG':18.0,'SGOV':0.5,'BMNR':95.0},
                    rho={('QQQ','IEMG'):0.66,('QQQ','BMNR'):0.65,('IEMG','BMNR'):0.55}),
 'normalized': dict(vol={'QQQ':21.0*UPLIFT,'IEMG':18.0*UPLIFT,'SGOV':0.5,'BMNR':95.0*1.15},
                    rho={('QQQ','IEMG'):0.85,('QQQ','BMNR'):0.80,('IEMG','BMNR'):0.72}),
}

PORTFOLIOS = {
 'baseline':  {'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5},
 'optimized': {'QQQ':35,'IEMG':30,'SGOV':30,'BMNR':5},
}

def rho(R, x, y):
    if x == y: return 1.0
    if 'SGOV' in (x, y): return 0.0
    return R.get((x, y), R.get((y, x)))

def stats(w, regime):
    reg = REGIME[regime]; V, R = reg['vol'], reg['rho']; ks = list(w)
    assert sum(w.values()) == 100, f'weights must sum to 100: {w}'
    assert all(v % 5 == 0 for v in w.values()), f'weights must be multiples of 5: {w}'
    cagr = sum(w[k]/100 * A[k]['net'] for k in ks)
    fee  = sum(w[k]/100 * A[k]['er']  for k in ks)
    var  = sum((w[x]/100)*(w[y]/100)*V[x]*V[y]*rho(R,x,y) for x in ks for y in ks)
    vol  = math.sqrt(var)
    mrc  = {x: (w[x]/100)*sum((w[y]/100)*V[x]*V[y]*rho(R,x,y) for y in ks)/vol for x in ks}
    tot  = sum(mrc.values())
    cagr_d = r2h(cagr)                       # what the page shows
    return dict(cagr=cagr, cagr_d=cagr_d, fee=fee, vol=vol, dd=vol*DD_MULT,
                naive=sum(w[k]/100*DD[k] for k in ks),
                rc={k: mrc[k]/tot*100 for k in ks},
                sharpe=(cagr - A[RF_LABEL]['net'])/vol,
                var={h: cagr*h - 1.645*vol*math.sqrt(h) for h in (0.25, 0.5, 1.0)},
                sigma_h={h: vol*math.sqrt(h) for h in (0.25, 0.5, 1.0)},
                terminal=10000*(1+cagr_d/100)**10,
                fee_drag=10000*(1+(cagr_d+fee)/100)**10 - 10000*(1+cagr_d/100)**10)

# ── 1-5 sentiment scales ─────────────────────────────────────────────────────
def to5(x):
    """Map a 1-10 score to 1-5. Both scales floor at 1, so this is not x/2."""
    return 1 + (x - 1) * 4 / 9

def fill(v):
    """Bar/arc fill for a 1-5 score: the floor sits at the left stop, not at zero."""
    return (v - 1) / 4 * 100

DRIVERS = [('Growth momentum',7.0,.25), ('Inflation trajectory',3.0,.15),
           ('Monetary policy',2.0,.20), ('Liquidity & credit',5.5,.15),
           ('Valuation & positioning',4.0,.15), ('Geopolitical risk',2.0,.10)]
REGIONS = {'Asia / EM':[5.5,6.5,7.0,7.5], 'United States':[5.0,5.5,6.5,7.0],
           'Europe':[3.0,3.5,4.0,5.0]}

def gauge():
    assert abs(sum(w for _,_,w in DRIVERS) - 1.0) < 1e-9, 'driver weights must sum to 1'
    composite10 = sum(s*w for _,s,w in DRIVERS)
    composite5  = sum(to5(s)*w for _,s,w in DRIVERS)
    # a linear map commutes with a weighted average - this must hold
    assert abs(composite5 - to5(composite10)) < 1e-9, 'rescale/average must commute'
    return composite10, composite5

def donut(w, r=64):
    C = 2*math.pi*r; off = 0.0; out = []
    for k in ('QQQ','IEMG','SGOV','BMNR'):
        seg = w[k]/100*C
        out.append((k, round(seg,2), round(C-seg,2), round(-off,2)))
        off += seg
    assert abs(off - C) < 1e-9, 'donut segments must close the circle'
    return out, C

def export():
    """Everything the page asserts, as plain data for validate.py."""
    g10, g5 = gauge()
    arc = math.pi*80
    f   = fill(g5)/100
    th  = math.radians(180 - f*180)
    return dict(
        sleeves={k: dict(net=round(v['net'],2), er=v['er'],
                         terminal=round(10000*(1+v['net']/100)**10)) for k,v in A.items()},
        components={k: {c: round(A[k][c],2) for c in ('div','eps','val','fx','gross','er','net')}
                    for k in ('QQQ','IEMG')},
        portfolios={p: {r: stats(w,r) for r in REGIME} for p,w in PORTFOLIOS.items()},
        weights=PORTFOLIOS,
        gauge=dict(score10=round(g10,4), score5=round(g5,4), display=round(g5,1),
                   arc_dash=round(f*arc,1), needle=(round(106+62*math.cos(th),1),
                                                    round(116-62*math.sin(th),1)),
                   drivers=[(n, round(to5(s),1), round(fill(to5(s)),1)) for n,s,_ in DRIVERS]),
        regions={k: dict(scores=[round(to5(x),1) for x in v],
                         fills=[round(fill(to5(x)),1) for x in v],
                         mean=round(sum(to5(x) for x in v)/len(v),1)) for k,v in REGIONS.items()},
        donuts={p: donut(w)[0] for p,w in PORTFOLIOS.items()},
        vix=dict(spot=VIX_SPOT, mean=VIX_MEAN,
                 below=round((VIX_SPOT-VIX_MEAN)/VIX_MEAN*100,1),
                 term={h: round(VIX_SPOT*math.sqrt(h),2) for h in (1/252,0.25,0.5,1.0)}),
        uplift=round(UPLIFT,4), revision=REVISION,
    )

if __name__ == '__main__':
    g10, g5 = gauge()
    print('== SLEEVES (10yr, net of fund fees) ==')
    for k,v in A.items():
        print(f"  {k:<5} gross {v['gross']:>5.2f} - fee {v['er']:.2f} = net {v['net']:>5.2f}%"
              f"   maxDD -{DD[k]:>4.1f}%   $10k -> ${10000*(1+v['net']/100)**10:>8,.0f}")
    print('\n== BUILDING BLOCKS ==')
    for k in ('QQQ','IEMG'):
        c=A[k]; print(f"  {k:<5} div {c['div']:+.2f}  eps {c['eps']:+.2f}  val {c['val']:+.2f}"
                      f"  fx {c['fx']:+.2f}  = gross {c['gross']:.2f}  net {c['net']:.2f}")
    print(f"\n== VOL REGIMES ==  uplift {VIX_MEAN}/{VIX_SPOT} = {UPLIFT:.4f}")
    for r in REGIME:
        print(f"  {r:<11}" + "  ".join(f"{k} {REGIME[r]['vol'][k]:.1f}%" for k in DD))
    for p,w in PORTFOLIOS.items():
        print(f"\n== {p.upper()} {w} ==")
        for r in REGIME:
            s = stats(w,r)
            print(f"  {r:<11} CAGR {s['cagr_d']:.2f}%  fee {s['fee']:.3f}%  sigma {s['vol']:.2f}%"
                  f"  maxDD -{s['dd']:.1f}%  Sharpe {s['sharpe']:.3f}")
            print(f"              3mo s {s['sigma_h'][0.25]:.2f}% VaR {s['var'][0.25]:+.1f}% | "
                  f"6mo s {s['sigma_h'][0.5]:.2f}% VaR {s['var'][0.5]:+.1f}% | "
                  f"12mo s {s['sigma_h'][1.0]:.2f}% VaR {s['var'][1.0]:+.1f}%")
        s = stats(w,'normalized')
        print(f"  naive-stress -{s['naive']:.1f}%   $10k -> ${s['terminal']:,.0f}"
              f"   fee drag ${s['fee_drag']:,.0f}")
        print("  risk contrib (normalized): " + "  ".join(f"{k} {s['rc'][k]:.1f}%" for k in w))
    print(f"\n== GAUGE ==  {g10:.4f}/10 -> {g5:.4f}/5 (displays {g5:.1f}), arc fill {fill(g5):.1f}%")
    for n,s,wt in DRIVERS:
        print(f"  {n:<26} {s:>4.1f}/10 -> {to5(s):.2f}/5  bar {fill(to5(s)):.1f}%  w {wt:.0%}")
    print('\n== REGIONS (1-5) ==')
    for k,v in REGIONS.items():
        n=[to5(x) for x in v]
        print(f"  {k:<14} " + " ".join(f"{x:.1f}" for x in n) + f"   mean {sum(n)/4:.1f}")
    print('\nJSON export OK:', len(json.dumps(export(), default=str)), 'bytes')


# ── claims the page makes that must stay reproducible ────────────────────────
def frontier(regime, bmnr=5, sgov_min=15):
    """Every 5%-increment allocation, ranked by Sharpe. The page states the
    unconstrained winner and then explains why it is rejected."""
    out = []
    for q in range(5, 101, 5):
        for i in range(5, 101, 5):
            s_ = 100 - q - i - bmnr
            if s_ < sgov_min: continue
            w = {'QQQ': q, 'IEMG': i, 'SGOV': s_, 'BMNR': bmnr}
            out.append((w, stats(w, regime)))
    return sorted(out, key=lambda x: -x[1]['sharpe'])

def risky_mix(name='optimized'):
    """The recommended book's risky sleeves, in weight order. Derived, because a
    hardcoded mix here silently went three revisions stale."""
    w = PORTFOLIOS[name]
    return (w['QQQ'], w['IEMG'], w['BMNR'])

def cal_line(regime='normalized', mix=None):
    """A TRUE capital-allocation line: hold the risky mix in exact proportion and
    scale it against cash. Return-per-drawdown is then invariant to machine
    precision when cash has zero variance -- which is why no optimizer can pick
    the cash weight. Continuous weights, so the 5% grid does not blur it."""
    q, i, b = mix or risky_mix(); tot = q + i + b
    prop = {'QQQ': q/tot, 'IEMG': i/tot, 'BMNR': b/tot}
    V, R = REGIME[regime]['vol'], REGIME[regime]['rho']
    rf, out = A[RF_LABEL]['net'], []
    for a in (0.80, 0.75, 0.70, 0.65, 0.60):
        w = {k: v*a for k, v in prop.items()}; w['SGOV'] = 1 - a
        mu  = sum(w[k]*A[k]['net'] for k in w)
        sd  = math.sqrt(sum(w[x]*w[y]*V[x]*V[y]*rho(R,x,y) for x in w for y in w))
        out.append((round(a*100), (mu-rf)/(sd*DD_MULT)))
    return out

def cash_line(regime='normalized'):
    """The illustration shown on the page: QQQ traded against SGOV with IEMG held
    at the recommended weight. NOT a pure CAL -- pinning IEMG changes the risky mix
    as well as its scale -- so the ratio drifts slightly instead of holding exactly."""
    rows = []
    iemg = PORTFOLIOS['optimized']['IEMG']
    span = [(PORTFOLIOS['optimized']['QQQ'] + d, 95 - iemg - PORTFOLIOS['optimized']['QQQ'] - d)
            for d in (10, 5, 0, -5, -10)]
    for q, s_ in span:
        w = {'QQQ': q, 'IEMG': iemg, 'SGOV': s_, 'BMNR': 5}
        st = stats(w, regime)
        rows.append((w, st['cagr_d'], st['dd'],
                     (st['cagr_d'] - A[RF_LABEL]['net']) / st['dd']))
    return rows

if __name__ == '__main__':
    print('\n== FRONTIER (top 3, each regime) ==')
    for r in REGIME:
        print(f'  {r}:')
        for w, st in frontier(r)[:3]:
            print(f"    QQQ {w['QQQ']:>3} IEMG {w['IEMG']:>3} SGOV {w['SGOV']:>3} BMNR {w['BMNR']:>2}"
                  f"  CAGR {st['cagr_d']:.2f}%  sigma {st['vol']:.2f}%  Sharpe {st['sharpe']:.3f}")
    print('\n== CASH LINE (QQQ <-> SGOV, IEMG fixed at 40) ==')
    for w, c, dd, r in cash_line():
        print(f"  {w['QQQ']:>3}/40/{w['SGOV']:<3}/5   CAGR {c:>5.2f}%  maxDD -{dd:>5.1f}%  ret/DD {r:.3f}")
    rs = [r for _, _, _, r in cash_line()]
    print(f"  spread {max(rs)-min(rs):.4f} -> drifts, because pinning IEMG changes the risky mix")
    print('\n== TRUE CAL (risky mix fixed in exact proportion, scaled against cash) ==')
    cal = cal_line()
    for a, r in cal: print(f"  {a:>3}% risky   ret/DD {r:.6f}")
    print(f"  spread {max(r for _,r in cal)-min(r for _,r in cal):.2e} -> invariant, as theory requires")

# ── efficient frontier, generated so the chart cannot drift from the model ────
FR_X = (10.0, 50.0,  58.0, 286.0)      # max drawdown %  -> svg x
FR_Y = ( 4.0, 10.0, 148.0,  22.0)      # net CAGR %      -> svg y

def fr_x(dd): lo, hi, a, b = FR_X; return a + (b - a) * (dd - lo) / (hi - lo)
def fr_y(c):  lo, hi, a, b = FR_Y; return a + (b - a) * (c  - lo) / (hi - lo)

def admissible(bmnr=None):
    """Every allocation the brief permits: four sleeves, multiples of 5, none under 5."""
    out = []
    for q in range(5, 101, 5):
        for i in range(5, 101, 5):
            for s in range(5, 101, 5):
                b = 100 - q - i - s
                if b < 5 or b % 5: continue
                if bmnr is not None and b != bmnr: continue
                out.append({'QQQ': q, 'IEMG': i, 'SGOV': s, 'BMNR': b})
    return out

def efficient(regime='normalized', bmnr=5):
    """Allocations nothing else beats on both return and drawdown at once."""
    pts = [(s['dd'], s['cagr'], w)
           for w, s in ((w, stats(w, regime)) for w in admissible(bmnr))]
    eff = [p for p in pts
           if not any(d <= p[0] and c >= p[1] and (d < p[0] or c > p[1]) for d, c, _ in pts)]
    return sorted(eff), len(pts)

def frontier_svg(regime='normalized'):
    """The whole chart, emitted from the model. Axes auto-label over FR_X/FR_Y."""
    eff, _ = efficient(regime)
    assert all(FR_X[0] <= dd <= FR_X[1] and FR_Y[0] <= c <= FR_Y[1] for dd, c, _ in eff), \
        f'frontier runs outside the plotted axes: widen FR_X/FR_Y'
    g = ['<svg viewBox="0 0 300 172" role="img" aria-label="Efficient frontier of net CAGR '
         'against maximum drawdown, with both portfolios on the frontier">']
    g.append('<line x1="44" y1="148" x2="288" y2="148" stroke="#DFE4EB" stroke-width="1"/>')
    g.append('<line x1="44" y1="22" x2="44" y2="148" stroke="#DFE4EB" stroke-width="1"/>')
    for c in range(int(FR_Y[0]) + 1, int(FR_Y[1]) + 1):
        y = fr_y(c)
        g.append(f'<line x1="44" y1="{y:.1f}" x2="288" y2="{y:.1f}" stroke="#EDF0F4" stroke-width="1"/>'
                 f'<text x="38" y="{y+3:.1f}" fill="#8A94A6" font-family="IBM Plex Mono, monospace" '
                 f'font-size="8" text-anchor="end">{c}%</text>')
    step = 5 if (FR_X[1] - FR_X[0]) / 5 <= 8 else 10
    for dd in range(int(FR_X[0]), int(FR_X[1]) + 1, step):
        g.append(f'<text x="{fr_x(dd):.1f}" y="160" fill="#8A94A6" font-family="IBM Plex Mono, '
                 f'monospace" font-size="8" text-anchor="middle">&#8722;{dd}%</text>')
    pts = ' '.join(f'{fr_x(dd):.1f},{fr_y(c):.1f}' for dd, c, _ in eff)
    g.append(f'<polyline points="{pts}" fill="none" stroke="#0F5E63" stroke-width="1.8" '
             f'stroke-linejoin="round"/>')
    b = stats(PORTFOLIOS['baseline'], regime); o = stats(PORTFOLIOS['optimized'], regime)
    g.append(f'<circle cx="{fr_x(b["dd"]):.1f}" cy="{fr_y(b["cagr"]):.1f}" r="4" fill="#FFFFFF" '
             f'stroke="#B3402F" stroke-width="2"/>'
             f'<text x="{fr_x(b["dd"])+8:.1f}" y="{fr_y(b["cagr"])+3:.1f}" fill="#B3402F" '
             f'font-family="Public Sans, sans-serif" font-size="8.5" text-anchor="start" '
             f'font-weight="600">Baseline</text>')
    g.append(f'<circle cx="{fr_x(o["dd"]):.1f}" cy="{fr_y(o["cagr"]):.1f}" r="4.5" fill="#0F5E63"/>'
             f'<text x="{fr_x(o["dd"])-8:.1f}" y="{fr_y(o["cagr"])+3:.1f}" fill="#0F5E63" '
             f'font-family="Public Sans, sans-serif" font-size="8.5" text-anchor="end" '
             f'font-weight="600">Optimized</text>')
    g.append('<text x="166" y="171" fill="#8A94A6" font-family="Public Sans, sans-serif" '
             'font-size="8" text-anchor="middle" letter-spacing="0.4">MAX DRAWDOWN, VOLATILITY '
             'NORMALIZED</text>')
    g.append('<text x="12" y="88" fill="#8A94A6" font-family="Public Sans, sans-serif" '
             'font-size="8" text-anchor="middle" letter-spacing="0.4" transform="rotate(-90 12 88)">'
             'NET CAGR</text>')
    return ''.join(g) + '</svg>'

def fr_slope(regime='normalized'):
    """CAGR points bought per extra point of drawdown, locally, at the recommendation."""
    eff, _ = efficient(regime); d0 = stats(PORTFOLIOS['optimized'], regime)['dd']
    below = [p for p in eff if p[0] < d0]; above = [p for p in eff if p[0] > d0]
    assert below and above, 'recommendation sits at an end of the frontier; no local slope'
    lo, hi = below[-1], above[0]
    return (hi[1] - lo[1]) / (hi[0] - lo[0])

# ── how much of this is signal ───────────────────────────────────────────────
def tracking(w1, w2, regime='calm'):
    """Annualised sigma of (w1 - w2). The error on a *difference* between two
    overlapping books is far smaller than the error on either level."""
    reg = REGIME[regime]; V, R = reg['vol'], reg['rho']; ks = list(w1)
    d = {k: w1[k] - w2[k] for k in ks}
    return math.sqrt(max(sum((d[x]/100)*(d[y]/100)*V[x]*V[y]*rho(R, x, y)
                             for x in ks for y in ks), 0.0))

def calibration(w1, w2, regime='calm', years=10):
    """Is the gap between two books distinguishable from noise inside the horizon?"""
    g  = sum(w1[k]/100*A[k]['net'] for k in w1) - sum(w2[k]/100*A[k]['net'] for k in w2)
    t  = tracking(w1, w2, regime)
    assert t > 1e-9, 'identical books have no tracking error to divide by'
    ir = g / t                                   # information ratio of the switch
    z  = ir * math.sqrt(years)
    return dict(gap=g, te=t, ir=ir, z=z, se=t/math.sqrt(years),
                p=0.5*(1 + math.erf(z/math.sqrt(2))), years95=(1.96/ir)**2)

def separable(regime='calm', years=10, conf=1.96):
    """How many admissible allocations differ from the recommendation by more than noise."""
    rec = PORTFOLIOS['optimized']; sep = 0; tot = 0
    for w in admissible():
        if w == rec: continue
        t = tracking(w, rec, regime)
        if t < 1e-9: continue
        tot += 1
        c = calibration(w, rec, regime, years)
        if abs(c['z']) > conf: sep += 1
    return sep, tot

def se_level(name, regime='calm', years=10):
    """Standard error on the *level* of a book's realised CAGR over the horizon."""
    return stats(PORTFOLIOS[name], regime)['vol'] / math.sqrt(years)

# ── which input should you argue with first ──────────────────────────────────
import copy as _copy

def build_with(**over):
    """Rebuild the sleeve table with one input overridden, through the same code
    path as build(), so a sensitivity is computed rather than asserted."""
    OBS_ = _copy.deepcopy(OBS); BM = dict(BMNR); sg, sger = SGOV_GROSS, SGOV_ER
    for key, v in over.items():
        tk, f = key.split('_', 1)
        if   tk in OBS_:
            assert f in OBS_[tk], f'unknown field {key}'
            OBS_[tk][f] = v
        elif tk == 'BMNR':
            assert f in BM, f'unknown field {key}'
            BM[f] = v
        elif key == 'SGOV_gross': sg = v
        elif key == 'SGOV_er':    sger = v
        else: raise KeyError(key)
    a = {}
    for k, o in OBS_.items():
        val   = r2h(annualised(o['fwd_pe'], o['pe_end']))
        gross = r2h(o['div'] + o['eps'] + val + o['fx'])
        a[k]  = dict(net=r2h(gross - o['er']), er=o['er'])
    a['SGOV'] = dict(net=r2h(sg - sger), er=sger)
    mn = r2h(annualised(BM['mnav'], 1.00)); st = r2h(BM['stake_share'] * BM['stake_yield'])
    a['BMNR'] = dict(net=r2h(BM['eth'] + st + mn - BM['drag']), er=0.0)
    return a

SENS = (('QQQ earnings growth',  '9.5%',   'QQQ_eps',          8.50),
        ('IEMG currency drag',   '−1.50%', 'IEMG_fx',         -0.50),
        ('SGOV gross yield',     '3.25%',  'SGOV_gross',       4.25),
        ('IEMG earnings growth', '7.5%',   'IEMG_eps',         6.50),
        ('IEMG forward P/E',     '11.7×',  'IEMG_fwd_pe',     12.70),
        ('IEMG terminal P/E',    '12.2×',  'IEMG_pe_end',     13.20),
        ('QQQ terminal P/E',     '22.9×',  'QQQ_pe_end',      21.90),
        ('QQQ forward P/E',      '22.4×',  'QQQ_fwd_pe',      23.40),
        ('BMNR ETH return',      '9.0%',   'BMNR_eth',         8.00),
        ('BMNR staking yield',   '2.61%',  'BMNR_stake_yield', 1.61))

def sensitivity():
    """Effect of moving each input by one unit on the optimized book's CAGR and on
    the baseline-minus-optimized gap that decides the recommendation."""
    def figs(a):
        c = lambda w: sum(w[k]/100 * a[k]['net'] for k in w)
        o = c(PORTFOLIOS['optimized'])
        return o, c(PORTFOLIOS['baseline']) - o
    o0, g0 = figs(build_with())
    rows = []
    for label, now, key, val in SENS:
        o, g = figs(build_with(**{key: val}))
        # clamp float dust so a zero effect never renders as "-0.000"
        z = lambda x: 0.0 if abs(x) < 5e-4 else x
        rows.append(dict(label=label, now=now, d_cagr=z(o - o0), d_gap=z(g - g0)))
    return sorted(rows, key=lambda r: -abs(r['d_cagr'])), o0, g0
