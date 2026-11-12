"""NEW (reconstructed): builds the bus-timetable windows used by the isochrone scripts.
Combines what were four separate working scripts (bus_load main, bus_avg, bus_rev, bus_rev5). Not the exact script used at the time.
Input : raw/gtfs_bus/{gtfs_m,gtfs_bx,gtfs_busco}/   Output: data/cache/bus_8.pkl, bus_12.pkl, bus_avg.pkl, bus_rev.pkl, bus_rev5.pkl
Service date 2026-11-18 (Wednesday); each window keeps the trips that overlap the time range."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py

import pickle
exec(open(S+"bus_load.py").read().split('if __name__')[0])       # defines load(), DATE, TLIM
FEEDS=["gtfs_m","gtfs_bx","gtfs_busco"]
for T0 in (8*3600, 12*3600):                                       # 08:00-08:30 and 12:00-12:30
    pickle.dump({f:load(f,T0) for f in FEEDS}, open(S+f"bus_{T0//3600}.pkl","wb"))
TLIM=5400                                                          # window = 90 minutes
pickle.dump({f:load(f,27000) for f in FEEDS}, open(S+"bus_avg.pkl","wb"))   # trips overlapping 07:30-09:00 (forward, 5 departure times)
pickle.dump({f:load(f,25200) for f in FEEDS}, open(S+"bus_rev5.pkl","wb"))  # trips overlapping 07:00-08:30 (reverse, 5 arrival deadlines)
TLIM=1800
pickle.dump({f:load(f,27000) for f in FEEDS}, open(S+"bus_rev.pkl","wb"))   # trips overlapping 07:30-08:00 (reverse 08:00 / forward 07:30)
