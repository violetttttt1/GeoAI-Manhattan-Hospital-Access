import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso2_core.py")).read())
old=pickle.load(open(S+"iso_res.pkl","rb"))["res"]
out={}
for T0h in (8,12):
    T0=T0h*3600; BUS=prep_bus(T0h)
    for use_bus in (False,True):
        for ada in (False,True):
            t0=time.time(); best=raptor2(T0,ada,BUS,use_bus); dist,parr,nbus=street_from(best,T0,BUS,use_bus)
            out[(T0h,use_bus,ada)]=dict(dist=dist,parr=parr,nbus=nbus,best=best)
            print(f"dep {T0h:02d}:00 bus={use_bus} ADA-only={ada}: subway stations {len(parr)} | bus stops used as walk sources {nbus} | street nodes {np.isfinite(dist).sum()} | {time.time()-t0:.0f}s")
            if not use_bus:
                o=old[(T0h,ada)]; same=(set(o["parr"])==set(parr)) and all(abs(o["parr"][k]-parr[k])<1e-6 for k in parr)
                dd=np.nanmax(np.abs(np.where(np.isfinite(o["dist"])&np.isfinite(dist),o["dist"]-dist,0))); print("   regression vs previous subway-only run: stations identical =",same,"| max node time diff (s) =",round(float(dd),3),"| finite-set equal =",bool((np.isfinite(o["dist"])==np.isfinite(dist)).all()))
    BUSsave={k:BUS[k] for k in ("ids","lat","lon","ok","snap")}; pickle.dump(BUSsave,open(S+f"bus_meta_{T0h}.pkl","wb"))
pickle.dump({k:dict(dist=v["dist"],parr=v["parr"],nbus=v["nbus"]) for k,v in out.items()},open(S+"iso2_res.pkl","wb"))
