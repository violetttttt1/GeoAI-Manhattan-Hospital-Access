import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import json, pickle, numpy as np, pandas as pd
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw
exec(open((S+"iso_core.py")).read().split("# ---------- GTFS")[0])
O=O; CELL=10.0
R3=pickle.load(open(S+"iso3_res.pkl","rb")); res=R3["res"]
fin=np.zeros(N,bool)
for v in res.values(): fin|=np.isfinite(v["dist"])
x0,x1=nx[fin].min()-400,nx[fin].max()+400; y0,y1=ny[fin].min()-400,ny[fin].max()+400
W=int(np.ceil((x1-x0)/CELL)); H=int(np.ceil((y1-y0)/CELL)); print("grid",W,"x",H,"=%.1fM cells"%(W*H/1e6))
# ---- borough land labels
BL={"Manhattan":1,"Bronx":2,"Brooklyn":3,"Queens":4,"Staten Island":5}
gj=json.load(open(R+"borough_boundaries/boroughs.geojson")); img=Image.new("L",(W,H),0); dr=ImageDraw.Draw(img); boro_polys=[]
for f in gj["features"]:
    lab=BL[f["properties"]["boroname"]]; g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        a=np.array(poly[0]); X,Y=xy(a[:,1],a[:,0]); boro_polys.append((lab,np.c_[X,Y])); dr.polygon(list(zip((X-x0)/CELL,(y1-Y)/CELL)),fill=lab)
        for hole in poly[1:]:
            b=np.array(hole); Xh,Yh=xy(b[:,1],b[:,0]); dr.polygon(list(zip((Xh-x0)/CELL,(y1-Yh)/CELL)),fill=0)
LAND=np.array(img,np.uint8)
# ---- tract raster + ACS
tg=json.load(open(R+"census/nyc_tracts_2020.geojson")); geoids=[f["properties"]["geoid"] for f in tg["features"]]
timg=Image.new("I",(W,H),0); td=ImageDraw.Draw(timg)
for i,f in enumerate(tg["features"],start=1):
    g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        a=np.array(poly[0]); X,Y=xy(a[:,1],a[:,0]); td.polygon(list(zip((X-x0)/CELL,(y1-Y)/CELL)),fill=i)
        for hole in poly[1:]:
            b=np.array(hole); Xh,Yh=xy(b[:,1],b[:,0]); td.polygon(list(zip((Xh-x0)/CELL,(y1-Yh)/CELL)),fill=0)
TR_=np.array(timg,np.int32); nT=len(geoids); tot=np.bincount(TR_.ravel(),minlength=nT+1)
acs=pd.read_csv(R+"census/acsdt5y2024-b18105.dat",sep="|",dtype=str); acs["geoid"]=acs.GEO_ID.str[-11:]; acs=acs[acs.geoid.isin(set(geoids))].set_index("geoid")
ce=[f"B18105_E{n:03d}" for n in (4,7,10,13,16,20,23,26,29,32)]; cm=[c.replace("_E","_M") for c in ce]
amb=np.zeros(nT+1); univ=np.zeros(nT+1); moe=np.zeros(nT+1); cty=np.zeros(nT+1,int)
for i,gid in enumerate(geoids,start=1):
    r=acs.loc[gid]; amb[i]=sum(float(r[c]) for c in ce); univ[i]=float(r["B18105_E001"]); moe[i]=np.sqrt(sum(float(r[c])**2 for c in cm)); cty[i]=int(gid[2:5])
vec_area=np.array([0]+[float(f["properties"]["shape_area"])*0.09290304 for f in tg["features"]])   # ft2 -> m2
ratio=np.where(vec_area>0,tot*CELL**2/np.maximum(vec_area,1),0)
print("tracts fully inside grid (raster/vector area >=0.97):",(ratio[1:]>=0.97).sum(),"of",nT,"| partially or fully outside grid:",(ratio[1:]<0.97).sum())
pickle.dump(dict(ratio=ratio),open(S+"tract_ratio.pkl","wb"))
DEN=np.where(ratio>=0.97,tot,vec_area/CELL**2).astype(float)   # raster count if tract fully inside grid, else vector area
print("ratio (raster/vector) among tracts inside grid: median %.3f, 5th pct %.3f, 95th pct %.3f"%tuple(np.percentile(ratio[1:][ratio[1:]>=0.97],[50,5,95])))
CNTY={5:"Bronx",47:"Brooklyn",61:"Manhattan",81:"Queens",85:"Staten Island"}
# ---- coverage
def coverage(dist):
    tu=dist[eu]; tv=dist[ev]; m=(np.isfinite(tu)&(tu<TLIM))|(np.isfinite(tv)&(tv<TLIM)); idx=np.flatnonzero(m)
    L=el[idx]; ru=np.where(np.isfinite(tu[idx]),np.maximum(0,TLIM-tu[idx])*WALK,0); rv=np.where(np.isfinite(tv[idx]),np.maximum(0,TLIM-tv[idx])*WALK,0)
    km=np.minimum(L,ru+rv).sum()/1000
    nS=np.ceil(L/5).astype(int)+1; rep=np.repeat(np.arange(len(idx)),nS); off=np.cumsum(nS)-nS; k=np.arange(nS.sum())-np.repeat(off,nS)
    s=k*(L[rep]/(nS[rep]-1)); keep=(s<=ru[rep])|(L[rep]-s<=rv[rep]); rep=rep[keep]; s=s[keep]
    e=idx[rep]; fx=nx[eu[e]]+(nx[ev[e]]-nx[eu[e]])*s/el[e]; fy=ny[eu[e]]+(ny[ev[e]]-ny[eu[e]])*s/el[e]
    ci=((fx-x0)/CELL).astype(int); ri=((y1-fy)/CELL).astype(int); okk=(ci>=0)&(ci<W)&(ri>=0)&(ri<H); ci=ci[okk]; ri=ri[okk]
    r0,r1,c0,c1=max(ri.min()-12,0),min(ri.max()+13,H),max(ci.min()-12,0),min(ci.max()+13,W)
    M=np.zeros((r1-r0,c1-c0),bool); M[ri-r0,ci-c0]=True
    return M,(r0,r1,c0,c1),km
def analyse(dist):
    M,(r0,r1,c0,c1),km=coverage(dist); d=distance_transform_edt(~M)*CELL; land=LAND[r0:r1,c0:c1]; trc=TR_[r0:r1,c0:c1]; out={"street_km":km,"crop":(r0,r1,c0,c1)}
    for buf in (100,50):
        B=d<=buf; A=B&(land>0); out[buf]=dict(area_incl_water=B.sum()*CELL**2/1e6,area_land=A.sum()*CELL**2/1e6,
            byb={n:(A&(land==l)).sum()*CELL**2/1e6 for n,l in BL.items()})
        cnt=np.bincount(trc[A],minlength=nT+1); frac=np.where(DEN>0,cnt/np.maximum(DEN,1),0); frac[0]=0
        out[buf].update(amb=(frac*amb).sum(),univ=(frac*univ).sum(),moe=np.sqrt(((frac*moe)**2).sum()),
            amb_by={CNTY[c]:(frac*amb)[cty==c].sum() for c in CNTY},no_tract_km2=(A&(trc==0)).sum()*CELL**2/1e6,
            edge_pop=(frac*amb)[(ratio<0.97)&(np.arange(nT+1)>0)].sum())
        if buf==100: out["mask"]=A
    return out
rows=[]; masks={}
for (h,lab,ub,ada),v in sorted(res.items(),key=lambda kv:str(kv[0])):
    o=analyse(v["dist"]); scen="walk" if lab=="walk" else {(False,False):"1",(False,True):"2",(True,False):"3",(True,True):"4"}[(ub,ada)]
    for buf in (100,50):
        b=o[buf]; r=dict(hospital=h,mode=lab,scenario=scen,buffer_m=buf,area_land_km2=round(b["area_land"],3),area_incl_water_km2=round(b["area_incl_water"],3),
            area_manhattan_km2=round(b["byb"]["Manhattan"],3),area_other_boroughs_km2=round(sum(b["byb"][k] for k in b["byb"] if k!="Manhattan"),3),
            **{f"area_{k.lower().replace(' ','_')}_km2":round(b["byb"][k],3) for k in ["Bronx","Brooklyn","Queens","Staten Island"]},
            street_km=round(o["street_km"],1),subway_stations=v["nsub"],bus_stops_used=v["nbus"],
            amb_pop=round(b["amb"]),amb_moe90=round(b["moe"]),universe_pop=round(b["univ"]),amb_manhattan=round(b["amb_by"]["Manhattan"]),amb_other_boroughs=round(sum(b["amb_by"][k] for k in b["amb_by"] if k!="Manhattan")),
            area_in_no_tract_km2=round(b["no_tract_km2"],3),amb_from_edge_tracts=round(b["edge_pop"]))
        rows.append(r)
    if buf==100: pass
    masks[(h,lab,ub,ada)]=(o["mask"],o["crop"])
T=pd.DataFrame(rows); T.to_csv(O+"hospital_isochrone_summary.csv",index=False)
pickle.dump(dict(masks=masks,x0=x0,y1=y1,W=W,H=H,CELL=CELL,boro=boro_polys),open(S+"iso3_masks.pkl","wb"))
pd.set_option("display.width",250)
print(T[(T.buffer_m==100)&(T["mode"].isin(["fwd0800"]))][["hospital","scenario","area_land_km2","area_incl_water_km2","area_manhattan_km2","area_other_boroughs_km2","amb_pop","amb_moe90","universe_pop"]].to_string(index=False))
print("max area in no-tract (km2):",T.area_in_no_tract_km2.max(),"| max amb from edge tracts:",T.amb_from_edge_tracts.max())
