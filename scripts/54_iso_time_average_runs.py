import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso3_core.py")).read())
exec(open((S+"iso4_grid.py")).read())
import time
BUSA=prep_bus("avg"); TIMES=[27000,27900,28800,29700,30600]; SC={"1":(False,False),"2":(False,True),"3":(True,False),"4":(True,True)}
prev=pd.read_csv((O+"hospital_isochrone_summary.csv"),dtype={"scenario":str})
rows=[]; t0=time.time()
for h,ll in HOSP.items():
    st=origin_state(ll)
    for T0 in TIMES:
        for s,(ub,ada) in SC.items():
            best=raptor_g(T0,ada,BUSA,ub,st,rev=False); dist,parr,nb=street_g(best,T0,BUSA,ub,st)
            A,crop,km=coverage_mask(dist); S_=stats(A,crop)
            rows.append(dict(hospital=h,dep=f"{T0//3600:02d}:{(T0%3600)//60:02d}",scenario=s,area_land_km2=S_["area"],area_manhattan_km2=S_["area_man"],area_bronx_km2=S_["area_bx"],amb_pop=S_["amb"],amb_manhattan=S_["amb_man"],amb_bronx=S_["amb_bx"],universe_pop=S_["univ"],street_km=km,subway_stations=len(parr),bus_stops_used=nb))
    print(h,"done %.0fs"%(time.time()-t0))
T=pd.DataFrame(rows); T.to_csv((O+"hospital_isochrone_timeavg_runs.csv"),index=False)
# regression at 08:00 vs previous run
m=T[T.dep=="08:00"].merge(prev[(prev["mode"]=="fwd0800")&(prev.buffer_m==100)][["hospital","scenario","area_land_km2","amb_pop"]],on=["hospital","scenario"],suffixes=("","_prev"))
print("regression 08:00: max |area diff| = %.3f km2, max |residents diff| = %.0f (of %.0f)"%((m.area_land_km2-m.area_land_km2_prev).abs().max(),(m.amb_pop-m.amb_pop_prev).abs().max(),m.amb_pop_prev.max()))
