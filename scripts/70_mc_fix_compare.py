import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pandas as pd, numpy as np
O=O; S=S
A=pd.read_csv(O+"mc_manhattan_summary.csv"); B=pd.read_csv(O+"mc_manhattan_summary_fixed.csv"); SGb=pd.read_csv(O+"mc_manhattan_single_failure_fixed.csv")
short={"Harlem Hospital":"Harlem","NYP/Columbia (CUIMC)":"NYP/Columbia","Mount Sinai Morningside":"Mount Sinai"}; dn={"reverse":"reverse","forward":"forward"}
a=A[(A.model=="expanded")&(A.fill=="mean")].set_index(["hospital","direction"]); b=B[(B.model=="expanded")&(B.fill=="mean")].set_index(["hospital","direction"]); bl=B[(B.model=="expanded")&(B.fill=="low")].set_index(["hospital","direction"])
print("fill variants identical in fixed run? max abs diff:",(b[["mean","p5","res_ge90","res_ge99","res_ge100","draws_with_loss"]]-bl[["mean","p5","res_ge90","res_ge99","res_ge100","draws_with_loss"]]).abs().max().round(3).to_dict(),"| draws with station block mean/low:",int(b.draws_with_station_block.iloc[0]),int(bl.draws_with_station_block.iloc[0]))
rows=["| Hospital / direction | Baseline before→after | Mean before→after | 5th percentile before→after | ≥99% before→after | Worst-5% mean before→after | Draws with loss before→after |","|---|---|---|---|---|---|---|"]
for h in short:
    for d in ("reverse","forward"):
        x=a.loc[(h,d)]; y=b.loc[(h,d)]
        rows.append(f"| {short[h]} {dn[d]} | {x.baseline_res:,.0f} → {y.baseline_res:,.0f} | {x['mean']:,.0f} → {y['mean']:,.0f} | {x.p5:,.0f} → **{y.p5:,.0f}** | {x.res_ge99:,.0f} → **{y.res_ge99:,.0f}** | {x.worst5_mean:,.0f} → {y.worst5_mean:,.0f} | {int(x.draws_with_loss)} → {int(y.draws_with_loss)} |")
open(S+"tbl_fix_cmp.md","w").write("\n".join(rows)); print("\n".join(rows))
print("\nfixed-run detail:")
for h in short:
    for d in ("reverse","forward"):
        y=b.loc[(h,d)]; B0=y.baseline_res
        print(f"{short[h]:12s} {d:7s} base {B0:7.0f} mean {y['mean']:7.0f} ({100*y['mean']/B0:.1f}%) sd {y.sd:6.0f} p5 {y.p5:7.0f} ({100*y.p5/B0:.0f}%) worst5 {y.worst5_mean:7.0f} ({100*y.worst5_mean/B0:.0f}%) min {y['min']:7.0f} | >=90 {y.res_ge90:7.0f} ({100*y.res_ge90/B0:.1f}%) >=95 {y.res_ge95:7.0f} ({100*y.res_ge95/B0:.1f}%) >=97 {y.res_ge97:7.0f} >=99 {y.res_ge99:7.0f} ({100*y.res_ge99/B0:.1f}%) =100 {y.res_ge100:7.0f} ({100*y.res_ge100/B0:.1f}%) | blocked {int(y.draws_with_station_block)} loss {int(y.draws_with_loss)} uniq {int(y.unique_configs)} stations {int(y.n_perturbed_stations)} elev {int(y.n_perturbed_elevators)}")
Z=B[B.model=="expanded_avail=1"].set_index(["hospital","direction"]); ok=all(abs(r["mean"]-r.baseline_res)<1e-6 and r.sd<1e-6 and abs(r["min"]-r.baseline_res)<1e-6 and abs(r.res_ge100-r.baseline_res)<1e-6 and r.unique_configs==1 and r.draws_with_loss==0 and r.draws_with_station_block==0 for _,r in Z.iterrows()); print("\navailability=1 check on fixed model, all 6 pass:",ok,"| max SD:",Z.sd.max())
T10=B[(B.model=="10-station")&(B.fill=="mean")].set_index(["hospital","direction"]); T10o=A[(A.model=="10-station")&(A.fill=="mean")].set_index(["hospital","direction"]); print("10-station results identical between the two runs:",bool(((T10[["mean","p5","res_ge99"]]-T10o[["mean","p5","res_ge99"]]).abs().max()<1e-6).all()))
print("\nsingle-station top 3 (fixed):")
for h in short:
    for d in ("reverse","forward"):
        x=SGb[(SGb.hospital==h)&(SGb.direction==d)&(SGb.kind=="station")].sort_values("loss",ascending=False).head(3); print(f"{short[h]:12s} {d:7s}",[(r["name"],round(r["loss"])) for _,r in x.iterrows() if r["loss"]>0.5])
for h in short:
    for d in ("reverse","forward"):
        y=SGb[(SGb.hospital==h)&(SGb.direction==d)&(SGb.kind=="elevator")].copy(); y["exp"]=y.p_out*y.loss; print(f"{short[h]:12s} {d:7s} top elevators by loss:",[(r["item"],round(r["loss"]),f"p={100*r.p_out:.1f}%") for _,r in y.sort_values("loss",ascending=False).head(3).iterrows()],"| by expected:",[(r["item"],round(r["exp"])) for _,r in y.sort_values("exp",ascending=False).head(3).iterrows()])
