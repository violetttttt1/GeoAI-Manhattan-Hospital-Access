import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import re, numpy as np, pandas as pd
R=R
rd=lambda p: pd.read_csv(R+p,dtype=str,low_memory=False)
av=rd("elevator_availability/elevator_availability.csv"); inv=rd("elevator_inventory/elevator_inventory.csv")
pr=rd("ped_ramp_locations/ped_ramp_locations.csv"); pg=rd("ramp_program_progress/ramp_program_progress.csv"); mb=rd("mbpo_ramp_report/mbpo_ramp_report.csv")
S_=S
LAT0,LON0=40.80,-73.95
def xy(lat,lon):
    lat=np.asarray(lat,float); lon=np.asarray(lon,float)
    return (lon-LON0)*111320*np.cos(np.radians(LAT0)), (lat-LAT0)*110574
A=np.array(xy(40.803967,-73.966847)); B=np.array(xy(40.79502,-73.94425))
d=(B-A)/np.linalg.norm(B-A); n=np.array([-d[1],d[0]])   # n points to the "north" side
if n[1]<0: n=-n
import os as _os
_f=np.load(S_+"fit.npy") if _os.path.exists(S_+"fit.npy") else np.r_[A,n]   # first run: two-station 110 St line; 21_study_area_line_fit.py writes the fitted line to data/cache/fit.npy
def north_m(lat,lon):
    x,y=xy(lat,lon); return (x-_f[0])*_f[2]+(y-_f[1])*_f[3]
print("check 110St stations signed dist (m):",{"B/C Cathedral":north_m(40.800603,-73.958161).round(0),"2/3 Malcolm X":north_m(40.7991,-73.9518).round(0)}, "angle deg",np.degrees(np.arctan2(d[1],d[0])).round(1))
HOSP={"Harlem Hospital":(40.8147102,-73.9392782),"NYP/CUIMC":(40.8409780,-73.9407016),"Mount Sinai Morningside":(40.8052373,-73.9613875)}
def hav(lat,lon,la0,lo0):
    lat=np.radians(np.asarray(lat,float));lon=np.radians(np.asarray(lon,float));la0=np.radians(la0);lo0=np.radians(lo0)
    a=np.sin((lat-la0)/2)**2+np.cos(lat)*np.cos(la0)*np.sin((lon-lo0)/2)**2; return 12742000*np.arcsin(np.sqrt(a))
def area(lat,lon):
    nm=north_m(lat,lon); north=nm>0
    hosp=np.zeros(len(nm),bool); parts={}
    for k,(la,lo) in HOSP.items():
        m=hav(lat,lon,la,lo)<=400; parts[k]=m; hosp|=m
    return north,hosp,north|hosp,parts
# ===== 1 elevators
ie=inv[(inv["Elevator or Escalator"]=="Elevator")].copy()
print("inv boroughs",ie.Borough.value_counts().to_dict())
ie["lat"]=ie["X Coordinate"].astype(float); ie["lon"]=ie["Y Coordinate"].astype(float)
nb,hb,inarea,parts=area(ie.lat,ie.lon); ie["north"]=nb; ie["hosp"]=hb; ie["inarea"]=inarea&(ie.Borough=="Manhattan").values
print("elev north-only",(nb&(ie.Borough=="Manhattan").values).sum(),"hosp-only (south of line)",(hb&~nb&(ie.Borough=="Manhattan").values).sum())
codes=set(av[av["Equipment Type"]=="Elevator"]["Equipment Code"]); av["m"]=pd.to_datetime(av.Month)
lastc=set(av[(av["Equipment Type"]=="Elevator")&(av.m==av.m.max())]["Equipment Code"])
z=ie[ie.inarea].copy(); z["in_av"]=z["Equipment Code"].isin(codes); z["in_last"]=z["Equipment Code"].isin(lastc)
print("T1 elevators in area",len(z),"with avail record",z.in_av.sum(),"WITHOUT",(~z.in_av).sum(),"| not in latest month",(~z.in_last).sum())
print(z[~z.in_av][["Equipment Code","Station Name","Station Description","Service Status","Maintained By","NYCT Owned","hosp","north"]].to_string())
print("in-area elevators by station null MRN",z["Station MRN"].isna().sum(), "| per-hospital counts",{k:int(np.sum(parts[k]&(ie.Borough=="Manhattan").values)) for k in parts})
z.to_csv(REB+"study_area_elevators.csv",index=False)
ie["dn"]=north_m(ie.lat,ie.lon); mm=ie[ie.Borough=="Manhattan"]; print("nearest elevators to 110St line (signed m):",mm.loc[(mm.dn.abs()).nsmallest(4).index,["Equipment Code","Station Name","dn"]].round(0).to_string())
# also escalators for reference
ies=inv[inv["Elevator or Escalator"]=="Escalator"].copy(); 
# ===== 2 ramps
pr["lon"]=pr.the_geom.str.extract(r"POINT \(([-\d.]+) ")[0].astype(float); pr["lat"]=pr.the_geom.str.extract(r" ([-\d.]+)\)")[0].astype(float)
print("ramp borough",pr.Borough.value_counts().to_dict(),"null geom",pr.lat.isna().sum())
nb,hb,ia,_=area(pr.lat.fillna(0),pr.lon.fillna(0)); pr["inarea"]=ia&(pr.Borough=="1").values&pr.lat.notna().values
pg["end"]=pd.to_datetime(pg.Construction_End_Date,errors="coerce")
r=pr[pr.inarea].merge(pg[["CornerID","end","Construction_Status_Value","Construction_Type"]],on="CornerID",how="left")
print("T2 ramps in area",len(r),"corners",r.CornerID.nunique(),"| ramp rows w/o Progress match",r.Construction_Status_Value.isna().sum())
print("   with end date",r.end.notna().sum(),"| end>=2020-02-01",(r.end>="2020-02-01").sum(),"| end>=2020-01-01",(r.end>="2020-01-01").sum(),"| end>2020-01-29(survey max)",(r.end>"2020-01-29").sum(),"| end<2020-02-01",(r.end<"2020-02-01").sum())
print("   status of in-area ramps",r.Construction_Status_Value.value_counts(dropna=False).to_dict())
print("   status among those with end date",r[r.end.notna()].Construction_Status_Value.value_counts().to_dict())
print("   end-date by year",r.end.dt.year.value_counts().sort_index().to_dict())
c=r.drop_duplicates("CornerID"); print("   corner level: corners",len(c),"with end",c.end.notna().sum(),">=2020-02",(c.end>="2020-02-01").sum())
# progress-side corners
pg["lon"]=pg.the_geom.str.extract(r"POINT \(([-\d.]+) ")[0].astype(float); pg["lat"]=pg.the_geom.str.extract(r" ([-\d.]+)\)")[0].astype(float)
_,_,ia2,_=area(pg.lat.fillna(0),pg.lon.fillna(0)); pg["inarea"]=ia2&(pg.Borough=="MANHATTAN").values&pg.lat.notna().values
p=pg[pg.inarea]; print("   Progress-side: corners in area",len(p),"with end",p.end.notna().sum(),">=2020-02",(p.end>="2020-02-01").sum(),"| status",p.Construction_Status_Value.value_counts().to_dict(), "| of which corner in ramp table",p.CornerID.isin(set(pr.CornerID)).sum())
pr[["RampID","lat","lon","inarea"]].to_pickle(S+"_ramps.pkl")
# ===== 3 MBPO
print("T3 MBPO rows",len(mb)); print("Compliant",mb.Compliant.value_counts(dropna=False).to_dict())
print("Station",mb.Station.value_counts(dropna=False).to_dict()); print("Center Cut",mb["Center Cut"].value_counts(dropna=False).to_dict(),"No Curb Cut",mb["No Curb Cut"].value_counts(dropna=False).to_dict())
rid="Ramp ID (No Id means a part of center cut)"; mb["RampID"]=mb[rid]
m=mb.merge(pr[["RampID","lat","lon","inarea"]],on="RampID",how="left")
print("   rows w/ RampID",mb.RampID.notna().sum(),"located",m.lat.notna().sum(),"in area",(m.inarea==True).sum())
j=m.Compliant.isin(["true","false"]); print("   judgeable",j.sum(),"compliant true",(m.Compliant=="true").sum(),"false",(m.Compliant=="false").sum())
print("   judgeable&located",(j&m.lat.notna()).sum(),"| in-area judgeable",(j&(m.inarea==True)).sum(),"in-area compliant",((m.Compliant=="true")&(m.inarea==True)).sum())
print("   duplicate RampID in MBPO",mb.RampID.dropna().duplicated().sum())
print(m.groupby("Station").agg(n=("Station","size"),loc=("lat",lambda s:s.notna().sum()),inarea=("inarea",lambda s:(s==True).sum()),comp=("Compliant",lambda s:(s=="true").sum()),judge=("Compliant",lambda s:s.isin(["true","false"]).sum())).to_string())
