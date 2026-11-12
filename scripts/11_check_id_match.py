import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pandas as pd
R=R
rd=lambda p: pd.read_csv(R+p,dtype=str,low_memory=False)
av=rd("elevator_availability/elevator_availability.csv"); inv=rd("elevator_inventory/elevator_inventory.csv")
st=rd("mta_stations/mta_stations.csv"); stops=rd("gtfs/unz/stops.txt")
pr=rd("ped_ramp_locations/ped_ramp_locations.csv"); pg=rd("ramp_program_progress/ramp_program_progress.csv"); mb=rd("mbpo_ramp_report/mbpo_ramp_report.csv")
print("--dates")
for n,s in [("ped GeoCyclora",pr.GeoCyclora),("progress End",pg.Construction_End_Date)]:
    d=pd.to_datetime(s,errors="coerce",format="mixed"); print(n,d.min(),d.max(),"nonnull",d.notna().sum(),"of",len(d))
print("progress status",pg.Construction_Status_Value.value_counts(dropna=False).to_dict())
av["m"]=pd.to_datetime(av.Month); print("avail months",av.m.nunique(),"latest rows",(av.m==av.m.max()).sum())
print("avail types",av["Equipment Type"].value_counts().to_dict(),"| inv types",inv["Elevator or Escalator"].value_counts().to_dict())
print("avail managed",av["Managed By"].value_counts().to_dict())
print("--ids")
ae=av[av["Equipment Type"]=="Elevator"]; ie=inv[inv["Elevator or Escalator"]=="Elevator"]
A=set(ae["Equipment Code"]); I=set(ie["Equipment Code"]); print("avail elev codes",len(A),"inv elev codes",len(I),"inv dup codes",inv["Equipment Code"].duplicated().sum())
print("avail∩inv",len(A&I),"avail matched %.1f%%"%(100*len(A&I)/len(A)),"inv matched %.1f%%"%(100*len(A&I)/len(I)))
print("avail-only sample",sorted(A-I)[:15]); print("inv-only sample",sorted(I-A)[:15])
al=set(av["Equipment Code"]); il=set(inv["Equipment Code"]); print("ALL equip avail∩inv",len(al&il),len(al),len(il))
# normalised (strip trailing letters)
n=lambda s:{x.rstrip("X") for x in s}; print("after stripping trailing X: matched",len(n(A)&n(I)))
lastA=set(ae[ae.m==ae.m.max()]["Equipment Code"]); print("latest-month elev codes",len(lastA),"in inv %.1f%%"%(100*len(lastA&I)/len(lastA)))
print("inv status",inv.Service_Status.value_counts().to_dict() if "Service_Status" in inv else inv["Service Status"].value_counts().to_dict())
print("--station keys")
for c in ["Station MRN","Station Complex MRN"]:
    print(c,"avail null",av[c].isna().sum(),"inv null",inv[c].isna().sum(),"| inv null among elevators",ie[c].isna().sum())
    a=set(av[c].dropna()); i=set(inv[c].dropna()); print("  distinct avail",len(a),"inv",len(i),"∩",len(a&i))
# avail code -> station consistency
print("avail codes w/ >1 station MRN",(av.groupby("Equipment Code")["Station MRN"].nunique()>1).sum())
m=ae.drop_duplicates("Equipment Code").merge(ie[["Equipment Code","Station MRN","Station Complex MRN"]],on="Equipment Code",suffixes=("_a","_i"))
print("same code, station MRN equal",(m["Station MRN_a"]==m["Station MRN_i"]).mean().round(3),"complex equal",(m["Station Complex MRN_a"]==m["Station Complex MRN_i"]).mean().round(3))
print("inv Station MRN vs stations Station ID/Complex ID/GTFS Stop ID:")
for k in ["Station ID","Complex ID","GTFS Stop ID"]:
    for c in ["Station MRN","Station Complex MRN"]:
        a=set(inv[c].dropna()); b=set(st[k].dropna()); print(f"  inv.{c} vs stations.{k}: {len(a&b)}/{len(a)}")
print("inv Station MRN sample",inv["Station MRN"].dropna().unique()[:5],"| stations Station ID",st["Station ID"].unique()[:5])
print("stations GTFS Stop ID in gtfs stops(parent)",st["GTFS Stop ID"].isin(set(stops.stop_id)).mean().round(3),"| stations ADA=1:",(st.ADA=="1").sum(),"of",len(st))
print("--ramp keys")
print("ped CornerID uniq",pr.CornerID.nunique(),"dup rows",pr.CornerID.duplicated().sum(),"| RampID null",pr.RampID.isna().sum(),"uniq",pr.RampID.nunique())
a=set(pr.CornerID); b=set(pg.CornerID); print("ped∩progress CornerID",len(a&b),"of",len(a),"ped /",len(b),"prog; prog uniq",pg.CornerID.nunique())
r=set(mb["Ramp ID (No Id means a part of center cut)"].dropna()); print("mbpo RampID uniq",len(r),"in ped RampID %.1f%%"%(100*len(r&set(pr.RampID.dropna()))/len(r)),"in ped CornerID",len(r&a),"in progress CornerID",len(r&b))
print("stop-level rows in gtfs: parent stations",(stops.location_type=="1").sum())
