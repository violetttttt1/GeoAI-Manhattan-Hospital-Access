import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import numpy as np, pandas as pd
R=R
HOSP={"Harlem Hospital":(40.8147102,-73.9392782),"NYP/Columbia Irving Medical Center":(40.8409780,-73.9407016),"Mount Sinai Morningside":(40.8052373,-73.9613875)}
def hav(lat,lon,la0,lo0):
    lat=np.radians(np.asarray(lat,float));lon=np.radians(np.asarray(lon,float));la0=np.radians(la0);lo0=np.radians(lo0)
    a=np.sin((lat-la0)/2)**2+np.cos(lat)*np.cos(la0)*np.sin((lon-lo0)/2)**2; return 12742000*np.arcsin(np.sqrt(a))
st=pd.read_csv(R+"mta_stations/mta_stations.csv",dtype=str); st["lat"]=st["GTFS Latitude"].astype(float); st["lon"]=st["GTFS Longitude"].astype(float)
en=pd.read_csv(R+"mta_entrances/entrances.csv",dtype=str); en["la"]=en["Entrance Latitude"].astype(float); en["lo"]=en["Entrance Longitude"].astype(float)
ada=st[st.ADA.isin(["1","2"])].copy(); print("ADA stations citywide",len(ada),"ADA=1",(ada.ADA=="1").sum(),"ADA=2",(ada.ADA=="2").sum())
rows=[]
for h,(la,lo) in HOSP.items():
    d=hav(ada.lat,ada.lon,la,lo); a=ada.assign(dist_m=d).sort_values("dist_m")
    # nearest entrance of each station (entrance dataset keyed by Station ID)
    def ne(sid):
        e=en[en["Station ID"]==sid]; return np.nan if e.empty else hav(e.la,e.lo,la,lo).min()
    a["nearest_entrance_m"]=a["Station ID"].map(ne)
    within=a[a.dist_m<=400]; print(f"\n== {h}: ADA stations within 400 m (station point): {len(within)}")
    print(within[["Station ID","Stop Name","Line","Daytime Routes","ADA","dist_m","nearest_entrance_m"]].round(0).to_string(index=False))
    print("-- nearest 3 ADA stations:"); print(a.head(3)[["Station ID","Stop Name","Daytime Routes","ADA","Borough","dist_m","nearest_entrance_m"]].round(0).to_string(index=False))
    n=a.iloc[0]; rows.append(dict(hospital=h,n_ada_within_400m=len(within),ada_within_400m="; ".join(f"{r['Stop Name']} ({r['Daytime Routes']}) {r.dist_m:.0f} m" for _,r in within.iterrows()),nearest_ada=f"{n['Stop Name']} ({n['Daytime Routes']})",nearest_ada_id=n["Station ID"],nearest_ada_m=round(n.dist_m),nearest_ada_entrance_m=None if np.isnan(n.nearest_entrance_m) else round(n.nearest_entrance_m)))
    # also all stations (any ADA) within 400 
    d2=hav(st.lat,st.lon,la,lo); print("   all stations within 400 m:",st[d2<=400][["Stop Name","Daytime Routes","ADA"]].values.tolist())
pd.DataFrame(rows).to_csv((O+"hospital_ada_stations.csv"),index=False,encoding="utf-8-sig")
