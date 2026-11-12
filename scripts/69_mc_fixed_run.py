import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"clip_core.py")).read())
exec(open((S+"mc2_model.py")).read())
import multiprocessing as mp, time, sys, os
M2=pickle.load(open(S+"mc3_model.pkl","rb")); STN=M2["STN"]; ELV=M2["ELV"]; AV12=M2["AVAIL12"]
# original 10-station model (same elevator order / seed as the earlier chapter => identical draws)
ST10=pd.read_csv(O+"station_table.csv",dtype=str); STN10={}
for _,r in ST10.iterrows():
    m=build_station(r["station_id"],r["ada_northbound"],r["ada_southbound"]); m.update(name=r["station_name"]); STN10[r["gtfs_stop_id"]]=m
ELV10=sorted({e for s in STN10.values() for e in s["elevators"]})
BUSF=prep_bus(8); BUSR=prep_bus("rev"); CFGS={"reverse":(BUSR,-28800,True),"forward":(BUSF,28800,False)}
NDRAW=1000; SEED=20261111; THR=[0.90,0.95,0.97,0.99]
def pvec(elv,variant,one=False):
    if one: return np.ones(len(elv))
    return np.array([AV12[e] if AV12.get(e) is not None else (M2["FILL_MEAN"] if variant=="mean" else M2["FILL_LOW"]) for e in elv])
def task(args):
    h,dn=args; t0=time.time(); st=origin_state(HOSP[h]); BUS,T0,rev=CFGS[dn]
    base,bd=run_cfg(st,BUS,T0,rev,set()); reached=set(np.flatnonzero(base[:len(kids)]<1e8))
    A0,crop0,_=coverage_mask(bd); q0=quick(A0,crop0); B=q0
    cache={}
    def evaluate(key):
        if key not in cache:
            _,d=run_cfg(st,BUS,T0,rev,set(key)); A,crop,_=coverage_mask(d); q=quick(A,crop); cache[key]=(A,crop,q)
        return cache[key]
    def mc(STNx,ELVx,variant,label,one=False):
        rng=np.random.default_rng(SEED); U=rng.random((NDRAW,len(ELVx))); up=U<pvec(ELVx,variant,one); sok=make_ok(STNx); keys=collections.Counter(); anyb=0
        for k in range(NDRAW):
            upset={e for e,u in zip(ELVx,up[k]) if u}; blk=blocked_children_g(sok(upset),STNx); anyb+=bool(blk); keys[frozenset(blk&reached)]+=1
        counts=np.zeros((GH,GW),np.int16); vals=[]
        for key,mult in keys.items():
            A,crop,q=evaluate(key); r0,r1,c0,c1=crop; part=PARTR[r0:r1,c0:c1]; counts[r0:r1,c0:c1]+=(mult*(A&(part>0))).astype(np.int16); vals+=[(q["res_after"],q["res_before"],q["area_after"])]*mult
        v=np.array(vals); res=v[:,0]; resb=v[:,1]; srt=np.sort(res); k5=int(np.ceil(0.05*NDRAW)); out=dict(hospital=h,direction=dn,model=label,fill=variant,baseline_res=B["res_after"],baseline_area=B["area_after"],baseline_res_before_clip=B["res_before"],
            n_perturbed_stations=sum(1 for s in STNx.values() if s["status"]=="modeled"),n_perturbed_elevators=len(ELVx),draws_with_station_block=anyb,unique_configs=len(keys),
            mean=res.mean(),sd=res.std(ddof=1),p5=np.percentile(res,5),worst5_mean=srt[:k5].mean(),min=res.min(),median=np.median(res),draws_with_loss=int((res<B["res_after"]-0.5).sum()),
            mean_before_clip=resb.mean(),p5_before_clip=np.percentile(resb,5),outside_baseline_cells=int(((counts>0)&~np.pad(np.zeros(1,bool),0)[:0].any()).sum()) if False else 0)
        for t in THR+[1.0]:
            thr=int(np.ceil(t*NDRAW-1e-9)); m=counts>=thr; out[f"res_ge{int(round(t*100))}"]=float(DC[m].sum()); out[f"area_ge{int(round(t*100))}"]=float(m.sum()*CELL**2/1e6)
        out["exp_cov_from_probs"]=float((counts/NDRAW*DC).sum()); out["unique_values"]=len(set(np.round(res,3)))
        return out
    rows=[]
    for variant in ("mean","low"): rows.append(mc(STN,ELV,variant,"expanded"))
    rows.append(mc(STN,ELV,"mean","expanded_avail=1",one=True))                                  # check: all availabilities 1 => baseline
    for variant in ("mean","low"): rows.append(mc(STN10,ELV10,variant,"10-station"))
    # single failures (expanded model): whole station out / single elevator out
    single=[]
    for P,s in STN.items():
        if s["status"]!="modeled": continue
        key=frozenset(i for i in blocked_children_g({P2:{"PN":P2!=P,"PS":P2!=P} for P2 in STN},STN) if i in reached)
        loss=0.0 if not key else B["res_after"]-evaluate(key)[2]["res_after"]
        single.append(dict(hospital=h,direction=dn,kind="station",item=P,name=s["name"],borough=s["borough"],loss=loss,reached_key=len(key)>0))
    sok=make_ok(STN)
    for e in ELV:
        upset=set(ELV)-{e}; key=frozenset(blocked_children_g(sok(upset),STN)&reached)
        loss=0.0 if not key else B["res_after"]-evaluate(key)[2]["res_after"]; pe=1-(AV12[e] if AV12.get(e) is not None else M2["FILL_MEAN"])
        single.append(dict(hospital=h,direction=dn,kind="elevator",item=e,name="",borough="",loss=loss,p_out=pe,reached_key=len(key)>0))
    return rows,single,len(cache),time.time()-t0
def quick(A,crop):
    r0,r1,c0,c1=crop; part=PARTR[r0:r1,c0:c1]; d=DC[r0:r1,c0:c1]; m=ISM[r0:r1,c0:c1]; Am=A&(part>0)
    return dict(res_after=float(d[Am&m].sum()),area_after=Am.sum()*CELL**2/1e6,res_before=float(d[A].sum()))
if __name__=="__main__":
    tasks=[(h,dn) for h in HOSP for dn in ("reverse","forward")]; t0=time.time()
    with mp.get_context("fork").Pool(min(6,os.cpu_count())) as pool: res=pool.map(task,tasks)
    rows=[r for rs,_,_,_ in res for r in rs]; single=[s for _,ss,_,_ in res for s in ss]
    for (h,dn),(_,_,n,t) in zip(tasks,res): print(f"{h[:24]:24s} {dn:7s}: {n} unique configs evaluated in {t:.0f}s")
    pd.DataFrame(rows).to_csv(O+"mc_manhattan_summary_fixed.csv",index=False); pd.DataFrame(single).to_csv(O+"mc_manhattan_single_failure_fixed.csv",index=False)
    print("total %.0fs"%(time.time()-t0))
