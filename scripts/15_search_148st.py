import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import json, re, pandas as pd
R=R
pd.set_option("display.width",250,"display.max_colwidth",160)
rx=re.compile(r"\b148\b|harlem|148\s?st|148th",re.I)
def hits(df,name,cols):
    m=pd.Series(False,index=df.index)
    for c in cols: m|=df[c].astype(str).str.contains(rx)
    print(f"{name}: rows {len(df)}, rows matching 148/Harlem in {len(cols)} text cols: {m.sum()}"); return df[m]
# stations
st=pd.read_csv(R+"mta_stations/mta_stations.csv",dtype=str); h=hits(st,"stations",st.columns); print(h[["GTFS Stop ID","Station ID","Complex ID","Stop Name","Daytime Routes","ADA","Structure"]].to_string())
# gtfs stops
gs=pd.read_csv(R+"gtfs/unz/stops.txt",dtype=str); h=hits(gs,"gtfs stops",["stop_id","stop_name"]); print(h.to_string())
# inventory
inv=pd.read_csv(R+"elevator_inventory/elevator_inventory.csv",dtype=str)
h=hits(inv,"inventory",inv.columns); print(h[["Equipment Code","Elevator or Escalator","Station Name","Station MRN","Station Complex MRN","Notes"]].to_string())
for k in ["Station MRN","Station Complex MRN"]: print("inventory",k,"== 436 or 0436:",inv[k].fillna("").str.lstrip("0").eq("436").sum())
txt=inv[inv["Alternative Route"].fillna("").str.contains(r"148 St|Harlem-148",regex=True)]; print("inventory Alternative Route text mentioning 148 St:",txt[["Equipment Code","Station Name"]].values.tolist())
# availability
av=pd.read_csv(R+"elevator_availability/elevator_availability.csv",dtype=str)
h=hits(av,"availability",["Station Name","Station Complex Name","Equipment Code","Borough"]); print(h.head())
for k in ["Station MRN","Station Complex MRN"]: print("availability",k,"== 436:",av[k].fillna("").str.lstrip("0").eq("436").sum())
print("availability: any station name with 'LWP' (Lenox/White Plains):",sorted(av[av["Station Name"].str.contains("LWP",na=False)]["Station Name"].unique()))
# live equipment
eq=json.load(open(R+"live_equipment/equipments.json")); out=json.load(open(R+"live_equipment/outages.json"))
E=pd.DataFrame(eq); O=pd.DataFrame(out)
h=hits(E,"live equipment",["station","serving","shortdescription","elevatorsgtfsstopid","elevatormrn","stationcomplexid","nextadanorth","nextadasouth"]); print(h[["station","trainno","equipmentno","equipmenttype","serving","elevatorsgtfsstopid","elevatormrn","stationcomplexid","nextadanorth","nextadasouth"]].to_string())
print("live equipment gtfs stop 301 / mrn 436 / complex 436:",(E.elevatorsgtfsstopid=="301").sum(),(E.elevatormrn=="436").sum(),(E.stationcomplexid=="436").sum())
txt=E[E.alternativeroute.fillna("").str.contains(r"148 St|Harlem-148",regex=True)]; print("live equipment alt-route text mentioning 148 St:",txt[["station","equipmentno"]].values.tolist())
print("live equipment lines '3' stations:",sorted(E[E.trainno.fillna("").str.contains(r"\b3\b")]["station"].unique()))
h=hits(O,"live outages",["station","equipment","serving"]); print(h.to_string())
print("live equipment: stations north of 135 St on 3 line:",sorted(E[(E.elevatorsgtfsstopid.isin(["301","302","303","224"]))]["station"].unique()))
E.to_csv((S+"live_eq.csv"),index=False)
