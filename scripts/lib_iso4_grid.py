import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
# shared full-extent 10 m grid, land labels, tract raster, ACS allocation (exec'd by other scripts; needs iso_core globals: nx, ny, eu, ev, el, N, TLIM, WALK, xy, R)
import json, pickle, numpy as np, pandas as pd
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw
CELL=10.0
used_=np.zeros(N,bool); used_[eu]=True; used_[ev]=True
gx0,gx1=nx[used_].min()-300,nx[used_].max()+300; gy0,gy1=ny[used_].min()-300,ny[used_].max()+300
GW=int(np.ceil((gx1-gx0)/CELL)); GH=int(np.ceil((gy1-gy0)/CELL)); print("grid %d x %d = %.1fM cells"%(GW,GH,GW*GH/1e6))
BL={"Manhattan":1,"Bronx":2,"Brooklyn":3,"Queens":4,"Staten Island":5}
_gj=json.load(open(R+"borough_boundaries/boroughs.geojson")); _img=Image.new("L",(GW,GH),0); _dr=ImageDraw.Draw(_img); BORO_POLYS=[]
for _f in _gj["features"]:
    _l=BL[_f["properties"]["boroname"]]; _g=_f["geometry"]; _ps=_g["coordinates"] if _g["type"]=="MultiPolygon" else [_g["coordinates"]]
    for _p in _ps:
        _a=np.array(_p[0]); _X,_Y=xy(_a[:,1],_a[:,0]); BORO_POLYS.append((_l,np.c_[_X,_Y])); _dr.polygon(list(zip((_X-gx0)/CELL,(gy1-_Y)/CELL)),fill=_l)
        for _h in _p[1:]:
            _b=np.array(_h); _Xh,_Yh=xy(_b[:,1],_b[:,0]); _dr.polygon(list(zip((_Xh-gx0)/CELL,(gy1-_Yh)/CELL)),fill=0)
LAND=np.array(_img,np.uint8)
_tg=json.load(open(R+"census/nyc_tracts_2020.geojson")); GEOIDS=[f["properties"]["geoid"] for f in _tg["features"]]; nT=len(GEOIDS)
_timg=Image.new("I",(GW,GH),0); _td=ImageDraw.Draw(_timg)
for _i,_f in enumerate(_tg["features"],start=1):
    _g=_f["geometry"]; _ps=_g["coordinates"] if _g["type"]=="MultiPolygon" else [_g["coordinates"]]
    for _p in _ps:
        _a=np.array(_p[0]); _X,_Y=xy(_a[:,1],_a[:,0]); _td.polygon(list(zip((_X-gx0)/CELL,(gy1-_Y)/CELL)),fill=_i)
        for _h in _p[1:]:
            _b=np.array(_h); _Xh,_Yh=xy(_b[:,1],_b[:,0]); _td.polygon(list(zip((_Xh-gx0)/CELL,(gy1-_Yh)/CELL)),fill=0)
TRID=np.array(_timg,np.int32); TOT=np.bincount(TRID.ravel(),minlength=nT+1)
_acs=pd.read_csv(R+"census/acsdt5y2024-b18105.dat",sep="|",dtype=str); _acs["geoid"]=_acs.GEO_ID.str[-11:]; _acs=_acs[_acs.geoid.isin(set(GEOIDS))].set_index("geoid")
_ce=[f"B18105_E{n:03d}" for n in (4,7,10,13,16,20,23,26,29,32)]; _cm=[c.replace("_E","_M") for c in _ce]
AMB=np.zeros(nT+1); UNIV=np.zeros(nT+1); MOE=np.zeros(nT+1); CTY=np.zeros(nT+1,int)
for _i,_gid in enumerate(GEOIDS,start=1):
    _r=_acs.loc[_gid]; AMB[_i]=sum(float(_r[c]) for c in _ce); UNIV[_i]=float(_r["B18105_E001"]); MOE[_i]=np.sqrt(sum(float(_r[c])**2 for c in _cm)); CTY[_i]=int(_gid[2:5])
_vec=np.array([0]+[float(f["properties"]["shape_area"])*0.09290304 for f in _tg["features"]]); _ratio=np.where(_vec>0,TOT*CELL**2/np.maximum(_vec,1),0)
DEN=np.where(_ratio>=0.97,TOT,_vec/CELL**2).astype(float)       # raster cells if the tract lies fully in the grid, else vector area
print("tracts fully in grid:",int((_ratio[1:]>=0.97).sum()),"of",nT)
DENS=np.where(DEN>0,AMB/np.maximum(DEN,1),0.0); DENS[0]=0.0       # residents (ambulatory difficulty) per 10 m cell
def coverage_mask(dist):
    tu=dist[eu]; tv=dist[ev]; m=(np.isfinite(tu)&(tu<TLIM))|(np.isfinite(tv)&(tv<TLIM)); idx=np.flatnonzero(m)
    L=el[idx]; ru=np.where(np.isfinite(tu[idx]),np.maximum(0,TLIM-tu[idx])*WALK,0); rv=np.where(np.isfinite(tv[idx]),np.maximum(0,TLIM-tv[idx])*WALK,0)
    km=np.minimum(L,ru+rv).sum()/1000
    nS=np.ceil(L/5).astype(int)+1; rep=np.repeat(np.arange(len(idx)),nS); off=np.cumsum(nS)-nS; k=np.arange(nS.sum())-np.repeat(off,nS)
    s=k*(L[rep]/(nS[rep]-1)); keep=(s<=ru[rep])|(L[rep]-s<=rv[rep]); rep=rep[keep]; s=s[keep]
    e=idx[rep]; fx=nx[eu[e]]+(nx[ev[e]]-nx[eu[e]])*s/el[e]; fy=ny[eu[e]]+(ny[ev[e]]-ny[eu[e]])*s/el[e]
    ci=((fx-gx0)/CELL).astype(int); ri=((gy1-fy)/CELL).astype(int); ok=(ci>=0)&(ci<GW)&(ri>=0)&(ri<GH); ci=ci[ok]; ri=ri[ok]
    r0,r1,c0,c1=max(ri.min()-12,0),min(ri.max()+13,GH),max(ci.min()-12,0),min(ci.max()+13,GW)
    M=np.zeros((r1-r0,c1-c0),bool); M[ri-r0,ci-c0]=True
    d=distance_transform_edt(~M)*CELL; A=(d<=100)&(LAND[r0:r1,c0:c1]>0)
    return A,(r0,r1,c0,c1),km
def stats(A,crop):
    r0,r1,c0,c1=crop; land=LAND[r0:r1,c0:c1]; trc=TRID[r0:r1,c0:c1]
    cnt=np.bincount(trc[A],minlength=nT+1); frac=np.where(DEN>0,cnt/np.maximum(DEN,1),0); frac[0]=0
    return dict(area=A.sum()*CELL**2/1e6,area_man=(A&(land==1)).sum()*CELL**2/1e6,area_bx=(A&(land==2)).sum()*CELL**2/1e6,
        amb=(frac*AMB).sum(),amb_man=(frac*AMB)[CTY==61].sum(),amb_bx=(frac*AMB)[CTY==5].sum(),univ=(frac*UNIV).sum(),moe=np.sqrt(((frac*MOE)**2).sum()))
