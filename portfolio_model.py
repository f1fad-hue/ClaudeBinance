#!/usr/bin/env python3
"""
Single source of truth for every figure in allocation.html.

Run directly for a readable report; `python3 validate.py` checks the published
page against whatever this file computes. If a number changes here, the page is
wrong until it is changed there too.

Market data as of 4 September 2026. Sources are linked on the page itself.
"""
import math, json
from decimal import Decimal, ROUND_HALF_UP

def r2h(x):
    """Round half away from zero, the convention a reader applies by hand.
    Python's round() is banker's rounding, which makes 7.205 -> 7.20."""
    return float(Decimal(repr(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

# ── observed inputs ──────────────────────────────────────────────────────────
OBS = {
    'QQQ' : dict(er=0.18, fwd_pe=25.17, div=0.65, eps=9.50, pe_end=21.0,  fx=0.0),
    'IEMG': dict(er=0.09, fwd_pe=11.70, div=2.29, eps=7.50, pe_end=12.2,  fx=-1.50),
}
SGOV_GROSS = 3.25          # assumed 10yr average bill yield (spot SEC yield 3.63%)
SGOV_ER    = 0.09
BMNR = dict(eth=9.00, stake_share=0.859, stake_yield=3.00, mnav=1.02, drag=1.40)

REVISION = 7                          # bump when publishing; validate.py enforces it
VIX_SPOT, VIX_MEAN = 15.30, 18.9      # 2016-2023 mean of annual closes
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
DD  = {'QQQ': 40.0, 'IEMG': 33.0, 'SGOV': 0.3, 'BMNR': 85.0}
UPLIFT = VIX_MEAN / VIX_SPOT

REGIME = {
 'calm':       dict(vol={'QQQ':21.0,'IEMG':18.0,'SGOV':0.5,'BMNR':95.0},
                    rho={('QQQ','IEMG'):0.72,('QQQ','BMNR'):0.65,('IEMG','BMNR'):0.55}),
 'normalized': dict(vol={'QQQ':21.0*UPLIFT,'IEMG':18.0*UPLIFT,'SGOV':0.5,'BMNR':95.0*1.15},
                    rho={('QQQ','IEMG'):0.85,('QQQ','BMNR'):0.80,('IEMG','BMNR'):0.72}),
}

PORTFOLIOS = {
 'baseline':  {'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5},
 'optimized': {'QQQ':25,'IEMG':40,'SGOV':30,'BMNR':5},
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
           ('Monetary policy',2.5,.20), ('Liquidity & credit',5.5,.15),
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

def cal_line(regime='normalized', mix=(25, 40, 5)):
    """A TRUE capital-allocation line: hold the risky mix in exact proportion and
    scale it against cash. Return-per-drawdown is then invariant to machine
    precision when cash has zero variance -- which is why no optimizer can pick
    the cash weight. Continuous weights, so the 5% grid does not blur it."""
    q, i, b = mix; tot = q + i + b
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
    """The illustration shown on the page: QQQ traded against SGOV with IEMG
    pinned at 40. NOT a pure CAL -- pinning IEMG changes the risky mix as well as
    its scale -- so the ratio drifts slightly instead of holding exactly."""
    rows = []
    for q, s_ in ((35,20),(30,25),(25,30),(20,35),(15,40)):
        w = {'QQQ': q, 'IEMG': 40, 'SGOV': s_, 'BMNR': 5}
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
