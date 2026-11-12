import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import json, pickle, numpy as np, pandas as pd
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw
exec(open((S+"iso_core.py")).read().split("# ---------- GTFS")[0])
O=O
new=pickle.load(open(S+"iso2_res.pkl","rb")); old=pickle.load(open(S+"iso_res.pkl","rb"))["res"]
CELL=10.0
alld=[v["dist"] for v in new.values()]; fin=np.zeros(N,bool)
for d in alld: fin|=np.isfinite(d)
x0,x1=nx[fin].min()-400,nx[fin].max()+400; y0,y1=ny[fin].min()-400,ny[fin].max()+400
W=int(np.ceil((x1-x0)/CELL)); H=int(np.ceil((y1-y0)/CELL)); print("grid",W,"x",H)
gj=json.load(open(R+"borough_boundaries/boroughs.geojson")); img=Image.new("L",(W,H),0); dr=ImageDraw.Draw(img); boro=[]
for f in gj["features"]:
    g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        a=np.array(poly[0]); X,Y=xy(a[:,1],a[:,0]); boro.append(np.c_[X,Y]); dr.polygon(list(zip((X-x0)/CELL,(y1-Y)/CELL)),fill=1)
        for hole in poly[1:]:
            b=np.array(hole); Xh,Yh=xy(b[:,1],b[:,0]); dr.polygon(list(zip((Xh-x0)/CELL,(y1-Yh)/CELL)),fill=0)
LAND=np.array(img,bool)
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
names={(False,False):"1 subway, anyone",(False,True):"2 subway, ADA stations only",(True,False):"3 subway+bus, anyone",(True,True):"4 subway+bus, ADA subway only (all buses usable)"}
rows=[]; masks={}
for (T0h,ub,ada),v in sorted(new.items()):
    M,km=coverage(v["dist"])
    for buf in (100,50):
        A,ar=area(M,buf); rows.append(dict(departure=f"{T0h:02d}:00",scenario=names[(ub,ada)],buffer_m=buf,area_km2=round(ar,2),reachable_street_km=round(km,1),subway_stations_reached=len(v["parr"]),bus_stops_used=v["nbus"]))
        if buf==100: masks[(T0h,ub,ada)]=A
# walk only and previous-run (buggy) subway-only for transparency
_on,_od=snap(40.8409780,-73.9407016); dw=dijkstra(G[:N,:N],directed=True,indices=int(_on[0]),limit=TLIM+1)+float(_od[0])/WALK
for key,label,dist in [("walk","0 walking only",dw),((8,False),"prev-run 1 (superseded)",old[(8,False)]["dist"]),((8,True),"prev-run 2 (superseded)",old[(8,True)]["dist"])]:
    M,km=coverage(dist)
    for buf in (100,50):
        A,ar=area(M,buf); rows.append(dict(departure="-" if key=="walk" else "08:00",scenario=label,buffer_m=buf,area_km2=round(ar,2),reachable_street_km=round(km,1),subway_stations_reached=0,bus_stops_used=0))
        if buf==100 and key=="walk": masks["walk"]=A
T=pd.DataFrame(rows); T.to_csv(O+"nyp_isochrone_bus_summary.csv",index=False); pd.set_option("display.width",200); print(T.to_string(index=False))
pickle.dump(dict(masks=masks,x0=x0,x1=x1,y0=y0,y1=y1,H=H,W=W,boro=boro),open(S+"iso2_masks.pkl","wb"))
