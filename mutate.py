#!/usr/bin/env python3
"""Mutation test for the validator.

validate.py can only be trusted if it actually fails when the model changes. This
perturbs one input at a time, re-runs validate.py, and reports any mutation that
still passes -- a figure the harness does not really police. More than half the
checks are `present()`, which only asserts a string appears somewhere in the page;
this is what proves they bite.

    python3 mutate.py        # expect: every mutation was caught

A mutation that cannot find its target is reported and FAILS the run. An earlier
version printed 'every mutation was caught' while quietly skipping seven whose
hardcoded old values no longer matched the model -- the harness reassuring itself
about inputs it had stopped testing. Value-specific targets are now read from the
live source.

The model file is restored after every run, including on failure.
"""
import subprocess, shutil, re, sys, os
REPO=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(REPO,'portfolio_model.py')
orig=open(SRC).read()
_REV=int(re.search(r'REVISION = (\d+)', orig).group(1))
_m=re.search(r"\('(\d{4}-\d\d-\d\d)', ([\d.]+)\)\)\n", orig)   # last VIX_SERIES entry
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
]
survived=[]; skipped=[]
for name, old, new in MUT:
    if orig.count(old)!=1:
        skipped.append((name, orig.count(old))); continue
    open(SRC,'w').write(orig.replace(old,new))
    try:
        r=subprocess.run([sys.executable,'validate.py'],cwd=REPO,capture_output=True,text=True,timeout=300)
        if r.returncode==0: survived.append(name)
    except Exception as e:
        survived.append(f'{name} (ERROR {e})')
    finally:
        open(SRC,'w').write(orig)
shutil.rmtree(f'{REPO}/__pycache__', ignore_errors=True)
print(f'{len(MUT)-len(skipped)} mutations run, {len(survived)} survived')
if skipped:
    print('SKIPPED -- these inputs are NOT being tested (pattern missing or ambiguous):')
    for s_ in skipped: print('   -', s_)
if survived:
    print('SURVIVED (unpoliced):')
    for s_ in survived: print('   -', s_)
if survived or skipped:
    sys.exit(1)
print('every mutation was caught')
