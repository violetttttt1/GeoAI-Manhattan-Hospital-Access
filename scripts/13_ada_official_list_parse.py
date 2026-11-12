import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import re, html, pandas as pd
S=S
t=open(S+"mta_acc.html",errors="ignore").read()
q0=t.find("Quick Reference Station List"); q1=t.find("Full Station List")
sec=t[q0:q1]
parts=re.split(r"<h3>(.*?)</h3>",sec)   # [pre, name, body, name, body...]
off=[]
for nm,body in zip(parts[1::2],parts[2::2]):
    nm=html.unescape(nm).replace("\xa0"," ").strip()
    if nm=="Quick Reference Station List": continue
    for li in re.findall(r"<li[^>]*>(.*?)</li>",body,re.S):
        lines=re.findall(r'aria-label="subway line-(\w+)"',li)
        txt=html.unescape(re.sub(r"<[^>]+>"," ",li)).replace("\xa0"," "); txt=re.sub(r"\s+"," ",txt).strip()
        name=html.unescape(re.sub(r"<span.*","",li,flags=re.S)).replace("\xa0"," ").strip()
        off.append(dict(borough=nm,name=name,lines=",".join(l.upper() for l in lines),text=txt,
            note=("partial" if re.search(r"only|bound",txt,re.I) else "")))
off=pd.DataFrame(off); print(off.groupby("borough").size().to_dict(),len(off))
print(off[off.note!=""][["borough","name","lines","text"]].to_string())
off.to_csv(S+"official_ada.csv",index=False)
st=pd.read_csv((R+"mta_stations/mta_stations.csv"),dtype=str)
print(pd.crosstab(st.Borough,st.ADA,margins=True))
print(st[st.ADA=="2"][["Stop Name","Daytime Routes","Borough","ADA Northbound","ADA Southbound","ADA Notes"]].to_string())
print(st[st["ADA Notes"].notna()][["Stop Name","Borough","ADA","ADA Notes"]].head(20).to_string())
