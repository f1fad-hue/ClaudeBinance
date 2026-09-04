import math, itertools

# Asset assumptions (annualised, %) -- forecasts, clearly estimates
A = {
 'QQQ' : dict(gross=8.48, er=0.18, vol=21.0, dd=40.0),
 'IEMG': dict(gross=8.69, er=0.09, vol=18.0, dd=33.0),
 'SGOV': dict(gross=3.19, er=0.09, vol=0.5,  dd=0.3),
 'BMNR': dict(gross=11.00, er=0.00, vol=95.0, dd=85.0),
}
for k,v in A.items(): v['net']=v['gross']-v['er']

RHO = {('QQQ','IEMG'):0.72, ('QQQ','BMNR'):0.65, ('IEMG','BMNR'):0.55,
       ('QQQ','SGOV'):0.0, ('IEMG','SGOV'):0.0, ('SGOV','BMNR'):0.0}
def rho(a,b):
    if a==b: return 1.0
    return RHO.get((a,b), RHO.get((b,a)))

def stats(w):
    keys=list(w)
    cagr=sum(w[k]/100*A[k]['net'] for k in keys)
    fee =sum(w[k]/100*A[k]['er']  for k in keys)
    var=0.0
    for a in keys:
        for b in keys:
            var += (w[a]/100)*(w[b]/100)*A[a]['vol']*A[b]['vol']*rho(a,b)
    vol=math.sqrt(var)
    # risk contribution
    mrc={}
    for a in keys:
        cov=sum((w[b]/100)*A[a]['vol']*A[b]['vol']*rho(a,b) for b in keys)
        mrc[a]=(w[a]/100)*cov/vol if vol else 0
    naive_dd=sum(w[k]/100*A[k]['dd'] for k in keys)
    return cagr, fee, vol, mrc, naive_dd

BASE = {'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5}
OPT  = {'QQQ':35,'IEMG':35,'SGOV':25,'BMNR':5}

for name,w in [('BASELINE',BASE),('OPTIMIZED',OPT)]:
    c,f,v,mrc,ndd = stats(w)
    print(f"\n=== {name} {w} sum={sum(w.values())}")
    print(f"  net CAGR   : {c:.2f}%   (weighted fee {f:.3f}%)")
    print(f"  vol ann    : {v:.2f}%")
    print(f"    3mo vol  : {v*math.sqrt(0.25):.2f}%   6mo: {v*math.sqrt(0.5):.2f}%   12mo: {v:.2f}%")
    print(f"  naive wDD  : -{ndd:.1f}%")
    print(f"  modelled maxDD (1.65-1.75x vol): -{v*1.75:.1f}% .. -{v*1.65:.1f}%")
    print(f"  Sharpe vs SGOV: {(c-A['SGOV']['net'])/v:.3f}")
    print(f"  95% 1yr VaR: {c-1.645*v:+.1f}%   3mo: {c*0.25-1.645*v*math.sqrt(0.25):+.1f}%   6mo: {c*0.5-1.645*v*math.sqrt(0.5):+.1f}%")
    tot=sum(mrc.values())
    print("  risk contribution:", {k: f"{mrc[k]/tot*100:.1f}%" for k in w})
    print(f"  $10,000 -> 10yr: ${10000*(1+c/100)**10:,.0f}")
    gc = c + f
    print(f"  gross-of-fee 10yr: ${10000*(1+gc/100)**10:,.0f}  (fee drag ${10000*(1+gc/100)**10-10000*(1+c/100)**10:,.0f})")

# per-asset 10yr on 10k
print("\n=== per-asset 10yr net")
for k,v in A.items():
    print(f"  {k}: gross {v['gross']:.2f} - fee {v['er']:.2f} = net {v['net']:.2f}%  ->  ${10000*(1+v['net']/100)**10:,.0f}   maxDD -{v['dd']:.0f}%  vol {v['vol']:.0f}%")

# BMNR derived
print("\n=== BMNR derived")
mc, eth_val, px = 15.96e9, 14.48e9, 26.45
print(f"  mNAV = {mc/eth_val:.3f}x")
print(f"  52w drawdown = {(12.80-65.60)/65.60*100:.1f}%")
print(f"  staked = {5067309/5901112*100:.1f}%")
print(f"  implied shares = {mc/px/1e6:.1f}M ; ETH/share = {5901112/(mc/px):.5f}")

# Macro gauge
sub = [('Growth momentum',7.0,.25),('Inflation trajectory',4.0,.15),('Monetary policy',4.0,.20),
       ('Liquidity & credit',6.0,.15),('Valuation & positioning',3.0,.15),('Geopolitical risk',3.0,.10)]
g=sum(s*w for _,s,w in sub); print(f"\n=== macro gauge = {g:.2f}/10  (weights sum {sum(w for _,_,w in sub)})")
