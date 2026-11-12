import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import json, glob, re, numpy as np, pickle, collections
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
S=S
LAT0,LON0=40.80,-73.95; KX=111320*np.cos(np.radians(LAT0)); KY=110574
def xy(lat,lon): return (np.asarray(lon)-LON0)*KX,(np.asarray(lat)-LAT0)*KY
rows=[]
for f in sorted(glob.glob((R+"nyc_centerline/cscl_*.json"))): rows+=json.load(open(f))
ALLOW={"1","5","6","7","10","3"}; HWY=re.compile(r"PKWY|EXPY|HWY|\bDR\b|TUNL|THRUWAY|TPKE|FWY|PKY|BYP|\bI \d")
keep=collections.Counter(); drop=collections.Counter()
nodes={}; eu=[];ev=[];el=[];et=[]
B=(40.60,40.93,-74.06,-73.78)
def nid(lon,lat):
    k=(round(lon,6),round(lat,6)); 
    if k not in nodes: nodes[k]=len(nodes)
    return nodes[k]
for r in rows:
    t=r["rw_type"]; 
    if r.get("status")!="2" or t not in ALLOW: drop["type/status "+t]+=1; continue
    if t=="3" and HWY.search(r.get("full_street_name","") or ""): drop["highway-named bridge"]+=1; continue
    for part in r["the_geom"]["coordinates"]:
        a=np.array(part); 
        if not ((B[2]<=a[:,0]).all() and (a[:,0]<=B[3]).all() and (B[0]<=a[:,1]).all() and (a[:,1]<=B[1]).all()): drop["outside bbox"]+=1; continue
        x,y=xy(a[:,1],a[:,0]); L=np.hypot(np.diff(x),np.diff(y)).sum()
        if L<0.5: continue
        eu.append(nid(*a[0])); ev.append(nid(*a[-1])); el.append(L); et.append(t); keep[t]+=1
eu=np.array(eu);ev=np.array(ev);el=np.array(el)
keys=np.array(list(nodes.keys())); nlon,nlat=keys[:,0],keys[:,1]; nx,ny=xy(nlat,nlon)
n=len(nodes); A=coo_matrix((np.ones(len(eu)),(eu,ev)),shape=(n,n)); nc,lab=connected_components(A,directed=False)
big=np.bincount(lab).argmax(); inl=lab==big
print("edges kept",len(eu),dict(keep),"| dropped",dict(drop)); print("nodes",n,"components",nc,"largest comp nodes",inl.sum(),"= %.1f%%"%(100*inl.mean()))
m=inl[eu]&inl[ev]; print("edges in LCC",m.sum(),"total length km %.0f"%(el[m].sum()/1000))
pickle.dump(dict(nx=nx,ny=ny,nlat=nlat,nlon=nlon,eu=eu[m],ev=ev[m],el=el[m],et=np.array(et)[m],inl=inl),open(S+"graph.pkl","wb"))
