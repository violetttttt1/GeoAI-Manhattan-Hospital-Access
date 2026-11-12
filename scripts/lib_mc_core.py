import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso3_core.py")).read())
exec(open((S+"iso4_grid.py")).read())
import re, collections
O=O
# ---------- electricity of the elevator model: parse station_table access paths + elevator_detail availability
ST=pd.read_csv(O+"station_table.csv",dtype=str); ED=pd.read_csv(O+"elevator_detail.csv")
AVAIL={r["Equipment Code"]:(float(r.avail_24h_12m) if r.avail_status=="known" else None) for _,r in ED[ED.in_probability_model].iterrows()}
FILL_MEAN=float(ST.fill_mean_used.iloc[0]); FILL_LOW=float(ST.fill_low_used.iloc[0])
STATIONS={}      # gtfs parent -> {name, paths:{'PN':[set..],'PS':[..]}}
for _,r in ST.iterrows():
    paths={}
    if isinstance(r.access_paths,str) and r.access_paths.strip():
        for part in r.access_paths.split(";"):
            d,rest=part.strip().split(":"); paths[d.strip()]=[set(p.strip().split("+")) for p in rest.split("|")]
    STATIONS[r.gtfs_stop_id]=dict(name=r.station_name+" ("+r.routes+")",paths=paths)
ELEVS=sorted(AVAIL); EIDX={e:i for i,e in enumerate(ELEVS)}
used_e={e for s in STATIONS.values() for pl in s["paths"].values() for p in pl for e in p}; assert used_e<=set(ELEVS),used_e-set(ELEVS)
print("stations",len(STATIONS),"| elevators in model",len(ELEVS),"| unknown availability:",[e for e in ELEVS if AVAIL[e] is None])
def p_up(variant):
    return np.array([AVAIL[e] if AVAIL[e] is not None else (FILL_MEAN if variant=="mean" else FILL_LOW) for e in ELEVS])
def station_ok(up):          # up: bool vector over ELEVS -> {parent:{'PN':bool,'PS':bool}}
    out={}
    for P,s in STATIONS.items():
        if not s["paths"]: out[P]={"PN":True,"PS":True}; continue   # Harlem-148 St: no elevator dependency
        out[P]={d:any(all(up[EIDX[e]] for e in path) for path in pl) for d,pl in s["paths"].items()}
    return out
def blocked_children(ok):
    b=set()
    for P,d in ok.items():
        for c in children.get(P,[]):
            if (c.endswith("N") and not d["PN"]) or (c.endswith("S") and not d["PS"]): b.add(sidx[c])
    return b
BASE_ALLOW_ADA=ALLOW[True].copy()
def run_cfg(st,BUS,T0,rev,blocked):
    al=BASE_ALLOW_ADA.copy()
    for i in blocked: al[i]=False
    ALLOW[True]=al
    try: best=raptor_g(T0,True,BUS,True,st,rev=rev)
    finally: ALLOW[True]=BASE_ALLOW_ADA
    dist,parr,nb=street_g(best,T0,BUS,True,st); return best,dist
