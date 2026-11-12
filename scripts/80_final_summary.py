import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pandas as pd, numpy as np, pickle
O=O; S=S
C=pd.read_csv(O+"manhattan_clip_comparison.csv",dtype={"scenario":str}); RT=pd.read_csv(O+"manhattan_clip_ratios.csv")
MC=pd.read_csv(O+"mc_manhattan_summary_fixed.csv"); SG=pd.read_csv(O+"mc_manhattan_single_failure_fixed.csv")
_m=pd.read_csv(O+"mc_elevator_station_map.csv"); e2s=dict(zip(_m.elevator,_m.station))   # data/clean (exported from the final model)
D="reverse (arrive by)"; rows=[]
for h in ["Harlem Hospital","NYP/Columbia (CUIMC)","Mount Sinai Morningside"]:
    r={"hospital":h}
    x={s:C[(C.hospital==h)&(C.direction==D)&(C["mode"]=="mean_5times")&(C.scenario==s)].iloc[0] for s in "1234"}
    for s in "1234": r[f"S{s}_residents_reverse_5time_mean_Manhattan"]=round(x[s].res_after)
    for s in "1234": r[f"S{s}_residents_SD_over_5_times_reverse_Manhattan"]=round(x[s].res_after_sd)
    for s in "1234": r[f"S{s}_area_km2_reverse_5time_mean_Manhattan"]=round(x[s].area_after,2)
    g=lambda metric,col:RT[(RT.hospital==h)&(RT.direction==D)&(RT["mode"]=="mean_5times")&(RT.metric==metric)&(RT["clip"]=="after")][col].iloc[0]
    r["ADAshare_subway_S2_over_S1_residents_pct_reverse_5time_mean_Manhattan"]=round(g("residents","ratio_2_over_1"),1)
    r["ADAshare_subway+bus_S4_over_S3_residents_pct_reverse_5time_mean_Manhattan"]=round(g("residents","ratio_4_over_3"),1)
    r["ADAshare_subway_S2_over_S1_area_pct_reverse_5time_mean_Manhattan"]=round(g("area","ratio_2_over_1"),1)
    r["ADAshare_subway+bus_S4_over_S3_area_pct_reverse_5time_mean_Manhattan"]=round(g("area","ratio_4_over_3"),1)
    m=MC[(MC.hospital==h)&(MC.direction=="reverse")&(MC.model=="expanded")&(MC.fill=="mean")].iloc[0]
    r["MC_S4_baseline_no_outage_residents_reverse_0800_Manhattan"]=round(m.baseline_res)
    r["MC_S4_mean_residents_reverse_0800_Manhattan"]=round(m["mean"])
    r["MC_S4_P5_residents_reverse_0800_Manhattan"]=round(m.p5)
    r["MC_S4_coverage_prob_ge99pct_residents_reverse_0800_Manhattan"]=round(m.res_ge99)
    r["MC_S4_coverage_prob_ge90pct_residents_reverse_0800_Manhattan"]=round(m.res_ge90)
    st=SG[(SG.hospital==h)&(SG.direction=="reverse")&(SG.kind=="station")].sort_values("loss",ascending=False).iloc[0]
    el=SG[(SG.hospital==h)&(SG.direction=="reverse")&(SG.kind=="elevator")].sort_values("loss",ascending=False).iloc[0]
    r["worst_single_station_outage_reverse_0800"]=st["name"]; r["worst_station_loss_residents_Manhattan"]=round(st.loss); r["worst_station_loss_pct_of_MC_baseline"]=round(100*st.loss/m.baseline_res,1)
    r["worst_single_elevator_outage_reverse_0800"]=f"{el['item']} ({e2s.get(el['item'],'')})"; r["worst_elevator_loss_residents_Manhattan"]=round(el.loss); r["worst_elevator_loss_pct_of_MC_baseline"]=round(100*el.loss/m.baseline_res,1); r["worst_elevator_outage_probability_pct"]=round(100*el.p_out,1)
    rows.append(r)
F=pd.DataFrame(rows); F.to_csv(O+"final_summary.csv",index=False,encoding="utf-8-sig"); pd.set_option("display.width",260,"display.max_columns",60); print(F.T.to_string())
