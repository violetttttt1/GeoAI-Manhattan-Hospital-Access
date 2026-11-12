import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import numpy as np, pandas as pd, sys
sys.argv=['x']; exec(open((S+"study.py")).read().split("# ===== 1 elevators")[0])
st=rd("mta_stations/mta_stations.csv"); 
for nm in ["110 St-Malcolm X Plaza","Cathedral Pkwy (110 St)","110 St"]:
    for _,x in st[(st["Stop Name"]==nm)&(st.Borough=="M")].iterrows(): print(nm,x.Line,float(x["GTFS Latitude"]),float(x["GTFS Longitude"]),"signed m",north_m(float(x["GTFS Latitude"]),float(x["GTFS Longitude"])).round(0))
# ramps hospital-only
pr["lon"]=pr.the_geom.str.extract(r"POINT \(([-\d.]+) ")[0].astype(float); pr["lat"]=pr.the_geom.str.extract(r" ([-\d.]+)\)")[0].astype(float)
nb,hb,ia,parts=area(pr.lat,pr.lon); man=(pr.Borough=="1").values
print("ramps north-only",(nb&man).sum(),"hosp-only (south of line)",(hb&~nb&man).sum(),"union",(ia&man).sum(),"| per hospital",{k:int((parts[k]&man).sum()) for k in parts})
# MBPO
rid="Ramp ID (No Id means a part of center cut)"; mb["RampID"]=mb[rid]
m=mb.merge(pr[["RampID","lat","lon"]].assign(inarea=(ia&man)),on="RampID",how="left")
print(pd.crosstab(m.Compliant.fillna("NA"),[m["Center Cut"],m.RampID.notna()]))
print("no-ID rows",m.RampID.isna().sum(),"| NaN Compliant & has ID",(m.Compliant.isna()&m.RampID.notna()).sum())
g=m.groupby("Station").agg(rows=("Station","size"),withID=("RampID",lambda s:s.notna().sum()),located=("lat",lambda s:s.notna().sum()),inarea=("inarea",lambda s:(s==True).sum()),minlat=("lat","min"),maxlat=("lat","max"))
g["noID"]=g.rows-g.withID; print(g.sort_values("minlat").to_string())
