import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pickle, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.lines import Line2D
S=S; O=O
D=pickle.load(open(S+"iso3_masks.pkl","rb")); masks=D["masks"]; x0,y1,CELL=D["x0"],D["y1"],D["CELL"]
T=pd.read_csv(O+"hospital_isochrone_summary.csv",dtype={"scenario":str})
C={"1":(0.99,0.72,0.35),"3":(0.84,0.25,0.12),"2":(0.45,0.62,0.82),"4":(0.05,0.45,0.42)}
SLUG={"Harlem Hospital":"harlem","NYP/Columbia (CUIMC)":"nyp_columbia","Mount Sinai Morningside":"mt_sinai_morningside"}
HX={"Harlem Hospital":(40.8147102,-73.9392782),"NYP/Columbia (CUIMC)":(40.8409780,-73.9407016),"Mount Sinai Morningside":(40.8052373,-73.9613875)}
LAT0,LON0=40.80,-73.95; KX=111320*np.cos(np.radians(LAT0)); KY=110574
for h in HX:
    keys={s:(h,"fwd0800",s in "34",s in "24") for s in "1234"}; keys["w"]=(h,"walk",False,False)
    r0=min(masks[k][1][0] for k in keys.values()); r1=max(masks[k][1][1] for k in keys.values()); c0=min(masks[k][1][2] for k in keys.values()); c1=max(masks[k][1][3] for k in keys.values())
    def canvas(k):
        m,(a,b,c,d)=masks[k]; Z=np.zeros((r1-r0,c1-c0),bool); Z[a-r0:b-r0,c-c0:d-c0]=m; return Z
    cv={s:canvas(k) for s,k in keys.items()}; ext=[x0+c0*CELL,x0+c1*CELL,y1-r1*CELL,y1-r0*CELL]; Wm,Hm=ext[1]-ext[0],ext[3]-ext[2]
    fig_h=float(np.clip(4.15*Hm/Wm+2.3,6.2,11.5)); fig,axs=plt.subplots(1,4,figsize=(16.5,fig_h))
    row=lambda s:T[(T.hospital==h)&(T["mode"]=="fwd0800")&(T.scenario==s)&(T.buffer_m==100)].iloc[0]
    r1_=row("1")
    titles={"1":"① Subway, anyone","2":"② Subway, ADA stations only","3":"③ Subway + bus, anyone","4":"④ Subway + bus, ADA subway only"}
    base={"1":None,"2":None,"3":"1","4":"2"}
    for ax,s in zip(axs,"1234"):
        r=row(s); ax.set_facecolor("#e8f1f8")
        for lab,poly in D["boro"]: ax.add_patch(MPoly(poly,closed=True,fc="#f2f2f2",ec="#a5a5a5",lw=0.4))
        ax.imshow(np.where(cv[s][...,None],np.array(list(C[s])+[0.9]),0),extent=ext,origin="upper",interpolation="nearest",zorder=3)
        if base[s]: ax.imshow(np.where(cv[base[s]][...,None],np.array(list(C[base[s]])+[0.95]),0),extent=ext,origin="upper",interpolation="nearest",zorder=4)
        ax.contour(np.linspace(ext[0],ext[1],c1-c0),np.linspace(ext[3],ext[2],r1-r0),cv["w"].astype(float),levels=[0.5],colors="k",linewidths=0.6,linestyles="--",zorder=5)
        la,lo=HX[h]; ax.plot((lo-LON0)*KX,(la-LAT0)*KY,"*",ms=14,color="#d62728",mec="white",mew=0.8,zorder=9)
        ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{titles[s]}\n{r.area_land_km2:.1f} km² land ({100*r.area_land_km2/r1_.area_land_km2:.0f}% of ①)\nManhattan {r.area_manhattan_km2:.1f} | other boroughs {r.area_other_boroughs_km2:.1f}\n{r.amb_pop/1000:.1f}k residents w/ ambulatory difficulty",fontsize=8.8)
    wk=T[(T.hospital==h)&(T["mode"]=="walk")&(T.buffer_m==100)].iloc[0]
    leg=[Line2D([0],[0],marker="s",ls="",color=C["1"],ms=10,label="Subway (anyone)"),Line2D([0],[0],marker="s",ls="",color=C["3"],ms=10,label="Added by bus (anyone)"),Line2D([0],[0],marker="s",ls="",color=C["2"],ms=10,label="ADA subway stations only"),Line2D([0],[0],marker="s",ls="",color=C["4"],ms=10,label="Added by bus (after ADA subway)"),Line2D([0],[0],ls="--",color="k",lw=1,label=f"Walking only ({wk.area_land_km2:.1f} km²)"),Line2D([0],[0],marker="*",ls="",color="#d62728",ms=12,label=h)]
    fig.legend(handles=leg,loc="lower center",ncol=6,fontsize=8.3,frameon=False)
    fig.suptitle(f"30-minute reach from {h} - weekday 08:00 departure",fontsize=12.5,y=0.99)
    fig.text(0.5,0.045,"Schedule-based (MTA subway + Manhattan/Bronx/Bus Co. bus GTFS, 2026-11-18). 4.8 km/h on NYC Centerline streets; no curb ramps; all buses and stops assumed usable. Land only (river removed): land within 100 m of streets reached.\nResidents: ACS 2020-2024 5-yr B18105 ambulatory difficulty, tract totals allocated by area share (approximate; tract-level margins of error are large). ADA-only: boarding/alighting/transfers at ADA subway stations only.",ha="center",fontsize=6.8,color="#444")
    fig.tight_layout(rect=(0,0.085,1,0.955)); fn=O+f"isochrone_{SLUG[h]}_4scenarios.png"; fig.savefig(fn,dpi=140); plt.close(fig); print("saved",fn,"| panel extent %.1f x %.1f km"%(Wm/1000,Hm/1000))
