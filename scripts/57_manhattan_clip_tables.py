"""NEW (reconstructed from an ad-hoc command run during the analysis; not the exact script used at the time).
Input : outputs/manhattan_clip_runs.csv   Output: outputs/manhattan_clip_comparison.csv, outputs/manhattan_clip_ratios.csv
Before/after-clip comparison (4 settings = forward/reverse x single 08:00 / mean of 5 times) and the ADA-share and bus-gain ratios."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py

import pandas as pd, numpy as np
T=pd.read_csv(O+"manhattan_clip_runs.csv",dtype={"scenario":str,"time":str}); R_=T[T.direction!="walk"]
H=list(R_.hospital.unique()); rows=[]
for h in H:
    for d in ("fwd","rev"):
        for mode in ("single_0800","mean_5times"):
            v={}
            for s in "1234":
                x=R_[(R_.hospital==h)&(R_.direction==d)&(R_.scenario==s)]; x=x[x.time=="08:00"] if mode=="single_0800" else x
                v[s]=dict(area_before=x.area_before.mean(),res_before=x.res_before.mean(),area_after=x.area_after.mean(),res_after=x.res_after.mean(),res_after_sd=x.res_after.std(ddof=1) if len(x)>1 else np.nan,area_after_sd=x.area_after.std(ddof=1) if len(x)>1 else np.nan,area_after_min=x.area_after.min(),area_after_max=x.area_after.max(),res_after_min=x.res_after.min(),res_after_max=x.res_after.max())
            for s in "1234":
                r=dict(hospital=h,direction={"fwd":"forward (depart)","rev":"reverse (arrive by)"}[d],mode=mode,scenario=s,**v[s])
                r["area_pct_of_1_before"]=100*v[s]["area_before"]/v["1"]["area_before"]; r["area_pct_of_1_after"]=100*v[s]["area_after"]/v["1"]["area_after"]; rows.append(r)
C=pd.DataFrame(rows); rt=[]
for h in H:
    for d in ("forward (depart)","reverse (arrive by)"):
        for mode in ("single_0800","mean_5times"):
            g=lambda s,c:C[(C.hospital==h)&(C.direction==d)&(C["mode"]==mode)&(C.scenario==s)][c].iloc[0]
            for c,n in (("area","area"),("res","residents")):
                for suffix in ("before","after"):
                    k=f"{c}_{suffix}"; rt.append(dict(hospital=h,direction=d,mode=mode,metric=n,clip=suffix,ratio_2_over_1=100*g("2",k)/g("1",k),ratio_4_over_3=100*g("4",k)/g("3",k),ratio_4_over_2=100*g("4",k)/g("2",k),ratio_3_over_1=100*g("3",k)/g("1",k),bus_gain_ada_abs=g("4",k)-g("2",k),bus_gain_anyone_abs=g("3",k)-g("1",k)))
C.to_csv(O+"manhattan_clip_comparison.csv",index=False); pd.DataFrame(rt).to_csv(O+"manhattan_clip_ratios.csv",index=False)
