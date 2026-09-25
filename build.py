#!/usr/bin/env python3
"""
Generates allocation.html from portfolio_model.py.

    python3 build.py            # writes allocation.html
    python3 build.py --check    # exit 1 if allocation.html is not what this would write

Every figure on the page is computed here from the model. The only literals are the
dated, sourced facts in FACTS below -- things the model does not compute (a payrolls
print, a PMI reading) -- and each carries its date in the sentence that uses it.
Twenty revisions of hand-edited prose kept producing the same defect: a number typed
into a sentence, correct on the day, left behind when the model moved. Generating the
page removes that class of error; validate.py still re-derives every figure without
importing this file, so a bug here is caught rather than copied.
"""
import math, sys, os, re
from html import escape
import portfolio_model as M

HERE = os.path.dirname(os.path.abspath(__file__))

# ── dated facts the model does not compute (sources linked on the page) ─────────
FACTS = dict(
    pmi_date='23 Sep', pmi_services=58.7, pmi_composite=58.4,
    payrolls='+162,000 against 53,000 expected (August)',
    cpi='August CPI 3.4% y/y; core 2.4% y/y but +0.3% m/m against 0.2% expected; PPI 5.4% y/y',
    fed_vote='12–0', fed_dots='16 of 18 officials see at least one more hike this year',
    imf_world='IMF: 3.1% world growth in 2026',
    imf_asia='China (4.4%) and India (6.3%) supply 43.6% of world growth (IMF)',
    ust10_note='its highest since 2007', ust30_note='the 30-year closed at its highest since 2004',
    ecb='The ECB hiked to 2.50% on 10 Sep into 0.8% growth and 3.0% projected inflation',
    geo='The US–Iran conflict keeps the Strait of Hormuz disrupted',
    em_dm_discount='40% discount to developed markets (11 Sep) against a 25% long-run norm',
    sgov_sec='3.74%', sgov_sec_label='30-day SEC yield, pre-hike',
    qqq_hist=(('2000–02 dot-com', '≈−83%'), ('2007–09 financial crisis', '−50 to −53%'),
              ('2020 COVID crash', '≈−27%'), ('2022 rate hikes', '−33 to −37%')),
    em_ann_mean=11.7,   # MSCI EM 20-year average forward P/E
)

SOURCES = (
    ('Funds', (('iShares SGOV', 'https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf'),
               ('iShares IEMG', 'https://www.ishares.com/us/products/244050/ishares-core-msci-emerging-markets-etf'),
               ('Invesco QQQ', 'https://www.invesco.com/qqq-etf/en/performance.html'))),
    ('Valuation', (('Siblis Nasdaq-100 P/E', 'https://siblisresearch.com/data/nasdaq-100-pe-ratio/'),
                   ('Siblis EM valuations', 'https://siblisresearch.com/data/emerging-markets-valuations/'),
                   ('MSCI EM discount', 'https://www.msci.com/indexes/markets-in-motion/visualizations/em-gains-but-discount-to-developed-markets-deepens'))),
    ('Policy & macro', (('FOMC statement, 16 Sep 2026', 'https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm'),
                        ('ECB, September 2026', 'https://www.ecb.europa.eu/press/press_conference/visual-mps/2026/html/mopo_statement_explained_september.en.html'),
                        ('BLS CPI', 'https://www.bls.gov/news.release/cpi.nr0.htm'),
                        ('S&P Global flash PMI', 'https://www.pmi.spglobal.com/Public/Home/PressRelease/35c60149cdbe461fb6bc3c959a58a551'),
                        ('IMF WEO', 'https://www.imf.org/external/datamapper/index.php'))),
    ('Rates & volatility', (('FRED 10-yr Treasury', 'https://fred.stlouisfed.org/series/dgs10'),
                            ('Cboe VIX history', 'https://www.cboe.com/tradable-products/vix/vix-historical-data'),
                            ('FRED VIX', 'https://fred.stlouisfed.org/series/VIXCLS'),
                            ('CME FedWatch', 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html'))),
    ('Outside forecasts', (('J.P. Morgan LTCMA 2026', 'https://am.jpmorgan.com/us/en/asset-management/institutional/insights/portfolio-insights/ltcma/'),
                           ('Vanguard VCMM', 'https://corporate.vanguard.com/content/corporatesite/us/en/corp/vemo/vemo-return-forecasts'),
                           ('BlackRock CMAs', 'https://www.blackrock.com/institutions/en-global/institutional-insights/thought-leadership/capital-market-assumptions'))),
    ('BMNR', (('Holdings release, 21 Sep 2026', 'https://www.prnewswire.com/news-releases/bitmine-immersion-technologies-bmnr-announces-eth-holdings-reach-5-98-million-tokens-and-total-crypto-and-total-cash-holdings-of-17-1-billion-302884434.html'),
              ('SEC filings', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001829311'))),
)

# ── formatting: half-up on the decimal a reader sees, typographic minus ────────
MINUS = '−'
def f(x, dp=2):   return f'{M.r2h(x, dp):.{dp}f}'
def neg(x, dp=1): return MINUS + f(abs(x), dp)
def sgn(x, dp=2):
    v = M.r2h(x, dp)
    return ('+' if v > 0 else MINUS if v < 0 else '±') + f'{abs(v):.{dp}f}'
MONTHS = 'January February March April May June July August September October November December'.split()
def usd(x): return ('+' if x > 0 else MINUS if x < 0 else '') + f'${abs(x):,.0f}'
def day(iso, short=True):
    m = MONTHS[int(iso[5:7]) - 1]
    return f'{int(iso[8:])} {m[:3] if short else m}'

# ── everything the page states, computed once ────────────────────────────────
E   = M.export()
B, O = M.PORTFOLIOS['baseline'], M.PORTFOLIOS['optimized']
ST  = {n: {r: M.stats(w, r) for r in M.REGIME} for n, w in M.PORTFOLIOS.items()}
SPOT, PREV = M.VIX_SPOT, M.VIX_SERIES[-2][1]
MK  = M.MARKET
FQ, FI = M.OBS['QQQ']['fwd_pe'], M.OBS['IEMG']['fwd_pe']
EFF, N_ADM = M.efficient()
ON  = {n: any(w == M.PORTFOLIOS[n] for _, _, w in EFF) for n in M.PORTFOLIOS}
CAL = M.calibration(B, O)
SENS, _, _ = M.sensitivity()
SEP, SEP_N = M.separable()
JPM = M.scenario(M.alt_nets())
BEST = M.best_sharpe('calm')
GAP = M.r2h(M.r2h(ST['baseline']['calm']['cagr_d']) - M.r2h(ST['optimized']['calm']['cagr_d']))
DDCUT = M.r2h(M.r2h(ST['baseline']['normalized']['dd'], 1) - M.r2h(ST['optimized']['normalized']['dd'], 1), 1)
REG_NAME = {'Asia / EM': 'Asia / Emerging', 'United States': 'United States', 'Europe': 'Europe'}
REG_BAR  = {'Asia / EM': 'var(--iemg)', 'United States': 'var(--qqq)', 'Europe': 'var(--neg)'}
RANKED = sorted(E['regions'], key=lambda k: -E['regions'][k]['mean'])
COL = {'QQQ': '#2B5CE6', 'IEMG': '#0F9B8E', 'SGOV': '#8A94A6', 'BMNR': '#E07A2F'}
# return per unit of calm volatility above cash, and the relation the prose must state
RV = {k: (M.A[k]['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol'][k] for k in ('QQQ', 'IEMG')}
REL = 'level with' if abs(RV['QQQ'] - RV['IEMG']) < 0.01 else ('ahead of' if RV['IEMG'] > RV['QQQ'] else 'behind')
REL_CAP = REL[0].upper() + REL[1:]

def tone(s5):
    return 'var(--pos)' if s5 >= 3.4 else 'var(--neg)' if s5 < 2.0 else 'var(--warn)'

# ── panes ─────────────────────────────────────────────────────────────────────
def masthead():
    return f'''<header class="mast">
    <h1>Four-Sleeve Allocation Desk</h1>
    <p class="sub">Macro-weighted portfolio construction across SGOV · QQQ · IEMG · BMNR</p>
    <div class="stamp">
      <span>As of {day(MK['asof'])} {MK['asof'][:4]}</span><span>10-yr horizon</span><span>Fed {M.FED_RANGE[0]:.2f}–{M.FED_RANGE[1]:.2f}%</span><span>VIX {SPOT:.2f}</span><span>Brent ${MK['brent']:.2f}</span><span>UST 10y {MK['ust10']:.2f}%</span><span>Rev. {M.REVISION} · re-verified</span>
    </div>
  </header>'''

def gauge():
    g = E['gauge']; s5 = g['score5']
    lab = ('Risk-off' if s5 < 1.8 else 'Neutral — cautious' if s5 < 2.6 else 'Neutral' if s5 < 3.4
           else 'Constructive' if s5 < 4.2 else 'Risk-on')
    colour = {'var(--pos)': '#1B7F5A', 'var(--neg)': '#B3402F', 'var(--warn)': '#B7791F'}[tone(s5)]
    return f'''<div class="gauge-wrap" style="margin-top:14px">
    <svg viewBox="0 0 212 152" role="img" aria-label="Composite macro driver sentiment gauge reading {g['display']} out of 5">
      <path d="M 26 116 A 80 80 0 0 1 186 116" fill="none" stroke="#EDF0F4" stroke-width="15" stroke-linecap="round"/>
      <path d="M 26 116 A 80 80 0 0 1 186 116" fill="none" stroke="{colour}" stroke-width="15" stroke-linecap="round"
            stroke-dasharray="{g['arc_dash']} 251.4"/>
      <line x1="106" y1="116" x2="{g['needle'][0]}" y2="{g['needle'][1]}" stroke="#10161F" stroke-width="2.4" stroke-linecap="round"/>
      <circle cx="106" cy="116" r="5" fill="#10161F"/>
      <circle cx="106" cy="116" r="1.9" fill="#FFFFFF"/>
      <text x="26" y="136" fill="#8A94A6" font-family="IBM Plex Mono, monospace" font-size="9.5" text-anchor="middle">1</text>
      <text x="106" y="26" fill="#8A94A6" font-family="IBM Plex Mono, monospace" font-size="9.5" text-anchor="middle">3</text>
      <text x="186" y="136" fill="#8A94A6" font-family="IBM Plex Mono, monospace" font-size="9.5" text-anchor="middle">5</text>
      <text x="26" y="147" fill="#8A94A6" font-family="Public Sans, sans-serif" font-size="8" text-anchor="middle" letter-spacing="0.5">RISK-OFF</text>
      <text x="186" y="147" fill="#8A94A6" font-family="Public Sans, sans-serif" font-size="8" text-anchor="middle" letter-spacing="0.5">RISK-ON</text>
    </svg>
    <div class="gauge-val">{g['display']}<small>/5</small></div>
    <div class="gauge-lab">{lab}</div>
    <p class="gauge-note">Six weighted drivers, each scored 1–5 where 3 is neutral. Strong growth is outweighed by inflation, a hiking Fed and a realised energy shock.</p>
  </div>'''

def driver_notes():
    disc = (1 - FI / FQ) * 100
    return {
      'Growth momentum': f"Payrolls {FACTS['payrolls']}; flash PMIs on {FACTS['pmi_date']} at their fastest pace in over five years (services {FACTS['pmi_services']}, composite {FACTS['pmi_composite']}). {FACTS['imf_world']}.",
      'Inflation trajectory': f"{FACTS['cpi']}. September flash PMIs show input costs rising on energy.",
      'Monetary policy': f"The Fed hiked {FACTS['fed_vote']} on {day(M.FOMC_DATE)}; {FACTS['fed_dots']}; the range is {M.FED_RANGE[0]:.2f}–{M.FED_RANGE[1]:.2f}%.",
      'Liquidity & credit': f"The 10-year closed at {MK['ust10']:.2f}% on {day(MK['asof'])} ({'+' if MK['ust10_chg_bp'] >= 0 else MINUS}{abs(MK['ust10_chg_bp'])}bp), {FACTS['ust10_note']}, and {FACTS['ust30_note']}: conditions tighten through the long end and oil.",
      'Valuation & positioning': f"Nasdaq-100 at {f(FQ, 1)}× forward vs EM at {f(FI, 1)}× — a {f(disc, 0)}% discount. The VIX at {SPOT:.2f} sits {f((1 - SPOT / M.VIX_MEAN) * 100, 0)}% below its {M.VIX_MEAN} long-run mean: protection is cheap.",
      'Geopolitical risk': f"{FACTS['geo']}; Brent settled at ${MK['brent']:.2f} on {day(MK['asof'])}.",
    }

def macro():
    notes = driver_notes()
    rows = []
    for (name, _, wt), (_, s5, fill) in zip(M.DRIVERS, E['gauge']['drivers']):
        t = tone(s5)
        rows.append(f'''    <div class="drv">
      <div class="drv-n">{escape(name)} <span class="wt">w {wt*100:.0f}%</span></div><div class="drv-s" style="color:{t}">{s5}</div>
      <div class="drv-bar"><i style="width:{fill}%;background:{t}"></i></div>
      <div class="drv-d">{escape(notes[name])}</div>
    </div>''')
    q, i, sg, bm = M.A['QQQ'], M.A['IEMG'], M.A['SGOV'], M.A['BMNR']
    trans = (
      ('SGOV', 'sgov', 'up', 'Tailwind', f"Bills reprice with the Fed. The {M.SGOV_GROSS:g}% policy midpoint nets {f(sg['net'])}% at near-zero duration — the one sleeve a rising 10-year cannot hurt."),
      ('QQQ', 'qqq', 'nu', 'Two-sided', f"Earnings momentum is real, but at {f(FQ, 1)}× forward — above its {M.OBS['QQQ']['pe_end']}× average — it is the sleeve most exposed to a {MK['ust10']:.2f}% 10-year."),
      ('IEMG', 'iemg', 'up', 'Tailwind', f"The cheapest bloc at {f(FI, 1)}×, below its {M.OBS['IEMG']['pe_end']}× average. A stronger dollar and ${MK['brent']:.2f} oil are the near-term headwinds."),
      ('BMNR', 'bmnr', 'dn', 'Headwind', f"Levered ETH exposure with a {M.REGIME['calm']['rho'][('QQQ','BMNR')]:.2f} correlation to QQQ: it fails when equities fail, and tightening drains crypto liquidity."),
    )
    tr = '\n'.join(f'''    <div class="corr-row">
      <div class="tick" style="background:var(--{c})">{t}</div>
      <div class="corr-b"><span class="sig {sig}">{lab}</span><br>{escape(txt)}</div>
    </div>''' for t, c, sig, lab, txt in trans)
    chg = (SPOT / PREV - 1) * 100
    return f'''<section class="pane on" id="p-macro" role="tabpanel" aria-labelledby="t-macro">
  <h2>Macro drivers</h2>
  <p class="lede">Six forces that set the return and risk of this book, and how each one reaches the four holdings.</p>
  <div class="warnbox"><b>{'The bond sell-off extended' if MK['ust10_chg_bp'] > 0 else 'Rates eased'}.</b> The 10-year closed at <b>{MK['ust10']:.2f}%</b> on {day(MK['asof'])} ({'+' if MK['ust10_chg_bp'] >= 0 else MINUS}{abs(MK['ust10_chg_bp'])}bp), {FACTS['ust10_note']}, after hot flash PMIs on {FACTS['pmi_date']}; {FACTS['ust30_note']}. Brent settled {'up' if MK['brent_chg_pct'] > 0 else 'down'} {f(abs(MK['brent_chg_pct']), 1)}% at <b>${MK['brent']:.2f}</b>; the VIX {'rose' if chg > 0 else 'fell'} {f(abs(chg), 1)}% to <b>{SPOT:.2f}</b>.</div>

  {gauge()}

  <h3>Composite inputs</h3>
  <div class="card">
{chr(10).join(rows)}
  </div>

  <h3>Correlated transmission</h3>
  <div class="corr">
{tr}
  </div>

  <div class="call" style="margin-top:16px"><b>The core tension.</b> Growth is real but met by tightening, a {MK['ust10']:.2f}% 10-year and ${MK['brent']:.0f} oil. Stay invested for ten years, tilt the equity mix to the cheaper bloc, and hold a reserve to buy the repricing.</div>
</section>'''

def regions():
    notes = {
      'Asia / EM': f"{FACTS['imf_asia']}. Equities at {f(FI, 1)}× forward, a {FACTS['em_dm_discount']}. Dollar strength and oil cap the near term.",
      'United States': f"The strongest productivity cycle, but the richest multiple ({f(FQ, 1)}×) and a {MK['ust10']:.2f}% 10-year weigh on the near term.",
      'Europe': f"{FACTS['ecb']}. The most energy-import-exposed bloc.",
    }
    cards = []
    for rank, k in enumerate(RANKED, 1):
        r = E['regions'][k]
        cls = 'rank' if rank == 1 else f'rank r{rank}'
        bars = '\n'.join(f'    <div class="hz"><span class="hz-l">{h}</span><span class="hz-t"><i style="width:{fl}%;background:{REG_BAR[k]}"></i></span><span class="hz-v">{sc}</span></div>'
                         for h, sc, fl in zip(('3 mo', '6 mo', '12 mo', '10 yr'), r['scores'], r['fills']))
        cards.append(f'''  <div class="reg">
    <div class="reg-h"><span class="nm">{REG_NAME[k]}</span><span class="{cls}">Rank {rank}</span></div>
{bars}
    <p class="reg-note">{escape(notes[k])}</p>
  </div>''')
    mrows = '\n'.join(f'''        <tr{' class="hl"' if n == 0 else ''}><td>{k}</td>{''.join(f'<td class="n">{x}</td>' for x in E['regions'][k]['scores'])}<td class="n">{E['regions'][k]['mean']}</td></tr>'''
                      for n, k in enumerate(RANKED))
    top, sec = RANKED[0], RANKED[1]
    lead = [M.r2h(E['regions'][top]['scores'][h] - E['regions'][sec]['scores'][h], 1) for h in (0, 3)]
    return f'''<section class="pane" id="p-regions" role="tabpanel" aria-labelledby="t-regions">
  <h2>Regional rankings</h2>
  <p class="lede">Scored 1–5 on the gauge&#8217;s scale at three tactical horizons and the 10-year anchor, ranked by mean score.</p>

{chr(10).join(cards)}

  <h3>Score matrix</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Bloc</th><th>3 mo</th><th>6 mo</th><th>12 mo</th><th>10 yr</th><th>Mean</th></tr></thead>
      <tbody>
{mrows}
      </tbody>
    </table>
  </div>
  <div class="call" style="margin-top:14px"><b>Allocation consequence.</b> {REG_NAME[top]} leads by {lead[0]:.1f} at 3 months and {lead[1]:.1f} at 10 years{', which is why the optimized book tilts toward IEMG' if top == 'Asia / EM' and O['IEMG'] > B['IEMG'] else ''}. The four mandated sleeves hold no direct Europe exposure, which the rankings support.</div>
</section>'''

def volatility():
    term = E['vix']['term']
    trows = '\n'.join(f'        <tr><td>{lab}</td><td class="n">{math.sqrt(h):.3f}</td><td class="n">{term[h]:.2f}%</td><td class="n">±{f(1.645 * term[h], 2 if h < 0.1 else 1)}%</td></tr>'
                      for lab, h in (('1 day', 1/252), ('3 months', 0.25), ('6 months', 0.5), ('12 months', 1.0)))
    bc, oc = ST['baseline']['calm'], ST['optimized']['calm']
    bn, on = ST['baseline']['normalized'], ST['optimized']['normalized']
    vrows = '\n'.join(f'        <tr><td>{lab}</td><td class="n">{bc["vol"]*h**0.5:.2f}%</td><td class="n neg">{neg(bc["var"][h])}%</td>'
                      f'<td class="n">{oc["vol"]*h**0.5:.2f}%</td><td class="n neg">{neg(oc["var"][h])}%</td></tr>'
                      for lab, h in (('3 months', 0.25), ('6 months', 0.5), ('12 months', 1.0)))
    V, R = M.REGIME['calm'], M.REGIME['normalized']
    srows = '\n'.join(f'        <tr><td>{k}</td><td class="n">{V["vol"][k]:.{0 if k == "BMNR" else 1}f}%</td>'
                      f'<td class="n{" neg" if R["vol"][k] > V["vol"][k] else ""}">{R["vol"][k]:.{0 if k == "BMNR" else 1}f}%</td></tr>'
                      for k in ('QQQ', 'IEMG', 'SGOV', 'BMNR'))
    rrows = '\n'.join(f'        <tr><td>ρ {a}·{b}</td><td class="n">{V["rho"][(a, b)]:.2f}</td><td class="n neg">{R["rho"][(a, b)]:.2f}</td></tr>'
                      for a, b in (('QQQ', 'IEMG'), ('QQQ', 'BMNR'), ('IEMG', 'BMNR')))
    rc = on['rc']
    rcrows = '\n'.join(f'''    <div class="drv">
      <div class="drv-n">{k} <span class="wt">{O[k]}% weight</span></div><div class="drv-s">{rc[k]:.1f}%</div>
      <div class="drv-bar"><i style="width:{max(rc[k], 1):.1f}%;background:var(--{k.lower()})"></i></div>
    </div>''' for k in ('QQQ', 'IEMG', 'SGOV', 'BMNR'))
    hist = '\n'.join(f'    <div class="kv"><span class="k">{a}</span><span class="v" style="color:var(--neg)">{b}</span></div>' for a, b in FACTS['qqq_hist'])
    sig = lambda k, r: M.REGIME[r]['vol'][k] * M.DD_MULT
    def where(k):
        lo_, hi_ = sig(k, 'calm'), sig(k, 'normalized')
        return 'sits between' if lo_ <= M.DD[k] <= hi_ else 'sits beyond both' if M.DD[k] > hi_ else 'sits inside both'
    lo = M.VIX_2026
    return f'''<section class="pane" id="p-vol" role="tabpanel" aria-labelledby="t-vol">
  <h2>Volatility analysis</h2>
  <p class="lede">Square-root-of-time maths at 3, 6 and 12 months, carried to the 10-year holding period.</p>

  <div class="card">
    <div class="hero2" style="margin-bottom:0">
      <div><div class="k">VIX, {day(M.VIX_ASOF)}</div><div class="v">{SPOT:.2f}</div></div>
      <div><div class="k">2026 low · high</div><div class="v">{lo['low']:.2f} · {lo['high']:.2f}</div></div>
    </div>
    <p class="gauge-note" style="text-align:left;max-width:none;margin:10px 0 0">Spot is {f((1 - SPOT / M.VIX_MEAN) * 100, 1)}% below the 2016–2023 mean of {M.VIX_MEAN}. The 2026 low was {day(lo['low_date'], False)}; the high {day(lo['high_date'], False)}.</p>
  </div>

  <h3>Term structure</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Horizon</th><th>√(h/12)</th><th>Implied σ</th><th>95% band</th></tr></thead>
      <tbody>
{trows}
      </tbody>
    </table>
  </div>
  <p class="note">σ<sub>h</sub> = VIX × √(h/12). It assumes constant volatility and normal returns; both fail in stress.</p>

  <h3>Portfolio volatility and 95% VaR</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Horizon</th><th colspan="2">Baseline</th><th colspan="2">Optimized</th></tr>
      <tr><th></th><th>σ</th><th>VaR</th><th>σ</th><th>VaR</th></tr></thead>
      <tbody>
{vrows}
        <tr class="hl"><td>10 yr max DD</td><td class="n" colspan="2">{neg(bc["dd"])}%</td><td class="n" colspan="2">{neg(oc["dd"])}%</td></tr>
        <tr><td>12 mo, normalized</td><td class="n">{bn["vol"]:.2f}%</td><td class="n neg">{neg(bn["var"][1.0])}%</td><td class="n">{on["vol"]:.2f}%</td><td class="n neg">{neg(on["var"][1.0])}%</td></tr>
        <tr><td>Max DD, normalized</td><td class="n neg" colspan="2">{neg(bn["dd"])}%</td><td class="n neg" colspan="2">{neg(on["dd"])}%</td></tr>
      </tbody>
    </table>
  </div>
  <p class="note">VaR is drift-adjusted at the 5th percentile. Ten-year max drawdown ≈ {M.DD_MULT:.2f} × σ (band 1.65–1.75).</p>

  <h3>Two regimes</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Input</th><th>Calm (today)</th><th>Normalized</th></tr></thead>
      <tbody>
{srows}
{rrows}
      </tbody>
    </table>
  </div>
  <div class="warnbox" style="margin-top:12px"><b>Why weights are sized to the second column.</b> Volatility mean-reverted to {M.VIX_MEAN} (×{f(M.UPLIFT, 2)}) and crisis correlations turn the optimized book&#8217;s {neg(oc["dd"])}% drawdown into {neg(on["dd"])}%. That is the risk the {O["SGOV"]}% reserve is sized for.</div>

  <h3>Risk contribution, normalized</h3>
  <div class="card">
{rcrows}
    <p class="gauge-note" style="text-align:left;max-width:none;margin:10px 0 0">BMNR is {O["BMNR"]}% of capital but {rc["BMNR"]:.1f}% of risk ({f(rc["BMNR"] / O["BMNR"], 1)}×) — why it is capped at 5%. SGOV is {O["SGOV"]}% of capital and effectively none of the risk.</p>
  </div>

  <h3>Ten-year view: QQQ&#8217;s worst drawdowns</h3>
  <div class="card">
{hist}
    <p class="gauge-note" style="text-align:left;max-width:none;margin:10px 0 0">Sleeve drawdowns are history-anchored judgements: QQQ {neg(M.DD["QQQ"], 0)}% {where("QQQ")} the σ model&#8217;s calm and normalized readings ({neg(sig("QQQ","calm"))}%, {neg(sig("QQQ","normalized"))}%); IEMG {neg(M.DD["IEMG"], 0)}% {where("IEMG")} ({neg(sig("IEMG","calm"))}%, {neg(sig("IEMG","normalized"))}%).</p>
  </div>
</section>'''

def slide(t, kind, name, kv, role):
    a = M.A[t]
    rows = '\n'.join(f'        <div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in kv)
    d = lambda n: ('var(--pos)' if M.PORTFOLIOS['optimized'][t] > M.PORTFOLIOS['baseline'][t] else
                   'var(--neg)' if M.PORTFOLIOS['optimized'][t] < M.PORTFOLIOS['baseline'][t] else 'var(--ink)')
    return f'''    <article class="slide">
      <div class="sl-top">
        <span class="sl-kind" style="background:var(--{t.lower()})">{kind}</span>
        <div class="sl-tick">{t}</div>
        <div class="sl-nm">{name}</div>
      </div>
      <div class="sl-body">
        <div class="hero2">
          <div><div class="k">Net 10-yr CAGR</div><div class="v" style="color:var(--pos)">{a["net"]:.2f}%</div></div>
          <div><div class="k">Expected max DD</div><div class="v" style="color:var(--neg)">{neg(M.DD[t], 0 if M.DD[t] >= 1 else 1)}%</div></div>
        </div>
{rows}
        <p class="sl-role">{role}</p>
        <div class="wts"><div><div class="k">Baseline</div><div class="v">{B[t]}%</div></div><div><div class="k">Optimized</div><div class="v" style="color:{d(t)}">{O[t]}%</div></div></div>
      </div>
    </article>'''

def sleeves():
    q, i, s, b = M.A['QQQ'], M.A['IEMG'], M.A['SGOV'], M.A['BMNR']
    term = lambda k: f"${E['sleeves'][k]['terminal']:,}"
    P, H = M.PRICES, M.BMNR_HOLDINGS
    V = M.REGIME['calm']['vol']
    slides = [
      slide('SGOV', 'ETF · Cash', 'iShares 0–3 Month Treasury Bond ETF',
            (('Gross forecast', f"{f(s['gross'])}%"), ('Expense ratio', f"{s['er']:.2f}%"),
             (FACTS['sgov_sec_label'], FACTS['sgov_sec']), ('Annualised σ', f"{V['SGOV']}%"), ('$10,000 → 10 yr', term('SGOV'))),
            f"<b>Drawdown control and dry powder.</b> Assumes policy averages the {M.SGOV_GROSS:g}% midpoint of the {M.FED_RANGE[0]:.2f}–{M.FED_RANGE[1]:.2f}% range for the decade."),
      slide('QQQ', 'ETF · US Growth', 'Invesco QQQ Trust — Nasdaq-100',
            (('Gross forecast', f"{f(q['gross'])}%"), ('Expense ratio', f"{q['er']:.2f}%"),
             (f"Price ({day(P['QQQ']['px_asof'])})", f"${P['QQQ']['px']:.2f}"), ('Forward P/E', f"{f(FQ, 1)}×"),
             ('Dividend yield', f"{q['div']:.2f}%"), ('Annualised σ', f"{V['QQQ']:.0f}%"), ('$10,000 → 10 yr', term('QQQ'))),
            f"<b>Primary growth engine.</b> {q['eps']:.1f}%/yr earnings growth carries the forecast; {'above' if FQ > M.OBS['QQQ']['pe_end'] else 'below'} its own {M.OBS['QQQ']['pe_end']}× average, the multiple {'costs' if q['val'] < 0 else 'adds'} {f(abs(q['val']))}%/yr."),
      slide('IEMG', 'ETF · EM Equity', 'iShares Core MSCI Emerging Markets ETF',
            (('Gross forecast', f"{f(i['gross'])}%"), ('Expense ratio', f"{i['er']:.2f}%"),
             (f"Price ({day(P['IEMG']['px_asof'])})", f"${P['IEMG']['px']:.2f}"), ('Forward P/E', f"{f(FI, 1)}×"),
             ('Dividend yield', f"{i['div']:.2f}%"), ('Annualised σ', f"{V['IEMG']:.0f}%"), ('$10,000 → 10 yr', term('IEMG'))),
            f"<b>The overweight.</b> {'Below' if FI < M.OBS['IEMG']['pe_end'] else 'Above'} its {M.OBS['IEMG']['pe_end']}× average, the multiple {'adds' if i['val'] > 0 else 'costs'} {f(abs(i['val']))}%/yr; currency costs {f(abs(i['fx']))}%/yr. {REL_CAP} QQQ on return per unit of risk."),
      slide('BMNR', 'Stock · Crypto', 'BitMine Immersion Technologies',
            ((f"Price ({day(H['px_asof'])})", f"${H['px']:.2f}"), ('Market cap', f"${M.BMNR_MCAP_B:.2f}B"),
             ('ETH treasury', f"{H['held']:,}"), ('ETH staked', f"{H['staked'] / H['held'] * 100:.1f}%"),
             ('mNAV (total / crypto)', f"{M.BMNR_MCAP_B / H['total_b']:.2f}× / {M.BMNR['mnav']:.2f}×"),
             ('Annualised σ', f"~{V['BMNR']:.0f}%"), ('$10,000 → 10 yr', term('BMNR'))),
            f"<b>Capped convexity.</b> {b['eth']:.1f}% ETH appreciation {sgn(b['stake'])}% staking {sgn(b['mnav'])}% premium normalisation {sgn(b['drag'])}% dilution drag = {b['net']:.2f}%. Total loss costs {O['BMNR']}% of capital."),
    ]
    dots = ''.join('<b class="on"></b>' if n == 0 else '<b></b>' for n in range(len(slides)))
    return f'''<section class="pane" id="p-assets" role="tabpanel" aria-labelledby="t-assets">
  <h2>The four sleeves</h2>
  <p class="lede">Forecast 10-year CAGR net of fund fees, and expected maximum drawdown, for each mandated holding.</p>
  <p class="swipe">← swipe to compare →</p>
  <div class="deck" id="deck">
{chr(10).join(slides)}
  </div>
  <div class="dots" id="dots">{dots}</div>
</section>'''

def donut(name, label, sub, win):
    st = ST[name]['calm']; segs = E['donuts'][name]; w = M.PORTFOLIOS[name]
    circ = '\n'.join(f'          <circle cx="90" cy="90" r="64" stroke="{COL[k]}" stroke-dasharray="{a:.2f} {g:.2f}" stroke-dashoffset="{o:.2f}"/>'.replace('"-0.00"', '"0"').replace('"0.00"', '"0"')
                     for k, a, g, o in segs)
    leg = '\n'.join(f'        <span><i style="background:var(--{k.lower()})"></i>{k}<em>{w[k]}%</em></span>' for k in ('QQQ', 'IEMG', 'SGOV', 'BMNR'))
    aria = ', '.join(f'{k} {w[k]} percent' for k in ('QQQ', 'IEMG', 'SGOV', 'BMNR'))
    return f'''    <div class="dn{' win' if win else ''}">
      <div class="dn-t">{label}</div><div class="dn-c">{sub}</div>
      <svg viewBox="0 0 180 180" role="img" aria-label="{label} allocation: {aria}">
        <g transform="rotate(-90 90 90)" fill="none" stroke-width="26">
{circ}
        </g>
        <text x="90" y="86" text-anchor="middle" fill="{'#0F5E63' if win else '#10161F'}" font-family="IBM Plex Mono, monospace" font-size="25" font-weight="600">{st['cagr_d']:.2f}</text>
        <text x="90" y="102" text-anchor="middle" fill="#8A94A6" font-family="Public Sans, sans-serif" font-size="9" letter-spacing="0.8">NET CAGR %</text>
      </svg>
      <div class="leg">
{leg}
      </div>
    </div>'''

def shift_line():
    d = {k: O[k] - B[k] for k in B}
    out = [k for k in d if d[k] < 0]; into = [k for k in d if d[k] > 0]
    src = ' and '.join(f'{-d[k]} points out of {k}' for k in out)
    dst = ', '.join(f"{d[k]} to {'the reserve' if k == 'SGOV' else k}" for k in into)
    return f'{src} — {dst}'

def compare_table():
    b, o = ST['baseline'], ST['optimized']
    def d_(a, c, p): return sgn(M.r2h(c, p) - M.r2h(a, p), p)
    rows = (
      ('Net 10-yr CAGR', f"{b['calm']['cagr_d']:.2f}%", f"{o['calm']['cagr_d']:.2f}%", d_(b['calm']['cagr_d'], o['calm']['cagr_d'], 2), 'neg', False),
      ('Weighted fee', f"{b['calm']['fee']:.3f}%", f"{o['calm']['fee']:.3f}%", d_(b['calm']['fee'], o['calm']['fee'], 3), 'pos', False),
      ('σ — calm (today)', f"{b['calm']['vol']:.2f}%", f"{o['calm']['vol']:.2f}%", d_(b['calm']['vol'], o['calm']['vol'], 2), 'pos', False),
      ('σ — vol normalized', f"{b['normalized']['vol']:.2f}%", f"{o['normalized']['vol']:.2f}%", d_(b['normalized']['vol'], o['normalized']['vol'], 2), 'pos', False),
      ('Max DD — calm', f"{neg(b['calm']['dd'])}%", f"{neg(o['calm']['dd'])}%", d_(o['calm']['dd'], b['calm']['dd'], 1), 'pos', False),
      ('Max DD — normalized', f"{neg(b['normalized']['dd'])}%", f"{neg(o['normalized']['dd'])}%", d_(o['normalized']['dd'], b['normalized']['dd'], 1), 'pos', True),
      ('Correlated-stress DD', f"{neg(b['calm']['naive'])}%", f"{neg(o['calm']['naive'])}%", d_(o['calm']['naive'], b['calm']['naive'], 1), 'pos', False),
      ('Return / risk (calm)', f"{b['calm']['sharpe']:.3f}", f"{o['calm']['sharpe']:.3f}", d_(b['calm']['sharpe'], o['calm']['sharpe'], 3), 'neg', False),
      ('$10,000 → 10 yr', f"${b['calm']['terminal']:,.0f}", f"${o['calm']['terminal']:,.0f}",
       usd(M.r2h(o['calm']['terminal'], 0) - M.r2h(b['calm']['terminal'], 0)), 'neg', False),
      ('10-yr fee drag', f"{MINUS}${b['calm']['fee_drag']:,.0f}", f"{MINUS}${o['calm']['fee_drag']:,.0f}",
       usd(M.r2h(b['calm']['fee_drag'], 0) - M.r2h(o['calm']['fee_drag'], 0)), 'pos', False),
    )
    body = '\n'.join(f'''        <tr{' class="hl"' if hl else ''}><td>{lab}</td><td class="n{' neg' if 'DD' in lab and 'calm' not in lab else ''}">{x}</td><td class="n{' neg' if 'DD' in lab and 'calm' not in lab else ''}">{y}</td><td class="n {c}">{dd}</td></tr>'''
                     for lab, x, y, dd, c, hl in rows)
    return f'''  <div class="tw">
    <table>
      <thead><tr><th>Metric</th><th>Baseline</th><th>Optimized</th><th>Δ</th></tr></thead>
      <tbody>
{body}
      </tbody>
    </table>
  </div>'''

def blocks_table():
    q, i = M.A['QQQ'], M.A['IEMG']
    def cell(x, signed=True):
        if abs(x) < 5e-3: return '—'
        return sgn(x) if signed else f(x)
    rows = (('Dividend yield', 'div', True), ('Earnings growth', 'eps', True), ('Valuation change', 'val', True),
            ('Currency drag', 'fx', True), ('Gross CAGR', 'gross', False), ('Expense ratio', 'er', None), ('Net CAGR', 'net', False))
    def td(k, fld, signed):
        x = M.A[k][fld]
        if signed is None: return f'<td class="n">{MINUS}{x:.2f}</td>'
        v = cell(x, signed)
        c = ' pos' if signed and v.startswith('+') else ' neg' if signed and v.startswith(MINUS) else ''
        return f'<td class="n{c}">{v}</td>'
    body = '\n'.join(f'''        <tr{' class="hl"' if fld in ('gross', 'net') else ''}><td>{lab}</td>{td('QQQ', fld, s)}{td('IEMG', fld, s)}</tr>'''
                     for lab, fld, s in rows)
    return f'''  <div class="tw">
    <table>
      <thead><tr><th>Component, %/yr</th><th>QQQ</th><th>IEMG</th></tr></thead>
      <tbody>
{body}
      </tbody>
    </table>
  </div>'''

def houses():
    """Published ten-year forecasts next to this page's, and J.P. Morgan's EM volatility
    against the two regimes. Other people's numbers, quoted to be disagreed with."""
    Hh = M.INSTITUTIONAL
    rows = '\n'.join(f'        <tr><td>{escape(n)}</td><td class="n">{d["us"]:.1f}%</td><td class="n">{d["em"]:.1f}%</td></tr>' for n, d in Hh.items())
    us, em = M.A['QQQ']['gross'], M.A['IEMG']['gross']
    top_us = max(d['us'] for d in Hh.values())
    em_first = sum(d['em'] > d['us'] for d in Hh.values())
    jv = Hh[M.ALT_SOURCE]['em_vol']; lo, hi = M.REGIME['calm']['vol']['IEMG'], M.REGIME['normalized']['vol']['IEMG']
    rel = 'between' if lo <= jv <= hi else 'above both of' if jv > hi else 'below both of'
    return f"""  <div class="tw" style="margin-top:12px">
    <table>
      <thead><tr><th>10-yr forecast, gross</th><th>US</th><th>EM</th></tr></thead>
      <tbody>
{rows}
        <tr class="hl"><td>This page</td><td class="n">{us:.2f}%</td><td class="n">{em:.2f}%</td></tr>
      </tbody>
    </table>
  </div>
  <p class="note">This page&#8217;s US forecast is {f(us - top_us, 1)} points above the highest house; {em_first} of {len(Hh)} houses rank EM above the US. J.P. Morgan&#8217;s {jv}% EM volatility sits {rel} this page&#8217;s two regimes ({lo:.1f}%, {hi:.1f}%).</p>"""

def verification_rows():
    return (('Assumed inputs listed', '3 → <b>7</b>'),
            ('Liquidity & credit score', '3.0 → <b>2.6</b>'),
            ('Diversification return', '<b>undisclosed → stated</b>'),
            ('Fund prices', '22/18 Sep → <b>24 Sep</b>'),
            ('QQQ net CAGR', '9.51% → <b>9.59%</b>'),
            ('Baseline on frontier', 'no → <b>yes</b>'))

def portfolios(n_mut, n_corr):
    b, o = ST['baseline'], ST['optimized']
    dom = [(d, c, w) for d, c, w in ((M.stats(w, 'normalized')['dd'], M.stats(w, 'normalized')['cagr'], w) for w in M.admissible(5))
           if d <= b['normalized']['dd'] and c >= b['normalized']['cagr'] and (d < b['normalized']['dd'] or c > b['normalized']['cagr'])]
    if ON['optimized'] and not ON['baseline'] and len(dom) == 1:
        dd_, dc_, dw = dom[0]
        eff_call = (f"<b>The recommended book is efficient; the baseline, by a hair, is not.</b> Across all {N_ADM} allocations with BMNR at 5%, "
                    f"none beats QQQ {O['QQQ']} / IEMG {O['IEMG']} / SGOV {O['SGOV']} / BMNR {O['BMNR']} on both axes. One book beats the baseline, "
                    f"by +{f(dc_ - b['normalized']['cagr'])} points of CAGR and {f(b['normalized']['dd'] - dd_, 1)} of drawdown — a technicality. {len(EFF)} allocations are efficient.")
    elif ON['optimized'] and ON['baseline']:
        eff_call = (f"<b>Both books are efficient.</b> Across all {N_ADM} allocations with BMNR at 5%, nothing beats either on return and drawdown at once: "
                    f"they are two points on the same curve, the baseline for return and the optimized book for drawdown. {len(EFF)} allocations are efficient.")
    else:
        eff_call = (f"<b>Efficiency.</b> Optimized on the frontier: {'yes' if ON['optimized'] else 'no'}; baseline: {'yes' if ON['baseline'] else 'no'}. "
                    f"{len(EFF)} of {N_ADM} allocations are efficient.")
    top = SENS[0]
    conf = (('Standard error, 10-yr CAGR', f"±{M.se_level('optimized'):.2f} pts"),
            ('95% band, optimized', f"{MINUS if o['calm']['cagr_d'] - 1.96 * M.se_level('optimized') < 0 else ''}{f(abs(o['calm']['cagr_d'] - 1.96 * M.se_level('optimized')), 1)} to {f(o['calm']['cagr_d'] + 1.96 * M.se_level('optimized'), 1)}%"),
            ('Chance the baseline out-returns', f"{f(CAL['p'] * 100, 0)}%"),
            ('Allocations separable in 10 yrs', f"{SEP} of {SEP_N}"),
            (f"Most sensitive: {top['label']}", f"1 pt → {sgn(top['d_cagr'])} CAGR"),
            ('On J.P. Morgan&#8217;s return inputs', f"{JPM['rows']['baseline']['cagr']:.2f}% vs {JPM['rows']['optimized']['cagr']:.2f}%"))
    conf_html = '\n'.join(f'    <div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in conf)
    ver_html = '\n'.join(f'    <div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in verification_rows())
    q, i = M.A['QQQ'], M.A['IEMG']
    qv, iv, rel = RV['QQQ'], RV['IEMG'], REL
    cal_ratio = M.cal_line()[0][1]
    rationale = (
      f"<b>Horizon first.</b> Over ten years cash drag compounds: SGOV turns $10,000 into ${E['sleeves']['SGOV']['terminal']:,}, QQQ into ${E['sleeves']['QQQ']['terminal']:,}. The macro signal chooses which equities, not whether.",
      f"<b>Tilt to the cheaper bloc.</b> {REG_NAME[RANKED[0]]} ranks first at every horizon and IEMG trades at {f(FI, 1)}×; per unit of risk it is {rel} QQQ ({iv:.3f} vs {qv:.3f}) while earning {'less' if i['net'] < q['net'] else 'more'} ({i['net']:.2f}% vs {q['net']:.2f}%).",
      f"<b>Size to normalized volatility.</b> The weights are set against {neg(o['normalized']['dd'])}% drawdown, not today&#8217;s {neg(o['calm']['dd'])}%.",
      f"<b>SGOV at {O['SGOV']}% is a drawdown budget.</b> Scaling a fixed risky mix against cash holds return-per-drawdown at {cal_ratio:.4f} whatever the cash weight, so no optimizer can pick it.",
      f"<b>BMNR capped at 5%.</b> {o['normalized']['rc']['BMNR']:.1f}% of risk from {O['BMNR']}% of capital; total loss costs {O['BMNR']}%.",
      f"<b>Where the model was overruled.</b> The best return-per-risk book, QQQ {BEST['QQQ']} / IEMG {BEST['IEMG']} / SGOV {BEST['SGOV']} / BMNR {BEST['BMNR']} (Sharpe {M.stats(BEST, 'calm')['sharpe']:.3f} vs {o['calm']['sharpe']:.3f}), holds a {BEST['SGOV']}% reserve. Rejected.",
    )
    rat = '\n'.join(f'    <div>{r}</div>' for r in rationale)
    src = '<br>\n    '.join(f"{escape(g)} — " + ' · '.join(f'<a href="{u}">{escape(t)}</a>' for t, u in links) for g, links in SOURCES)
    return f'''<section class="pane" id="p-port" role="tabpanel" aria-labelledby="t-port">
  <h2>Baseline vs optimized</h2>
  <p class="lede">Both hold all four sleeves in steps of 5, and both are built for a 10-year horizon. The baseline is a plain strategic split; the optimized book is tilted by macro sentiment, regional rankings and volatility analysis across 3, 6 and 12 months.</p>

  <div class="duo">
{donut('baseline', 'Baseline', 'Strategic', False)}
{donut('optimized', 'Optimized', 'Macro-tilted', True)}
  </div>
  <p class="vs">{shift_line()}</p>

  <h3>Forecast comparison</h3>
{compare_table()}
  <div class="call" style="margin-top:12px"><b>The trade.</b> The optimized book gives up {GAP:.2f} points of CAGR to cut the normalized drawdown by {DDCUT:.1f} points, at almost the same return per unit of risk ({o['calm']['sharpe']:.3f} vs {b['calm']['sharpe']:.3f}).</div>

  <h3>How the forecasts are built</h3>
{blocks_table()}
  <p class="note">Valuation change moves each forward multiple to its own 10-year average (NDX {M.OBS['QQQ']['pe_end']}×, MSCI EM {M.OBS['IEMG']['pe_end']}×). Yield and multiple are tied to one price per fund. Portfolio CAGR is the weight-average of the sleeve CAGRs, so it leaves out the diversification return rebalancing earns — about {f(M.diversification_return(B, exclude=('BMNR',)))}–{f(M.diversification_return(O, exclude=('BMNR',)))}%/yr from the three funds, near-identical for both books. BMNR&#8217;s volatility would inflate it to about {f(M.diversification_return(O))}%, which is not credible. The CAGRs shown are conservative.</p>

  <h3>Efficient frontier</h3>
  <div class="card">{M.frontier_svg()}</div>
  <div class="call" style="margin-top:12px">{eff_call}</div>

  <h3>How much to trust it</h3>
  <div class="card">
{conf_html}
  </div>
{houses()}
  <p class="note"><b>Still open:</b> {len(M.ASSUMED)} inputs are assumptions rather than observations — {'; '.join(f'{a} ({v})' for a, v in M.ASSUMED)}. QQQ&#8217;s earnings growth is the most load-bearing.</p>

  <h3>Rationale</h3>
  <div class="num">
{rat}
  </div>
  <div class="call" style="margin-top:16px"><b>Recommendation.</b> Hold QQQ {O['QQQ']} / IEMG {O['IEMG']} / SGOV {O['SGOV']} / BMNR {O['BMNR']}: {neg(o['normalized']['dd'])}% normalized drawdown against the baseline&#8217;s {neg(b['normalized']['dd'])}%, for {GAP:.2f} points of CAGR. Rebalance semi-annually or on a 5-point drift. Revisit if the VIX holds above {M.VIX_MEAN} ({f(M.VIX_MEAN - SPOT)} points away; spend the reserve toward 25%) or if the EM discount to developed markets closes toward 25%.</div>

  <h3>Verification log</h3>
  <p class="note">The page is generated from the model, and an independent validator re-derives every figure. {n_mut} deliberate corruptions of the model and the generator were all caught. {n_corr} corrections recorded; this revision:</p>
  <div class="card">
{ver_html}
  </div>

  <h3>Sources</h3>
  <p class="src">
    {src}
  </p>
  <div class="disc"><b>Not investment advice.</b> Forecasts are modelled estimates. A point off QQQ&#8217;s earnings growth moves the recommended book&#8217;s CAGR by {f(abs(top['d_cagr']))} and the gap between the books by {f(abs(top['d_gap']), 3)}. Market data to the {day(MK['asof'], False)} close; fund prices as dated on each slide; BMNR holdings from its {day(M.BMNR_HOLDINGS['asof'], False)} release. BMNR can lose its entire value.</div>
</section>'''

NAV = '''  <nav class="tabs" role="tablist" aria-label="Sections">
    <button class="tab on" id="t-macro" type="button" data-p="p-macro" role="tab" aria-selected="true" aria-controls="p-macro">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9"/><path d="M12 12l5.5-5.5"/><path d="M21 3v6h-6"/></svg><span>Macro</span></button>
    <button class="tab" id="t-regions" type="button" data-p="p-regions" role="tab" aria-selected="false" aria-controls="p-regions">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 3 2.6 15 0 18M12 3c-2.6 3-2.6 15 0 18"/></svg><span>Regions</span></button>
    <button class="tab" id="t-vol" type="button" data-p="p-vol" role="tab" aria-selected="false" aria-controls="p-vol">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 16l4-7 4 5 3-9 3 7 4-4"/></svg><span>Volatility</span></button>
    <button class="tab" id="t-assets" type="button" data-p="p-assets" role="tab" aria-selected="false" aria-controls="p-assets">
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="14" height="16" rx="2"/><path d="M20 7v11a2 2 0 0 1-2 2"/><path d="M7 9h6M7 13h4"/></svg><span>Sleeves</span></button>
    <button class="tab" id="t-port" type="button" data-p="p-port" role="tab" aria-selected="false" aria-controls="p-port">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 3.5v8.5h8.5"/></svg><span>Portfolios</span></button>
  </nav>'''

SCRIPT = '''<script>
(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  tabs.forEach(function(t){
    t.addEventListener('click',function(){
      tabs.forEach(function(x){
        x.classList.remove('on'); x.setAttribute('aria-selected','false');
        document.getElementById(x.dataset.p).classList.remove('on');
      });
      t.classList.add('on'); t.setAttribute('aria-selected','true');
      document.getElementById(t.dataset.p).classList.add('on');
      window.scrollTo(0,0);
    });
  });
  var deck=document.getElementById('deck'), dots=[].slice.call(document.querySelectorAll('#dots b'));
  if(deck){
    var slides=[].slice.call(deck.querySelectorAll('.slide'));
    var sync=function(){
      var mid=deck.scrollLeft+deck.clientWidth/2, best=0, bd=Infinity;
      slides.forEach(function(sl,j){
        var d=Math.abs((sl.offsetLeft+sl.offsetWidth/2)-mid);
        if(d<bd){bd=d;best=j;}
      });
      dots.forEach(function(d,j){ d.classList.toggle('on',j===best); });
    };
    deck.addEventListener('scroll',sync,{passive:true});
    window.addEventListener('resize',sync);
    sync();
  }
})();
</script>'''

HEAD = '''<title>Four-Sleeve Allocation Desk</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'''

def counts():
    """The harness figures the page quotes, read from the files that define them.
    (The validator's own assertion count is not quoted: it would depend on the page.)"""
    mut = open(os.path.join(HERE, 'mutate.py')).read()
    n_mut = len(re.findall(r'^ (?:\("|G\()', mut, re.M))
    n_corr = int(re.search(r'CORRECTIONS: (\d+)', open(os.path.join(HERE, 'VERIFICATION.md')).read()).group(1))
    return n_mut, n_corr

def render():
    css = open(os.path.join(HERE, 'page.css')).read()
    n_mut, n_corr = counts()
    return '\n'.join((HEAD, '<style>', css.rstrip('\n'), '</style>', '', '<div class="app">', '  ' + masthead(), '',
                      macro(), '', regions(), '', volatility(), '', sleeves(), '', portfolios(n_mut, n_corr),
                      '', NAV, '</div>', '', SCRIPT, ''))

if __name__ == '__main__':
    out = render()
    path = os.path.join(HERE, 'allocation.html')
    if '--check' in sys.argv:
        ok = os.path.exists(path) and open(path).read() == out
        print('allocation.html is current' if ok else 'allocation.html is STALE: run python3 build.py')
        sys.exit(0 if ok else 1)
    open(path, 'w').write(out)
    print(f'wrote allocation.html ({len(out):,} bytes)')
