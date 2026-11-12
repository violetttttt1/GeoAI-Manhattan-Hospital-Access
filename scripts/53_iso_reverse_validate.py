import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso3_core.py")).read())
R3=pickle.load(open(S+"iso3_res.pkl","rb")); res=R3["res"]; sts=R3["sts"]
BUSR=prep_bus("rev"); rng=np.random.default_rng(7)
for h in ["NYP/Columbia (CUIMC)","Mount Sinai Morningside"]:
    on_h,od_h=sts[h]["on"],sts[h]["od"]
    for ub,ada in [(False,False),(True,False),(True,True)]:
        dist=res[(h,"rev0800",ub,ada)]["dist"]; cand=np.flatnonzero(np.isfinite(dist)&(dist>400)&(dist<1500))
        pick=rng.choice(cand,size=min(25,len(cand)),replace=False); ok_pos=0; ok_neg=0; errs=[]
        for n in pick:
            L=int(np.floor(28800-dist[n]))                # latest departure (s), rounded DOWN so we never leave a fraction of a second late
            for dep,expect in ((L,True),(L+90,False)):
                st=origin_state(node=n); best=raptor_g(dep,ada,BUSR,ub,st,rev=False); d,_,_=street_g(best,dep,BUSR,ub,st)
                arr=dep+d[on_h]+od_h/WALK if np.isfinite(d[on_h]) else np.inf
                made=arr<=28800+2
                if expect: ok_pos+=made; errs.append(arr-28800)
                else: ok_neg+=(not made)
        print(f"{h:26s} bus={ub!s:5} ADA={ada!s:5}: {len(pick)} nodes | depart at L reaches hospital by 08:00: {ok_pos}/{len(pick)} | depart L+90s misses: {ok_neg}/{len(pick)} | arrival-0800 at L: median {np.median([e for e in errs if np.isfinite(e)]):.0f}s max {max(e for e in errs if np.isfinite(e)):.0f}s")
