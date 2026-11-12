import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import re, pandas as pd
S=S
off=pd.read_csv(S+"official_ada.csv",dtype=str).fillna("")
st=pd.read_csv((R+"mta_stations/mta_stations.csv"),dtype=str)
bmap={"Manhattan":"M","Brooklyn":"Bk","Queens":"Q","The Bronx":"Bx","Staten Island Railway":"SI"}
off["b"]=off.borough.map(bmap)
def nz(s): 
    s=s.lower().replace("street","st").replace("avenue","av"); s=re.sub(r"\(.*?\)","",s); return re.sub(r"[^a-z0-9]","",s)
off["nz"]=off.name.map(nz); off["rt"]=off.lines.map(lambda x:set(x.split(",")) if x else set())
ada=st[st.ADA.isin(["1","2"])].copy(); ada["nz"]=ada["Stop Name"].map(nz); ada["rt"]=ada["Daytime Routes"].map(lambda x:set(x.split()))
# per-borough counts
print("official entries by borough",off.groupby("b").size().to_dict()," | dataset ADA rows (1/2)",ada.groupby("Borough").size().to_dict(),"| ADA=1",st[st.ADA=="1"].groupby("Borough").size().to_dict())
print("official entries w/ partial note",off[off.note!=""].groupby("b").size().to_dict(),"| dataset ADA=2",st[st.ADA=="2"].groupby("Borough").size().to_dict())
# matching: official entry -> dataset ADA rows with same borough and (name equal) and route overlap
used=set(); rows=[]
for i,o in off.iterrows():
    c=ada[(ada.Borough==o.b)&(ada.nz==o.nz)]
    if len(c)==0: c=ada[(ada.Borough==o.b)&ada.nz.map(lambda x:len(o.nz)>3 and (x.startswith(o.nz) or o.nz.startswith(x)))]
    c2=c[c.rt.map(lambda r: bool(r&o.rt) if o.rt else True)]
    rows.append((i,list(c2.index)))
    used|=set(c2.index)
unm_o=[off.loc[i] for i,ix in rows if not ix]
print("official entries with NO dataset ADA row:",len(unm_o)); print(pd.DataFrame(unm_o)[["borough","name","lines","text"]].to_string())
un_d=ada[~ada.index.isin(used)]; print("dataset ADA rows not matched by any official entry:",len(un_d)); print(un_d[["Stop Name","Daytime Routes","Borough","ADA","GTFS Stop ID"]].to_string())
multi=[(off.loc[i,"name"],len(ix)) for i,ix in rows if len(ix)>1]; print("official entries mapping to >1 dataset rows:",len(multi))
# dataset rows whose official entry says not accessible
