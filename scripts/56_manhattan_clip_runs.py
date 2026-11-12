import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"clip_core.py")).read())
import time
BUSF=prep_bus("avg"); BUSR=prep_bus("rev5"); DEPS=[27000,27900,28800,29700,30600]
SC={"1":(False,False),"2":(False,True),"3":(True,False),"4":(True,True)}; rows=[]; t0=time.time()
for h,ll in HOSP.items():
    st=origin_state(ll)
    dw=st["d0"]+st["od"]/WALK; A,crop,km=coverage_mask(dw); r,_=analyse_clip(A,crop); rows.append(dict(hospital=h,direction="walk",time="-",scenario="walk",**r))
    for dirn,BUS in (("fwd",BUSF),("rev",BUSR)):
        for D in DEPS:
            T0=D if dirn=="fwd" else -D
            for s,(ub,ada) in SC.items():
                best=raptor_g(T0,ada,BUS,ub,st,rev=(dirn=="rev")); dist,parr,nb=street_g(best,T0,BUS,ub,st)
                A,crop,km=coverage_mask(dist); r,_=analyse_clip(A,crop)
                rows.append(dict(hospital=h,direction=dirn,time=f"{D//3600:02d}:{(D%3600)//60:02d}",scenario=s,subway_stations=len(parr),bus_stops_used=nb,**r))
    print(h,"done %.0fs"%(time.time()-t0))
T=pd.DataFrame(rows); T.to_csv((O+"manhattan_clip_runs.csv"),index=False)
# regression: 'before' numbers vs earlier chapters
prev=pd.read_csv((O+"hospital_isochrone_timeavg_runs.csv"),dtype={"scenario":str,"dep":str})
m=T[(T.direction=="fwd")].merge(prev,left_on=["hospital","time","scenario"],right_on=["hospital","dep","scenario"],suffixes=("","_p"))
print("regression vs previous chapter forward runs (n=%d): max |area diff| %.4f km2, max |residents diff| %.2f"%(len(m),(m.area_before-m.area_land_km2).abs().max(),(m.res_before-m.amb_pop).abs().max()))
print("clipped residents vs previous 'Manhattan' residents (tract county) max abs diff: %.0f"%((m.res_after-m.amb_manhattan).abs().max()))
print("area in Manhattan polygon but tract outside New York County (max over runs): %.4f km2"%T.area_after_not_county.max())
