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
_LAST, _SPOT = _m.group(1), float(_m.group(2))
_MEAN = float(re.search(r'VIX_SERIES\[-1\]\[1\], ([\d.]+)', orig).group(1))
_SGOV = float(re.search(r'SGOV_GROSS = ([\d.]+)', orig).group(1))
def _num(pat):
    m = re.search(pat, orig)
    if not m: raise SystemExit(f'mutate.py: cannot locate {pat!r} in the model; update the table')
    return m.group(1)
_B = {f: _num(rf'BMNR = dict\([^)]*{f}=([\d.]+)') for f in ('stake_share','stake_yield','mnav')}
_P = {(t, f): _num(rf"'{t}':\s+dict\([^)]*{f}=([\d.]+)") for t in ('QQQ','IEMG')
      for f in ('ttm_div','px','basis_px','basis_fwd')}
_bump = lambda v, d: f'{float(v) + d:.{len(v.split(".")[1]) if "." in v else 0}f}'
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
 ("VIX latest close", f"('{_LAST}', {_SPOT})",  f"('{_LAST}', {_SPOT + 1})"),
 ("VIX series date", f"('{_LAST}', {_SPOT})",  f"('{_LAST[:-2]}20', {_SPOT})"),
 ("VIX_MEAN",       f"VIX_SERIES[-1][1], {_MEAN}", f"VIX_SERIES[-1][1], {_MEAN + 0.5}"),
 ("DD_MULT",        "DD_MULT = 1.70",           "DD_MULT = 1.75"),
 ("DD QQQ",         "'QQQ': 40.0",              "'QQQ': 42.0"),
 ("DD IEMG",        "'IEMG': 39.0",             "'IEMG': 36.0"),
 ("DD BMNR",        "'BMNR': 85.0",             "'BMNR': 80.0"),
 ("vol QQQ calm",   "vol={'QQQ':21.0,'IEMG':18.0","vol={'QQQ':22.0,'IEMG':18.0"),
 ("vol IEMG calm",  "'IEMG':18.0,'SGOV':0.5,'BMNR':95.0}","'IEMG':19.0,'SGOV':0.5,'BMNR':95.0}"),
 ("vol SGOV norm",  "'SGOV':0.5,'BMNR':95.0*1.15}",     "'SGOV':1.5,'BMNR':95.0*1.15}"),
 ("rho QQQ-IEMG",   "('QQQ','IEMG'):0.66",      "('QQQ','IEMG'):0.70"),
 ("rho QQQ-BMNR",   "('QQQ','BMNR'):0.65",      "('QQQ','BMNR'):0.60"),
 ("rho stressed",   "('QQQ','IEMG'):0.85",      "('QQQ','IEMG'):0.88"),
 ("rho BMNR stressed","('QQQ','BMNR'):0.80",    "('QQQ','BMNR'):0.84"),
 ("rho IEMG-BMNR str","('IEMG','BMNR'):0.72",   "('IEMG','BMNR'):0.76"),
 ("BMNR norm mult", "95.0*1.15",                "95.0*1.20"),
 ("baseline QQQ",   "'baseline':  {'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5}",
                    "'baseline':  {'QQQ':40,'IEMG':30,'SGOV':25,'BMNR':5}"),
 ("optimized QQQ",  "'optimized': {'QQQ':35,'IEMG':30,'SGOV':30,'BMNR':5}",
                    "'optimized': {'QQQ':30,'IEMG':35,'SGOV':30,'BMNR':5}"),
 ("driver growth",  "('Growth momentum',7.0,.25)","('Growth momentum',6.5,.25)"),
 ("driver policy",  "('Monetary policy',2.0,.20)","('Monetary policy',2.5,.20)"),
 ("region asia",    "'Asia / EM':[5.5,6.5,7.0,7.5]","'Asia / EM':[5.0,6.5,7.0,7.5]"),
 ("region europe",  "'Europe':[3.0,3.5,4.0,5.0]", "'Europe':[3.5,3.5,4.0,5.0]"),
 ("JPM us",         "dict(us=6.70, em=7.80",    "dict(us=6.20, em=7.80"),
 ("JPM em",         "us=6.70, em=7.80",         "us=6.70, em=8.30"),
 ("Vanguard em",    "dict(us=5.20, em=4.30",    "dict(us=5.20, em=6.30"),
 ("REVISION",       f"REVISION = {_REV}",       f"REVISION = {_REV + 1}"),
 # added in Rev. 20: inputs the review found no mutation for
 ("IEMG basis px",  f"basis_px={_P['IEMG','basis_px']}",   f"basis_px={_bump(_P['IEMG','basis_px'], 2)}"),
 ("IEMG er",        "er=0.09, eps=7.50",        "er=0.11, eps=7.50"),
 ("VIX 2026 low",   "low=14.13,",               "low=13.63,"),
 ("VIX low date",   "low_date='2026-08-14'",    "low_date='2026-08-21'"),
 ("FOMC date",      "FOMC_DATE  = '2026-09-16'", "FOMC_DATE  = '2026-09-17'"),
 ("BMNR held",      "held=5_983_940",           "held=6_083_940"),
 ("Brent level only", "brent=103.08,",          "brent=104.08,"),
 ("10y level+change", "ust10=5.12,   ust10_prev=4.96,  ust10_chg_bp=16",
                      "ust10=5.15,   ust10_prev=4.96,  ust10_chg_bp=19"),
 ("driver inflation", "('Inflation trajectory',3.0,.15)", "('Inflation trajectory',3.5,.15)"),
 ("driver liquidity", "('Liquidity & credit',5.5,.15)",   "('Liquidity & credit',5.0,.15)"),
 ("driver valuation", "('Valuation & positioning',4.0,.15)", "('Valuation & positioning',4.5,.15)"),
 ("driver geopol",  "('Geopolitical risk',2.0,.10)",    "('Geopolitical risk',2.5,.10)"),
 ("region US",      "'United States':[5.0,5.5,6.5,7.0]", "'United States':[5.0,5.5,6.0,7.0]"),
 ("Fidelity em",    "dict(us=4.40, em=8.10",    "dict(us=4.40, em=8.60"),
 ("BlackRock us",   "dict(us=5.00, em=7.10",    "dict(us=5.50, em=7.10"),
 ("JPM EM vol",     "em_vol=20.9",              "em_vol=24.9"),
]

# generator mutations: (name, text in build.py, replacement) -- each a plausible bug
def G(name, old, new): return (name, old, new)
GEN = [
 G("VaR column from the wrong book", 'neg(bc["var"][h])', 'neg(oc["var"][h])'),
 G("term band from unrounded sigma", "±{f(1.645 * term[h], 2 if h < 0.1 else 1)}%", "±{f(1.645 * SPOT * math.sqrt(h), 2 if h < 0.1 else 1)}%"),
 G("regions ranked ascending", "RANKED = sorted(E['regions'], key=lambda k: -E['regions'][k]['mean'])", "RANKED = sorted(E['regions'], key=lambda k: E['regions'][k]['mean'])"),
 G("slide drawdown from the sigma model", "{neg(M.DD[t], 0 if M.DD[t] >= 1 else 1)}%", "{neg(M.REGIME['calm']['vol'][t] * M.DD_MULT, 0)}%"),
 G("CAGR delta reversed", "d_(b['calm']['cagr_d'], o['calm']['cagr_d'], 2)", "d_(o['calm']['cagr_d'], b['calm']['cagr_d'], 2)"),
 G("risk-adjusted tie threshold", "abs(RV['QQQ'] - RV['IEMG']) < 0.01", "abs(RV['QQQ'] - RV['IEMG']) < 0.0001"),
 G("masthead shows the prior 10-year", "<span>UST 10y {MK['ust10']:.2f}%</span>", "<span>UST 10y {MK['ust10_prev']:.2f}%</span>"),
 G("risk card from the calm regime", "    rc = on['rc']", "    rc = oc['rc']"),
 G("gap from unrounded CAGRs", "GAP = M.r2h(M.r2h(ST['baseline']['calm']['cagr_d']) - M.r2h(ST['optimized']['calm']['cagr_d']))", "GAP = M.r2h(ST['baseline']['calm']['cagr'] - ST['optimized']['calm']['cagr'])"),
 G("standard error from the wrong regime", "f\"±{M.se_level('optimized'):.2f} pts\"", "f\"±{M.se_level('optimized', 'normalized'):.2f} pts\""),
 G("slide terminal from gross", "term = lambda k: f\"${E['sleeves'][k]['terminal']:,}\"", "term = lambda k: f\"${round(10000 * (1 + M.A[k]['gross'] / 100) ** 10):,}\""),
 G("expense row loses its minus", "if signed is None: return f'<td class=\"n\">{MINUS}{x:.2f}</td>'", "if signed is None: return f'<td class=\"n\">{x:.2f}</td>'"),
 G("VIX discount from the prior close", "Spot is {f((1 - SPOT / M.VIX_MEAN) * 100, 1)}% below", "Spot is {f((1 - PREV / M.VIX_MEAN) * 100, 1)}% below"),
 G("gauge needle axes swapped", "x2=\"{g['needle'][0]}\" y2=\"{g['needle'][1]}\"", "x2=\"{g['needle'][1]}\" y2=\"{g['needle'][0]}\""),
 G("disclaimer dated to a fund price", "Market data to the {day(MK['asof'], False)} close", "Market data to the {day(M.PRICES['QQQ']['px_asof'], False)} close"),
 G("efficient count off by one", "{len(EFF)} allocations are efficient.", "{len(EFF) + 1} allocations are efficient."),
 G("driver bar on the 1-10 scale", '<div class="drv-bar"><i style="width:{fill}%;background:{t}"></i></div>', '<div class="drv-bar"><i style="width:{s5 * 20:.1f}%;background:{t}"></i></div>'),
 G("BMNR total mNAV over crypto", "{M.BMNR_MCAP_B / H['total_b']:.2f}×", "{M.BMNR_MCAP_B / H['crypto_b']:.2f}×"),
 G("regional lead from 6 months", "for h in (0, 3)]", "for h in (1, 3)]"),
 G("QQQ price dated from IEMG", "(f\"Price ({day(P['QQQ']['px_asof'])})\"", "(f\"Price ({day(P['IEMG']['px_asof'])})\""),
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

jobs = [('model',) + m for m in MUT] + [('gen',) + g for g in GEN]
with ThreadPoolExecutor(max_workers=4) as ex:
    res = list(ex.map(lambda j: run(*j), jobs))
bad = [r for r in res if r[0] != 'caught']
print(f'{len(MUT)} model and {len(GEN)} generator mutations run, '
      f'{sum(r[0] == "survived" for r in res)} survived')
for r in bad:
    print(f'  {r[0].upper():<9} {r[1]}  {r[2] if r[2] else ""}')
if bad:
    sys.exit(1)
print('every mutation was caught')
