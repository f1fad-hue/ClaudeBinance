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
    payrolls='+29,000 in September against 84,000 expected, unemployment 4.2%',
    ism='ISM manufacturing 54.5 and services 54.9',
    claims='claims 199,000, a fifth week under 200,000; September retail sales +0.8%, +0.2% excluding gasoline',
    umich=('46.3', 'Michigan, preliminary October', 'near its May record low'),
    imf_world='IMF (October): 3.1% world growth in 2026',
    cpi='September CPI 3.7% y/y and core 2.6%, both above forecast; producer prices +1.3% m/m (6.3% y/y), the most since March 2022',
    ism_prices='ISM prices paid 77.9 (manufacturing) and 74.0 (services)',
    infl_exp='one-year inflation expectations 4.7% (Michigan)',
    fed_vote='12–0',
    fed_odds='futures put an October hike at 54% after the CPI but about 15% once Chair Warsh declined to prejudge meetings on 16 Oct (CME FedWatch); a December hike is still priced as likely',
    hy_oas=('3.23%', '15 Oct', '2.80%', '24 Sep'),
    dollar=('an 18-month high', '5 Oct'),
    ust10_high='highest close since 2002',
    # the day's lead, dated so validate.py can refuse it once MARKET moves on
    lead=('2026-10-19', 'Tech rebounded', 'Chipmakers led a rebound from the S&P 500’s worst week since June, the Nasdaq rising 1.1% and the S&P 0.4%, and China’s third-quarter growth beat forecasts at 4.5%'),
    geo='Missile attacks on Saudi Arabia, Ukrainian strikes on Russian refineries and Iranian attacks on Hormuz shipping keep supply at risk, and on 19 Oct the IRGC threatened the strait’s undersea cables. President Trump has ruled out resuming strikes on Iran before the 3 Nov midterms, but the US blockade stays in force and a third carrier could arrive by month end',
    imf_asia='IMF (October): China 4.5% and India 7.0% in 2026. China’s third quarter grew 4.5%, above the 4.4% expected, on exports up 36.3% in September, though property investment fell 20.6% in nine months',
    eu='Composite PMI 53.1 in September, the highest since April 2023, but flash inflation jumped to 3.8% and the ECB hiked to 2.50% into 0.9% growth',
    bmnr_stop='The chairman said on 7 Oct that buying stops at 5% of supply, which ends most of the issuance behind that drag',
    em_dm_discount='40% discount to developed markets (11 Sep)',
    sgov_sec='3.71%', sgov_sec_label='30-day SEC yield, 7 Oct',
    # peak to trough: Nasdaq-100 2000-02; QQQ 2007-09 (Bloomberg, via Advisor Perspectives),
    # 2020 (Portfolioslab; "close to 30%" elsewhere) and 2021-22 (Portfolioslab -35.1%, QQQM
    # -35.6%). Rev. 26 and earlier said -27% for 2020 and -50 to -53% for 2007-09.
    qqq_hist=(('2000–02 dot-com', '≈−83%'), ('2007–09 financial crisis', '≈−53.5%'),
              ('2020 COVID crash', '≈−28.6%'), ('2022 rate hikes', '−35 to −36%')),
)

SOURCES = (
    ('Funds', (('iShares SGOV', 'https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf'),
               ('iShares IEMG', 'https://www.ishares.com/us/products/244050/ishares-core-msci-emerging-markets-etf'),
               ('Invesco QQQ', 'https://www.invesco.com/qqq-etf/en/performance.html'))),
    ('Valuation', (('Siblis Nasdaq-100 P/E', 'https://siblisresearch.com/data/nasdaq-100-pe-ratio/'),
                   ('Siblis EM valuations', 'https://siblisresearch.com/data/emerging-markets-valuations/'),
                   ('MSCI EM discount', 'https://www.msci.com/indexes/markets-in-motion/visualizations/em-gains-but-discount-to-developed-markets-deepens'))),
    ('Policy & macro', (('FOMC statement, 16 Sep 2026', 'https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm'),
                        ('FOMC minutes, 7 Oct 2026', 'https://www.federalreserve.gov/newsevents/pressreleases/monetary20261007a.htm'),
                        ('ISM services, September', 'https://www.prnewswire.com/news-releases/services-pmi-at-54-9-september-2026-ism-services-pmi-report-302898421.html'),
                        ('ECB, September 2026', 'https://www.ecb.europa.eu/press/press_conference/visual-mps/2026/html/mopo_statement_explained_september.en.html'),
                        ('BLS CPI', 'https://www.bls.gov/news.release/cpi.nr0.htm'),
                        ('S&P Global flash PMI', 'https://www.pmi.spglobal.com/Public/Home/PressRelease/35c60149cdbe461fb6bc3c959a58a551'),
                        ('IMF WEO', 'https://www.imf.org/external/datamapper/index.php'))),
    ('Trend', (('iShares IVV (S&P 500)', 'https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf'),
               ('iShares EEM (MSCI EM)', 'https://www.ishares.com/us/products/239637/ishares-msci-emerging-markets-etf'),
               ('iShares STOXX Europe 600', 'https://www.ishares.com/ch/individual/en/products/251931/ishares-stoxx-europe-600-ucits-etf-de-fund'),
               ('Nasdaq-100 factsheet', 'https://indexes.nasdaqomx.com/docs/FS_XNDX.pdf'),
               ('Invesco QQQ quarterly', 'https://www.invesco.com/qqq-etf/en/etf-insights/qqq-quarterly-outlook.html'))),
    ('Rates & volatility', (('FRED 10-yr Treasury', 'https://fred.stlouisfed.org/series/dgs10'),
                            ('Cboe VIX history', 'https://www.cboe.com/tradable-products/vix/vix-historical-data'),
                            ('FRED VIX', 'https://fred.stlouisfed.org/series/VIXCLS'),
                            ('CME FedWatch', 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html'))),
    ('Outside forecasts', (('J.P. Morgan LTCMA 2026', 'https://am.jpmorgan.com/us/en/asset-management/institutional/insights/portfolio-insights/ltcma/'),
                           ('Vanguard VCMM', 'https://corporate.vanguard.com/content/corporatesite/us/en/corp/vemo/vemo-return-forecasts'),
                           ('Morningstar survey, 2026 (Fidelity, BlackRock)', 'https://www.morningstar.com/markets/experts-forecast-stock-bond-returns-2026-edition'),
                           ('BlackRock CMAs', 'https://www.blackrock.com/institutions/en-global/institutional-insights/thought-leadership/capital-market-assumptions'))),
    ('BMNR', (('Holdings release, 19 Oct 2026', 'https://www.prnewswire.com/apac/news-releases/bitmine-immersion-technologies-bmnr-announces-eth-holdings-reach-6-04-million-tokens-and-total-crypto-and-total-cash--marketable-securities-holdings-of-15-1-billion-302912189.html'),
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
def mf(x, dp=1): return f(x, dp).replace('-', MINUS)
def usd(x): return ('+' if x > 0 else MINUS if x < 0 else '') + f'${abs(x):,.0f}'
def day(iso, short=True):
    m = MONTHS[int(iso[5:7]) - 1]
    return f'{int(iso[8:])} {m[:3] if short else m}'

# ── everything the page states, computed once ────────────────────────────────
E   = M.export()
B, O = M.PORTFOLIOS['baseline'], M.PORTFOLIOS['optimized']
ST  = {n: {r: M.stats(w, r) for r in M.REGIME} for n, w in M.PORTFOLIOS.items()}
SPOT, PREV = M.VIX_SPOT, M.VIX_SERIES[-2][1]
AVG = M.VIX_AVG                     # what the rule's volatility pillar reads
MK  = M.MARKET
FQ, FI = M.OBS['QQQ']['fwd_pe'], M.OBS['IEMG']['fwd_pe']
assert FI < FQ, 'the page calls EM the cheaper bloc'
def vs_avg(x, avg):
    """A multiple against its 10-year average, judged at the one decimal the page shows.
    Rev. 28 and earlier typed "above" for QQQ; at $728 its 22.8x is below the 22.9x average."""
    x1 = M.r2h(x, 1)
    return 'above' if x1 > avg else 'below' if x1 < avg else 'at'
EFF, N_ADM = M.efficient()
ON  = {n: any(w == M.PORTFOLIOS[n] for _, _, w in EFF) for n in M.PORTFOLIOS}
CAL = M.calibration(B, O)
SENS, _, _ = M.sensitivity()
BEST = M.best_sharpe('calm')
GAP = M.r2h(M.r2h(ST['baseline']['calm']['cagr_d']) - M.r2h(ST['optimized']['calm']['cagr_d']))
DDCUT = M.r2h(M.r2h(ST['baseline']['normalized']['dd'], 1) - M.r2h(ST['optimized']['normalized']['dd'], 1), 1)
REG_NAME = {'Asia / EM': 'Asia / Emerging', 'United States': 'United States', 'Europe': 'Europe'}
REG_BAR  = {'Asia / EM': 'var(--iemg)', 'United States': 'var(--qqq)', 'Europe': 'var(--neg)'}
RANKED = sorted(E['regions'], key=lambda k: -E['regions'][k]['mean'])
LEADS_ALL = all(E['regions'][RANKED[0]]['scores'][h] > max(E['regions'][k]['scores'][h] for k in RANKED[1:]) for h in range(4))
COL = {'QQQ': '#2B5CE6', 'IEMG': '#0F9B8E', 'SGOV': '#8A94A6', 'BMNR': '#E07A2F'}
# return per unit of calm volatility above cash, and the relation the prose must state
RV = {k: (M.A[k]['net'] - M.A['SGOV']['net']) / M.REGIME['calm']['vol'][k] for k in ('QQQ', 'IEMG')}
def rel_word(rq, ri):
    """IEMG against QQQ on return per unit of calm risk: within 0.01 is level."""
    return 'level with' if abs(rq - ri) < 0.01 else ('ahead of' if ri > rq else 'behind')
REL = rel_word(RV['QQQ'], RV['IEMG'])
REL_CAP = REL[0].upper() + REL[1:]

SIG = {1: 'up', 0: 'nu', -1: 'down'}   # not 'dn': that is the donut card's class

def tone(s5):
    return 'var(--pos)' if s5 >= 3.4 else 'var(--neg)' if s5 < 2.0 else 'var(--warn)'

# ── panes ─────────────────────────────────────────────────────────────────────
def masthead():
    return f'''<header class="mast">
    <h1>Four-Sleeve Allocation Desk</h1>
    <p class="sub">Macro-weighted portfolio construction across SGOV · QQQ · IEMG · BMNR</p>
    <div class="stamp">
      <span>As of {day(MK['asof'])} {MK['asof'][:4]}</span><span>10-yr horizon</span><span>Fed {M.FED_RANGE[0]:.2f}–{M.FED_RANGE[1]:.2f}%</span><span>VIX {SPOT:.2f}{f' ({SPOT_DATE})' if VIX_STALE else ''}</span><span>Brent ${MK['brent']:.2f}</span><span>UST 10y {MK['ust10']:.2f}%{f' ({day(MK["ust10_asof"])})' if MK['ust10_asof'] != MK['asof'] else ''}</span><span>Rev. {M.REVISION} · re-verified</span>
    </div>
  </header>'''

def growth_clause():
    """The gauge note names growth by its own score. Rev. 24 hard-coded "Strong growth",
    which a 29,000 payrolls print and a 3.2 score made false."""
    g5 = dict((n, s) for n, s, _ in E['gauge']['drivers'])['Growth momentum']
    return ('Strong growth is' if g5 >= 3.4 else 'Growth, positive but softening, is' if g5 >= 3.0
            else 'Weak growth adds to the drag and is')

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
    <p class="gauge-note">Six weighted drivers, each scored 1–5 where 3 is neutral. {growth_clause()} outweighed by inflation, a hiking Fed and a realised energy shock.</p>
  </div>'''

def ust10_note():
    """'Its highest since 2007' is true only of a close that equals the high on file; any
    other close says where and when the high was. (Rev. 23 keyed this on the sign of the
    day's change, which a rise that stops short of the high would have got wrong.)"""
    if MK['ust10'] >= MK['ust10_high']:
        return f"its {FACTS['ust10_high']}"
    return (f"{round((MK['ust10_high'] - MK['ust10']) * 100):.0f}bp below the {MK['ust10_high']:.2f}% of "
            f"{day(MK['ust10_high_date'])}, the {FACTS['ust10_high']}")

def spread_verb():
    """The spread's direction between its two dated levels, read from the levels: Rev. 26
    and earlier typed "widened", which would have stayed on the page the day it narrowed."""
    now, then = (float(FACTS['hy_oas'][i].rstrip('%')) for i in (0, 2))
    return 'widened' if now > then else 'narrowed' if now < then else 'held'

def bond_headline():
    """The macro lead's headline. "The sell-off extended" only of a close at a new high;
    Rev. 26 and earlier keyed it on the day's sign, so a 2bp uptick 7bp under the high, in
    a week the 10-year fell, would have been called an extension of the sell-off."""
    if MK['ust10'] >= MK['ust10_high'] and MK['ust10_chg_bp'] > 0:
        return 'The bond sell-off extended'
    return ('Yields edged up' if MK['ust10_chg_bp'] > 0 else
            'Yields eased' if MK['ust10_chg_bp'] < 0 else 'Yields held')

def vix_price(x):
    """What protection costs against the long-run mean. Within 5% either side it is near its
    long-run price: Rev. 29 and earlier called 18.44, 2% under an 18.9 mean, "cheap"."""
    d = (1 - x / M.VIX_MEAN) * 100
    return 'cheap' if d >= 5 else 'dear' if d <= -5 else 'close to its long-run price'

def vix_rel(x, dp):
    """The VIX's distance from its long-run mean, in words that stay true either side."""
    d = (1 - x / M.VIX_MEAN) * 100
    return f"{f(abs(d), dp)}% {'below' if d >= 0 else 'above'}"

# When the latest VIX close is held back, every sentence that quotes the VIX says which
# close it is; the held date must be the market date, or the page would mix three days.
VIX_STALE = M.VIX_HELD if M.VIX_ASOF != MK['asof'] else None
assert VIX_STALE is None or VIX_STALE['asof'] == MK['asof'], 'VIX is stale but no held close is recorded'
SPOT_DATE = day(M.VIX_ASOF)
def lead_fact():
    """The dated lead, only on its own market date: refused once MARKET moves on."""
    return FACTS['lead'] if FACTS['lead'][0] == MK['asof'] else None
UST_DATE = day(MK['ust10_asof'])

def bp(x):
    return f"{'+' if x >= 0 else MINUS}{abs(x)}bp"

def lead():
    """The macro lead: the day's dated event when there is one, else the bond move. The
    10-year carries its own date, since its close can lag the market date."""
    ten = f"the 10-year closed at {MK['ust10']:.2f}% on {UST_DATE} ({bp(MK['ust10_chg_bp'])}), {ust10_note()}"
    brent = f"Brent settled {'up' if MK['brent_chg_pct'] > 0 else 'down'} {f(abs(MK['brent_chg_pct']), 1)}% at <b>${MK['brent']:.2f}</b>"
    ld = lead_fact()
    if ld:
        return f"<b>{ld[1]}.</b> {ld[2]}. {vix_lead()} {brent}; {ten}."
    return f"<b>{bond_headline()}.</b> {ten[0].upper() + ten[1:]}. {brent}. {vix_lead()}"

def revisit_txt():
    """The recommendation's VIX trigger, read from the average the rule uses; it runs into
    "... if the EM discount closes toward 25%". Through Rev. 28 it read the last close."""
    if AVG < M.VIX_MEAN:
        to = f" to the {SPOT_DATE} close" if VIX_STALE else ''
        hot = f", though the {SPOT_DATE} close was {SPOT:.2f}" if SPOT >= M.VIX_MEAN else ''
        return (f"revisit if the VIX holds above {M.VIX_MEAN} (its {M.VIX_WINDOW}-session average{to} is {AVG:.2f}, "
                f"{f(M.VIX_MEAN - AVG)} points away{hot}; spend the reserve toward {O['SGOV'] - M.RULE['step']}%) or")
    moved = next(mv for p, _, mv, _ in M.TILT['steps'] if p == 'Volatility') != 'no move'
    return (f"the VIX has held above its {M.VIX_MEAN} mean, so the rule has "
            f"{'spent a step of the reserve' if moved else 'left the reserve at its floor'}; revisit")

def regime_warn(oc, on):
    """The two-regime warning, true either side of the mean. Below it the normalized column
    is the deeper; well above it today's can be. Rev. 28 and earlier assumed below."""
    if on['dd'] >= oc['dd']:
        return (f"<b>Weights are sized to the second column.</b> A VIX at its {M.VIX_MEAN} mean (volatility ×{f(M.UPLIFT, 2)}) "
                f"and crisis correlations take the optimized book&#8217;s {neg(oc['dd'])}% drawdown to {neg(on['dd'])}%; "
                f"the {O['SGOV']}% reserve is sized for that.")
    return (f"<b>Today is the deeper column.</b> With the VIX {vix_rel(SPOT, 0)} its {M.VIX_MEAN} mean, the optimized "
            f"book&#8217;s {neg(oc['dd'])}% calm drawdown exceeds the {neg(on['dd'])}% normalized one the weights are sized to.")

def vix_lead():
    if VIX_STALE:
        return (f"The VIX&#8217;s {day(VIX_STALE['asof'])} close is held back — sources report {VIX_STALE['lo']:.2f} to "
                f"{VIX_STALE['hi']:.2f} — so the page stays on <b>{SPOT:.2f}</b>, the {SPOT_DATE} close.")
    chg = (SPOT / PREV - 1) * 100
    return f"The VIX {'rose' if chg > 0 else 'fell'} {f(abs(chg), 1)}% to <b>{SPOT:.2f}</b>."

def driver_notes():
    disc = (1 - FI / FQ) * 100
    return {
      'Growth momentum': f"Payrolls {FACTS['payrolls']}; {FACTS['claims']}. {FACTS['ism']}, but consumer sentiment fell to {FACTS['umich'][0]} ({FACTS['umich'][1]}), {FACTS['umich'][2]}. {FACTS['imf_world']}.",
      'Inflation trajectory': f"{FACTS['cpi']}; {FACTS['ism_prices']}; {FACTS['infl_exp']}.",
      'Monetary policy': f"The Fed hiked {FACTS['fed_vote']} on {day(M.FOMC_DATE)} to {M.FED_RANGE[0]:.2f}–{M.FED_RANGE[1]:.2f}%; {FACTS['fed_odds']}.",
      'Liquidity & credit': f"The 10-year closed at {MK['ust10']:.2f}% on {UST_DATE} ({bp(MK['ust10_chg_bp'])}), {ust10_note()}. High-yield spreads {spread_verb()} to {FACTS['hy_oas'][0]} ({FACTS['hy_oas'][1]}) from {FACTS['hy_oas'][2]} ({FACTS['hy_oas'][3]}); the dollar index touched {FACTS['dollar'][0]} on {FACTS['dollar'][1]}.",
      'Valuation & positioning': f"Nasdaq-100 at {f(FQ, 1)}× forward vs EM at {f(FI, 1)}×, a {f(disc, 0)}% discount. The VIX at {SPOT:.2f} ({SPOT_DATE}) sits {vix_rel(SPOT, 0)} its {M.VIX_MEAN} mean: protection is {vix_price(SPOT)}.",
      'Geopolitical risk': f"{FACTS['geo']}. Brent settled at ${MK['brent']:.2f} on {day(MK['asof'])}.",
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
    sg = M.A['SGOV']
    trans = (
      ('SGOV', 'sgov', SIG[M.CORRELATED['SGOV'][0]], M.CORRELATED['SGOV'][1], f"Bills reprice with the Fed: the {M.SGOV_GROSS:g}% midpoint nets {f(sg['net'])}% at near-zero duration."),
      ('QQQ', 'qqq', SIG[M.CORRELATED['QQQ'][0]], M.CORRELATED['QQQ'][1],
       f"Real earnings momentum, but at {f(FQ, 1)}× forward, above its {M.OBS['QQQ']['pe_end']}× average, it is the sleeve most exposed to a {MK['ust10']:.2f}% 10-year."
       if vs_avg(FQ, M.OBS['QQQ']['pe_end']) == 'above' else
       f"Real earnings momentum at {f(FQ, 1)}× forward, {vs_avg(FQ, M.OBS['QQQ']['pe_end'])} its {M.OBS['QQQ']['pe_end']}× average, but still the sleeve most exposed to a {MK['ust10']:.2f}% 10-year."),
      ('IEMG', 'iemg', SIG[M.CORRELATED['IEMG'][0]], M.CORRELATED['IEMG'][1], f"The cheapest bloc at {f(FI, 1)}×, {vs_avg(FI, M.OBS['IEMG']['pe_end'])} its {M.OBS['IEMG']['pe_end']}× average; the dollar and ${MK['brent']:.0f} oil are near-term headwinds."),
      ('BMNR', 'bmnr', SIG[M.CORRELATED['BMNR'][0]], M.CORRELATED['BMNR'][1], f"High-beta ETH with a {M.REGIME['calm']['rho'][('QQQ','BMNR')]:.2f} correlation to QQQ: it fails when equities fail."),
    )
    tr = '\n'.join(f'''    <div class="corr-row">
      <div class="tick" style="background:var(--{c})">{t}</div>
      <div class="corr-b"><span class="sig {sig}">{lab}</span><br>{escape(txt)}</div>
    </div>''' for t, c, sig, lab, txt in trans)
    return f'''<section class="pane on" id="p-macro" role="tabpanel" aria-labelledby="t-macro">
  <h2>Macro drivers</h2>
  <p class="lede">Six forces that set this book&#8217;s return and risk, and how each reaches the four holdings.</p>
  <div class="warnbox">{lead()}</div>

  {gauge()}

  <h3>Composite inputs</h3>
  <div class="card">
{chr(10).join(rows)}
  </div>

  <h3>Correlated transmission</h3>
  <div class="corr">
{tr}
  </div>

  <div class="call" style="margin-top:16px"><b>The core tension.</b> Growth is real but met by tightening, a {MK['ust10']:.2f}% 10-year and ${MK['brent']:.0f} oil: stay invested, tilt to the cheaper bloc, and hold a reserve.</div>
</section>'''

def regions():
    notes = {
      'Asia / EM': f"{FACTS['imf_asia']}. Equities trade at {f(FI, 1)}× forward, a {FACTS['em_dm_discount']}.",
      'United States': f"The strongest productivity cycle, against the richest multiple ({f(FQ, 1)}×) and a {MK['ust10']:.2f}% 10-year.",
      'Europe': f"{FACTS['eu']}. The most energy-import-exposed bloc.",
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
  <p class="lede">Scored 1–5 at three tactical horizons and the 10-year anchor, ranked by mean score.</p>

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
  <div class="call" style="margin-top:14px"><b>Allocation consequence.</b> {REG_NAME[top]} leads by {lead[0]:.1f} at 3 months and {lead[1]:.1f} at 10 years{', which is why the optimized book tilts toward IEMG' if top == 'Asia / EM' and O['IEMG'] > B['IEMG'] else ''}. No sleeve holds Europe directly.</div>
</section>'''

TREND_LABEL = {'S&P 500': 'United States', 'Nasdaq-100': 'QQQ&#8217;s index', 'MSCI EM': 'IEMG&#8217;s market · Asia / EM',
               'STOXX Europe 600': 'Europe · in euros', 'Ether': 'BMNR&#8217;s asset'}
HORIZON = ('3 months', '6 months', '12 months')

TREND_SIG = {'Uptrend': 'up', 'Mixed': 'nu', 'Downtrend': 'down'}

def trend_rows():
    out = []
    for name, d in M.TREND.items():
        sc = M.trend_score(d['r']); v = M.trend_verdict(sc)
        cls = lambda x: ' pos' if x > M.TREND_DEADBAND else ' neg' if x < -M.TREND_DEADBAND else ''
        cells = ''.join(f'<td class="n{cls(x)}">{sgn(x, 1)}%</td>' for x in d['r'])
        # the verdict sits under the market's name: as a fifth column it ran off a phone screen
        out.append(f'        <tr><td>{escape(name)}<br><span class="tsub">{TREND_LABEL[name]}</span><br>'
                   f'<span class="sig {TREND_SIG[v]}">{v} ({sgn(sc, 0) if sc else 0})</span></td>{cells}</tr>')
    return '\n'.join(out)

def region_trend_leaders():
    """For each horizon, which regional market led: the trend's own regional ranking."""
    reg = {d['region']: d['r'] for d in M.TREND.values() if d['region']}
    return [max(reg, key=lambda k: reg[k][h]) for h in range(3)]

def ether_txt():
    """The trend's call on BMNR, read from ether's own signs and BMNR's weight. Through Rev. 29
    "(a 3-month rebound against a 12-month loss), so BMNR stays at its 5% cap" was typed."""
    r = M.TREND['Ether']['r']; v = M.trend_verdict(M.trend_score(r))
    word = {1: 'gain', 0: 'flat reading', -1: 'loss'}
    s3, s12 = M.trend_sign(r[0]), M.trend_sign(r[2])
    why = f"a 3-month {word[s3]} {'against' if s3 != s12 else 'and'} a 12-month {word[s12]}"
    if v == 'Downtrend':
        then = (f"but BMNR is already at its {M.RULE['floor']}% floor" if O['BMNR'] - M.RULE['step'] < M.RULE['floor']
                else 'so BMNR gives a step to cash')
    else:
        then = f"so BMNR stays at {O['BMNR']}%" + (', its cap' if O['BMNR'] == M.RULE['bmnr_cap'] else '')
    return f"ether is {v.lower()} ({why}), {then}"

def trend_pane():
    signs, net = M.relative_trend(M.SLEEVE_MARKET['QQQ'], M.SLEEVE_MARKET['IEMG'])
    q, e = M.TREND[M.SLEEVE_MARKET['QQQ']]['r'], M.TREND[M.SLEEVE_MARKET['IEMG']]['r']
    who = {1: 'QQQ', -1: 'IEMG', 0: 'neither'}
    rel = '; '.join(f"{HORIZON[h]} {who[signs[h]]} ({mf(q[h])} vs {mf(e[h])})" for h in range(3))
    lead = region_trend_leaders()
    agree = [HORIZON[h] for h in range(3) if lead[h] == RANKED[0]]
    differ = [f"over {HORIZON[h]} it ranks {the(lead[h])} first" for h in range(3) if lead[h] != RANKED[0]]
    agree_txt = ((f"The trend ranks {REG_NAME[RANKED[0]]} first over {' and '.join(agree)}, as the regional scores do" if agree else
                  f"Unlike the regional scores, the trend never ranks {REG_NAME[RANKED[0]]} first")
                 + (f"; {'; '.join(differ)}." if differ else "."))
    since = '; '.join(f"{k} {sgn((M.PRICES[k]['px'] / M.QE_CLOSE[k] - 1) * 100, 1)}% to {day(M.PRICES[k]['px_asof'])}" for k in ('QQQ', 'IEMG'))
    down = [k for k in ('QQQ', 'IEMG', 'BMNR') if M.trend_verdict(M.trend_score(M.TREND[M.SLEEVE_MARKET[k]]['r'])) == 'Downtrend']
    return f'''<section class="pane" id="p-trend" role="tabpanel" aria-labelledby="t-trend">
  <h2>Market trend</h2>
  <p class="lede">Total returns over 3, 6 and 12 months to {day(M.TREND_ASOF, False)}, the last quarter end, for the market behind each sleeve and region.</p>

  <div class="tw">
    <table class="trend">
      <thead><tr><th>Market · trend</th><th>3 mo</th><th>6 mo</th><th>12 mo</th></tr></thead>
      <tbody>
{trend_rows()}
      </tbody>
    </table>
  </div>
  <p class="note">Each horizon scores +1 or −1, or 0 inside ±{M.TREND_DEADBAND:g}%, weighted {M.TREND_WEIGHTS[0]}/{M.TREND_WEIGHTS[1]}/{M.TREND_WEIGHTS[2]}; +2 or more is an uptrend, −2 or less a downtrend. MSCI EM stands in for IEMG&#8217;s MSCI EM IMI benchmark. Since the quarter end: {since}.</p>

  <h3>QQQ against IEMG</h3>
  <div class="card">
    <p class="gauge-note" style="text-align:left;max-width:none;margin:0">{rel}. Weighted, that nets <b>{sgn(net, 0) if net else 0}</b> — {'short of' if abs(net) < M.RULE['trend_tilt'] else 'past'} the ±{M.RULE['trend_tilt']} that would move 5 points between them.</p>
  </div>

  <h3>Trend against the regional ranking</h3>
  <div class="card">
    <p class="gauge-note" style="text-align:left;max-width:none;margin:0">{agree_txt} Europe is in euros.</p>
  </div>

  <div class="call" style="margin-top:16px"><b>What the trend says.</b> {('No equity sleeve is in a downtrend, so none is cut' if not down else 'In a downtrend: ' + ', '.join(down))}; {ether_txt()}.</div>
</section>'''

def place(dd, a, b):
    """A judged drawdown against the two regimes' readings. Ordered, not assumed: Rev. 28 and
    earlier took calm as the shallower, which a VIX above its mean reverses."""
    lo_, hi_ = sorted((a, b))
    return 'sits between' if lo_ <= dd <= hi_ else 'sits beyond both' if dd > hi_ else 'sits below both'

def volatility():
    term = E['vix']['term']
    trows = '\n'.join(f'        <tr><td>{lab}</td><td class="n">{math.sqrt(h):.3f}</td><td class="n">{term[h]:.2f}%</td><td class="n">±{f(1.96 * term[h], 2 if h < 0.1 else 1)}%</td></tr>'
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
    where = lambda k: place(M.DD[k], sig(k, 'calm'), sig(k, 'normalized'))
    lo = M.VIX_2026
    return f'''<section class="pane" id="p-vol" role="tabpanel" aria-labelledby="t-vol">
  <h2>Volatility analysis</h2>
  <p class="lede">Square-root-of-time volatility at 3, 6 and 12 months, carried to the 10-year horizon.</p>

  <div class="card">
    <div class="hero2" style="margin-bottom:0">
      <div><div class="k">VIX, {day(M.VIX_ASOF)}</div><div class="v">{SPOT:.2f}</div></div>
      <div><div class="k">2026 low · high</div><div class="v">{lo['low']:.2f} · {lo['high']:.2f}</div></div>
    </div>
    <p class="gauge-note" style="text-align:left;max-width:none;margin:10px 0 0">Spot is {vix_rel(SPOT, 1)} the 2016–2023 mean of {M.VIX_MEAN}; the {M.VIX_WINDOW}-session average the rule reads, {AVG:.2f}, is {vix_rel(AVG, 1)} it. The 2026 low was {day(lo['low_date'])}, the high {day(lo['high_date'])}.</p>
  </div>

  <h3>Term structure</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Horizon</th><th>√(h/12)</th><th>Implied <span class="sym">σ</span></th><th>95% band</th></tr></thead>
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
      <tr><th></th><th class="sym">σ</th><th>VaR</th><th class="sym">σ</th><th>VaR</th></tr></thead>
      <tbody>
{vrows}
        <tr class="hl"><td>10 yr max DD</td><td class="n" colspan="2">{neg(bc["dd"])}%</td><td class="n" colspan="2">{neg(oc["dd"])}%</td></tr>
        <tr><td>12 mo, normalized</td><td class="n">{bn["vol"]:.2f}%</td><td class="n neg">{neg(bn["var"][1.0])}%</td><td class="n">{on["vol"]:.2f}%</td><td class="n neg">{neg(on["var"][1.0])}%</td></tr>
        <tr><td>Max DD, normalized</td><td class="n neg" colspan="2">{neg(bn["dd"])}%</td><td class="n neg" colspan="2">{neg(on["dd"])}%</td></tr>
      </tbody>
    </table>
  </div>
  <p class="note">VaR is drift-adjusted at the 5th percentile. Ten-year max drawdown ≈ {M.DD_MULT:.2f} × σ, from a daily-step simulation (median to mean {M.DD_BAND[0]:.2f}–{M.DD_BAND[1]:.2f}×); fat tails would deepen it.</p>

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
  <div class="warnbox" style="margin-top:12px">{regime_warn(oc, on)}</div>

  <h3>Risk contribution, normalized</h3>
  <div class="card">
{rcrows}
    <p class="gauge-note" style="text-align:left;max-width:none;margin:10px 0 0">BMNR is {O["BMNR"]}% of capital but {rc["BMNR"]:.1f}% of risk ({f(rc["BMNR"] / O["BMNR"], 1)}×), hence the 5% cap; SGOV carries almost none.</p>
  </div>

  <h3>Ten-year view: QQQ&#8217;s worst drawdowns</h3>
  <div class="card">
{hist}
    <p class="gauge-note" style="text-align:left;max-width:none;margin:10px 0 0">The sleeve drawdowns are judgements: QQQ {neg(M.DD["QQQ"], 0)}% {where("QQQ")} the σ model&#8217;s calm and normalized readings ({neg(sig("QQQ","calm"))}%, {neg(sig("QQQ","normalized"))}%); IEMG {neg(M.DD["IEMG"], 0)}% {where("IEMG")} ({neg(sig("IEMG","calm"))}%, {neg(sig("IEMG","normalized"))}%).</p>
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
            f"<b>Drawdown control and dry powder.</b> Assumes the {M.SGOV_GROSS:g}% midpoint of the {M.FED_RANGE[0]:.2f}–{M.FED_RANGE[1]:.2f}% range holds for the decade."),
      slide('QQQ', 'ETF · US Growth', 'Invesco QQQ Trust — Nasdaq-100',
            (('Gross forecast', f"{f(q['gross'])}%"), ('Expense ratio', f"{q['er']:.2f}%"),
             (f"Price ({day(P['QQQ']['px_asof'])})", f"${P['QQQ']['px']:.2f}"), ('Forward P/E', f"{f(FQ, 1)}×"),
             ('Dividend yield', f"{q['div']:.2f}%"), ('Annualised σ', f"{V['QQQ']:.0f}%"), ('$10,000 → 10 yr', term('QQQ'))),
            f"<b>Primary growth engine.</b> {q['eps']:.1f}%/yr earnings growth carries the forecast; {vs_avg(FQ, M.OBS['QQQ']['pe_end'])} its own {M.OBS['QQQ']['pe_end']}× average, the multiple {'costs' if q['val'] < 0 else 'adds'} {f(abs(q['val']))}%/yr."),
      slide('IEMG', 'ETF · EM Equity', 'iShares Core MSCI Emerging Markets ETF',
            (('Gross forecast', f"{f(i['gross'])}%"), ('Expense ratio', f"{i['er']:.2f}%"),
             (f"Price ({day(P['IEMG']['px_asof'])})", f"${P['IEMG']['px']:.2f}"), ('Forward P/E', f"{f(FI, 1)}×"),
             ('Dividend yield', f"{i['div']:.2f}%"), ('Annualised σ', f"{V['IEMG']:.0f}%"), ('$10,000 → 10 yr', term('IEMG'))),
            f"<b>The overweight.</b> {vs_avg(FI, M.OBS['IEMG']['pe_end']).capitalize()} its {M.OBS['IEMG']['pe_end']}× average, the multiple {'adds' if i['val'] > 0 else 'costs'} {f(abs(i['val']))}%/yr; currency costs {f(abs(i['fx']))}%/yr. {REL_CAP} QQQ on return per unit of risk."),
      slide('BMNR', 'Stock · Crypto', 'BitMine Immersion Technologies',
            ((f"Price ({day(H['px_asof'])})", f"${H['px']:.2f}"), ('Market cap', f"${M.BMNR_MCAP_B:.2f}B"),
             ('ETH treasury', f"{H['held']:,}"), ('ETH staked', f"{H['staked'] / H['held'] * 100:.1f}%"),
             ('mNAV (total / crypto)', f"{M.BMNR_MCAP_B / H['total_b']:.2f}× / {M.BMNR['mnav']:.2f}×"),
             ('Annualised σ', f"~{V['BMNR']:.0f}%"), ('$10,000 → 10 yr', term('BMNR'))),
            f"<b>Capped convexity.</b> {b['eth']:.1f}% ETH appreciation {sgn(b['stake'])}% staking {sgn(b['mnav'])}% {'premium normalisation' if M.BMNR['mnav'] >= 1 else 'discount closing'} {sgn(b['drag'])}% dilution drag = {b['net']:.2f}%. {FACTS['bmnr_stop']}; the drag is held until the share count updates. Total loss costs {O['BMNR']}% of capital."),
    ]
    dots = ''.join('<b class="on"></b>' if n == 0 else '<b></b>' for n in range(len(slides)))
    return f'''<section class="pane" id="p-assets" role="tabpanel" aria-labelledby="t-assets">
  <h2>The four sleeves</h2>
  <p class="lede">Net 10-year CAGR after fund fees, and expected maximum drawdown, for each holding.</p>
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
        <text x="90" y="102" text-anchor="middle" fill="#8A94A6" font-family="Public Sans, sans-serif" font-size="12" letter-spacing="0.5">NET CAGR %</text>
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
    """Published ten-year forecasts next to this page's: other people's numbers, quoted to be
    disagreed with."""
    Hh = M.INSTITUTIONAL
    rows = '\n'.join(f'        <tr><td>{escape(n)}</td><td class="n">{d["us"]:.1f}%</td><td class="n">{d["em"]:.1f}%</td></tr>' for n, d in Hh.items())
    us, em = M.A['QQQ']['gross'], M.A['IEMG']['gross']
    top_us = max(d['us'] for d in Hh.values())
    em_first = sum(d['em'] > d['us'] for d in Hh.values())
    return f"""  <div class="tw" style="margin-top:12px">
    <table>
      <thead><tr><th>10-yr forecast, gross</th><th>US</th><th>EM</th></tr></thead>
      <tbody>
{rows}
        <tr class="hl"><td>This page</td><td class="n">{us:.2f}%</td><td class="n">{em:.2f}%</td></tr>
      </tbody>
    </table>
  </div>
  <p class="note">This page&#8217;s US forecast is {f(abs(us - top_us), 1)} points {'above' if us > top_us else 'below'} the highest house; {em_first} of {len(Hh)} houses rank EM above the US.</p>"""

# The previous revision's figures, for the "this revision" rows. validate.py requires each
# one to appear in that revision's entry in VERIFICATION.md, so the left side of a row is
# tied to the record rather than typed twice.
PRIOR = dict(rev=29, asof='2026-10-16', QQQ=9.78, IEMG=9.29, BMNR=10.01, optimized=7.85, baseline=8.17, gauge=2.2,
             bmnr_release='2026-10-05')

def the(region):
    return ('the ' if region == 'United States' else '') + REG_NAME[region]

def book_txt(w):
    return f"QQQ {w['QQQ']} / IEMG {w['IEMG']} / SGOV {w['SGOV']} / BMNR {w['BMNR']}"

def build_steps():
    """The rule's five steps as the page states them, from M.TILT."""
    out = []
    for pillar, rd, mv, after in M.TILT['steps']:
        if pillar == 'Regional rankings':
            top, sec, both = rd; a, b = E['regions'][top]['scores'], E['regions'][sec]['scores']
            why = (f"{REG_NAME[top]} leads {the(sec)} at 3 months ({a[0]} vs {b[0]}) and at 10 years ({a[3]} vs {b[3]})"
                   if both else f"{REG_NAME[top]} does not lead {the(sec)} at both 3 months and 10 years")
        elif pillar == 'Broad and correlated macro sentiment':
            g5, funder = rd
            band = ('below ' + f"{M.RULE['gauge_cautious']}" if g5 < M.RULE['gauge_cautious'] else
                    'at or above ' + f"{M.RULE['gauge_constructive']}" if g5 >= M.RULE['gauge_constructive'] else 'in the neutral band')
            # "the worst" must allow for sleeves at their floor: BMNR is rated worse but cannot fund
            why = (f"The gauge reads {E['gauge']['display']}, {band}, so the reserve grows, funded by {funder}, the worst-rated equity "
                   f"sleeve above its {M.RULE['floor']}% floor (&#8216;{M.CORRELATED[funder][1].lower()}&#8217; on the transmission map)")
        elif pillar == 'Volatility':
            vx, mean = rd
            why = (f"The VIX&#8217;s {M.VIX_WINDOW}-session average, {vx:.2f}, sits {vix_rel(vx, 0)} its {mean} mean, so " +
                   ('the reserve is held' if vx < mean else 'the reserve is spent'))
            # a last close on the other side of the mean is stated, with the book it would give
            if (SPOT >= mean) != (vx >= mean):
                why += (f"; the {SPOT_DATE} close, {SPOT:.2f}, is {'above' if SPOT >= mean else 'below'} it, and a rule on "
                        f"that one close would hold {book_txt(M.TILT_SPOT)}")
        elif pillar == 'Market trend':
            signs, net = rd
            down = [k for k in ('QQQ', 'IEMG', 'BMNR') if M.trend_verdict(M.trend_score(M.TREND[M.SLEEVE_MARKET[k]]['r'])) == 'Downtrend']
            why = (("No sleeve&#8217;s market is in a downtrend" if not down else f"In a downtrend: {', '.join(down)}") +
                   (f"; QQQ against IEMG nets {sgn(net, 0) if net else 0}, short of ±{M.RULE['trend_tilt']}" if abs(net) < M.RULE['trend_tilt'] else
                    f"; QQQ against IEMG nets {sgn(net, 0)}, a clear lead"))
        else:
            near, far = rd
            why = ('Nothing admissible beats the book on both return and normalized drawdown' if far == 0 else
                   f"{near} of the books one step away beat{'s' if near == 1 else ''} it on both return and normalized drawdown, "
                   f"so the one with the least drawdown replaces it" if near else
                   f"No book one step away beats it; {far} further away {'does' if far == 1 else 'do'}, but a pillar moves one step, "
                   f"so the signals&#8217; book stands")
        # the book is restated only where the step moved it
        out.append(f"<b>{pillar} — {mv}.</b> {why}." + ('' if mv == 'no move' else f" Book: {book_txt(after)}."))
    return out

def change_triggers():
    _, net = M.relative_trend(M.SLEEVE_MARKET['QQQ'], M.SLEEVE_MARKET['IEMG'])
    return (f"the gauge reaching {M.RULE['gauge_cautious']} (now {E['gauge']['display']}), the VIX&#8217;s {M.VIX_WINDOW}-session average "
            f"{'reaching' if AVG < M.VIX_MEAN else 'falling below'} {M.VIX_MEAN} (now {AVG:.2f}; last close {SPOT:.2f}), "
            f"the QQQ–IEMG trend net reaching ±{M.RULE['trend_tilt']} (now {sgn(net, 0) if net else 0}), "
            f"or {REG_NAME[RANKED[0]]} losing its lead at 3 months or 10 years")

def verification_rows():
    """What this revision changed: prior figure on the left, current on the right."""
    return (('Market data', f"{day(PRIOR['asof'])} → <b>{day(MK['asof'])}</b>"),
            ('Macro gauge', f"{PRIOR['gauge']} → <b>{E['gauge']['display']}</b>"),
            ('BMNR holdings', f"{day(PRIOR['bmnr_release'])} → <b>{day(M.BMNR_HOLDINGS['released'])} release</b>"),
            ('Optimized net CAGR', f"{PRIOR['optimized']:.2f}% → <b>{f(ST['optimized']['calm']['cagr'])}%</b>"),
            ('QQQ net CAGR', f"{PRIOR['QQQ']:.2f}% → <b>{f(M.A['QQQ']['net'])}%</b>"),
            ('IEMG net CAGR', f"{PRIOR['IEMG']:.2f}% → <b>{f(M.A['IEMG']['net'])}%</b>"),
            ('BMNR net CAGR', f"{PRIOR['BMNR']:.2f}% → <b>{f(M.A['BMNR']['net'])}%</b>"))

def portfolios(n_mut, n_corr):
    b, o = ST['baseline'], ST['optimized']
    dom = [(d, c, w) for d, c, w in ((M.stats(w, 'normalized')['dd'], M.stats(w, 'normalized')['cagr'], w) for w in M.admissible(5))
           if d <= b['normalized']['dd'] and c >= b['normalized']['cagr'] and (d < b['normalized']['dd'] or c > b['normalized']['cagr'])]
    if ON['optimized'] and not ON['baseline'] and dom:
        # Rev. 27 handled exactly one dominating book; with three (Rev. 28) the call-out fell
        # through to a bare yes/no line. Any number now gets the count and the widest margins.
        up = max(dc_ for _, dc_, _ in dom) - b['normalized']['cagr']; cut = b['normalized']['dd'] - min(dd_ for dd_, _, _ in dom)
        n_txt = 'one beats' if len(dom) == 1 else f'{len(dom)} beat'
        eff_call = (f"<b>The recommended book is efficient; the baseline{', by a hair,' if up < 0.05 and cut < 0.5 else ''} is not.</b> Of {N_ADM} allocations with BMNR at 5%, "
                    f"none beats the optimized book on both axes; {n_txt} the baseline, by up to +{f(up)} points of CAGR "
                    f"and {f(cut, 1)} of drawdown. {len(EFF)} allocations are efficient.")
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
            (f"Most sensitive: {top['label']}", f"1 pt → {sgn(top['d_cagr'])} CAGR"))
    conf_html = '\n'.join(f'    <div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in conf)
    ver_html = '\n'.join(f'    <div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in verification_rows())
    q, i = M.A['QQQ'], M.A['IEMG']
    qv, iv, rel = RV['QQQ'], RV['IEMG'], REL
    cal_ratio = M.cal_line()[0][1]
    rationale = (
      f"<b>Tilt to the cheaper bloc.</b> {REG_NAME[RANKED[0]]} ranks first {'at every horizon' if LEADS_ALL else 'on mean score'} and IEMG trades at {f(FI, 1)}×; per unit of risk it is {rel} QQQ ({iv:.3f} vs {qv:.3f}) while earning {'less' if i['net'] < q['net'] else 'more'} ({i['net']:.2f}% vs {q['net']:.2f}%).",
      f"<b>SGOV at {O['SGOV']}% is a drawdown budget.</b> It is set against the {neg(o['normalized']['dd'])}% normalized drawdown, not today&#8217;s {neg(o['calm']['dd'])}%; scaling a risky mix against cash holds return-per-drawdown at {cal_ratio:.4f}, so no optimizer can choose it.",
      f"<b>BMNR capped at 5%.</b> {o['normalized']['rc']['BMNR']:.1f}% of risk from {O['BMNR']}% of capital; total loss costs {O['BMNR']}%.",
      f"<b>Where the model was overruled.</b> The best return-per-risk book, QQQ {BEST['QQQ']} / IEMG {BEST['IEMG']} / SGOV {BEST['SGOV']} / BMNR {BEST['BMNR']} (Sharpe {M.stats(BEST, 'calm')['sharpe']:.3f} vs {o['calm']['sharpe']:.3f}), holds a {BEST['SGOV']}% reserve. Rejected.",
    )
    rat = '\n'.join(f'    <div>{r}</div>' for r in rationale)
    steps_html = '\n'.join(f'    <div>{r}</div>' for r in build_steps())
    src = '<br>\n    '.join(f"{escape(g)} — " + ' · '.join(f'<a href="{u}">{escape(t)}</a>' for t, u in links) for g, links in SOURCES)
    return f'''<section class="pane" id="p-port" role="tabpanel" aria-labelledby="t-port">
  <h2>Baseline vs optimized</h2>
  <p class="lede">Both hold all four sleeves in steps of 5, and both are built for a 10-year horizon. The baseline is a plain strategic split; the optimized book is derived from it by rule.</p>

  <div class="duo">
{donut('baseline', 'Baseline', 'Strategic', False)}
{donut('optimized', 'Optimized', 'Macro-tilted', True)}
  </div>
  <p class="vs">{shift_line()}</p>

  <h3>How the optimized book is built</h3>
  <p class="note" style="margin:0 0 10px">Each pillar may move one 5-point step from the baseline; no sleeve goes under 5%, and BMNR stays at or under its cap.</p>
  <div class="num">
{steps_html}
  </div>
  <p class="note">The book changes on {change_triggers()}.</p>

  <h3>Forecast comparison</h3>
{compare_table()}
  <div class="call" style="margin-top:12px"><b>The trade.</b> {GAP:.2f} points of CAGR for {DDCUT:.1f} points less normalized drawdown, at {'almost the same' if abs(o['calm']['sharpe'] - b['calm']['sharpe']) < 0.01 else 'a higher' if o['calm']['sharpe'] > b['calm']['sharpe'] else 'a lower'} return per unit of risk.</div>

  <h3>How the forecasts are built</h3>
{blocks_table()}
  <p class="note">Each forward multiple moves to its 10-year average (NDX {M.OBS['QQQ']['pe_end']}×, MSCI EM {M.OBS['IEMG']['pe_end']}×); yield and multiple share one price. Weight-averaged CAGRs leave out about {f(M.diversification_return(B, exclude=('BMNR',)))}–{f(M.diversification_return(O, exclude=('BMNR',)))}%/yr of rebalancing return from the three funds, so they are conservative.</p>

  <h3>Efficient frontier</h3>
  <div class="card">{M.frontier_svg()}</div>
  <div class="call" style="margin-top:12px">{eff_call}</div>

  <h3>How much to trust it</h3>
  <div class="card">
{conf_html}
  </div>
{houses()}
  <p class="note"><b>Still open:</b> {len(M.ASSUMED)} inputs are assumptions rather than observations — {'; '.join(f'{a} ({v})' for a, v in M.ASSUMED)}. QQQ&#8217;s earnings growth matters most.</p>

  <h3>Rationale</h3>
  <div class="num">
{rat}
  </div>
  <div class="call" style="margin-top:16px"><b>Recommendation.</b> Hold QQQ {O['QQQ']} / IEMG {O['IEMG']} / SGOV {O['SGOV']} / BMNR {O['BMNR']}: {neg(o['normalized']['dd'])}% normalized drawdown against the baseline&#8217;s {neg(b['normalized']['dd'])}%, for {GAP:.2f} points of CAGR. Rebalance semi-annually or on a 5-point drift; {revisit_txt()} if the EM discount to developed markets closes toward 25%.</div>

  <h3>Verification log</h3>
  <p class="note">Generated from the model; an independent validator re-derives every figure, and {n_mut} planted errors were all caught. {n_corr} corrections recorded; this revision:</p>
  <div class="card">
{ver_html}
  </div>

  <h3>Sources</h3>
  <p class="src">
    {src}
  </p>
  <div class="disc"><b>Not investment advice.</b> Forecasts are modelled estimates; a point off QQQ&#8217;s earnings growth moves the recommended book&#8217;s CAGR by {f(abs(top['d_cagr']))}. Market data to the {day(MK['asof'], False)} close, the 10-year to {day(MK['ust10_asof'], False)}; fund prices as dated on each slide; BMNR holdings from its {day(M.BMNR_HOLDINGS['released'], False)} release. BMNR can lose its entire value.</div>
</section>'''

NAV = '''  <nav class="tabs" role="tablist" aria-label="Sections">
    <button class="tab on" id="t-macro" type="button" data-p="p-macro" role="tab" aria-selected="true" aria-controls="p-macro">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9"/><path d="M12 12l5.5-5.5"/><path d="M21 3v6h-6"/></svg><span>Macro</span></button>
    <button class="tab" id="t-regions" type="button" data-p="p-regions" role="tab" aria-selected="false" aria-controls="p-regions">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 3 2.6 15 0 18M12 3c-2.6 3-2.6 15 0 18"/></svg><span>Regions</span></button>
    <button class="tab" id="t-trend" type="button" data-p="p-trend" role="tab" aria-selected="false" aria-controls="p-trend">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg><span>Trend</span></button>
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
                      macro(), '', regions(), '', trend_pane(), '', volatility(), '', sleeves(), '', portfolios(n_mut, n_corr),
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
