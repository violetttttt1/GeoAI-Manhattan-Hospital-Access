import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import sys, pandas as pd
R=R
files={"elevator_availability":R+"elevator_availability/elevator_availability.csv",
"elevator_inventory":R+"elevator_inventory/elevator_inventory.csv",
"mta_stations":R+"mta_stations/mta_stations.csv",
"gtfs_stops":R+"gtfs/unz/stops.txt","gtfs_trips":R+"gtfs/unz/trips.txt","gtfs_routes":R+"gtfs/unz/routes.txt","gtfs_calendar":R+"gtfs/unz/calendar.txt","gtfs_transfers":R+"gtfs/unz/transfers.txt",
"ped_ramp_locations":R+"ped_ramp_locations/ped_ramp_locations.csv",
"ramp_program_progress":R+"ramp_program_progress/ramp_program_progress.csv",
"mbpo_ramp_report":R+"mbpo_ramp_report/mbpo_ramp_report.csv"}
for k,f in files.items():
    df=pd.read_csv(f,dtype=str,low_memory=False)
    print("=====",k,len(df)); print(list(df.columns))
    for c in df.columns:
        if any(t in c.lower() for t in ("date","time","month","year","start","end")) and "stop" not in c.lower():
            d=pd.to_datetime(df[c],errors="coerce",format="mixed")
            if d.notna().mean()>0.5: print("  date col",c,"min",d.min(),"max",d.max(),"nulls",d.isna().sum())
    print(df.head(2).T.to_string()[:1800])
