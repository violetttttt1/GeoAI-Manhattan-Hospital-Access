import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso3_core.py")).read())
exec(open((S+"iso4_grid.py")).read())
# ---- Manhattan parts of the official borough boundary, rasterised with part ids
PNAMES={1:"main island",2:"Randalls/Wards Island",3:"Roosevelt Island",4:"Marble Hill",5:"Governors Island",6:"other small islands"}
_mf=[f for f in _gj["features"] if f["properties"]["boroname"]=="Manhattan"][0]; _pimg=Image.new("L",(GW,GH),0); _pd=ImageDraw.Draw(_pimg); _parts=[]
_polys=_mf["geometry"]["coordinates"]; _areas=[]
for _p in _polys:
    _a=np.array(_p[0]); _X,_Y=xy(_a[:,1],_a[:,0]); _areas.append(0.5*abs(np.dot(_X,np.roll(_Y,-1))-np.dot(_Y,np.roll(_X,-1))))
_main=int(np.argmax(_areas))
for _i,_p in enumerate(_polys):
    _a=np.array(_p[0]); la,lo=_a[:,1].mean(),_a[:,0].mean()
    pid=1 if _i==_main else 4 if (40.865<la<40.885 and -73.925<lo<-73.900) else 3 if (40.750<la<40.775 and -73.965<lo<-73.940) else 2 if (40.780<la<40.805 and -73.935<lo<-73.910) else 5 if (40.680<la<40.700 and -74.025<lo<-74.010) else 6
    _parts.append((pid,_areas[_i]/1e6)); _X,_Y=xy(_a[:,1],_a[:,0]); _pd.polygon(list(zip((_X-gx0)/CELL,(gy1-_Y)/CELL)),fill=pid)
    for _h in _p[1:]:
        _b=np.array(_h); _Xh,_Yh=xy(_b[:,1],_b[:,0]); _pd.polygon(list(zip((_Xh-gx0)/CELL,(gy1-_Yh)/CELL)),fill=0)
PARTR=np.array(_pimg,np.uint8)
print("Manhattan parts (km2):",{PNAMES[k]:round(sum(a for p,a in _parts if p==k),3) for k in PNAMES},"| raster Manhattan land %.2f km2"%((PARTR>0).sum()*CELL**2/1e6))
CTYC=CTY[TRID]; ISM=(CTYC==61); DC=DENS[TRID]
print("raster cells: Manhattan polygon but tract not in New York County: %.3f km2 | tract in New York County but outside Manhattan polygon: %.3f km2"%(((PARTR>0)&(TRID>0)&~ISM).sum()*CELL**2/1e6,((PARTR==0)&(TRID>0)&ISM).sum()*CELL**2/1e6))
def analyse_clip(A,crop):
    r0,r1,c0,c1=crop; part=PARTR[r0:r1,c0:c1]; d=DC[r0:r1,c0:c1]; m=ISM[r0:r1,c0:c1]; Am=A&(part>0)
    out=dict(area_before=A.sum()*CELL**2/1e6,res_before=float(d[A].sum()),res_before_man=float(d[A&m].sum()),res_before_other=float(d[A&~m].sum()),
             area_after=Am.sum()*CELL**2/1e6,res_after=float(d[Am&m].sum()),area_after_not_county=(Am&~m&(TRID[r0:r1,c0:c1]>0)).sum()*CELL**2/1e6)
    for k,nme in PNAMES.items(): out[f"area_{nme}"]=(Am&(part==k)).sum()*CELL**2/1e6; out[f"res_{nme}"]=float(d[Am&m&(part==k)].sum())
    return out,Am
