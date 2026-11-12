import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import numpy as np, pandas as pd
exec(open((S+"study.py")).read().split("# ===== 1 elevators")[0])
pr["lon"]=pr.the_geom.str.extract(r"POINT \(([-\d.]+) ")[0].astype(float); pr["lat"]=pr.the_geom.str.extract(r" ([-\d.]+)\)")[0].astype(float)
mn=pr[pr.Borough=="1"]
f=lambda s: s.fillna("").str.upper().str.contains(r"\b110 STREET\b|\b110 ST\b|CENTRAL PARK NORTH")
sel=mn[f(mn.StName1)|f(mn.StName2)]; print(len(sel)); print(sel[["StName1","StName2"]].value_counts().head(8))
# keep corners where 110 is the *street running* (other street is avenue-ish); just fit robustly
x,y=xy(sel.lat,sel.lon); P=np.c_[x,y]; c=P.mean(0)
for it in range(5):
    u,s,vt=np.linalg.svd(P-c); dirv=vt[0]; nrm=np.array([-dirv[1],dirv[0]]); r=(P-c)@nrm
    keep=np.abs(r)<max(3*np.median(np.abs(r))*1.48,40); P=P[keep]; c=P.mean(0)
print("fit n",len(P),"angle",np.degrees(np.arctan2(dirv[1],dirv[0])).round(1),"resid sd m",r[keep].std().round(1))
if nrm[1]<0: nrm=-nrm
def north_fit(lat,lon):
    xx,yy=xy(lat,lon); return (xx-c[0])*nrm[0]+(yy-c[1])*nrm[1]
# compare two lines at test points
for nm,la,lo in [("1 Cathedral",40.803967,-73.966847),("B/C Cath",40.800603,-73.958161),("2/3 110",40.799075,-73.951822),("6 110",40.79502,-73.94425)]:
    print(nm,"fit signed m",north_fit(la,lo).round(0),"two-station line",north_m(la,lo).round(0))
man=(pr.Borough=="1").values
print("ramps north by 2-station line",((north_m(pr.lat,pr.lon)>0)&man).sum(),"| by fitted 110St line",((north_fit(pr.lat,pr.lon)>0)&man).sum(),"| differ",(((north_m(pr.lat,pr.lon)>0)!=(north_fit(pr.lat,pr.lon)>0))&man).sum())
np.save((S+"fit.npy"),np.r_[c,nrm])
