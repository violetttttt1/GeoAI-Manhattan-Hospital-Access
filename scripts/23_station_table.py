import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import itertools, numpy as np, pandas as pd
exec(open((S+"study.py")).read().split("# ===== 1 elevators")[0])
OUT=REB   # rebuilt copies go to data/cache/rebuilt, never over data/clean
st=rd("mta_stations/mta_stations.csv"); st["lat"]=st["GTFS Latitude"].astype(float); st["lon"]=st["GTFS Longitude"].astype(float)
nb,hb,ia,parts=area(st.lat,st.lon); st["inarea"]=ia&(st.Borough=="M").values
st["why"]=[("north_of_110St" if n else "")+(";" if n and h else "")+("hospital_400m:"+"/".join(k for k in parts if parts[k][i]) if h else "") for i,(n,h) in enumerate(zip(nb,hb))]
ada=st[st.inarea&st.ADA.isin(["1","2"])].copy(); assert ada["Station ID"].is_unique; print("ADA stations in area",len(ada))
# ---- elevators
ie=inv[inv["Elevator or Escalator"]=="Elevator"].copy(); ie["sid"]=ie["Station MRN"].str.lstrip("0")
ie["lat"]=ie["X Coordinate"].astype(float); ie["lon"]=ie["Y Coordinate"].astype(float)
nb2,hb2,ia2,_=area(ie.lat,ie.lon); ie["in_study_area"]=ia2&(ie.Borough=="Manhattan").values
# ---- availability, last 12 months
av["m"]=pd.to_datetime(av.Month); last=av.m.max(); start=last-pd.DateOffset(months=11); print("window",start.date(),last.date())
w=av[(av["Equipment Type"]=="Elevator")&(av.m>=start)].copy()
for c in ["24-Hour Hours Available","24-Hour Total Hours","AM Peak Hours Available","AM Peak Total Hours","PM Peak Hours Available","PM Peak Total Hours","Unscheduled Outages","Total Outages"]: w[c]=pd.to_numeric(w[c])
g=w.groupby("Equipment Code")
import warnings; warnings.filterwarnings('ignore')
M=pd.DataFrame({"months_in_window":g.apply(lambda d:int((d["24-Hour Total Hours"]>0).sum())),
 "avail_24h_12m":g.apply(lambda d:d["24-Hour Hours Available"].sum()/d["24-Hour Total Hours"].sum() if d["24-Hour Total Hours"].sum()>0 else np.nan),
 "avail_am_peak_12m":g.apply(lambda d:d["AM Peak Hours Available"].sum()/d["AM Peak Total Hours"].sum() if d["AM Peak Total Hours"].sum()>0 else np.nan),
 "avail_pm_peak_12m":g.apply(lambda d:d["PM Peak Hours Available"].sum()/d["PM Peak Total Hours"].sum() if d["PM Peak Total Hours"].sum()>0 else np.nan),
 "unscheduled_outages_12m":g["Unscheduled Outages"].sum(),"total_outages_12m":g["Total Outages"].sum()})
ever=set(av[av["Equipment Type"]=="Elevator"]["Equipment Code"])
ie=ie.merge(M,left_on="Equipment Code",right_index=True,how="left")
ie["avail_status"]=np.where(ie.avail_24h_12m.notna(),"已知",np.where(ie["Equipment Code"].isin(ever),"未知(近12月无数据)","未知(无任何记录)"))
# fill values from study-area elevators with known availability
sa=ie[ie.in_study_area&ie.avail_24h_12m.notna()]; FILL_MEAN=sa.avail_24h_12m.mean(); FILL_LOW=sa.avail_24h_12m.quantile(0.10)
print("study-area elevators",ie.in_study_area.sum(),"known",len(sa),"mean fill %.4f p10 fill %.4f min %.4f median %.4f"%(FILL_MEAN,FILL_LOW,sa.avail_24h_12m.min(),sa.avail_24h_12m.median()))
# ---- the 6 without station info
six=ie[ie.in_study_area&ie.sid.isna()].copy(); print("no-station elevators in area",list(six["Equipment Code"]))
ada_ids=set(ada["Station ID"])
rows6=[]
for _,r in six.iterrows():
    d=hav(st.lat,st.lon,r.lat,r.lon); o=np.argsort(d); da=hav(ada.lat,ada.lon,r.lat,r.lon); oa=np.argsort(da)
    rows6.append(dict(equipment_code=r["Equipment Code"],lat=r.lat,lon=r.lon,asset_class=r["Asset Class"],notes=r["Notes"],service_status=r["Service Status"],maintained_by=r["Maintained By"],
      installed=r["Original Installation Date"],avail_status=r.avail_status,
      nearest_station_id=st.iloc[o[0]]["Station ID"],nearest_station=st.iloc[o[0]]["Stop Name"]+" ("+st.iloc[o[0]]["Daytime Routes"]+")",nearest_station_ada=st.iloc[o[0]]["ADA"],nearest_dist_m=round(d[o[0]]),
      second_station=st.iloc[o[1]]["Stop Name"]+" ("+st.iloc[o[1]]["Daytime Routes"]+")",second_dist_m=round(d[o[1]]),
      nearest_ada_station=ada.iloc[oa[0]]["Stop Name"]+" ("+ada.iloc[oa[0]]["Daytime Routes"]+")",nearest_ada_dist_m=round(da[oa[0]])))
six_df=pd.DataFrame(rows6); six_df.to_csv(OUT+"elevators_assigned_by_coordinates.csv",index=False,encoding="utf-8-sig"); print(six_df[["equipment_code","notes","nearest_station","nearest_dist_m","nearest_ada_station","nearest_ada_dist_m"]].to_string())
# ---- network model
def landings(r):
    n=set()
    if r["Street Access"]=="YES": n.add("Street")
    if r["Elevator Mezzanine 1 Access"]=="+": n.add("M1")
    if r["Elevator Mezzanine 2 Access"]=="+": n.add("M2")
    if r["Elevator Platform Access"]=="+":
        d=r["Elevator Direction Serviced"]
        n|={"Both":{"PN","PS"},"Northbound":{"PN"},"Southbound":{"PS"}}.get(d,set())
    return n
def connected(edges,states,a,b_list):
    par={}
    def f(x):
        par.setdefault(x,x)
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for (code,nodes),up in zip(edges,states):
        if up:
            nl=list(nodes)
            for x in nl[1:]: par[f(x)]=f(nl[0])
    return all(f(a)==f(b) for b in b_list)
def analyse(edges,entr,targets,p):
    k=len(edges); tot=0.0
    for st_ in itertools.product([0,1],repeat=k):
        if connected(edges,st_,entr,targets):
            pr_=1.0
            for (c,_),u in zip(edges,st_): pr_*= p[c] if u else 1-p[c]
            tot+=pr_
    return tot
def min_paths(edges,entr,target):
    found=[]
    for r_ in range(1,len(edges)+1):
        for comb in itertools.combinations(range(len(edges)),r_):
            if any(set(f_)<=set(comb) for f_ in found): continue
            if connected([edges[i] for i in comb],[1]*r_,entr,[target]): found.append(comb)
    return " | ".join("+".join(edges[i][0] for i in c) for c in found)
srows=[]; erows=[]
for _,s in ada.sort_values(["lat"],ascending=False).iterrows():
    L=ie[ie.sid==s["Station ID"]].copy(); notes=[]
    edges=[];unplaced=[]
    for _,e in L.iterrows():
        nl=landings(e); ok=len(nl)>=2 and not str(e["Service Status"]).startswith("Removed")
        reason="" if ok else ("无出入口层级字段，无法确定在通道中的位置" if len(nl)<2 else "已拆除")
        if ok: edges.append((e["Equipment Code"],frozenset(nl)))
        else: unplaced.append((e["Equipment Code"],reason,e.Notes))
        erows.append((e["Equipment Code"],s["Station ID"],ok,reason,sorted(nl)))
    edges.sort(key=lambda x:x[0])
    dirs=[d for d,fl in (("PN","ADA Northbound"),("PS","ADA Southbound")) if s[fl]=="1"]
    entr=None
    if edges:
        allnodes=set().union(*[n for _,n in edges])
        if "Street" in allnodes: entr="Street"
        else: entr="M2" if "M2" in allnodes else "M1"; notes.append(f"清单中无街面直达电梯，入口按推断设为{entr}（地面入口进入最外层夹层）")
        miss=[d for d in dirs if d not in allnodes]
        if miss: notes.append(f"{'/'.join(miss)} 站台无电梯可达")
    ks=L[L["Equipment Code"].isin([c for c,_ in edges])].set_index("Equipment Code")
    status={c:ks.loc[c,"avail_status"] for c,_ in edges}; av12={c:ks.loc[c,"avail_24h_12m"] for c,_ in edges}
    p_mean={c:(av12[c] if status[c]=="已知" else FILL_MEAN) for c,_ in edges}; p_low={c:(av12[c] if status[c]=="已知" else FILL_LOW) for c,_ in edges}
    if edges and not [d for d in dirs if d not in allnodes]:
        pm=analyse(edges,entr,dirs,p_mean); pl=analyse(edges,entr,dirs,p_low)
        paths="; ".join(f"{d}: "+min_paths(edges,entr,d) for d in dirs)
    else: pm=pl=np.nan; paths=""
    if not len(L): notes.append("资产清单中没有任何电梯可对应到该站")
    if unplaced: notes.append("已关联但未纳入计算："+"; ".join(f"{c}({r}; {n})" for c,r,n in unplaced))
    nunk=sum(1 for c,_ in edges if status[c]!="已知")
    short=[f"{c}({int(ks.loc[c,'months_in_window'])}个月)" for c,_ in edges if status[c]=="已知" and ks.loc[c,"months_in_window"]<12]
    if short: notes.append("近12个月数据不足12个月，可用率与停运次数只覆盖部分月份："+"; ".join(short))
    if nunk: notes.append("有 %d 部电梯无可用率，概率为补值结果"%nunk)
    if s["Station ID"]=="143": notes.append("车辆段电梯 EL147/150/151/152/153/155 离本站最近(319–575m)，见 elevators_assigned_by_coordinates.csv；它们不是站内通道，未纳入")
    fmt=lambda f_:";".join(f_(c) for c,_ in edges)
    pe=lambda c: f"{av12[c]:.4f}" if status[c]=="已知" else "未知"
    srows.append(dict(station_id=s["Station ID"],gtfs_stop_id=s["GTFS Stop ID"],complex_id=s["Complex ID"],station_name=s["Stop Name"],line=s["Line"],routes=s["Daytime Routes"],
      ada=s.ADA,ada_northbound=s["ADA Northbound"],ada_southbound=s["ADA Southbound"],north_label=s["North Direction Label"],south_label=s["South Direction Label"],lat=s.lat,lon=s.lon,in_area_reason=s.why,
      n_elevators_linked=len(L),n_elevators_in_model=len(edges),n_unknown_avail=nunk,
      elevator_codes=fmt(lambda c:c),
      elevator_locations=fmt(lambda c:f"{c}@{ks.loc[c,'lat']:.5f},{ks.loc[c,'lon']:.5f}"),
      elevator_roles=fmt(lambda c:f"{c}:{'-'.join(n for n in ['Street','M2','M1','PN','PS'] if n in dict(edges)[c])}"),
      elevator_avail_status=fmt(lambda c:f"{c}={status[c]}"),
      elevator_avail_24h_12m=fmt(lambda c:f"{c}={pe(c)}"),
      elevator_unsched_outages_12m=fmt(lambda c:f"{c}="+(str(int(ks.loc[c,'unscheduled_outages_12m'])) if status[c]=="已知" else "未知")),
      access_paths=paths,station_prob_mean_fill=pm,station_prob_low_fill=pl,fill_mean_used=round(FILL_MEAN,4),fill_low_used=round(FILL_LOW,4),
      needs_review="是" if notes else "否",review_note=" | ".join(notes)))
T=pd.DataFrame(srows); 
for c in ["station_prob_mean_fill","station_prob_low_fill"]: T[c]=T[c].round(4)
T.to_csv(OUT+"station_table.csv",index=False,encoding="utf-8-sig")
pd.set_option("display.width",250,"display.max_colwidth",70)
print(T[["station_id","station_name","routes","ada_northbound","ada_southbound","n_elevators_linked","n_elevators_in_model","n_unknown_avail","station_prob_mean_fill","station_prob_low_fill"]].to_string())
print(T[["station_name","elevator_avail_24h_12m","elevator_unsched_outages_12m","access_paths"]].to_string())
print(T[["station_name","review_note"]].to_string())
# ---- elevator_detail
sidmap=dict(zip(ada["Station ID"],ada["Stop Name"]+" ("+ada["Daytime Routes"]+")"))
placed={c:(ok,rs,nl) for c,sid,ok,rs,nl in erows}
D=ie[ie.in_study_area|ie.sid.isin(ada_ids)].copy()
D["linked_station_id"]=D.sid; D["link_method"]=np.where(D.sid.notna(),"Station MRN",np.where(D["Equipment Code"].isin(six_df.equipment_code),"最近车站(按坐标)","无"))
D["linked_station"]=D.sid.map(lambda x:sidmap.get(x,"")) 
nm=st.set_index("Station ID")
D["linked_station"]=[ (nm.loc[x,"Stop Name"]+" ("+nm.loc[x,"Daytime Routes"]+")") if isinstance(x,str) and x in nm.index else "" for x in D.sid]
D.loc[D.link_method=="最近车站(按坐标)","linked_station_id"]=D["Equipment Code"].map(dict(zip(six_df.equipment_code,six_df.nearest_station_id)))
D.loc[D.link_method=="最近车站(按坐标)","linked_station"]=D["Equipment Code"].map(dict(zip(six_df.equipment_code,six_df.nearest_station)))
D["station_is_ada_in_table"]=D.sid.isin(ada_ids)
D["in_probability_model"]=D["Equipment Code"].map(lambda c:placed.get(c,(False,"",""))[0]); D["model_exclusion_reason"]=D["Equipment Code"].map(lambda c:placed.get(c,(False,"车站不在 ADA 车站表中",""))[1])
keep=["Equipment Code","linked_station_id","linked_station","link_method","station_is_ada_in_table","in_study_area","lat","lon","Street Access","Elevator Direction Serviced","Elevator Mezzanine 1 Access","Elevator Mezzanine 2 Access","Elevator Platform Access","Redundant Elevator","Notes","Service Status","Maintained By","ADA Compliant","avail_status","months_in_window","avail_24h_12m","avail_am_peak_12m","avail_pm_peak_12m","unscheduled_outages_12m","total_outages_12m","in_probability_model","model_exclusion_reason"]
D[keep].sort_values(["linked_station_id","Equipment Code"]).to_csv(OUT+"elevator_detail.csv",index=False,encoding="utf-8-sig")
print("elevator_detail rows",len(D),"| in model",D.in_probability_model.sum(),"| ada-linked",D.station_is_ada_in_table.sum())
print("months_in_window<12 among known in model:",D[D.in_probability_model&(D.avail_status=="已知")&(D.months_in_window<12)][["Equipment Code","months_in_window"]].values.tolist())
# link sanity: elevator distance to its station
dd=[hav(nm.loc[r.sid,"lat"],nm.loc[r.sid,"lon"],r.lat,r.lon) for _,r in D[D.station_is_ada_in_table].iterrows()] if False else None
