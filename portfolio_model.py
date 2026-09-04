import math, itertools

# ============ VERIFIED INPUTS (Sep 4 2026) ============
# QQQ  : fwd P/E 25.17 (Siblis, Jul 1 26); div yld 0.65% (ChartRow, Aug 28 26); ER 0.18%
# IEMG : fwd P/E 11.61 (Siblis, Jan 1 26); div yld 2.29% (EEM proxy, May 8 26); ER 0.09%
# SGOV : 30-day SEC yield 3.63% (Sep 2 26); ER 0.09%
# BMNR : mNAV 1.02x on total NAV $15.6B; 85.9% of ETH staked

def valuation_drag(p_now, p_end, yrs=10):
    return ((p_end/p_now)**(1/yrs) - 1) * 100

print("=== BUILDING-BLOCK RETURN FORECASTS (10yr) ===")
qqq_val  = valuation_drag(25.17, 21.0)
iemg_val = valuation_drag(11.61, 12.5)
print(f"QQQ  valuation 25.17->21.0 : {qqq_val:+.2f}%/yr")
print(f"IEMG valuation 11.61->12.5 : {iemg_val:+.2f}%/yr")

qqq_gross  = 0.65 + 9.50 + qqq_val
iemg_gross = 2.29 + 7.50 + iemg_val - 1.50          # -1.50 EM FX drag for USD investor
sgov_gross = 3.25
bmnr_net   = 9.00 + 0.859*3.00 - valuation_drag(1.02,1.00)*-1*0 - 0.20 - 1.40
bmnr_net   = 9.00 + 0.859*3.00 - 0.20 - 1.40
print(f"\nQQQ  gross = 0.65 div + 9.50 eps {qqq_val:+.2f} val        = {qqq_gross:.2f}%")
print(f"IEMG gross = 2.29 div + 7.50 eps {iemg_val:+.2f} val -1.50 fx = {iemg_gross:.2f}%")
print(f"SGOV gross = {sgov_gross:.2f}%   (10yr avg bill yield assumption)")
print(f"BMNR net   = 9.00 eth + {0.859*3.00:.2f} stake -0.20 mnav -1.40 drag = {bmnr_net:.2f}%")

A = {
 'QQQ' : dict(gross=qqq_gross,  er=0.18, vol=21.0, dd=40.0),
 'IEMG': dict(gross=iemg_gross, er=0.09, vol=18.0, dd=33.0),
 'SGOV': dict(gross=sgov_gross, er=0.09, vol=0.5,  dd=0.3),
 'BMNR': dict(gross=bmnr_net,   er=0.00, vol=95.0, dd=85.0),
}
for k,v in A.items(): v['net']=round(v['gross']-v['er'],2)
print("\n=== NET (after fund fees) ===")
for k,v in A.items():
    print(f"  {k}: gross {v['gross']:.2f} - fee {v['er']:.2f} = NET {v['net']:.2f}%  -> $10k becomes ${10000*(1+v['net']/100)**10:,.0f}")

RHO={('QQQ','IEMG'):0.72,('QQQ','BMNR'):0.65,('IEMG','BMNR'):0.55,
     ('QQQ','SGOV'):0.0,('IEMG','SGOV'):0.0,('SGOV','BMNR'):0.0}
def rho(a,b): return 1.0 if a==b else RHO.get((a,b),RHO.get((b,a)))

def stats(w):
    ks=list(w)
    cagr=sum(w[k]/100*A[k]['net'] for k in ks)
    fee =sum(w[k]/100*A[k]['er']  for k in ks)
    var=sum((w[a]/100)*(w[b]/100)*A[a]['vol']*A[b]['vol']*rho(a,b) for a in ks for b in ks)
    vol=math.sqrt(var)
    mrc={a:(w[a]/100)*sum((w[b]/100)*A[a]['vol']*A[b]['vol']*rho(a,b) for b in ks)/vol for a in ks}
    ndd=sum(w[k]/100*A[k]['dd'] for k in ks)
    return dict(cagr=cagr,fee=fee,vol=vol,mrc=mrc,ndd=ndd,
                dd=vol*1.65, dd_hi=vol*1.75, sharpe=(cagr-A['SGOV']['net'])/vol)

# ---- frontier search: 5% increments, all sleeves >=5, BMNR<=5 (risk cap), SGOV>=20 (dd floor)
print("\n=== FRONTIER SEARCH (5% increments) ===")
cands=[]
for q in range(5,101,5):
  for i in range(5,101,5):
    for s in range(20,101,5):
      b=100-q-i-s
      if b!=5: continue
      w={'QQQ':q,'IEMG':i,'SGOV':s,'BMNR':b}
      st=stats(w); cands.append((w,st))
cands.sort(key=lambda x:-x[1]['sharpe'])
print(f"{'QQQ':>4}{'IEMG':>5}{'SGOV':>5}{'BMNR':>5} | {'CAGR':>6}{'vol':>7}{'maxDD':>7}{'Sharpe':>8}")
for w,st in cands[:8]:
    print(f"{w['QQQ']:>4}{w['IEMG']:>5}{w['SGOV']:>5}{w['BMNR']:>5} | "
          f"{st['cagr']:>6.2f}{st['vol']:>7.2f}{-st['dd']:>7.1f}{st['sharpe']:>8.3f}")

BASE={'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5}
OPT ={'QQQ':30,'IEMG':40,'SGOV':25,'BMNR':5}
print("\n=== CANDIDATE PORTFOLIOS ===")
for nm,w in [('BASELINE',BASE),('OPTIMIZED',OPT)]:
    st=stats(w); tot=sum(st['mrc'].values())
    print(f"\n--- {nm} {w}  (sum {sum(w.values())})")
    print(f"  net CAGR {st['cagr']:.2f}%  | wtd fee {st['fee']:.3f}%  | vol {st['vol']:.2f}%")
    print(f"  horizon vol   3mo {st['vol']*.5:.2f}%  6mo {st['vol']*math.sqrt(.5):.2f}%  12mo {st['vol']:.2f}%")
    print(f"  95% VaR       3mo {st['cagr']*.25-1.645*st['vol']*.5:+.1f}%  "
          f"6mo {st['cagr']*.5-1.645*st['vol']*math.sqrt(.5):+.1f}%  12mo {st['cagr']-1.645*st['vol']:+.1f}%")
    print(f"  maxDD  model -{st['dd']:.1f}% (hi -{st['dd_hi']:.1f}%)  | naive wtd -{st['ndd']:.1f}%")
    print(f"  Sharpe {st['sharpe']:.3f}")
    print(f"  risk contrib " + "  ".join(f"{k} {st['mrc'][k]/tot*100:.1f}%" for k in w))
    print(f"  $10,000 -> ${10000*(1+st['cagr']/100)**10:,.0f}   "
          f"fee drag ${10000*(1+(st['cagr']+st['fee'])/100)**10 - 10000*(1+st['cagr']/100)**10:,.0f}")

# ---- macro gauge
print("\n=== MACRO GAUGE ===")
sub=[('Growth momentum',7.0,.25),('Inflation trajectory',4.0,.15),('Monetary policy',3.5,.20),
     ('Liquidity & credit',6.0,.15),('Valuation & positioning',3.5,.15),('Geopolitical risk',3.0,.10)]
assert abs(sum(w for _,_,w in sub)-1.0)<1e-9
g=sum(s*w for _,s,w in sub)
for n,s,w in sub: print(f"  {n:<26} {s:>4.1f} x {w:.2f} = {s*w:.3f}")
print(f"  GAUGE = {g:.2f}/10")

# ---- VIX term structure
print("\n=== VIX TERM STRUCTURE (spot 14.32) ===")
vix=14.32
for lbl,h in [('1 day',1/252),('3 months',0.25),('6 months',0.5),('12 months',1.0)]:
    s=vix*math.sqrt(h); print(f"  {lbl:<10} sqrt {math.sqrt(h):.3f}  sigma {s:.2f}%  95% band +/-{1.645*s:.1f}%")
va=18.4
print(f"  VIX vs ~{va} 10yr avg: {(vix-va)/va*100:.1f}% below")

# ---- SVG geometry check
print("\n=== SVG GEOMETRY ===")
C=2*math.pi*64
print(f"  donut circumference r=64: {C:.3f}")
for nm,w in [('BASELINE',BASE),('OPTIMIZED',OPT)]:
    off=0.0; print(f"  {nm}:")
    for k in ['QQQ','IEMG','SGOV','BMNR']:
        seg=w[k]/100*C
        print(f"    {k:<5} {w[k]:>3}%  dasharray=\"{seg:.2f} {C-seg:.2f}\" dashoffset=\"{-off:.2f}\"")
        off+=seg
    assert abs(off-C)<1e-6, "segments must close the circle"
    print(f"    closes at {off:.3f} == {C:.3f} OK")
L=math.pi*80
print(f"  gauge semicircle r=80 length {L:.3f}; fill {g/10:.3f} -> dasharray {g/10*L:.2f} {L:.2f}")
th=math.radians(180-g/10*180)
print(f"  needle angle {math.degrees(th):.2f}deg -> x={106+62*math.cos(th):.2f} y={116-62*math.sin(th):.2f}")
