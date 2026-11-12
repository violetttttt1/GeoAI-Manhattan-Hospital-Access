import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
# generalised elevator model (needs clip_core globals). Builds station -> {direction: [minimal elevator sets]} for ADA stations from the inventory.
import itertools, collections
O=O
INV=pd.read_csv(R+"elevator_inventory/elevator_inventory.csv",dtype=str); INV["sid"]=INV["Station MRN"].str.lstrip("0")
STAB=pd.read_csv(R+"mta_stations/mta_stations.csv",dtype=str)
AVT=pd.read_csv(R+"elevator_availability/elevator_availability.csv",dtype=str); AVT["m"]=pd.to_datetime(AVT.Month)
_last=AVT.m.max(); _start=_last-pd.DateOffset(months=11); _w=AVT[(AVT["Equipment Type"]=="Elevator")&(AVT.m>=_start)].copy()
for c in ["24-Hour Hours Available","24-Hour Total Hours"]: _w[c]=pd.to_numeric(_w[c])
_g=_w.groupby("Equipment Code")[["24-Hour Hours Available","24-Hour Total Hours"]].sum()
AVAIL12={e:(r["24-Hour Hours Available"]/r["24-Hour Total Hours"] if r["24-Hour Total Hours"]>0 else None) for e,r in _g.iterrows()}   # same formula as elevator_detail.csv
_st1=pd.read_csv(O+"station_table.csv",dtype=str); FILL_MEAN=float(_st1.fill_mean_used.iloc[0]); FILL_LOW=float(_st1.fill_low_used.iloc[0])
def _landings(r):
    n=set()
    if r["Street Access"]=="YES": n.add("Street")
    if r["Elevator Mezzanine 1 Access"]=="+": n.add("M1")
    if r["Elevator Mezzanine 2 Access"]=="+": n.add("M2")
    if r["Elevator Platform Access"]=="+": n|={"Both":{"PN","PS"},"Northbound":{"PN"},"Southbound":{"PS"}}.get(r["Elevator Direction Serviced"],set())
    return n
def _connected(edges,sel,a,targets):
    par={}
    def f(x):
        par.setdefault(x,x)
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for i in sel:
        nl=list(edges[i][1])
        for x in nl[1:]: par[f(x)]=f(nl[0])
    return all(f(a)==f(b) for b in targets)
def build_station(sid,ada_n,ada_s):
    L=INV[(INV["Elevator or Escalator"]=="Elevator")&(INV.sid==sid)]
    edges=[];unplaced=[]
    for _,e in L.iterrows():
        nl=_landings(e)
        if len(nl)>=2 and not str(e["Service Status"]).startswith("Removed"): edges.append((e["Equipment Code"],frozenset(nl)))
        else: unplaced.append(e["Equipment Code"])
    edges.sort(key=lambda x:x[0]); dirs=[d for d,fl in (("PN",ada_n),("PS",ada_s)) if fl=="1"]
    if not len(L): return dict(status="no_elevators",paths={},elevators=[],unplaced=[],entrance=None,inferred=False,n_inv=0)
    if not edges: return dict(status="unmodelable",paths={},elevators=[],unplaced=unplaced,entrance=None,inferred=False,n_inv=len(L),why="no elevator with >=2 landing fields")
    allnodes=set().union(*[n for _,n in edges]); inferred=False
    if "Street" in allnodes: entr="Street"
    else: entr="M2" if "M2" in allnodes else "M1"; inferred=True
    paths={}
    for d in dirs:
        found=[]
        for r_ in range(1,len(edges)+1):
            for comb in itertools.combinations(range(len(edges)),r_):
                if any(set(f_)<=set(comb) for f_ in found): continue
                if _connected(edges,comb,entr,[d]): found.append(comb)
        if not found: return dict(status="unmodelable",paths={},elevators=[e for e,_ in edges],unplaced=unplaced,entrance=entr,inferred=inferred,n_inv=len(L),why=f"no elevator path from {entr} to {d}")
        paths[d]=[set(edges[i][0] for i in c) for c in found]
    return dict(status="modeled",paths=paths,elevators=[e for e,_ in edges],unplaced=unplaced,entrance=entr,inferred=inferred,n_inv=len(L))
ADAROWS=STAB[STAB.ADA.isin(["1","2"])].set_index("GTFS Stop ID")
def build_all(parents_wanted):
    out={}
    for P in sorted(parents_wanted):
        r=ADAROWS.loc[P]; m=build_station(r["Station ID"],r["ADA Northbound"],r["ADA Southbound"]); m.update(name=f'{r["Stop Name"]} ({r["Daytime Routes"]})',borough=r["Borough"],ada=r["ADA"],sid=r["Station ID"]); out[P]=m
    return out
def make_ok(STN):
    def station_ok(upset):
        out={}
        for P,s in STN.items():
            if s["status"]!="modeled": out[P]={"PN":True,"PS":True}; continue
            out[P]={d:any(all(e in upset for e in path) for path in pl) for d,pl in s["paths"].items()}
        return out
    return station_ok
def blocked_children_g(ok,STN):
    b=set()
    for P,d in ok.items():
        for c in children.get(P,[]):
            if (c.endswith("N") and not d.get("PN",True)) or (c.endswith("S") and not d.get("PS",True)): b.add(sidx[c])
    return b
BASE_ALLOW_ADA=ALLOW[True].copy()
def run_cfg(st,BUS,T0,rev,blocked):
    al=BASE_ALLOW_ADA.copy()
    for i in blocked: al[i]=False
    ALLOW[True]=al
    try: best=raptor_g(T0,True,BUS,True,st,rev=rev)
    finally: ALLOW[True]=BASE_ALLOW_ADA
    dist,parr,nb=street_g(best,T0,BUS,True,st); return best,dist
