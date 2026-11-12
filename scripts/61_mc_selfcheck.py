import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"mc_core.py")).read())
import time
# 1) sampling frequency vs analytic probability
rng=np.random.default_rng(20261111); U=rng.random((20000,len(ELEVS))); p=p_up("mean"); up=U<p
blk={P:{"PN":0,"PS":0,"both":0} for P in STATIONS}
for k in range(len(U)):
    ok=station_ok(up[k])
    for P,d in ok.items():
        blk[P]["PN"]+=not d["PN"]; blk[P]["PS"]+=not d["PS"]; blk[P]["both"]+=(not d["PN"]) or (not d["PS"])
stt=ST.set_index("gtfs_stop_id")
print("station 'not fully accessible' frequency (20,000 draws) vs 1 - station_prob_mean_fill from station_table:")
for P,s in STATIONS.items():
    an=(1-float(stt.loc[P,"station_prob_mean_fill"])) if P in stt.index else np.nan
    print(f"  {s['name']:28s} MC {100*blk[P]['both']/len(U):5.2f}%   analytic {100*an:5.2f}%")
# 2) dedup (blocked ∩ reached) equals full recompute
BUSR=prep_bus("rev"); h="NYP/Columbia (CUIMC)"; st_=origin_state(HOSP[h]); T0=-28800
base,bd=run_cfg(st_,BUSR,T0,True,set()); reached=set(np.flatnonzero(base[:len(kids)]<1e8))
print("reverse baseline: child platforms reached",len(reached),"of",len(kids))
bad=0; tested=0; t0=time.time()
for k in range(1000):
    full=blocked_children(station_ok(up[k])); 
    if not full: continue
    if tested>=25: break
    restr=full&reached
    _,d_full=run_cfg(st_,BUSR,T0,True,full); _,d_res=run_cfg(st_,BUSR,T0,True,restr)
    same=(np.isfinite(d_full)==np.isfinite(d_res)).all() and np.nanmax(np.abs(np.where(np.isfinite(d_full),d_full-d_res,0)))<1e-6
    bad+=not same; tested+=1
print(f"dedup check: {tested} random outage draws, full recompute == restricted-to-reached recompute in {tested-bad}/{tested} ({time.time()-t0:.0f}s)")
