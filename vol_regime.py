import math
# Return forecasts unchanged (building blocks are vol-independent)
NET={'QQQ':8.18,'IEMG':8.94,'SGOV':3.16,'BMNR':9.98}
ER ={'QQQ':.18,'IEMG':.09,'SGOV':.09,'BMNR':0.}
DD ={'QQQ':40.,'IEMG':33.,'SGOV':.3,'BMNR':85.}

UPLIFT = 18.9/14.32          # VIX mean 18.9 vs spot 14.32
print(f"vol uplift factor = 18.9/14.32 = {UPLIFT:.4f}\n")

CALM = dict(vol={'QQQ':21.,'IEMG':18.,'SGOV':.5,'BMNR':95.},
            rho={('QQQ','IEMG'):.72,('QQQ','BMNR'):.65,('IEMG','BMNR'):.55})
NORM = dict(vol={'QQQ':21*UPLIFT,'IEMG':18*UPLIFT,'SGOV':.5,'BMNR':95*1.15},
            rho={('QQQ','IEMG'):.85,('QQQ','BMNR'):.80,('IEMG','BMNR'):.72})
print("sleeve vol by regime:")
for k in NET: print(f"  {k:<5} calm {CALM['vol'][k]:>6.1f}%   normalized {NORM['vol'][k]:>6.1f}%")

def rho(R,a,b):
    if a==b: return 1.
    if 'SGOV' in (a,b): return 0.
    return R.get((a,b),R.get((b,a)))

def stats(w,REG,ddmult=1.70):
    ks=list(w); V=REG['vol']; R=REG['rho']
    cagr=sum(w[k]/100*NET[k] for k in ks)
    var=sum((w[a]/100)*(w[b]/100)*V[a]*V[b]*rho(R,a,b) for a in ks for b in ks)
    vol=math.sqrt(var)
    mrc={a:(w[a]/100)*sum((w[b]/100)*V[a]*V[b]*rho(R,a,b) for b in ks)/vol for a in ks}
    t=sum(mrc.values())
    return dict(cagr=cagr,vol=vol,dd=vol*ddmult,
                fee=sum(w[k]/100*ER[k] for k in ks),
                rc={k:mrc[k]/t*100 for k in ks},
                sharpe=(cagr-NET['SGOV'])/vol,
                naive=sum(w[k]/100*DD[k] for k in ks))

# ---- frontier under the NORMALIZED regime (the design case) ----
print("\n=== frontier, NORMALIZED-vol regime (BMNR=5 mandated floor/cap) ===")
c=[]
for q in range(5,101,5):
  for i in range(5,101,5):
    for s in range(15,101,5):
      if q+i+s+5!=100: continue
      w={'QQQ':q,'IEMG':i,'SGOV':s,'BMNR':5}
      st=stats(w,NORM); c.append((w,st))
c.sort(key=lambda x:-x[1]['sharpe'])
print(f"{'QQQ':>4}{'IEMG':>5}{'SGOV':>5} | {'CAGR':>6}{'vol':>7}{'maxDD':>7}{'Sharpe':>8}")
for w,st in c[:6]:
    print(f"{w['QQQ']:>4}{w['IEMG']:>5}{w['SGOV']:>5} | {st['cagr']:>6.2f}{st['vol']:>7.2f}{-st['dd']:>7.1f}{st['sharpe']:>8.3f}")

CANDS={'BASELINE (10yr strategic)':{'QQQ':45,'IEMG':25,'SGOV':25,'BMNR':5},
       'PRIOR OPT (calm-vol sized)':{'QQQ':30,'IEMG':40,'SGOV':25,'BMNR':5},
       'NEW OPT (vol-normalized)':{'QQQ':25,'IEMG':40,'SGOV':30,'BMNR':5}}
for nm,w in CANDS.items():
    print(f"\n--- {nm}  {w}")
    for rn,REG in [('calm  ',CALM),('normal',NORM)]:
        st=stats(w,REG)
        print(f"   {rn}: CAGR {st['cagr']:.2f}%  vol {st['vol']:.2f}%  maxDD -{st['dd']:.1f}%  Sharpe {st['sharpe']:.3f}")
    st=stats(w,NORM)
    print(f"   fee {st['fee']:.3f}%   naive-stress DD -{st['naive']:.1f}%")
    print(f"   risk contrib (normalized): " + "  ".join(f"{k} {st['rc'][k]:.1f}%" for k in w))
    print(f"   $10,000 -> ${10000*(1+st['cagr']/100)**10:,.0f}")
    for h,lab in [(0.25,'3mo'),(0.5,'6mo'),(1.0,'12mo')]:
        print(f"     {lab:>4} sigma {st['vol']*math.sqrt(h):5.2f}%   95% VaR {st['cagr']*h-1.645*st['vol']*math.sqrt(h):+6.1f}%")

# ---- Booth-Fama diversification (rebalancing) return: 0.5*(sum wi*sigma_i^2 - sigma_p^2)
print("\n=== REBALANCING PREMIUM (Booth-Fama diversification return) ===")
def rebal(w,REG):
    V=REG['vol']
    wavg=sum(w[k]/100*(V[k]/100)**2 for k in w)
    sp=(stats(w,REG)['vol']/100)**2
    return 0.5*(wavg-sp)*100
for nm,w in CANDS.items():
    rc_=rebal(w,CALM); rn_=rebal(w,NORM)
    print(f"  {nm:<28} calm {rc_:.3f}%/yr   normalized {rn_:.3f}%/yr   uplift {rn_-rc_:+.3f}")

print("\n=== TOTAL EXPECTED (static CAGR + rebalancing premium), NORMALIZED regime ===")
for nm,w in CANDS.items():
    st=stats(w,NORM); tot=st['cagr']+rebal(w,NORM)
    print(f"  {nm:<28} static {st['cagr']:.2f}% + rebal {rebal(w,NORM):.2f}% = {tot:.2f}%   "
          f"maxDD -{st['dd']:.1f}%   ret/risk {(tot-NET['SGOV'])/st['dd']:.3f}")
    print(f"     $10,000 -> ${10000*(1+tot/100)**10:,.0f}")

# ---- frontier on TOTAL return incl. rebalancing, normalized regime, penalising drawdown
print("\n=== frontier on (static+rebal) per unit of maxDD, normalized regime ===")
c2=[]
for q in range(5,101,5):
  for i in range(5,101,5):
    for s in range(15,101,5):
      if q+i+s+5!=100: continue
      w={'QQQ':q,'IEMG':i,'SGOV':s,'BMNR':5}
      st=stats(w,NORM); tot=st['cagr']+rebal(w,NORM)
      c2.append((w,tot,st['dd'],(tot-NET['SGOV'])/st['dd']))
c2.sort(key=lambda x:-x[3])
print(f"{'QQQ':>4}{'IEMG':>5}{'SGOV':>5} | {'total':>7}{'maxDD':>8}{'ret/DD':>8}")
for w,tot,dd,r in c2[:8]:
    print(f"{w['QQQ']:>4}{w['IEMG']:>5}{w['SGOV']:>5} | {tot:>7.2f}{-dd:>8.1f}{r:>8.3f}")
