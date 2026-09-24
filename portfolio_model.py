#!/usr/bin/env python3
"""
Single source of truth for every figure in allocation.html.

build.py generates the page from this file; validate.py re-derives every figure
independently and fails if the published page is not what build.py would write.
Change an input here, then run build.py -- never edit the page. Run this file
directly for a readable report.

Market data to the 23 September 2026 close; each fund price carries its own
date in PRICES. Sources are linked on the page itself.
"""
import math, json, copy as _copy
from decimal import Decimal, ROUND_HALF_UP

def r2h(x, places=2):
    """Round half away from zero, the convention a reader applies by hand.
    Python's round() is banker's rounding, which makes 7.205 -> 7.20. Float dust
    is snapped off first: a difference that is exactly -0.0395 in decimal arrives
    as -0.03949999..., and half-up on that gives the wrong last digit."""
    return float(Decimal(repr(round(x, 9))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))

# ── observed inputs ──────────────────────────────────────────────────────────
# Terminal multiples are each index's OWN 10-year average forward P/E (NDX 22.9x,
# MSCI EM 12.2x). Applying one rule to both keeps the comparison symmetric; an
# earlier revision marked QQQ down to a hand-picked 21.0x, below its own average,
# while marking IEMG up only as far as its average -- an asymmetry that favoured
# the EM sleeve, which is the page's central recommendation.
OBS = {
    'QQQ' : dict(er=0.18, eps=9.50, pe_end=22.9,  fx=0.0),
    'IEMG': dict(er=0.09, eps=7.50, pe_end=12.2,  fx=-1.50),
}
# Dividend yield and forward P/E are both price over something, so they are
# derived here from ONE price per fund and can never drift apart. An earlier
# revision re-priced the yields to the latest close while leaving the forward
# multiples at an older basis: QQQ rallied 4.6% to a record and IEMG fell 2.0%,
# and the valuation model -- whose whole job is to respond to price -- did not
# move. Forward EPS is held fixed over the few weeks between basis and now, which
# is the standard short-window approximation; for QQQ it is independently
# confirmed by the trailing multiple moving 28.55x -> 29.85x (+4.55%) against a
# +4.56% price move.
PRICES = {
    'QQQ':  dict(ttm_div=3.03, px=747.46, px_asof='2026-09-22',
                 basis_px=714.88, basis_fwd=22.40, basis_asof='2026-09-11'),
    'IEMG': dict(ttm_div=1.80, px=81.66,  px_asof='2026-09-18',
                 basis_px=83.33, basis_fwd=11.70, basis_asof='2026-09-11'),
}
for _k, _p in PRICES.items():
    OBS[_k]['div']    = r2h(_p['ttm_div'] / _p['px'] * 100)
    OBS[_k]['fwd_pe'] = r2h(_p['basis_fwd'] * _p['px'] / _p['basis_px'])
FED_RANGE  = (3.75, 4.00)  # target range set on 16 Sep 2026
FOMC_DATE  = '2026-09-16'
SGOV_GROSS = 3.875         # midpoint of FED_RANGE; validate.py asserts it
# 0-3 month bills track the effective funds rate, so the decade assumption is simply
# that policy averages where it now sits: the 3.75-4.00% range the FOMC set on
# 16 September, midpoint 3.875%. That is neutral by construction -- it neither
# extrapolates the hiking path futures price (about 4.1% by December) nor assumes a
# return to the 3.25% this file carried, which was below both spot and the curve.
SGOV_ER    = 0.09
BMNR = dict(eth=9.00, stake_share=0.847, stake_yield=2.62, mnav=1.08, drag=1.40)
BMNR_HOLDINGS = dict(held=5_983_940, staked=5_067_309, asof='2026-09-21',
                     eth_px=2688, crypto_b=16.11, total_b=17.1,        # 21 Sep release
                     px=28.75, px_asof='2026-09-22', shares_m=603.2)   # close, shares out
# mnav above is the crypto-only premium, derived here rather than typed:
BMNR_MCAP_B = BMNR_HOLDINGS['px'] * BMNR_HOLDINGS['shares_m'] / 1000
assert abs(BMNR['mnav'] - round(BMNR_MCAP_B / BMNR_HOLDINGS['crypto_b'], 2)) < 1e-9, \
    'BMNR mnav must equal market cap over crypto holdings'
# From the 21 Sep 2026 holdings release: 5,983,940 ETH at $2,688 (Coinbase), of which
# 5,067,309 staked -- the same staked count as a fortnight earlier, so the staked
# SHARE falls to 84.7% as new purchases sit unstaked. The 7-day yield is 2.62%.
# mnav uses the crypto-only reading, the conservative one: market cap $17.34B
# ($28.75 x 603.2M shares, 22 Sep) against ~$16.11B of crypto = 1.08x; against total
# holdings of $17.1B it is 1.01x. The stock rose ~6% on the release, which is what
# widened the premium.

REVISION = 21                          # bump when publishing; validate.py enforces it
# Daily closes, newest last. VIX_SPOT is taken from here rather than typed, and
# the assertion below is why: an earlier revision published 16.93 for 15 September
# from a source whose own stated change (-0.27, -1.57%) implied a prior close of
# 17.20 -- not the 17.62 this file already held for 14 September, verified against
# 11 September's 15.84 at +11.24%. A quoted level whose change does not reconcile
# with the close already on file is the tell, and it now fails the build.
# Rev. 19 carried 14.25 for 22 September. The close was 14.21 ("fell 4.44% to
# 14.21, a 21-session low"), which reconciles with 14.87 on the 21st, and the
# 23 September close was reported as +0.97 / +6.83% -- from 14.21, not 14.25.
# Rev. 20 then published 15.35 for the 23rd, from a live blog written at the bell
# ("+1.14 / +8.02%"). That also reconciles from 14.21, so the change test could
# not tell the two apart; the official 4:15pm close in the history tables is 15.18.
# Rule since Rev. 21: closes come from history tables, never from live coverage.
VIX_SERIES = (('2026-09-11', 15.84), ('2026-09-14', 17.62),
              ('2026-09-15', 17.20), ('2026-09-16', 17.71),
              ('2026-09-17', 15.42), ('2026-09-18', 14.81),
              ('2026-09-21', 14.87), ('2026-09-22', 14.21),
              ('2026-09-23', 15.18))
# The 2026 closing low: "fell to 14.13 on Friday, its lowest level of 2026", in a
# report dated 17 August -- Friday 14 August. Rev. 19 dated it 28 August; a
# 21-session low of 14.21 on 22 September rules that out.
VIX_2026 = dict(low=14.13, low_date='2026-08-14', high=31.65, high_date='2026-03-27')
VIX_SPOT, VIX_MEAN = VIX_SERIES[-1][1], 18.9   # 2016-2023 mean of annual closes
VIX_ASOF = VIX_SERIES[-1][0]
assert all(abs(b - a) / a < 0.25 for (_, a), (_, b) in zip(VIX_SERIES, VIX_SERIES[1:])), \
    'a >25% single-session move in the series is a transcription error until proven'

# Masthead levels, each with the change its source reported, so a level whose
# change does not reconcile with the close on file fails here -- the rule the VIX
# series already follows. Rev. 19 carried 4.93% for the 22 September 10-year;
# the close was 4.96%, and 23 September's +16bp to 5.12% is quoted from 4.96%.
MARKET = dict(asof='2026-09-23',
              brent=103.08, brent_prev=99.25, brent_chg_pct=3.86,
              ust10=5.12,   ust10_prev=4.96,  ust10_chg_bp=16)
assert abs(MARKET['brent_prev'] * (1 + MARKET['brent_chg_pct'] / 100) - MARKET['brent']) < 0.02, \
    'Brent level does not reconcile with its stated change'
assert abs(MARKET['ust10_prev'] + MARKET['ust10_chg_bp'] / 100 - MARKET['ust10']) < 0.005, \
    '10-year level does not reconcile with its stated change'

DD_MULT = 1.70                        # 10yr E[maxDD] ~= 1.65-1.75 x sigma
RF_LABEL = 'SGOV'

def annualised(p_now, p_end, yrs=10):
    return ((p_end / p_now) ** (1 / yrs) - 1) * 100

# ── forecasts ────────────────────────────────────────────────────────────────
def _build(obs, b, sg, sger):
    """Components are rounded to the precision the page displays, then summed, so
    every figure on the page can be reproduced by hand from the components shown.
    build() and build_with() both go through here, so a sensitivity cannot drift
    from the forecast it perturbs."""
    a = {}
    for k, o in obs.items():
        val   = r2h(annualised(o['fwd_pe'], o['pe_end']))
        gross = r2h(o['div'] + o['eps'] + val + o['fx'])
        a[k] = dict(div=o['div'], eps=o['eps'], val=val, fx=o['fx'],
                    gross=gross, er=o['er'], net=r2h(gross - o['er']))
    a['SGOV'] = dict(gross=sg, er=sger, net=r2h(sg - sger))
    mnav  = r2h(annualised(b['mnav'], 1.00))
    stake = r2h(b['stake_share'] * b['stake_yield'])
    net   = r2h(b['eth'] + stake + mnav - b['drag'])
    a['BMNR'] = dict(eth=b['eth'], stake=stake, mnav=mnav, drag=-b['drag'],
                     er=0.0, net=net, gross=net)
    return a

def build():
    return _build(OBS, BMNR, SGOV_GROSS, SGOV_ER)

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
                 term={h: r2h(VIX_SPOT*math.sqrt(h)) for h in (1/252,0.25,0.5,1.0)}),
        uplift=round(UPLIFT,4), revision=REVISION,
    )

# ── claims the page makes that must stay reproducible ────────────────────────
def frontier(regime, bmnr=5, sgov_min=15):
    """Allocations with BMNR pinned (default 5%), ranked by Sharpe. For the page's
    "subject only to the 5% floor" claim use best_sharpe(), which searches every
    admissible allocation; validate.py asserts the two agree."""
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

def cal_line(regime='normalized', mix=None, cash_vol=None):
    """A TRUE capital-allocation line: hold the risky mix in exact proportion and
    scale it against cash. Return-per-drawdown is exactly invariant only when cash
    has zero variance (pass cash_vol=0 to test the theorem itself); SGOV's own
    0.5% volatility leaves a small residual, which the page states rather than
    rounding away. Continuous weights, so the 5% grid does not blur it."""
    q, i, b = mix or risky_mix(); tot = q + i + b
    prop = {'QQQ': q/tot, 'IEMG': i/tot, 'BMNR': b/tot}
    V, R = dict(REGIME[regime]['vol']), REGIME[regime]['rho']
    if cash_vol is not None:
        V['SGOV'] = cash_vol
    rf, out = A[RF_LABEL]['net'], []
    for a in (0.80, 0.75, 0.70, 0.65, 0.60):
        w = {k: v*a for k, v in prop.items()}; w['SGOV'] = 1 - a
        mu  = sum(w[k]*A[k]['net'] for k in w)
        sd  = math.sqrt(sum(w[x]*w[y]*V[x]*V[y]*rho(R,x,y) for x in w for y in w))
        out.append((round(a*100), (mu-rf)/(sd*DD_MULT)))
    return out

# ── what the professionals publish, as an outside check ──────────────────────
# Ten-to-fifteen-year, USD, total return, gross of fund fees. These are other
# people's numbers, quoted to be disagreed with in the open -- not inputs.
INSTITUTIONAL = {
    'J.P. Morgan LTCMA 2026': dict(us=6.70, em=7.80, em_vol=20.9, note='US large cap; EM vol 20.9%'),
    'Fidelity':               dict(us=4.40, em=8.10, note='US large cap midpoint 3.4-5.4; US growth 2.3-4.3'),
    'Vanguard':               dict(us=5.20, em=4.30, note='midpoints of 4.2-6.2 and 3.3-5.3'),
    'BlackRock':              dict(us=5.00, em=7.10, note='EM figure is non-US broadly'),
}
ALT_SOURCE = 'J.P. Morgan LTCMA 2026'

def alt_nets(source=ALT_SOURCE):
    """Sleeve net returns if the US and EM sleeves took a published house forecast
    instead of this page's building blocks. Fund fees still come off; SGOV and BMNR
    are unchanged, since no house publishes a figure for either."""
    f = INSTITUTIONAL[source]
    return {'QQQ':  r2h(f['us'] - OBS['QQQ']['er']),
            'IEMG': r2h(f['em'] - OBS['IEMG']['er']),
            'SGOV': A['SGOV']['net'], 'BMNR': A['BMNR']['net']}

def scenario(nets, regime='calm'):
    """Re-run the whole comparison on a different set of sleeve returns. Risk inputs
    are unchanged -- only the return assumptions move -- so this isolates how much of
    the recommendation rests on this page's own forecasts."""
    cg = lambda w: sum(w[k]/100 * nets[k] for k in w)
    rows = {}
    for name, w in PORTFOLIOS.items():
        st = stats(w, regime)
        rows[name] = dict(cagr=cg(w), sharpe=(cg(w) - nets['SGOV']) / st['vol'], dd=st['dd'])
    best = max(((cg(w) - nets['SGOV']) / stats(w, regime)['vol'], w) for w in admissible())
    pts  = [(stats(w, 'normalized')['dd'], cg(w), w) for w in admissible(5)]
    eff  = [q for q in pts
            if not any(d <= q[0] and c >= q[1] and (d < q[0] or c > q[1]) for d, c, _ in pts)]
    return dict(rows=rows, gap=rows['baseline']['cagr'] - rows['optimized']['cagr'],
                best_sharpe=best[0], best_w=best[1], n_eff=len(eff),
                on_frontier={n: any(w == PORTFOLIOS[n] for _, _, w in eff)
                             for n in PORTFOLIOS})

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

def best_sharpe(regime='calm'):
    """Highest return-per-unit-risk allocation over EVERY admissible book, BMNR
    weight included: the page's claim is "subject only to the brief's 5% floor"."""
    return max(admissible(), key=lambda w: stats(w, regime)['sharpe'])

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
    on = [n for n in PORTFOLIOS if any(w == PORTFOLIOS[n] for _, _, w in eff)]
    who = ('both portfolios' if len(on) == len(PORTFOLIOS) else
           f'the {on[0]} book' if on else 'neither portfolio')
    g = [f'<svg viewBox="0 0 300 172" role="img" aria-label="Efficient frontier of net CAGR '
         f'against maximum drawdown, with {who} on the frontier">']
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

# ── testing a candidate sleeve, through the same code path ───────────────────
# A fifth sleeve was once evaluated in a throwaway script that reimplemented
# stats(). It got the regime wrong: the page stresses every correlation when it
# normalises volatility, and the ad-hoc version left the candidate's correlations
# at their calm values while stressing everyone else's. That flattered the
# candidate's diversification in exactly the regime that sets the weights, and
# turned two allocations that beat the recommended book into none. Nothing
# reimplements stats() now.

def stress_lift():
    """How much the normalised regime lifts a correlation, averaged over the pairs
    the page actually stresses. A candidate sleeve gets the same treatment."""
    pairs = [k for k in REGIME['calm']['rho']]
    return sum(REGIME['normalized']['rho'][p] - REGIME['calm']['rho'][p] for p in pairs) / len(pairs)

def with_candidate(name, net, er, vol, dd, rho_calm, norm_vol_mult=None):
    """Return REGIME / A / DD extended by one sleeve, with its correlations
    stressed by the same lift the page applies to every other pair. Returns a
    context the caller passes to stats_n()."""
    lift = stress_lift()
    reg = {}
    for r in REGIME:
        V = dict(REGIME[r]['vol'])
        V[name] = vol * ((norm_vol_mult if norm_vol_mult is not None else UPLIFT)
                         if r == 'normalized' else 1.0)
        R = dict(REGIME[r]['rho'])
        for (a, b), c in rho_calm.items():
            R[(a, b)] = c if r == 'calm' else min(0.95, c + lift)
        reg[r] = dict(vol=V, rho=R)
    a = {k: dict(v) for k, v in A.items()}; a[name] = dict(net=net, er=er, gross=net)
    d = dict(DD); d[name] = dd
    return dict(regime=reg, nets={k: v['net'] for k, v in a.items()},
                ers={k: v['er'] for k, v in a.items()}, dd=d, rf=A[RF_LABEL]['net'])

def stats_n(w, regime, ctx):
    """stats() over an arbitrary sleeve set. The four-sleeve path must agree with
    stats() exactly; validate.py asserts that on every portfolio and regime."""
    V, R = ctx['regime'][regime]['vol'], ctx['regime'][regime]['rho']
    ks = list(w)
    assert sum(w.values()) == 100 and all(v % 5 == 0 for v in w.values()), w
    cagr = sum(w[k]/100 * ctx['nets'][k] for k in ks)
    fee  = sum(w[k]/100 * ctx['ers'][k]  for k in ks)
    vol  = math.sqrt(sum((w[x]/100)*(w[y]/100)*V[x]*V[y]*rho(R, x, y) for x in ks for y in ks))
    mrc  = {x: (w[x]/100)*sum((w[y]/100)*V[x]*V[y]*rho(R, x, y) for y in ks)/vol for x in ks}
    tot  = sum(mrc.values())
    cagr_d = r2h(cagr)
    return dict(cagr=cagr, cagr_d=cagr_d, fee=fee, vol=vol, dd=vol*DD_MULT,
                naive=sum(w[k]/100*ctx['dd'][k] for k in ks),
                rc={k: mrc[k]/tot*100 for k in ks},
                sharpe=(cagr - ctx['rf'])/vol,
                terminal=10000*(1 + cagr_d/100)**10)

def base_ctx():
    """The four-sleeve book as a context, so stats_n() can be checked against stats()."""
    return dict(regime={r: dict(vol=REGIME[r]['vol'], rho=REGIME[r]['rho']) for r in REGIME},
                nets={k: v['net'] for k, v in A.items()},
                ers={k: v['er'] for k, v in A.items()}, dd=dict(DD), rf=A[RF_LABEL]['net'])

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
    return _build(OBS_, BM, sg, sger)

# Built from the live constants, never typed. An earlier revision hardcoded both
# the displayed level and the perturbed value; when SGOV's assumed yield moved from
# 3.25% to 3.875% the row went on claiming 3.25% and its "one unit" step quietly
# shrank to 0.375, understating that input's influence by two thirds.
def _sens_spec():
    q, i, b = OBS['QQQ'], OBS['IEMG'], BMNR
    pct = lambda x: f'{x:.1f}%' if abs(x*10 - round(x*10)) < 1e-9 else f'{x:g}%'
    mult = lambda x: f'{x:g}\u00d7'
    return (('QQQ earnings growth',  pct(q['eps']),      'QQQ_eps',          q['eps'] - 1),
            ('IEMG currency drag',   f"\u2212{abs(i['fx']):.2f}%", 'IEMG_fx', i['fx'] + 1),
            ('SGOV gross yield',     pct(SGOV_GROSS),    'SGOV_gross',       SGOV_GROSS + 1),
            ('IEMG earnings growth', pct(i['eps']),      'IEMG_eps',         i['eps'] - 1),
            ('IEMG forward P/E',     mult(i['fwd_pe']),  'IEMG_fwd_pe',      i['fwd_pe'] + 1),
            ('IEMG terminal P/E',    mult(i['pe_end']),  'IEMG_pe_end',      i['pe_end'] + 1),
            ('QQQ terminal P/E',     mult(q['pe_end']),  'QQQ_pe_end',       q['pe_end'] - 1),
            ('QQQ forward P/E',      mult(q['fwd_pe']),  'QQQ_fwd_pe',       q['fwd_pe'] + 1),
            ('BMNR ETH return',      pct(b['eth']),      'BMNR_eth',         b['eth'] - 1),
            ('BMNR staking yield',   pct(b['stake_yield']), 'BMNR_stake_yield', b['stake_yield'] - 1))

SENS = _sens_spec()

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
        z = lambda x: 0.0 if abs(x) < 5e-4 else round(x, 9)
        rows.append(dict(label=label, now=now, d_cagr=z(o - o0), d_gap=z(g - g0)))
    return sorted(rows, key=lambda r: -abs(r['d_cagr'])), o0, g0


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
    print('\n== FRONTIER (top 3, each regime) ==')
    for r in REGIME:
        print(f'  {r}:')
        for w, st in frontier(r)[:3]:
            print(f"    QQQ {w['QQQ']:>3} IEMG {w['IEMG']:>3} SGOV {w['SGOV']:>3} BMNR {w['BMNR']:>2}"
                  f"  CAGR {st['cagr_d']:.2f}%  sigma {st['vol']:.2f}%  Sharpe {st['sharpe']:.3f}")
    print('\n== AGAINST THE PROFESSIONALS (10-15yr, USD, gross of fees) ==')
    for nm, d in INSTITUTIONAL.items():
        print(f"  {nm:<24} US {d['us']:>5.2f}%  EM {d['em']:>5.2f}%   {d['note']}")
    print(f"  {'this page':<24} US {A['QQQ']['gross']:>5.2f}%  EM {A['IEMG']['gross']:>5.2f}%")
    _m = scenario({k: A[k]['net'] for k in A}); _j = scenario(alt_nets())
    for lbl, sc in (('this page', _m), (ALT_SOURCE, _j)):
        w = sc['best_w']
        print(f"  {lbl:<24} baseline {sc['rows']['baseline']['cagr']:.2f}%  optimized "
              f"{sc['rows']['optimized']['cagr']:.2f}%  lead {sc['gap']:+.2f}  best "
              f"{w['QQQ']}/{w['IEMG']}/{w['SGOV']}/{w['BMNR']}  efficient {sc['n_eff']}"
              f"  both on frontier {all(sc['on_frontier'].values())}")

    print('\n== TRUE CAL (risky mix fixed in exact proportion, scaled against cash) ==')
    cal = cal_line()
    for a, r in cal: print(f"  {a:>3}% risky   ret/DD {r:.6f}")
    cal0 = cal_line(cash_vol=0.0)
    print(f"  spread {max(r for _,r in cal)-min(r for _,r in cal):.2e} with SGOV at its "
          f"{REGIME['normalized']['vol']['SGOV']}% vol; "
          f"{max(r for _,r in cal0)-min(r for _,r in cal0):.2e} with riskless cash -> the theorem")
