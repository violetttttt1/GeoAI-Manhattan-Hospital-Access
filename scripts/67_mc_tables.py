import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pandas as pd, numpy as np
O=O; S=S
M=pd.read_csv(O+"mc_manhattan_summary.csv"); SG=pd.read_csv(O+"mc_manhattan_single_failure.csv"); MOD=pd.read_csv(O+"mc_station_model.csv")
short={"Harlem Hospital":"Harlem","NYP/Columbia (CUIMC)":"NYP/Columbia","Mount Sinai Morningside":"Mount Sinai"}; dname={"reverse":"反向","forward":"正向"}
pd.set_option("display.width",250,"display.max_columns",60)
E=M[(M.model=="expanded")]
print("== fill variants identical? max abs diff of key stats between mean and low fill")
a=E[E.fill=="mean"].set_index(["hospital","direction"]); b=E[E.fill=="low"].set_index(["hospital","direction"])
cols=["mean","sd","p5","worst5_mean","min","res_ge90","res_ge95","res_ge97","res_ge99","res_ge100","draws_with_loss"]
print((a[cols]-b[cols]).abs().max().round(3).to_dict()); print("draws with station block mean/low:",a.draws_with_station_block.to_dict(),b.draws_with_station_block.to_dict())
print("\n== expanded model, mean fill")
rows=["| 医院 / 方向 | 基线（无停运） | 均值 | SD | **第 5 百分位** | 最差 5% 的均值 | 最小 | ≥ 90% | ≥ 95% | ≥ 97% | ≥ 99% | = 100% | 有损失的次数 |","|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for h in short:
    for dn in ("reverse","forward"):
        r=a.loc[(h,dn)]; B=r.baseline_res
        rows.append(f"| {short[h]} {dname[dn]} | {B:,.0f} | {r['mean']:,.0f}（{100*r['mean']/B:.1f}%） | {r.sd:,.0f} | **{r.p5:,.0f}**（{100*r.p5/B:.0f}%） | {r.worst5_mean:,.0f}（{100*r.worst5_mean/B:.0f}%） | {r['min']:,.0f}（{100*r['min']/B:.0f}%） | {r.res_ge90:,.0f}（{100*r.res_ge90/B:.1f}%） | {r.res_ge95:,.0f}（{100*r.res_ge95/B:.1f}%） | {r.res_ge97:,.0f}（{100*r.res_ge97/B:.1f}%） | {r.res_ge99:,.0f}（{100*r.res_ge99/B:.1f}%） | {r.res_ge100:,.0f}（{100*r.res_ge100/B:.1f}%） | {int(r.draws_with_loss)} |")
open(S+"tbl_mc_main.md","w").write("\n".join(rows)); print("\n".join(rows))
rows=["| 医院 / 方向 | 至少一个站被堵的次数 | 有居民损失的次数 | 独立重算次数 | 参与扰动的站 / 电梯 | 面积 ≥90%（km²） | 面积 ≥99%（km²） | 面积 =100%（km²） | 基线面积（km²） |","|---|---|---|---|---|---|---|---|---|"]
for h in short:
    for dn in ("reverse","forward"):
        r=a.loc[(h,dn)]; rows.append(f"| {short[h]} {dname[dn]} | {int(r.draws_with_station_block)} | {int(r.draws_with_loss)} | {int(r.unique_configs)} | {int(r.n_perturbed_stations)} / {int(r.n_perturbed_elevators)} | {r.area_ge90:.2f} | {r.area_ge99:.2f} | {r.area_ge100:.2f} | {r.baseline_area:.2f} |")
open(S+"tbl_mc_area.md","w").write("\n".join(rows))
print("\n== CHECK availability = 1")
Z=M[M.model=="expanded_avail=1"].set_index(["hospital","direction"]); rows=["| 医院 / 方向 | 基线 | 1000 次均值 | SD | 最小 | ≥ 99% 的居民 | = 100% 的居民 | 独立重算次数 | 有损失的次数 | 至少一站被堵的次数 | 通过 |","|---|---|---|---|---|---|---|---|---|---|---|"]; allok=True
for h in short:
    for dn in ("reverse","forward"):
        r=Z.loc[(h,dn)]; ok=(abs(r["mean"]-r.baseline_res)<1e-6 and r.sd<1e-6 and abs(r["min"]-r.baseline_res)<1e-6 and abs(r.res_ge100-r.baseline_res)<1e-6 and r.unique_configs==1 and r.draws_with_loss==0 and r.draws_with_station_block==0); allok&=ok
        rows.append(f"| {short[h]} {dname[dn]} | {r.baseline_res:,.2f} | {r['mean']:,.2f} | {r.sd:.2g} | {r['min']:,.2f} | {r.res_ge99:,.2f} | {r.res_ge100:,.2f} | {int(r.unique_configs)} | {int(r.draws_with_loss)} | {int(r.draws_with_station_block)} | {'是' if ok else '**否**'} |")
open(S+"tbl_mc_check1.md","w").write("\n".join(rows)); print("\n".join(rows)); print("ALL PASS:",allok)
print("\n== 10-station model vs expanded (mean fill)")
T10=M[(M.model=="10-station")&(M.fill=="mean")].set_index(["hospital","direction"]); rows=["| 医院 / 方向 | 基线 | 10 站：均值 / P5 / ≥90% / ≥99% | 扩展：均值 / P5 / ≥90% / ≥99% |","|---|---|---|---|"]
for h in short:
    for dn in ("reverse","forward"):
        x=T10.loc[(h,dn)]; y=a.loc[(h,dn)]; f=lambda r:f"{r['mean']:,.0f} / {r.p5:,.0f} / {r.res_ge90:,.0f} / {r.res_ge99:,.0f}"
        rows.append(f"| {short[h]} {dname[dn]} | {y.baseline_res:,.0f} | {f(x)} | {f(y)} |")
open(S+"tbl_mc_cmp10.md","w").write("\n".join(rows)); print("\n".join(rows))
print("\n== engine regression: 10-station UNclipped mean/p5 vs earlier chapter (mc_scenario4_summary.csv, mean fill)")
old=pd.read_csv(O+"mc_scenario4_summary.csv"); old=old[old.fill=="mean"].set_index(["hospital","direction"]); rows=[]
for h in short:
    for dn in ("reverse","forward"):
        x=T10.loc[(h,dn)]; o=old.loc[(h,dn)]; rows.append((short[h],dn,round(x.baseline_res_before_clip),round(o.baseline_residents),round(x.mean_before_clip,1),round(o.mc_mean,1),round(x.p5_before_clip),round(o.mc_p5)))
print(pd.DataFrame(rows,columns=["hospital","dir","baseline_new","baseline_old","mean_new","mean_old","p5_new","p5_old"]).to_string(index=False))
print("\n== single failures: top station and elevator per hospital/direction (clipped residents lost)")
rows_s=["| 医院 / 方向 | 基线 | 一停损失最大的车站（损失，占基线） | 其次 | 第三 |","|---|---|---|---|---|"]; rows_e=["| 医院 / 方向 | 单独停运损失最大的电梯（损失，占基线，停运概率） | 按\"停运概率 × 损失\"排序的前三（期望损失） |","|---|---|---|"]
for h in short:
    for dn in ("reverse","forward"):
        B=a.loc[(h,dn)].baseline_res; x=SG[(SG.hospital==h)&(SG.direction==dn)&(SG.kind=="station")].sort_values("loss",ascending=False); t=[f"{r['name']}（{r['loss']:,.0f}，{100*r['loss']/B:.0f}%）" for _,r in x.head(3).iterrows() if r["loss"]>0.5]
        t+= [""]*(3-len(t)); rows_s.append(f"| {short[h]} {dname[dn]} | {B:,.0f} | "+" | ".join(t)+" |")
        y=SG[(SG.hospital==h)&(SG.direction==dn)&(SG.kind=="elevator")].copy(); y["exp"]=y.p_out*y.loss; top=y.sort_values("loss",ascending=False).iloc[0]; ex=y.sort_values("exp",ascending=False).head(3)
        rows_e.append(f"| {short[h]} {dname[dn]} | {top['item']}（{top['loss']:,.0f}，{100*top['loss']/B:.0f}%，p={100*top.p_out:.1f}%） | "+"；".join(f"{r['item']}（{r['exp']:,.0f}）" for _,r in ex.iterrows())+" |")
open(S+"tbl_mc_single_station.md","w").write("\n".join(rows_s)); open(S+"tbl_mc_single_elev.md","w").write("\n".join(rows_e)); print("\n".join(rows_s)); print("\n".join(rows_e))
# overall max
ov=SG[SG.kind=="station"].sort_values("loss",ascending=False).head(5); print("\nlargest single-station losses overall:"); print(ov[["hospital","direction","name","loss"]].round(0).to_string(index=False))
ovE=SG[SG.kind=="elevator"].sort_values("loss",ascending=False).head(5); print("largest single-elevator losses overall:"); print(ovE[["hospital","direction","item","loss","p_out"]].round(3).to_string(index=False))
print("\nstations whose single failure matters (loss>0) among modelled, per combo:"); print(SG[(SG.kind=="station")].groupby(["hospital","direction"]).apply(lambda d:(d.loss>0.5).sum()).to_string())
