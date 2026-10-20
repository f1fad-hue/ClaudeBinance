#!/usr/bin/env python3
"""Mutation test for the validator.

validate.py can only be trusted if it fails when something is wrong. Two kinds of
corruption are applied, one at a time, each in a throwaway copy of the repo:

  model mutations      change one input in portfolio_model.py and leave the page as
                       it is. validate.py must fail: the published page is stale.
  generator mutations  plant a realistic bug in build.py (a swapped column, the wrong
                       rounding, a reversed ranking), REBUILD the page from it, and run
                       validate.py. The freshness check passes -- the page is exactly
                       what the buggy generator writes -- so only the independent
                       re-derivations can catch it. This is what proves they bite.

    python3 mutate.py        # expect: every mutation was caught

A mutation whose target text is missing or ambiguous is reported and FAILS the run:
an earlier version reported success while silently skipping seven.
"""
import subprocess, shutil, re, sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor
REPO = os.path.dirname(os.path.abspath(__file__))
FILES = ('portfolio_model.py', 'build.py', 'validate.py', 'page.css', 'allocation.html', 'mutate.py', 'VERIFICATION.md')
orig = open(os.path.join(REPO, 'portfolio_model.py')).read()
gen  = open(os.path.join(REPO, 'build.py')).read()
_REV = int(re.search(r'REVISION = (\d+)', orig).group(1))
_m = re.search(r"\('(\d{4}-\d\d-\d\d)', ([\d.]+)\)\)\n", orig)   # last VIX_SERIES entry
_LAST, _SPOT_S = _m.group(1), _m.group(2)          # as written ("15.40"), not float-printed
_SPOT = float(_SPOT_S)
_MEAN = float(re.search(r'VIX_SERIES\[-1\]\[1\], ([\d.]+)', orig).group(1))
_SGOV = float(re.search(r'SGOV_GROSS = ([\d.]+)', orig).group(1))
def _num(pat):
    m = re.search(pat, orig)
    if not m: raise SystemExit(f'mutate.py: cannot locate {pat!r} in the model; update the table')
    return m.group(1)
_B = {f: _num(rf'BMNR = dict\([^)]*{f}=([\d.]+)') for f in ('stake_share','stake_yield','mnav')}
# non-greedy and word-bounded: through Rev. 28 the greedy "[^)]*px=" matched basis_px, so the
# "price" mutants mutated the basis price and duplicated the basis mutants
_P = {(t, f): _num(rf"'{t}':\s+dict\([^)]*?\b{f}=([\d.]+)") for t in ('QQQ','IEMG')
      for f in ('ttm_div','px','basis_px','basis_fwd')}
assert _P['QQQ', 'px'] != _P['QQQ', 'basis_px'], 'price lookup matched the basis price'
# the prior revision's QQQ figure, read from build.py so the mutant survives each roll
_PQ = re.search(r"PRIOR = dict\([^)]*QQQ=([\d.]+)", gen).group(1)
_bump = lambda v, d: f'{float(v) + d:.{len(v.split(".")[1]) if "." in v else 0}f}'
# the rolled inputs, read from the model as written so these mutants survive each roll
def _drv(name, d):
    m = re.search(r"\('%s',([\d.]+),(\.\d+)\)" % re.escape(name), orig)
    if not m: raise SystemExit(f'mutate.py: cannot locate driver {name!r} in the model')
    return m.group(0), f"('{name}',{float(m.group(1)) + d:.1f},{m.group(2)})"
_U = re.search(r"ust10_asof='([\d-]+)', ust10=([\d.]+), ust10_prev=([\d.]+), ust10_chg_bp=(-?\d+),", orig)
_MKT_ASOF = re.search(r"MARKET = dict\(asof='([\d-]+)'", orig).group(1)
_BRENT = _num(r"brent=([\d.]+),")
_BH = {f: _num(rf"BMNR_HOLDINGS = dict\([^)]*?\b{f}=([\d_.]+)") for f in ('held', 'crypto_b')}
_BPX = re.search(r"px=([\d.]+), px_asof='([\d-]+)', shares_m", orig)
import datetime as _dt
_d = _dt.date.fromisoformat(_BPX.group(2)) + _dt.timedelta(days=1)
while _d.weekday() >= 5: _d += _dt.timedelta(days=1)
_BPX_NEXT = _d.isoformat()
MUT=[
 ("QQQ ttm div",    f"ttm_div={_P['QQQ','ttm_div']}",   f"ttm_div={_bump(_P['QQQ','ttm_div'], 0.40)}"),
 ("IEMG ttm div",   f"ttm_div={_P['IEMG','ttm_div']}",  f"ttm_div={_bump(_P['IEMG','ttm_div'], 0.10)}"),
 ("QQQ price",      f"px={_P['QQQ','px']},",           f"px={_bump(_P['QQQ','px'], 20)},"),
 ("IEMG price",     f"px={_P['IEMG','px']},",          f"px={_bump(_P['IEMG','px'], 2)},"),
 ("QQQ eps",        "eps=9.50",                 "eps=9.00"),
 ("IEMG eps",       "eps=7.50",                 "eps=7.00"),
 ("QQQ basis fwd",  f"basis_fwd={_P['QQQ','basis_fwd']}",  f"basis_fwd={_bump(_P['QQQ','basis_fwd'], 1)}"),
 ("IEMG basis fwd", f"basis_fwd={_P['IEMG','basis_fwd']}", f"basis_fwd={_bump(_P['IEMG','basis_fwd'], 1)}"),
 ("QQQ basis px",   f"basis_px={_P['QQQ','basis_px']}",    f"basis_px={_bump(_P['QQQ','basis_px'], 20)}"),
 ("QQQ pe_end",     "pe_end=22.9",              "pe_end=21.9"),
 ("IEMG pe_end",    "pe_end=12.2",              "pe_end=13.2"),
 ("IEMG fx",        "fx=-1.50",                 "fx=-1.00"),
 ("QQQ er",         "er=0.18",                  "er=0.20"),
 ("SGOV_GROSS",     f"SGOV_GROSS = {_SGOV:g}",   f"SGOV_GROSS = {_SGOV + 0.25:g}"),
 ("SGOV_ER",        "SGOV_ER    = 0.09",        "SGOV_ER    = 0.12"),
 ("BMNR eth",       "eth=9.00",                 "eth=8.50"),
 ("BMNR stake_sh",  f"stake_share={_B['stake_share']}", f"stake_share={_bump(_B['stake_share'], 0.03)}"),
 ("BMNR stake_yld", f"stake_yield={_B['stake_yield']}", f"stake_yield={_bump(_B['stake_yield'], 0.30)}"),
 ("BMNR mnav",      f"mnav={_B['mnav']}",               f"mnav={_bump(_B['mnav'], 0.05)}"),
 ("BMNR drag",      "drag=1.40",                "drag=1.20"),
 ("VIX latest close", f"('{_LAST}', {_SPOT_S})",  f"('{_LAST}', {_SPOT + 1:.2f})"),
 ("VIX series date", f"('{_LAST}', {_SPOT_S})",  f"('{_LAST[:-2]}20', {_SPOT_S})"),
 ("VIX 28 Sep snapshot", "('2026-09-28', 16.07)", "('2026-09-28', 16.37)"),
 ("VIX reported change", "'2026-09-29': -0.2,", "'2026-09-29': -2.0,"),
 ("VIX_MEAN",       f"VIX_SERIES[-1][1], {_MEAN}", f"VIX_SERIES[-1][1], {_MEAN + 0.5}"),
 ("VIX rule reads one close", "vix = VIX_AVG if vix is None else vix", "vix = VIX_SPOT if vix is None else vix"),
 ("VIX average window", "VIX_WINDOW = 5", "VIX_WINDOW = 4"),
 ("one-close book read from the average", "TILT_SPOT = tilt_book(vix=VIX_SPOT)['book']", "TILT_SPOT = tilt_book()['book']"),
 ("DD_MULT",        "DD_MULT = 2.00",           "DD_MULT = 2.05"),
 ("DD band",        "DD_BAND = (1.90, 2.05)",   "DD_BAND = (1.65, 2.05)"),
 ("DD QQQ",         "'QQQ': 40.0",              "'QQQ': 42.0"),
 ("DD IEMG",        "'IEMG': 39.0",             "'IEMG': 36.0"),
 ("DD BMNR",        "'BMNR': 85.0",             "'BMNR': 80.0"),
 ("vol QQQ calm",   "vol={'QQQ':21.0*SPOT_SCALE,","vol={'QQQ':22.0*SPOT_SCALE,"),
 ("vol IEMG calm",  "'IEMG':18.0*SPOT_SCALE,","'IEMG':19.0*SPOT_SCALE,"),
 ("vol BMNR calm",  "'SGOV':0.5,'BMNR':95.0}",          "'SGOV':0.5,'BMNR':100.0}"),
 ("vol struck at",  "VOL_STRUCK_AT = 15.67",            "VOL_STRUCK_AT = 16.67"),
 ("calm ignores spot", "vol={'QQQ':21.0*SPOT_SCALE,'IEMG':18.0*SPOT_SCALE", "vol={'QQQ':21.0,'IEMG':18.0"),
 ("old inverted uplift", "'QQQ':21.0*NORM_SCALE,'IEMG':18.0*NORM_SCALE", "'QQQ':21.0*UPLIFT,'IEMG':18.0*UPLIFT"),
 ("vol SGOV norm",  "'SGOV':0.5,'BMNR':95.0*1.15}",     "'SGOV':1.5,'BMNR':95.0*1.15}"),
 ("rho QQQ-IEMG",   "('QQQ','IEMG'):0.66",      "('QQQ','IEMG'):0.70"),
 ("rho QQQ-BMNR",   "('QQQ','BMNR'):0.65",      "('QQQ','BMNR'):0.60"),
 ("rho stressed",   "('QQQ','IEMG'):0.85",      "('QQQ','IEMG'):0.88"),
 ("rho BMNR stressed","('QQQ','BMNR'):0.80",    "('QQQ','BMNR'):0.84"),
 ("rho IEMG-BMNR str","('IEMG','BMNR'):0.72",   "('IEMG','BMNR'):0.76"),
 ("BMNR norm mult", "95.0*1.15",                "95.0*1.20"),
 ("baseline QQQ",   "'baseline':  {'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5}",
                    "'baseline':  {'QQQ':40,'IEMG':30,'SGOV':25,'BMNR':5}"),
 ("optimized typed over the rule", "PORTFOLIOS['optimized'] = TILT['book']",
                    "PORTFOLIOS['optimized'] = {'QQQ':30,'IEMG':35,'SGOV':30,'BMNR':5}"),
 ("rule gauge threshold", "gauge_cautious=2.6,", "gauge_cautious=2.2,"),
 ("rule trend threshold", "trend_tilt=2)", "trend_tilt=1)"),
 ("rule funder by weight only", "funder = min(eq, key=lambda k: (CORRELATED[k][0], -w[k]))", "funder = min(eq, key=lambda k: (-w[k],))"),
 ("transmission label", "'QQQ': (0, 'Two-sided')", "'QQQ': (0, 'Tailwind')"),
 ("transmission sign", "'IEMG': (1, 'Tailwind')", "'IEMG': (-1, 'Tailwind')"),
 ("trend S&P 3m", "r=(2.30, 17.85, 15.74)", "r=(1.30, 17.85, 15.74)"),
 ("trend EM 12m", "r=(-0.37, 23.59, 29.22)", "r=(-0.37, 23.59, 25.22)"),
 ("trend NDX 6m", "r=(0.58, 28.42, 24.00)", "r=(0.58, 27.42, 24.00)"),
 ("trend ether 12m", "r=(70.6, 27.5, -35.3)", "r=(70.6, 27.5, -30.3)"),
 ("trend chain part", "('S&P 500', 1): (15.2, 2.30)", "('S&P 500', 1): (15.2, 3.30)"),
 ("trend deadband", "TREND_DEADBAND = 2.0", "TREND_DEADBAND = 0.5"),
 ("trend weights", "TREND_WEIGHTS = (1, 1, 2)", "TREND_WEIGHTS = (2, 1, 1)"),
 ("trend window", "TREND_ASOF = '2026-09-30'", "TREND_ASOF = '2026-09-29'"),
 ("quarter-end close", "QE_CLOSE = {'QQQ': 739.77,", "QE_CLOSE = {'QQQ': 729.77,"),
 ("drawdown control leaps", "near = [v for v in far if sum(abs(v[k] - w[k]) for k in w) == 2 * st]", "near = far"),
 ("drawdown tie-break by return", "key=lambda v: (stats(v, 'normalized')['dd'], -stats(v, 'normalized')['cagr'])", "key=lambda v: -stats(v, 'normalized')['cagr']"),
 ("driver growth",  *_drv('Growth momentum', 0.5)),
 ("driver policy",  *_drv('Monetary policy', -0.5)),
 ("region asia",    "'Asia / EM':[5.5,6.5,7.0,7.5]","'Asia / EM':[5.0,6.5,7.0,7.5]"),
 ("region europe",  "'Europe':[3.0,3.5,4.0,5.0]", "'Europe':[3.5,3.5,4.0,5.0]"),
 ("JPM us",         "dict(us=6.70, em=7.80",    "dict(us=6.20, em=7.80"),
 ("JPM em",         "us=6.70, em=7.80",         "us=6.70, em=8.30"),
 ("Vanguard em",    "dict(us=5.20, em=3.00",    "dict(us=5.20, em=6.30"),
 ("REVISION",       f"REVISION = {_REV}",       f"REVISION = {_REV + 1}"),
 # added in Rev. 20: inputs the review found no mutation for
 ("IEMG basis px",  f"basis_px={_P['IEMG','basis_px']}",   f"basis_px={_bump(_P['IEMG','basis_px'], 2)}"),
 ("IEMG er",        "er=0.09, eps=7.50",        "er=0.11, eps=7.50"),
 ("VIX 2026 low",   "low=14.13,",               "low=13.63,"),
 ("VIX low date",   "low_date='2026-08-14'",    "low_date='2026-08-21'"),
 ("FOMC date",      "FOMC_DATE  = '2026-09-16'", "FOMC_DATE  = '2026-09-17'"),
 ("BMNR held",      f"held={_BH['held']}",       f"held={int(_BH['held'].replace('_', '')) + 100_000:_}"),
 ("BMNR priced a session after its holdings", f"px_asof='{_BPX.group(2)}', shares_m", f"px_asof='{_BPX_NEXT}', shares_m"),
 ("BMNR crypto typed below its own ETH", f"crypto_b={_BH['crypto_b']},", f"crypto_b={_bump(_BH['crypto_b'], -0.05)},"),
 ("Brent level only", f"brent={_BRENT},",        f"brent={_bump(_BRENT, 1)},"),
 # September 2025's payout ($0.69395) in place of September 2026's ($0.75143): the Rev. 25-26 error
 ("QQQ trailing dividend a quarter stale", f"ttm_div={_P['QQQ','ttm_div']}, px={_P['QQQ','px']}",
                      f"ttm_div={float(_P['QQQ','ttm_div']) - 0.75143 + 0.69395:.5f}, px={_P['QQQ','px']}"),
 ("IEMG dividend rounded to the cent", f"ttm_div={_P['IEMG','ttm_div']}", f"ttm_div={float(_P['IEMG','ttm_div']):.2f}"),
 ("10y below its high", f"ust10={_U.group(2)}, ust10_prev={_U.group(3)}, ust10_chg_bp={_U.group(4)},",
                      f"ust10={_bump(_U.group(2), -0.01)}, ust10_prev={_U.group(3)}, ust10_chg_bp={int(_U.group(4)) - 1},"),
 ("10y dated to the market date", f"ust10_asof='{_U.group(1)}'", f"ust10_asof='{_MKT_ASOF}'"),
 ("VIX 2 Oct close",  "('2026-10-02', 15.31)", "('2026-10-02', 15.40)"),
 ("assumed input dropped", "           ('IEMG currency drag', f\"{OBS", "           ('IEMG FX (observed)', f\"{OBS"),
 ("driver inflation", *_drv('Inflation trajectory', 0.5)),
 ("driver liquidity", *_drv('Liquidity & credit', 0.5)),
 ("driver valuation", *_drv('Valuation & positioning', 0.5)),
 ("driver geopol",  *_drv('Geopolitical risk', 0.5)),
 ("region US",      "'United States':[5.0,5.5,6.5,7.0]", "'United States':[5.0,5.5,6.0,7.0]"),
 ("Fidelity em",    "dict(us=5.80, em=8.10",    "dict(us=5.80, em=8.60"),
 ("BlackRock us",   "dict(us=5.20, em=7.10",    "dict(us=5.70, em=7.10"),
]

# generator mutations: (name, text in build.py, replacement) -- each a plausible bug
def G(name, old, new): return (name, old, new)
GEN = [
 G("VaR column from the wrong book", 'neg(bc["var"][h])', 'neg(oc["var"][h])'),
 G("every term band from the 12-month sigma", "±{f(1.96 * term[h], 2 if h < 0.1 else 1)}%", "±{f(1.96 * term[1.0], 2 if h < 0.1 else 1)}%"),
 G("95% band with the one-sided z", "±{f(1.96 * term[h], 2 if h < 0.1 else 1)}%", "±{f(1.645 * term[h], 2 if h < 0.1 else 1)}%"),
 G("regions ranked ascending", "RANKED = sorted(E['regions'], key=lambda k: -E['regions'][k]['mean'])", "RANKED = sorted(E['regions'], key=lambda k: E['regions'][k]['mean'])"),
 G("slide drawdown from the sigma model", "{neg(M.DD[t], 0 if M.DD[t] >= 1 else 1)}%", "{neg(M.REGIME['calm']['vol'][t] * M.DD_MULT, 0)}%"),
 G("CAGR delta reversed", "d_(b['calm']['cagr_d'], o['calm']['cagr_d'], 2)", "d_(o['calm']['cagr_d'], b['calm']['cagr_d'], 2)"),
 G("risk-adjusted tie threshold", "abs(rq - ri) < 0.01", "abs(rq - ri) < 0.0001"),
 G("masthead shows the prior 10-year", "<span>UST 10y {MK['ust10']:.2f}%{", "<span>UST 10y {MK['ust10_prev']:.2f}%{"),
 G("masthead drops the 10-year's own date", "{f' ({day(MK[\"ust10_asof\"])})' if MK['ust10_asof'] != MK['asof'] else ''}", "{''}"),
 G("risk card from the calm regime", "    rc = on['rc']", "    rc = oc['rc']"),
 G("gap with the books reversed", "GAP = M.r2h(M.r2h(ST['baseline']['calm']['cagr_d']) - M.r2h(ST['optimized']['calm']['cagr_d']))", "GAP = M.r2h(M.r2h(ST['optimized']['calm']['cagr_d']) - M.r2h(ST['baseline']['calm']['cagr_d']))"),
 G("standard error from the wrong regime", "f\"±{M.se_level('optimized'):.2f} pts\"", "f\"±{M.se_level('optimized', 'normalized'):.2f} pts\""),
 G("slide terminal from gross", "term = lambda k: f\"${E['sleeves'][k]['terminal']:,}\"", "term = lambda k: f\"${round(10000 * (1 + M.A[k]['gross'] / 100) ** 10):,}\""),
 G("expense row loses its minus", "if signed is None: return f'<td class=\"n\">{MINUS}{x:.2f}</td>'", "if signed is None: return f'<td class=\"n\">{x:.2f}</td>'"),
 G("VIX discount from the prior close", "Spot is {vix_rel(SPOT, 1)} the", "Spot is {vix_rel(PREV, 1)} the"),
 G("VIX distance words reversed", "{'below' if d >= 0 else 'above'}", "{'above' if d >= 0 else 'below'}"),
 G("held VIX narrated as a move", "    if VIX_STALE:\n        return (f\"The VIX", "    if False:\n        return (f\"The VIX"),
 G("masthead VIX undated while held", "{f' ({SPOT_DATE})' if VIX_STALE else ''}</span>", "</span>"),
 G("trigger distance undated while held", "to = f\" to the {SPOT_DATE} close\" if VIX_STALE else ''", "to = ''"),
 G("gauge needle axes swapped", "x2=\"{g['needle'][0]}\" y2=\"{g['needle'][1]}\"", "x2=\"{g['needle'][1]}\" y2=\"{g['needle'][0]}\""),
 G("disclaimer dated to BMNR's holdings", "Market data to the {day(MK['asof'], False)} close", "Market data to the {day(M.BMNR_HOLDINGS['asof'], False)} close"),
 G("efficient count off by one", "they are two points on the same curve, the baseline for return and the optimized book for drawdown. {len(EFF)}", "they are two points on the same curve, the baseline for return and the optimized book for drawdown. {len(EFF) + 1}"),
 G("driver bar on the 1-10 scale", '<div class="drv-bar"><i style="width:{fill}%;background:{t}"></i></div>', '<div class="drv-bar"><i style="width:{s5 * 20:.1f}%;background:{t}"></i></div>'),
 G("BMNR total mNAV over crypto", "{M.BMNR_MCAP_B / H['total_b']:.2f}×", "{M.BMNR_MCAP_B / H['crypto_b']:.2f}×"),
 G("regional lead from 6 months", "for h in (0, 3)]", "for h in (1, 3)]"),
 G("QQQ slide shows the basis price", "f\"${P['QQQ']['px']:.2f}\"), ('Forward P/E'", "f\"${P['QQQ']['basis_px']:.2f}\"), ('Forward P/E'"),
 G("diversification return from the normalized regime", "{f(M.diversification_return(O, exclude=('BMNR',)))}%/yr of rebalancing", "{f(M.diversification_return(O, 'normalized', exclude=('BMNR',)))}%/yr of rebalancing"),
 G("both-efficient call-out on the wrong test", "    elif ON['optimized'] and ON['baseline']:", "    elif ON['optimized'] and not ON['baseline']:"),
 G("still-open list truncated", "{'; '.join(f'{a} ({v})' for a, v in M.ASSUMED)}", "{'; '.join(f'{a} ({v})' for a, v in M.ASSUMED[:3])}"),
 G("10-year high keyed on the day's sign", "    if MK['ust10'] >= MK['ust10_high']:\n        return f\"its", "    if MK['ust10_chg_bp'] >= 0:\n        return f\"its"),
 G("revision row shows gross, not net", "{PRIOR['QQQ']:.2f}% → <b>{f(M.A['QQQ']['net'])}%</b>", "{PRIOR['QQQ']:.2f}% → <b>{f(M.A['QQQ']['gross'])}%</b>"),
 G("prior figure not in the record", f"QQQ={_PQ}, IEMG=", f"QQQ={float(_PQ) + 0.01:.2f}, IEMG="),
 G("disclaimer drops the holdings date", "BMNR holdings from its {day(M.BMNR_HOLDINGS['released'], False)} release.", "BMNR holdings from its latest release."),
 G("drawdown band typed, not from the model", "(median to mean {M.DD_BAND[0]:.2f}–{M.DD_BAND[1]:.2f}×)", "(median to mean 1.65–1.75×)"),
 G("high-yield spreads called tight again", "High-yield spreads {spread_verb()} to {FACTS['hy_oas'][0]}", "High-yield spreads stay tight at {FACTS['hy_oas'][0]}"),
 G("QQQ 2020 drawdown understated again", "('2020 COVID crash', '≈−28.6%')", "('2020 COVID crash', '≈−27%')"),
 G("spread verb typed again", "High-yield spreads {spread_verb()} to", "High-yield spreads narrowed to"),
 G("headline back on the day's sign", "if MK['ust10'] >= MK['ust10_high'] and MK['ust10_chg_bp'] > 0:", "if MK['ust10_chg_bp'] > 0:"),
 G("dollar claim typed again", "; the dollar index touched {FACTS['dollar'][0]} on {FACTS['dollar'][1]}.", "; the dollar sits at a 16-month high."),
 G("dated lead shown on any date", "return FACTS['lead'] if FACTS['lead'][0] == MK['asof'] else None", "return FACTS['lead']"),
 G("frontier call-out back to one dominator only", "if ON['optimized'] and not ON['baseline'] and dom:", "if ON['optimized'] and not ON['baseline'] and len(dom) == 1:"),
 G("a fact's apostrophe double-escaped", "the strait’s undersea cables", "the strait&#8217;s undersea cables"),
 G("funder called the worst outright", "the worst-rated equity \"\n                   f\"sleeve above its", "the worst \"\n                   f\"sleeve of all, above its"),
 G("book restated on a no-move step", "('' if mv == 'no move' else f\" Book: {book_txt(after)}.\")", "f\" Book: {book_txt(after)}.\""),
 G("gauge note calls growth strong regardless", "return ('Strong growth is' if g5 >= 3.4 else", "return ('Strong growth is' if g5 >= 0 else"),
 G("trend verdict from the 12-month figure only", "sc = M.trend_score(d['r']); v = M.trend_verdict(sc)", "sc = M.trend_score(d['r']); v = M.trend_verdict(2 * M.trend_sign(d['r'][2]))"),
 G("trend cells lose their signs", "cells = ''.join(f'<td class=\"n{cls(x)}\">{sgn(x, 1)}%</td>' for x in d['r'])", "cells = ''.join(f'<td class=\"n{cls(x)}\">{f(abs(x), 1)}%</td>' for x in d['r'])"),
 G("relative trend net unweighted", "Weighted, that nets <b>{sgn(net, 0) if net else 0}</b>", "Weighted, that nets <b>{sgn(sum(signs), 0) if sum(signs) else 0}</b>"),
 G("rule steps shown without their books", "Book: {book_txt(after)}.", "Book: {book_txt(O)}."),
 G("trend leader from the wrong horizon", "return [max(reg, key=lambda k: reg[k][h]) for h in range(3)]", "return [max(reg, key=lambda k: reg[k][2]) for h in range(3)]"),
 G("since-quarter move from the wrong close", "(M.PRICES[k]['px'] / M.QE_CLOSE[k] - 1) * 100", "(M.PRICES[k]['basis_px'] / M.QE_CLOSE[k] - 1) * 100"),
 G("triggers quote the close as the average", "(now {AVG:.2f}; last close {SPOT:.2f})", "(now {SPOT:.2f}; last close {SPOT:.2f})"),
 G("triggers quote the wrong close", "(now {AVG:.2f}; last close {SPOT:.2f})", "(now {AVG:.2f}; last close {PREV:.2f})"),
 G("QQQ multiple side typed", "if vs_avg(FQ, M.OBS['QQQ']['pe_end']) == 'above' else", "if True else"),
 G("multiple side judged unrounded", "x1 = M.r2h(x, 1)", "x1 = x"),
 G("regime warning branch inverted", "if on['dd'] >= oc['dd']:", "if on['dd'] < oc['dd']:"),
 G("one-close book not stated", "if (SPOT >= mean) != (vx >= mean):", "if False:"),
 G("drawdown placement unordered", "lo_, hi_ = sorted((a, b))", "lo_, hi_ = a, b"),
 G("revisit trigger reads the last close", "    if AVG < M.VIX_MEAN:\n        to = ", "    if SPOT < M.VIX_MEAN:\n        to = "),
 G("protection band dropped", "return 'cheap' if d >= 5 else 'dear' if d <= -5 else 'close to its long-run price'", "return 'cheap' if d >= 0 else 'dear'"),
 G("ether's horizons swapped", "s3, s12 = M.trend_sign(r[0]), M.trend_sign(r[2])", "s3, s12 = M.trend_sign(r[2]), M.trend_sign(r[0])"),
 G("BMNR cap claimed without checking", "+ (', its cap' if O['BMNR'] == M.RULE['bmnr_cap'] else '')", "+ ', its cap'"),
 G("reserve step typed", "spend the reserve toward {O['SGOV'] - M.RULE['step']}%", "spend the reserve toward 25%"),
 G("transmission labels typed", "('QQQ', 'qqq', SIG[M.CORRELATED['QQQ'][0]], M.CORRELATED['QQQ'][1],", "('QQQ', 'qqq', 'up', 'Tailwind',"),
 G("signal pill shares the donut card's class", "SIG = {1: 'up', 0: 'nu', -1: 'down'}", "SIG = {1: 'up', 0: 'nu', -1: 'dn'}"),
 G("sigma header left to uppercase", '<th class="sym">σ</th><th>VaR</th><th class="sym">σ</th>', '<th>σ</th><th>VaR</th><th>σ</th>'),
 G("trend verdict back in a fifth column", "<th>Market · trend</th><th>3 mo</th><th>6 mo</th><th>12 mo</th></tr>", "<th>Market · trend</th><th>3 mo</th><th>6 mo</th><th>12 mo</th><th>Trend</th></tr>"),
 G("trend verdict pill colour fixed", "f'<span class=\"sig {TREND_SIG[v]}\">", "f'<span class=\"sig up\">"),
 G("donut offsets shifted", 'stroke-dashoffset=\"{o:.2f}\"', 'stroke-dashoffset=\"{o - 1:.2f}\"'),
]

def run(kind, name, old, new):
    src = orig if kind == 'model' else gen
    if src.count(old) != 1:
        return ('skip', name, src.count(old))
    d = tempfile.mkdtemp(prefix='mut_')
    try:
        for f_ in FILES: shutil.copy(os.path.join(REPO, f_), d)
        target = 'portfolio_model.py' if kind == 'model' else 'build.py'
        open(os.path.join(d, target), 'w').write(src.replace(old, new))
        if kind == 'gen':
            b = subprocess.run([sys.executable, 'build.py'], cwd=d, capture_output=True, text=True, timeout=300)
            if b.returncode != 0:
                return ('broken', name, b.stderr.strip().splitlines()[-1:])
        r = subprocess.run([sys.executable, 'validate.py'], cwd=d, capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            return ('survived', name, '')
        if kind == 'gen' and 'page is exactly what build.py writes' in r.stdout:
            return ('broken', name, 'freshness failed: the harness did not rebuild')
        return ('caught', name, '')
    finally:
        shutil.rmtree(d, ignore_errors=True)

# The unmutated repo must pass first. Without this guard a baseline failure (an unrecorded
# revision, say) makes validate.py exit 1 for every mutant and each one reads as "caught":
# Rev. 24 found exactly that run, 94 of 94 caught by a check that was failing anyway.
def baseline():
    d = tempfile.mkdtemp(prefix='mut_base_')
    try:
        for f_ in FILES: shutil.copy(os.path.join(REPO, f_), d)
        r = subprocess.run([sys.executable, 'validate.py'], cwd=d, capture_output=True, text=True, timeout=600)
        return r.returncode, (r.stdout.strip().splitlines() or [''])[-1]
    finally:
        shutil.rmtree(d, ignore_errors=True)
_rc, _last = baseline()
if _rc != 0:
    raise SystemExit(f'mutate.py: validate.py fails on the unmutated repo ({_last}); fix that first, '
                     'or every mutation would read as caught')

jobs = [('model',) + m for m in MUT] + [('gen',) + g for g in GEN]
with ThreadPoolExecutor(max_workers=4) as ex:
    res = list(ex.map(lambda j: run(*j), jobs))
bad = [r for r in res if r[0] != 'caught']
# A skipped mutant is one whose target no longer matches (the code moved under it); it
# tests nothing, so it fails the run like a survivor. The line counts both.
print(f'{len(MUT)} model and {len(GEN)} generator mutations, '
      f'{sum(r[0] == "survived" for r in res)} survived, {sum(r[0] == "skip" for r in res)} skipped')
for r in bad:
    print(f'  {r[0].upper():<9} {r[1]}  {r[2] if r[2] else ""}')
if bad:
    sys.exit(1)
print('every mutation was caught')
