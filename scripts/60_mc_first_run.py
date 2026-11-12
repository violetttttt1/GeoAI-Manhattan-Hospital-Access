import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"mc_core.py")).read())
import time
BUSF=prep_bus(8); BUSR=prep_bus("rev"); CFG={"reverse":(BUSR,-28800,True),"forward":(BUSF,28800,False)}
NDRAW=1000; rng=np.random.default_rng(20261111); U=rng.random((NDRAW,len(ELEVS)))
CTYC=CTY[TRID]; ISMAN=(CTYC==61); ISBX=(CTYC==5); DC=DENS[TRID]   # per-cell residents (tract density mapped to cells)
rows=[]; single=[]; counts_save={}; t0=time.time(); uniq_info=[]
def vals(A,crop):
    r0,r1,c0,c1=crop; d=DC[r0:r1,c0:c1]; m=ISMAN[r0:r1,c0:c1]; b=ISBX[r0:r1,c0:c1]
    return float(d[A].sum()),float(d[A&m].sum()),float(d[A&b].sum())
for h,ll in HOSP.items():
    st=origin_state(ll)
    for dname,(BUS,T0,rev) in CFG.items():
        base,bd=run_cfg(st,BUS,T0,rev,set()); reached=set(np.flatnonzero(base[:len(kids)]<1e8))
        A0,crop0,_=coverage_mask(bd); B=vals(A0,crop0); base_full=np.zeros((GH,GW),bool); r0,r1,c0,c1=crop0; base_full[r0:r1,c0:c1]=A0
        cache={}
        def evaluate(key):
            if key not in cache:
                _,d=run_cfg(st,BUS,T0,rev,set(key)); A,crop,_=coverage_mask(d); cache[key]=(A,crop,vals(A,crop))
            return cache[key]
        for variant in ("mean","low"):
            up=U<p_up(variant); keys=collections.Counter(); anyblock=0
            for k in range(NDRAW):
                blk=blocked_children(station_ok(up[k])); anyblock+=bool(blk); keys[frozenset(blk&reached)]+=1
            counts=np.zeros((GH,GW),np.int16); draw_vals=[]
            for key,mult in keys.items():
                A,crop,v=evaluate(key); r0,r1,c0,c1=crop; counts[r0:r1,c0:c1]+=(mult*A).astype(np.int16); draw_vals+= [v]*mult
            tot=np.array([v[0] for v in draw_vals]); P=counts/NDRAW
            # coverage probability bands (residents = ambulatory-difficulty residents, uniform within tract)
            def band(mask): return (float(DC[mask].sum()),float(DC[mask&ISMAN].sum()),float(DC[mask&ISBX].sum()),float(mask.sum()*CELL**2/1e6))
            ge=lambda t:counts>=int(np.ceil(t*NDRAW-1e-9))
            R=dict(ge90=band(ge(0.90)),ge95=band(ge(0.95)),ge99=band(ge(0.99)),always=band(counts==NDRAW),mid=band((counts>=NDRAW//2)&(counts<int(0.9*NDRAW))),low=band((counts>0)&(counts<NDRAW//2)),anyp=band(counts>0))
            outside=int(((counts>0)&~base_full).sum()); exp_cov=float((P*DC).sum())
            rows.append(dict(hospital=h,direction=dname,fill=variant,baseline_residents=B[0],baseline_manhattan=B[1],baseline_bronx=B[2],
                mc_mean=tot.mean(),mc_sd=tot.std(ddof=1),mc_min=tot.min(),mc_p5=np.percentile(tot,5),mc_median=np.median(tot),mc_p95=np.percentile(tot,95),
                draws_with_any_station_block=anyblock,draws_with_loss=int((tot<B[0]-0.5).sum()),unique_configs=len(keys),
                exp_cov_from_probs=exp_cov,cells_outside_baseline=outside,
                **{f"res_{k}":v[0] for k,v in R.items()},**{f"man_{k}":v[1] for k,v in R.items()},**{f"bx_{k}":v[2] for k,v in R.items()},**{f"area_{k}":v[3] for k,v in R.items()}))
            if variant=="mean": counts_save[(h,dname)]=(counts.copy(),crop0)
        # single failures (full station both directions / single elevator) for this hospital & direction
        for P_,s in STATIONS.items():
            if not s["paths"]: continue
            key=frozenset(c for c in blocked_children({P2:{"PN":P2!=P_,"PS":P2!=P_} for P2 in STATIONS}) if c in reached)
            if not key: single.append(dict(hospital=h,direction=dname,kind="station",item=s["name"],loss=0.0,reached=False)); continue
            A,crop,v=evaluate(key); single.append(dict(hospital=h,direction=dname,kind="station",item=s["name"],loss=B[0]-v[0],reached=True))
        for e in ELEVS:
            up1=np.ones(len(ELEVS),bool); up1[EIDX[e]]=False; key=frozenset(blocked_children(station_ok(up1))&reached)
            if not key: single.append(dict(hospital=h,direction=dname,kind="elevator",item=e,loss=0.0,reached=False,p_out=1-(AVAIL[e] if AVAIL[e] is not None else FILL_MEAN))); continue
            A,crop,v=evaluate(key); single.append(dict(hospital=h,direction=dname,kind="elevator",item=e,loss=B[0]-v[0],reached=True,p_out=1-(AVAIL[e] if AVAIL[e] is not None else FILL_MEAN)))
        print(f"{h} {dname}: baseline {B[0]:.0f} | unique configs evaluated {len(cache)} | elapsed {time.time()-t0:.0f}s")
M=pd.DataFrame(rows); M.to_csv(O+"mc_scenario4_summary.csv",index=False)
SG=pd.DataFrame(single); SG.to_csv(O+"mc_single_failure.csv",index=False)
pickle.dump(dict(counts=counts_save,GW=GW,GH=GH,gx0=gx0,gy1=gy1),open(S+"mc_counts.pkl","wb"))
pd.set_option("display.width",250)
print(M[["hospital","direction","fill","baseline_residents","mc_mean","mc_sd","mc_min","mc_p5","res_ge90","res_ge95","res_ge99","res_always","draws_with_any_station_block","draws_with_loss","unique_configs","cells_outside_baseline"]].round(0).to_string(index=False))
print("check E[covered] from per-cell probabilities vs mean of draws (max abs diff):",(M.exp_cov_from_probs-M.mc_mean).abs().max())
