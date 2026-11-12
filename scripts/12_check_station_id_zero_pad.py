import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pandas as pd
R=R
rd=lambda p: pd.read_csv(R+p,dtype=str,low_memory=False)
av=rd("elevator_availability/elevator_availability.csv"); inv=rd("elevator_inventory/elevator_inventory.csv"); st=rd("mta_stations/mta_stations.csv")
z=lambda s:s.dropna().str.lstrip("0")
ae=av[av["Equipment Type"]=="Elevator"]; ie=inv[inv["Elevator or Escalator"]=="Elevator"]
m=ae.drop_duplicates("Equipment Code").merge(ie,on="Equipment Code",suffixes=("_a","_i"))
print("station MRN equal after zero-strip",(m["Station MRN_a"].str.lstrip("0")==m["Station MRN_i"].str.lstrip("0")).mean())
a=set(z(av["Station MRN"])); i=set(z(inv["Station MRN"])); b=set(z(st["Station ID"])); c=set(z(st["Complex ID"]))
print("avail stationMRN",len(a),"inv",len(i),"a∩i",len(a&i),"| vs stations Station ID: avail",len(a&b),"/",len(a),"inv",len(i&b),"/",len(i))
print("raw stations Station ID has leading zeros?",(st["Station ID"].str.startswith("0")).sum(),"| inv Station MRN with leading 0:",inv["Station MRN"].dropna().str.startswith("0").sum(),"| avail:",av["Station MRN"].str.startswith("0").sum())
ac=set(z(av["Station Complex MRN"])); print("complex avail→stations Complex ID",len(ac&c),"/",len(ac))
# stations in complexes with elevators
cx=set(z(ie["Station Complex MRN"])); sc=st["Complex ID"].str.lstrip("0")
print("stations rows in a complex that has an inventory elevator",sc.isin(cx).sum(),"| ADA=1 rows",(st.ADA=="1").sum(),"| ADA=1 rows w/ elevator complex",((st.ADA=="1")&sc.isin(cx)).sum(),"| ADA=1 without",((st.ADA=="1")&~sc.isin(cx)).sum())
