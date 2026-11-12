import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso_core.py")).read().split("# ---------- street graph")[0])
exec(open((S+"iso_core.py")).read().split("# ---------- GTFS")[1].replace("GT=R+","GT=R+",1)) if False else None
import pickle, pandas as pd, numpy as np, collections
O=O; R=R
M=pickle.load(open(S+"mc2_model.pkl","rb")); STN=M["STN"]; REACH=M["REACH"]; FILL_MEAN=M["FILL_MEAN"]; FILL_LOW=M["FILL_LOW"]
# 12-month availability for ALL elevators (same formula as before)
av=pd.read_csv(R+"elevator_availability/elevator_availability.csv",dtype=str); av["m"]=pd.to_datetime(av.Month); last=av.m.max(); w=av[(av["Equipment Type"]=="Elevator")&(av.m>=last-pd.DateOffset(months=11))].copy()
for c in ["24-Hour Hours Available","24-Hour Total Hours"]: w[c]=pd.to_numeric(w[c])
g=w.groupby("Equipment Code")[["24-Hour Hours Available","24-Hour Total Hours"]].sum(); AVALL={e:(float(r.iloc[0]/r.iloc[1]) if r.iloc[1]>0 else None) for e,r in g.iterrows()}
L=pd.read_csv(S+"live_eq.csv",dtype=str); L=L[L.equipmenttype=="EL"].set_index("equipmentno")
# ---- overrides: structure read from the official live equipment list (serving / shortdescription / linesservedbyelevator / elevatorsgtfsstopid)
S1=lambda *a:{*a}
OVR={
 "123":dict(why="elevators have Street access but no direction field in the inventory; live list says EL239 'Street to Northbound platform', EL240 'Street to Southbound platform'",paths={"PN":[S1("EL239")],"PS":[S1("EL240")]}),
 "120":dict(why="inventory has no direction field; live list: EL146 'Street to uptown platform', EL145 'Street to downtown platform'",paths={"PN":[S1("EL146")],"PS":[S1("EL145")]}),
 "R15":dict(why="single elevator without direction field; live list: EL268X 'Street to uptown platform'. Station is ADA = 2 (uptown only), so only the northbound platform is required",paths={"PN":[S1("EL268X")]}),
 "222":dict(why="elevators are registered in the inventory under the 4-line row (Station MRN 390) but the live list gives them stops 222/415 and lines 2/4/5: EL100 Street->mezzanine, EL101 mezzanine->Bronx-bound 2/5 platform, EL102 mezzanine->Manhattan-bound 2/5 platform",paths={"PN":[S1("EL100","EL101")],"PS":[S1("EL100","EL102")]}),
 "414":dict(why="elevators registered under the B/D row (Station MRN 219); live list: EL131 Street->mezzanine (B/D/4), EL132 mezzanine->Northbound (Woodlawn-bound) 4 platform, EL133 mezzanine->Manhattan-bound 4 platform",paths={"PN":[S1("EL131","EL132")],"PS":[S1("EL131","EL133")]}),
 "D11":dict(why="CORRECTION of an existing model: EL132 and EL133 serve the 4-line platforms (live list lines = 4) and were wrongly counted as alternatives for the B/D platforms. Live list: EL135 mezzanine->Bronx-bound B/D, EL134 mezzanine->Manhattan-bound B/D",paths={"PN":[S1("EL131","EL135")],"PS":[S1("EL131","EL134")]}),
 "127":dict(why="complex Times Sq-42 St: entrance elevators EL231X (42 St & 7 Av) and EL619 (43 St & Broadway) both 'to mezzanine for service on all lines in both directions'; EL233 mezzanine->uptown 1/2/3 platform; EL232 mezzanine->downtown 1/2/3 (and 7) platform",paths={"PN":[S1("EL231X","EL233"),S1("EL619","EL233")],"PS":[S1("EL231X","EL232"),S1("EL619","EL232")]}),
 "725":dict(why="same complex: the 7 platform is reached by EL232 ('Mezzanine to 7 & downtown 1/2/3'); both directions share it. Assumes the 7 platform serves both directions through EL232",paths={"PN":[S1("EL231X","EL232"),S1("EL619","EL232")],"PS":[S1("EL231X","EL232"),S1("EL619","EL232")]}),
 "R16":dict(why="same complex: EL230 mezzanine->uptown N/Q/R/W platform, EL229 mezzanine->downtown N/Q/R/W platform",paths={"PN":[S1("EL231X","EL230"),S1("EL619","EL230")],"PS":[S1("EL231X","EL229"),S1("EL619","EL229")]}),
 "125":dict(why="elevators registered under the A/C/B/D row (Station MRN 161). EL280 Street->uptown 1 platform; EL276X Street->mezzanine; EL278 mezzanine->uptown A/B/C/D; EL279 uptown 1 platform->uptown A/B/C/D platform; EL277 and EL622 mezzanine->downtown platforms (A/B/C/D and 1). The uptown alternative EL276X+EL278+EL279 is INFERRED from those descriptions",paths={"PN":[S1("EL280"),S1("EL276X","EL278","EL279")],"PS":[S1("EL276X","EL277"),S1("EL276X","EL622")]}),
 "A24":dict(why="CORRECTION of an existing model: the street entrance EL276X had no landing fields and was dropped, so the platform elevators were treated as independent alternatives. Rebuilt from the live list (same elevators as station 125). The uptown alternative EL280+EL279 is inferred",paths={"PN":[S1("EL276X","EL278"),S1("EL280","EL279")],"PS":[S1("EL276X","EL277"),S1("EL276X","EL622")]}),
}
UNFIX={
 "902":("Times Sq-42 St (S)","inventory: no elevators under this station; live list gives only the complex-wide entrance elevators (lines list includes S) and no elevator to the S shuttle platform","the S platform has no described elevator connection (platform may be reachable from the mezzanine without an elevator, but the data do not say)"),
 "A27":("42 St-Port Authority Bus Terminal (A C E)","inventory elevators have no usable platform fields; live list: EL291X Street->intermediate landing, EL290X landing->mezzanine, EL288X/EL289X bus terminal->mezzanine, all 'for A/C/E service in both directions'","no elevator is described between the mezzanine and the A/C/E platforms, so the street-to-platform chain is incomplete"),
 "630":("51 St (6)","inventory: EL201, EL202 have fields but no mezzanine-to-platform path; live list describes platform<->underpass links between the uptown and downtown 6 platforms and a street->mezzanine elevator (EL203X)","how the mezzanine reaches each 6 platform is not described; the underpass description is ambiguous"),
 "A32":("W 4 St-Wash Sq (A C E)","inventory: EL333 street entrance has no direct path to the platform fields; live list: EL334/EL335 link A/C/E platforms to the transfer mezzanine and B/D/F/M, EL333 street->'upper platform level'","which platforms the street elevator reaches is ambiguous (upper vs lower level)"),
 "301":("Harlem-148 St (3)","no elevator in inventory, availability table, live equipment list, amenities or entrances (see the 148 St search chapter)","genuinely no elevator on record; station has an ADA gate and a single station-house entrance. Kept as 'no elevator dependence' (not verified on site)"),
}
STN2={P:dict(s) for P,s in STN.items()}; log=[]
for P,o in OVR.items():
    old=STN[P]; paths={d:[set(p) for p in pl] for d,pl in o["paths"].items()}; els=sorted({e for pl in paths.values() for p in pl for e in p})
    s=dict(old); s.update(status="modeled",paths=paths,elevators=els,source="live equipment list description",override_why=o["why"],entrance=("Street" if True else None),inferred=False); STN2[P]=s
    log.append(dict(gtfs_stop_id=P,station=old["name"],borough=old["borough"],status_before=old["status"],reason_before=old.get("why",""),status_after="modeled",how=o["why"],paths_after=" ; ".join(f"{d}: "+" | ".join("+".join(sorted(p)) for p in pl) for d,pl in paths.items()),
        corrected_existing=P in ("D11","A24"),paths_before=" ; ".join(f"{d}: "+" | ".join("+".join(sorted(p)) for p in pl) for d,pl in old["paths"].items()) if old["paths"] else ""))
for P,(nm,ev,why) in UNFIX.items():
    old=STN[P]; log.append(dict(gtfs_stop_id=P,station=old["name"],borough=old["borough"],status_before=old["status"],reason_before=old.get("why",""),status_after="not modeled",how="NOT FIXABLE: "+why,paths_after="",corrected_existing=False,paths_before="",evidence=ev))
ELV=sorted({e for s in STN2.values() if s["status"]=="modeled" for e in s["elevators"]}); AV12={e:AVALL.get(e) for e in ELV}; unk=[e for e in ELV if AV12[e] is None]
print("modeled stations before/after:",sum(1 for s in STN.values() if s["status"]=="modeled"),"->",sum(1 for s in STN2.values() if s["status"]=="modeled"),"| elevators",len(ELV),"| without availability:",unk)
print("not modeled after:",[ (P,STN2[P]["name"]) for P in STN2 if STN2[P]["status"]!="modeled"])
# sanity: every elevator of an override must exist in the live list and serve the stop
bad=[]
for P in OVR:
    for e in STN2[P]["elevators"]:
        if e not in L.index: bad.append((P,e,"not in live list")); continue
        if P not in str(L.loc[e,"elevatorsgtfsstopid"]).split("/"): bad.append((P,e,"stop not in elevator's stop list: "+str(L.loc[e,"elevatorsgtfsstopid"])))
print("override consistency vs live list (stop ids):",bad if bad else "all elevators serve their station per the live list")
pickle.dump(dict(STN=STN2,ELV=ELV,REACH=REACH,AVAIL12=AV12,FILL_MEAN=FILL_MEAN,FILL_LOW=FILL_LOW),open(S+"mc3_model.pkl","wb"))
pd.DataFrame(log).to_csv(REB+"station_model_fixes.csv",index=False)
# share modelled per combo after the fix
mod=lambda P:STN2[P]["status"]=="modeled"; st=pd.read_csv(R+"mta_stations/mta_stations.csv",dtype=str).set_index("GTFS Stop ID")
for (h,dn),R_ in REACH.items():
    man=[P for P in R_ if st.loc[P,"Borough"]=="M"]
    print(f"{h[:22]:22s} {dn:7s}: reached {len(R_)} modeled {sum(mod(P) for P in R_)} ({100*sum(mod(P) for P in R_)/len(R_):.0f}%) | Manhattan {len(man)} modeled {sum(mod(P) for P in man)} ({100*sum(mod(P) for P in man)/len(man):.0f}%)")
