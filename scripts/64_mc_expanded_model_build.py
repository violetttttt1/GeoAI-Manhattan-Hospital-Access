import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"clip_core.py")).read())
exec(open((S+"mc2_model.py")).read())
# 1) validate the generalised builder on the original 10 stations
ST10=pd.read_csv(O+"station_table.csv",dtype=str); ok_all=True
for _,r in ST10.iterrows():
    m=build_station(r["station_id"],r["ada_northbound"],r["ada_southbound"])
    old={}
    if isinstance(r.access_paths,str) and r.access_paths.strip():
        for part in r.access_paths.split(";"):
            d,rest=part.strip().split(":"); old[d.strip()]=sorted(sorted(p.strip().split("+")) for p in rest.split("|"))
    new={d:sorted(sorted(p) for p in pl) for d,pl in m["paths"].items()}
    same=(old==new) if old else (m["status"]!="modeled")
    ok_all&=same; print(f"  {r.station_name:24s} old-vs-new paths identical: {same} ({m['status']})")
print("generalised builder reproduces all 10 station_table access_paths:",ok_all)
# 2) availability consistency with elevator_detail.csv
ED=pd.read_csv(O+"elevator_detail.csv"); k=ED[ED.in_probability_model&(ED.avail_status=="已知")]
dif=max(abs(AVAIL12[e]-a) for e,a in zip(k["Equipment Code"],k.avail_24h_12m)); print("recomputed 12-month availability vs elevator_detail.csv for %d elevators: max abs diff %.2e"%(len(k),dif))
# 3) ADA stations reached in baseline scenario 4 (forward 08:00 and reverse 08:00), all three hospitals
BUSF=prep_bus(8); BUSR=prep_bus("rev"); reached_by={}; REACH={}
for h,ll in HOSP.items():
    st=origin_state(ll)
    for dn,(BUS,T0,rev) in {"reverse":(BUSR,-28800,True),"forward":(BUSF,28800,False)}.items():
        best,_=run_cfg(st,BUS,T0,rev,set()); par={par_of[s] for i,s in enumerate(kids.stop_id) if best[i]<1e8}; REACH[(h,dn)]=par&set(ADA)
        reached_by[(h,dn)]=len(REACH[(h,dn)])
U=sorted(set().union(*REACH.values())); print("ADA stations reached by baseline scenario 4 in any hospital/direction:",len(U),"| per combo:",reached_by)
STN=build_all(U)
import collections as C_
print("model status:",dict(C_.Counter(s["status"] for s in STN.values())),"| entrance inferred (no street elevator):",sum(1 for s in STN.values() if s["inferred"]))
print("by borough (M/Bx/other):",dict(C_.Counter(s["borough"] for s in STN.values())))
for P,s in STN.items():
    if s["status"]!="modeled": print("   NOT MODELED:",P,s["name"],s["borough"],s["status"],s.get("why",""),"| inventory elevators:",s["n_inv"])
ELV=sorted({e for s in STN.values() for e in s["elevators"]}); unk=[e for e in ELV if AVAIL12.get(e) is None]
print("elevators in expanded model:",len(ELV),"| without availability record (fill):",len(unk),unk)
print("unplaced (linked to a modelled station but no landing fields):",{P:s["unplaced"] for P,s in STN.items() if s["unplaced"]})
# ADA Compliant=NO elevators inside modelled ADA stations?
bad=INV[(INV["Equipment Code"].isin(ELV))&(INV["ADA Compliant"]=="NO")]; print("modelled elevators flagged ADA Compliant = NO:",len(bad),list(bad["Equipment Code"])[:10])
pickle.dump(dict(STN=STN,ELV=ELV,REACH=REACH,AVAIL12={e:AVAIL12.get(e) for e in ELV},FILL_MEAN=FILL_MEAN,FILL_LOW=FILL_LOW),open(S+"mc2_model.pkl","wb"))
