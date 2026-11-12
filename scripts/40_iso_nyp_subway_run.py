import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso_core.py")).read())
ORIG=(40.8409780,-73.9407016)
on,od=snap(*ORIG); print("origin snapped to node at %.0f m"%od[0])
# walk origin -> all parent stations
d0=dijkstra(G[:N,:N],directed=True,indices=int(on),limit=TLIM+1)
pnodes,pd_=snap(parents.lat.values,parents.lon.values); pw={}
for P,nd,sd in zip(parents.index,pnodes,pd_):
    t=(od[0]+d0[nd]*WALK+sd)/WALK if np.isfinite(d0[nd]) else np.inf
    if t<=TLIM: pw[P]=t
print("stations within walking reach:",len(pw)); nm=parents.stop_name.to_dict(); print(sorted([(round(v/60,1),nm[k],k) for k,v in pw.items()])[:6])
res={}
for T0h in (8,12):
    T0=T0h*3600
    for ada in (False,True):
        pwm=dict(pw)
        best=raptor(pwm,T0,ada)
        # best arrival per parent (relative seconds)
        parr={}
        for i,s in enumerate(kids.stop_id):
            if best[i]<1e8: P=par_of[s]; parr[P]=min(parr.get(P,1e9),best[i]-T0)
        srcs=[(int(on),od[0]/WALK)]
        for P,t in parr.items():
            if t<=TLIM:
                k=list(parents.index).index(P); srcs.append((int(pnodes[k]),t+pd_[k]/WALK))
        dist=street_times(srcs); res[(T0h,ada)]=dict(parr=parr,dist=dist)
        print(f"dep {T0h:02d}:00 ADA-only={ada}: stations reachable (incl. walking-only) {len(parr)} | street nodes reachable {np.isfinite(dist).sum()}")
# walk only
dw=dijkstra(G[:N,:N],directed=True,indices=int(on),limit=TLIM+1); dw=dw+od[0]/WALK
res["walk"]=dict(dist=dw)
# sanity: some travel times (08:00, ordinary)
pa=res[(8,False)]["parr"]; 
for P in ["A15","A24","A27","A34","A09","A07","112","A12","120","310","228","A25"]:
    if P in pa: print("  ",nm[P],P,"%.1f min"%(pa[P]/60),"| ADA-only:", ("%.1f"%(res[(8,True)]["parr"][P]/60) if P in res[(8,True)]["parr"] else "unreachable"))
# monotonic check: ADA-only times >= ordinary at every street node
a=res[(8,False)]["dist"]; b=res[(8,True)]["dist"]; bad=np.isfinite(b)&~(a<=b+1e-6); print("ADA-only faster than ordinary at",bad.sum(),"nodes (should be 0)")
pickle.dump(dict(res=res,orig=ORIG,on=int(on),od=float(od[0]),pw=pw,pnodes=pnodes,pd=pd_),open(S+"iso_res.pkl","wb"))
