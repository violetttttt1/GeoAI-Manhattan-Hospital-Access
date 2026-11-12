import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"mc_core.py")).read())
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.lines import Line2D
BUSF=prep_bus(8); BUSR=prep_bus("rev"); CFG={"reverse":(BUSR,-28800,True),"forward":(BUSF,28800,False)}
# per-station block frequency in the 1000 draws actually used
rng=np.random.default_rng(20261111); U=rng.random((1000,len(ELEVS))); up=U<p_up("mean"); freq={P:0 for P in STATIONS}; anyb=0
for k in range(1000):
    ok=station_ok(up[k]); b=False
    for P,d in ok.items():
        if not (d["PN"] and d["PS"]): freq[P]+=1; b=True
    anyb+=b
print("draws with >=1 station not fully accessible:",anyb,"| per-station counts of 1000:",{STATIONS[P]["name"]:c for P,c in freq.items()})
# share of reached ADA stations that are perturbed
nm=parents.stop_name.to_dict()
for h,ll in HOSP.items():
    st=origin_state(ll)
    for dn,(BUS,T0,rev) in CFG.items():
        base,_=run_cfg(st,BUS,T0,rev,set()); par={par_of[s] for i,s in enumerate(kids.stop_id) if base[i]<1e8}
        adapar={P for P in par if P in ADA}; pert={P for P in adapar if P in STATIONS}
        print(f"{h[:24]:24s} {dn:7s}: ADA stations reached {len(adapar)} | of which perturbed (in the 10-station model) {len(pert)} | not perturbed {len(adapar)-len(pert)}")
# coverage-probability maps
D=pickle.load(open(S+"mc_counts.pkl","rb")); counts=D["counts"]
HX=HOSP; band=[(1000,1000,"#9ecae1","P = 100%"),(990,999,"#fee391","99% - <100%"),(950,989,"#fdae61","95% - <99%"),(900,949,"#f46d43","90% - <95%"),(1,899,"#a50026","< 90%")]
ADAXY={P:(float(r.lat),float(r.lon)) for P,r in ST.set_index("gtfs_stop_id").iterrows()}
LAT0,LON0=40.80,-73.95; KX=111320*np.cos(np.radians(LAT0)); KY=110574
for dn in ("reverse","forward"):
    fig,axs=plt.subplots(1,3,figsize=(16.5,10.3))
    for ax,(h,ll) in zip(axs,HOSP.items()):
        C_,crop=counts[(h,dn)]; ok=np.argwhere(C_>0); r0,c0=ok.min(0); r1,c1=ok.max(0)+1; r0=max(r0-20,0); c0=max(c0-20,0); r1=min(r1+20,C_.shape[0]); c1=min(c1+20,C_.shape[1])
        ext=[gx0+c0*CELL,gx0+c1*CELL,gy1-r1*CELL,gy1-r0*CELL]; ax.set_facecolor("#e8f1f8")
        for lab,poly in BORO_POLYS: ax.add_patch(MPoly(poly,closed=True,fc="#f2f2f2",ec="#a5a5a5",lw=0.4))
        img=np.zeros((r1-r0,c1-c0,4))
        for lo,hi,col,_ in band:
            m=(C_[r0:r1,c0:c1]>=lo)&(C_[r0:r1,c0:c1]<=hi); img[m]=matplotlib.colors.to_rgba(col,0.95)
        ax.imshow(img,extent=ext,origin="upper",interpolation="nearest",zorder=3)
        for P,(la,lo) in ADAXY.items():
            if P in STATIONS and STATIONS[P]["paths"]: ax.plot((lo-LON0)*KX,(la-LAT0)*KY,"^",ms=6,color="#1b7f3b",mec="white",mew=0.5,zorder=6)
        ax.plot((ll[1]-LON0)*KX,(ll[0]-LAT0)*KY,"*",ms=14,color="#d62728",mec="white",mew=0.8,zorder=9)
        ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        row=pd.read_csv(O+"mc_scenario4_summary.csv"); row=row[(row.hospital==h)&(row.direction==dn)&(row.fill=="mean")].iloc[0]
        ax.set_title(f"{h}\nbaseline {row.baseline_residents/1000:.1f}k residents | P>=90%: {row.res_ge90/1000:.1f}k | P>=99%: {row.res_ge99/1000:.1f}k",fontsize=9.5)
    leg=[Line2D([0],[0],marker="s",ls="",color=c,ms=10,label=l) for _,_,c,l in band]+[Line2D([0],[0],marker="^",ls="",color="#1b7f3b",ms=8,label="perturbed ADA station (10-station model)"),Line2D([0],[0],marker="*",ls="",color="#d62728",ms=12,label="hospital")]
    fig.legend(handles=leg,loc="lower center",ncol=7,fontsize=8.5,frameon=False,title="Probability that a location is inside the scenario-4 isochrone (1000 elevator-outage draws)",title_fontsize=9)
    fig.suptitle(f"Scenario 4 (ADA subway + bus), {'arrive by 08:00 (reverse)' if dn=='reverse' else 'depart 08:00 (forward)'}: coverage probability under random elevator outages",fontsize=12.5,y=0.99)
    fig.text(0.5,0.075,"Elevators drawn independently from 12-month 24h availability (station_table / elevator_detail); only the 10 study-area ADA stations are perturbed, all other ADA stations assumed always up. Land only, 100 m street buffer.",ha="center",fontsize=7,color="#444")
    fig.tight_layout(rect=(0,0.11,1,0.96)); fig.savefig(O+f"mc_scenario4_coverage_{dn}.png",dpi=120); plt.close(fig); print("saved",dn)
