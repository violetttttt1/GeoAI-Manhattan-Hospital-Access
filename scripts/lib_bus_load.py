import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pandas as pd, numpy as np, pickle, os, collections, datetime as dt
S=S
BG=(R+"gtfs_bus/")
DATE=dt.date(2026,11,18); TLIM=1800
def active_services(d):
    cal=pd.read_csv(d+"calendar.txt",dtype=str); ymd=DATE.strftime("%Y%m%d"); col=DATE.strftime("%A").lower()
    ok=cal[(cal.start_date<=ymd)&(cal.end_date>=ymd)&(cal[col]=="1")].service_id; act=set(ok)
    if os.path.exists(d+"calendar_dates.txt"):
        cd=pd.read_csv(d+"calendar_dates.txt",dtype=str); x=cd[cd.date==ymd]
        act|=set(x[x.exception_type=="1"].service_id); act-=set(x[x.exception_type=="2"].service_id)
    return act
def load(feed,T0):
    d=BG+feed+"/"; act=active_services(d)
    tr=pd.read_csv(d+"trips.txt",dtype=str,usecols=["route_id","trip_id","service_id"]); tr=tr[tr.service_id.isin(act)]
    st=pd.read_csv(d+"stop_times.txt",dtype=str,usecols=["trip_id","stop_id","departure_time","stop_sequence","pickup_type","drop_off_type"]); st=st[st.trip_id.isin(set(tr.trip_id))].copy()
    p=st.departure_time.str.split(":",expand=True).astype(int); st["dep"]=p[0]*3600+p[1]*60+p[2]; st["seq"]=st.stop_sequence.astype(int); st["pk"]=(st.pickup_type.fillna("0")!="1"); st["dr"]=(st.drop_off_type.fillna("0")!="1")
    st=st.sort_values(["trip_id","seq"]); g=st.groupby("trip_id").dep; first=g.first(); last=g.last()
    keep=first.index[(first<=T0+TLIM)&(last>=T0)]; st=st[st.trip_id.isin(set(keep))]
    rmap=dict(zip(tr.trip_id,tr.route_id)); pat=collections.defaultdict(list)
    for tid,grp in st.groupby("trip_id",sort=False): pat[(feed+":"+rmap[tid],tuple(feed+":"+s for s in grp.stop_id),tuple(grp.pk),tuple(grp.dr))].append(grp.dep.values)
    stops=pd.read_csv(d+"stops.txt",dtype=str,low_memory=False); stops["id"]=feed+":"+stops.stop_id
    print(f"{feed}: active services {len(act)} | trips total {tr.trip_id.nunique()} | trips in window {len(keep)} | patterns {len(pat)} | routes {len({k[0] for k in pat})}")
    return dict(pat=dict(pat),stops=stops[["id","stop_lat","stop_lon","stop_name"]])
if __name__=="__main__":
    for T0 in (8*3600,12*3600):
        out={f:load(f,T0) for f in ["gtfs_m","gtfs_bx","gtfs_busco"]}
        pickle.dump(out,open(S+f"bus_{T0//3600}.pkl","wb"))
