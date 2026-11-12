import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pickle, heapq, numpy as np, pandas as pd, collections
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
S=S
R=R
LAT0,LON0=40.80,-73.95; KX=111320*np.cos(np.radians(LAT0)); KY=110574
def xy(lat,lon): return (np.asarray(lon,float)-LON0)*KX,(np.asarray(lat,float)-LAT0)*KY
WALK=1.33; TLIM=1800.0
# ---------- street graph
g=pickle.load(open(S+"graph.pkl","rb")); nx,ny,eu,ev,el=g["nx"],g["ny"],g["eu"],g["ev"],g["el"]; N=len(nx)
used=np.zeros(N,bool); used[eu]=True; used[ev]=True
tree=cKDTree(np.c_[nx[used],ny[used]]); idmap=np.flatnonzero(used)
def snap(lat,lon):
    x,y=xy(lat,lon); d,i=tree.query(np.c_[x,y]); return idmap[i],d
w=el/WALK
G=csr_matrix((np.r_[w,w],(np.r_[eu,ev],np.r_[ev,eu])),shape=(N+1,N+1))   # last node = super source
# ---------- GTFS
GT=R+"gtfs/unz/"
stops=pd.read_csv(GT+"stops.txt",dtype=str); stops["lat"]=stops.stop_lat.astype(float); stops["lon"]=stops.stop_lon.astype(float)
parents=stops[stops.location_type=="1"].set_index("stop_id"); kids=stops[stops.location_type!="1"].copy(); kids["parent"]=kids.parent_station
sidx={s:i for i,s in enumerate(kids.stop_id)}; par_of=kids.set_index("stop_id").parent.to_dict()
children=kids.groupby("parent").stop_id.apply(list).to_dict()
trips=pd.read_csv(GT+"trips.txt",dtype=str); wk=trips[trips.service_id=="Weekday"]
stt=pd.read_csv(GT+"stop_times.txt",dtype=str,usecols=["trip_id","stop_id","departure_time","stop_sequence"]); stt=stt[stt.trip_id.isin(set(wk.trip_id))].copy()
def sec(t): h,m,s=t.split(":"); return int(h)*3600+int(m)*60+int(s)
stt["dep"]=stt.departure_time.map(sec); stt["seq"]=stt.stop_sequence.astype(int); stt=stt.sort_values(["trip_id","seq"])
route_of=dict(zip(wk.trip_id,wk.route_id))
pat=collections.defaultdict(list)
for tid,grp in stt.groupby("trip_id",sort=False): pat[(route_of[tid],tuple(grp.stop_id))].append(grp.dep.values)
PATS=[]
for (rt,sl),tl in pat.items():
    M=np.array(sorted(tl,key=lambda a:a[0])); PATS.append((rt,[sidx[s] for s in sl],M))
stops_pats=collections.defaultdict(list)
for pi,(rt,sl,M) in enumerate(PATS):
    for pos,s in enumerate(sl): stops_pats[s].append((pi,pos))
tr=pd.read_csv(GT+"transfers.txt",dtype=str); TR=collections.defaultdict(list)
for a,b,m in zip(tr.from_stop_id,tr.to_stop_id,tr.min_transfer_time.astype(float)): TR[a].append((b,m))
# ADA permissions per child stop
st=pd.read_csv(R+"mta_stations/mta_stations.csv",dtype=str); ADA={}
for _,r in st.iterrows():
    if r.ADA=="1": ADA[r["GTFS Stop ID"]]=("1","1")
    elif r.ADA=="2": ADA[r["GTFS Stop ID"]]=(r["ADA Northbound"],r["ADA Southbound"])
def allowed(stop,ada_only):
    if not ada_only: return True
    p=par_of[stop]
    if p not in ADA: return False
    n,s=ADA[p]; return (n=="1" if stop.endswith("N") else s=="1" if stop.endswith("S") else True)
ALLOW={m:np.array([allowed(s,m) for s in kids.stop_id]) for m in (False,True)}
print("patterns",len(PATS),"| child stops",len(kids),"| allowed ADA-only",ALLOW[True].sum(),"of",len(kids))
def raptor(walk_to_parent,T0,ada_only,K=7):
    al=ALLOW[ada_only]; INF=1e9; best=np.full(len(kids),INF); tau=np.full(len(kids),INF); marked=set()
    par_arr={}
    def relax_children(P,t,marked_new):
        for c in children.get(P,[]):
            i=sidx[c]
            if al[i] and t<best[i]: best[i]=t; tau[i]=t; marked_new.add(i)
    for P,wt in walk_to_parent.items():
        if P in children: relax_children(P,T0+wt,marked)
    sid_list=list(kids.stop_id)
    for k in range(K):
        new=set(); Qp={}
        for s in marked:
            for pi,pos in stops_pats.get(s,[]):
                if pi not in Qp or pos<Qp[pi]: Qp[pi]=pos
        prev=tau.copy()
        for pi,pos0 in Qp.items():
            rt,sl,M=PATS[pi]; cur=None
            for pos in range(pos0,len(sl)):
                s=sl[pos]
                if cur is not None:
                    a=M[cur,pos]
                    if al[s] and a<best[s] and a<=T0+TLIM: best[s]=a; tau[s]=a; new.add(s)
                if al[s] and prev[s]<INF:
                    j=int(np.searchsorted(M[:,pos],prev[s],side="left"))
                    if j<M.shape[0] and (cur is None or j<cur): cur=j
        # transfers from newly improved children
        tn=set(new); parr={}
        for s in new:
            P=par_of[sid_list[s]]; parr[P]=min(parr.get(P,INF),tau[s])
        for P,t in parr.items():
            for (P2,mt) in TR.get(P,[]):
                if P2 not in children: continue
                relax_children(P2,t+mt,tn)
        marked=tn
        if not marked: break
    return best
def street_times(sources):   # sources: list of (node, init_seconds)
    r=[];c=[];v=[]
    for n,t in sources: r.append(N); c.append(n); v.append(max(t,1e-3))
    G2=G.copy().tolil(); 
    for a,b,x in zip(r,c,v): G2[a,b]=x
    d=dijkstra(G2.tocsr(),directed=True,indices=N,limit=TLIM+1)
    return d[:N]
