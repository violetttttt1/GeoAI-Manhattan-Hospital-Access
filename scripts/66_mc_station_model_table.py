"""NEW (reconstructed from an ad-hoc command run during the analysis; not the exact script used at the time).
Input : data/cache/mc2_model.pkl (from 64), data/cache/mc3_model.pkl (from 68)
Output (rebuilt copies in data/cache/rebuilt/): mc_station_model.csv (the 59 ADA stations reached, before the fixes),
        mc_elevator_station_map.csv (elevator -> station for the FINAL model; lets 80_final_summary.py run without pickles)."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py

import pickle, pandas as pd
M=pickle.load(open(S+"mc2_model.pkl","rb")); STN=M["STN"]; REACH=M["REACH"]; AV=M["AVAIL12"]; rows=[]
for P,s in STN.items():
    inw={f"{h.split()[0][:6]}-{dn[:3]}":(P in R_) for (h,dn),R_ in REACH.items()}
    el=s["elevators"]; pa=" ; ".join(f"{d}: "+" | ".join("+".join(sorted(p)) for p in pl) for d,pl in s["paths"].items())
    rows.append(dict(gtfs_stop_id=P,station=s["name"],borough=s["borough"],ada=s["ada"],status=s["status"],reason=s.get("why",""),n_inventory_elevators=s["n_inv"],n_modeled_elevators=len(el),unplaced=";".join(s["unplaced"]),entrance=s["entrance"],entrance_inferred=s["inferred"],access_paths=pa,
        elevators_without_availability=";".join(e for e in el if AV.get(e) is None),**{"reached_by_"+k:v for k,v in inw.items()}))
pd.DataFrame(rows).sort_values(["status","borough","station"]).to_csv(REB+"mc_station_model.csv",index=False)
M3=pickle.load(open(S+"mc3_model.pkl","rb"))["STN"]
pd.DataFrame([dict(elevator=e,gtfs_stop_id=P,station=s["name"]) for P,s in M3.items() if s["status"]=="modeled" for e in s["elevators"]]).to_csv(REB+"mc_elevator_station_map.csv",index=False)
