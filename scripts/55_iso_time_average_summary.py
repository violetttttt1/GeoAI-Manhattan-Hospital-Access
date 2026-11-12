"""NEW (reconstructed from an ad-hoc command run during the analysis; not the exact script used at the time).
Input : outputs/hospital_isochrone_timeavg_runs.csv   Output: outputs/hospital_isochrone_timeavg_summary.csv
Mean / SD / min / max / CV over the five departure times (07:30-08:30), per hospital and scenario (forward, whole network, unclipped)."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py

import pandas as pd
T=pd.read_csv(O+"hospital_isochrone_timeavg_runs.csv",dtype={"scenario":str,"dep":str}); H=list(T.hospital.unique()); out=[]
for h in H:
    for s in "1234":
        x=T[(T.hospital==h)&(T.scenario==s)].sort_values("dep"); r=dict(hospital=h,scenario=s)
        for c,n in (("area_land_km2","area"),("amb_pop","res"),("area_manhattan_km2","area_man"),("area_bronx_km2","area_bx"),("amb_manhattan","res_man"),("amb_bronx","res_bx")):
            v=x[c].values; r[n+"_mean"]=v.mean(); r[n+"_sd"]=v.std(ddof=1); r[n+"_min"]=v.min(); r[n+"_max"]=v.max(); r[n+"_cv"]=100*v.std(ddof=1)/v.mean(); r[n+"_range_pct"]=100*(v.max()-v.min())/v.mean()
        r["univ_mean"]=x.universe_pop.mean(); out.append(r)
pd.DataFrame(out).to_csv(O+"hospital_isochrone_timeavg_summary.csv",index=False)
