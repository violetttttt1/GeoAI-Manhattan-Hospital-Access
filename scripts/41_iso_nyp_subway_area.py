import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import json, pickle, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw
exec(open((S+"iso_core.py")).read().split("# ---------- GTFS")[0])
O=O
P=pickle.load(open(S+"iso_res.pkl","rb")); res=P["res"]; ORIG=P["orig"]
CELL=10.0
# grid extent from ordinary 12:00 (largest) reach
dmax=res[(12,False)]["dist"]; ok=np.isfinite(dmax); x0,x1=nx[ok].min()-400,nx[ok].max()+400; y0,y1=ny[ok].min()-400,ny[ok].max()+400
W=int(np.ceil((x1-x0)/CELL)); H=int(np.ceil((y1-y0)/CELL)); print("grid",W,"x",H)
gj=json.load(open(R+"borough_boundaries/boroughs.geojson")); img=Image.new("L",(W,H),0); dr=ImageDraw.Draw(img); boro=[]
for f in gj["features"]:
    g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        a=np.array(poly[0]); X,Y=xy(a[:,1],a[:,0]); boro.append(np.c_[X,Y])
        dr.polygon(list(zip((X-x0)/CELL,(y1-Y)/CELL)),fill=1)
        for hole in poly[1:]:
            b=np.array(hole); Xh,Yh=xy(b[:,1],b[:,0]); dr.polygon(list(zip((Xh-x0)/CELL,(y1-Yh)/CELL)),fill=0)
LAND=np.array(img,bool); print("land cells km2 in grid %.0f"%(LAND.sum()*CELL**2/1e6))
def coverage(dist):
    tu=dist[eu]; tv=dist[ev]; m=(np.isfinite(tu)&(tu<TLIM))|(np.isfinite(tv)&(tv<TLIM)); idx=np.flatnonzero(m)
    L=el[idx]; ru=np.where(np.isfinite(tu[idx]),np.maximum(0,TLIM-tu[idx])*WALK,0); rv=np.where(np.isfinite(tv[idx]),np.maximum(0,TLIM-tv[idx])*WALK,0)
    km=np.minimum(L,ru+rv).sum()/1000
    nS=np.ceil(L/5).astype(int)+1; rep=np.repeat(np.arange(len(idx)),nS); off=np.cumsum(nS)-nS; k=np.arange(nS.sum())-np.repeat(off,nS)
    s=k*(L[rep]/(nS[rep]-1)); keep=(s<=ru[rep])|(L[rep]-s<=rv[rep]); rep=rep[keep]; s=s[keep]
    e=idx[rep]; fx=nx[eu[e]]+(nx[ev[e]]-nx[eu[e]])*s/el[e]; fy=ny[eu[e]]+(ny[ev[e]]-ny[eu[e]])*s/el[e]
    M=np.zeros((H,W),bool); ci=((fx-x0)/CELL).astype(int); ri=((y1-fy)/CELL).astype(int); okk=(ci>=0)&(ci<W)&(ri>=0)&(ri<H); M[ri[okk],ci[okk]]=True
    return M,km
def area(M,buf):
    d=distance_transform_edt(~M)*CELL; A=(d<=buf)&LAND; return A,A.sum()*CELL**2/1e6
_st=pd.read_csv(R+"mta_stations/mta_stations.csv",dtype=str); cx=dict(zip(_st["GTFS Stop ID"],_st["Complex ID"]))
rows=[]; masks={}
for key,label in [((8,False),"ordinary"),((8,True),"ADA-only"),((12,False),"ordinary"),((12,True),"ADA-only"),("walk","walk only")]:
    dep="08:00" if key!="walk" and key[0]==8 else ("12:00" if key!="walk" else "-")
    M,km=coverage(res[key]["dist"]); 
    for buf in (100,50):
        A,ar=area(M,buf); rows.append(dict(departure=dep,group=label,buffer_m=buf,area_km2=round(ar,2),reachable_street_km=round(km,1),stations_reached=(len([v for v in res[key]["parr"].values() if v<=TLIM]) if key!="walk" else 0),complexes_reached=(len({cx.get(k,k) for k,v in res[key]["parr"].items() if v<=TLIM}) if key!="walk" else 0)))
        if buf==100: masks[key]=A
T=pd.DataFrame(rows); print(T.to_string(index=False)); T.to_csv(O+"nyp_isochrone_summary.csv",index=False)
pickle.dump(dict(masks=masks,x0=x0,x1=x1,y0=y0,y1=y1,H=H,W=W,boro=boro),open(S+"iso_masks.pkl","wb"))
