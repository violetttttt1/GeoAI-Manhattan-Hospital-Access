import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso3_core.py")).read())
BUS8=prep_bus(8); BUS12=prep_bus(12); BUSR=prep_bus("rev")
CFG={"fwd0800":(BUS8,28800,False),"fwd1200":(BUS12,43200,False),"fwd0730":(BUSR,27000,False),"rev0800":(BUSR,-28800,True)}
res={}; sts={}
for h,ll in HOSP.items():
    st=origin_state(ll); sts[h]=dict(on=st["on"],od=st["od"]); print(f"== {h}: origin snapped {st['od']:.0f} m")
    dw=st["d0"]+st["od"]/WALK; res[(h,"walk",False,False)]=dict(dist=dw,nsub=0,nbus=0)
    for lab,(BUS,T0,rev) in CFG.items():
        for ub in (False,True):
            for ada in (False,True):
                best=raptor_g(T0,ada,BUS,ub,st,rev=rev); dist,parr,nb=street_g(best,T0,BUS,ub,st)
                res[(h,lab,ub,ada)]=dict(dist=dist,nsub=len(parr),nbus=nb)
        print("  ",lab,{(ub,ada):(res[(h,lab,ub,ada)]["nsub"],res[(h,lab,ub,ada)]["nbus"],int(np.isfinite(res[(h,lab,ub,ada)]["dist"]).sum())) for ub in (False,True) for ada in (False,True)})
pickle.dump(dict(res=res,sts=sts),open(S+"iso3_res.pkl","wb"))
# regression vs previous CUIMC results
prev=pickle.load(open(S+"iso2_res.pkl","rb"))
for ub in (False,True):
    for ada in (False,True):
        a=prev[(8,ub,ada)]["dist"]; b=res[("NYP/Columbia (CUIMC)","fwd0800",ub,ada)]["dist"]
        print("regression CUIMC fwd0800 bus=%s ada=%s: identical node times = %s"%(ub,ada,bool((np.isfinite(a)==np.isfinite(b)).all() and np.nanmax(np.abs(np.where(np.isfinite(a),a-b,0)))<1e-6)))
