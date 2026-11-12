import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pickle, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.lines import Line2D
S=S; O=O
M=pickle.load(open(S+"iso2_masks.pkl","rb")); m=M["masks"]; x0,x1,y0,y1=M["x0"],M["x1"],M["y0"],M["y1"]; ext=[x0,x1,y0,y1]
T=pd.read_csv(O+"nyp_isochrone_bus_summary.csv",dtype={"departure":str}); a=lambda d,s:float(T[(T.departure==d)&(T.scenario.str.startswith(s))&(T.buffer_m==100)].area_km2.iloc[0])
A1,A2,A3,A4=[a("08:00",s) for s in "1234"]
LAT0,LON0=40.80,-73.95; ox,oy=(-73.9407016-LON0)*111320*np.cos(np.radians(LAT0)),(40.8409780-LAT0)*110574
C={"sub_all":(0.99,0.72,0.35),"bus_all":(0.84,0.25,0.12),"sub_ada":(0.45,0.62,0.82),"bus_ada":(0.05,0.45,0.42)}
def rgba(mask,c,al): a_=np.zeros(mask.shape+(4,)); a_[mask]=list(c)+[al]; return a_
fig,axs=plt.subplots(1,4,figsize=(16.5,9.6))
panels=[("① Subway, anyone",f"{A1:.1f} km²   (100%)",[(m[(8,False,False)],C["sub_all"],0.9)]),
        ("② Subway, ADA stations only",f"{A2:.1f} km²   ({100*A2/A1:.0f}% of ①)",[(m[(8,False,True)],C["sub_ada"],0.95)]),
        ("③ Subway + bus, anyone",f"{A3:.1f} km²   ({100*A3/A1:.0f}% of ①)",[(m[(8,True,False)],C["bus_all"],0.9),(m[(8,False,False)],C["sub_all"],0.95)]),
        ("④ Subway + bus, ADA subway stations only",f"{A4:.1f} km²   ({100*A4/A3:.0f}% of ③, {100*A4/A1:.0f}% of ①)",[(m[(8,True,True)],C["bus_ada"],0.9),(m[(8,False,True)],C["sub_ada"],0.95)])]
for ax,(t,sub,layers) in zip(axs,panels):
    ax.set_facecolor("#e8f1f8")
    for r in M["boro"]: ax.add_patch(MPoly(r,closed=True,fc="#f2f2f2",ec="#a5a5a5",lw=0.4))
    for mask,c,al in layers: ax.imshow(rgba(mask,c,al),extent=ext,origin="upper",interpolation="nearest",zorder=3)
    ax.contour(np.linspace(x0,x1,M["W"]),np.linspace(y1,y0,M["H"]),m["walk"].astype(float),levels=[0.5],colors="k",linewidths=0.6,linestyles="--",zorder=5)
    ax.plot(ox,oy,"*",ms=14,color="#d62728",mec="white",mew=0.8,zorder=9)
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(t+"\n"+sub,fontsize=9.6)
leg=[Line2D([0],[0],marker="s",ls="",color=C["sub_all"],ms=11,label="Reached by subway (anyone)"),Line2D([0],[0],marker="s",ls="",color=C["bus_all"],ms=11,label="Added by bus (anyone)"),
     Line2D([0],[0],marker="s",ls="",color=C["sub_ada"],ms=11,label="Reached by ADA subway stations only"),Line2D([0],[0],marker="s",ls="",color=C["bus_ada"],ms=11,label="Added by bus (after ADA subway)"),
     Line2D([0],[0],ls="--",color="k",lw=1,label=f"Walking only ({a('-','0'):.1f} km²)"),Line2D([0],[0],marker="*",ls="",color="#d62728",ms=12,label="NYP/CUIMC")]
fig.legend(handles=leg,loc="lower center",ncol=6,fontsize=8.5,frameon=False)
fig.suptitle("30-minute reach from NYP/Columbia Irving Medical Center - weekday 08:00 departure",fontsize=12.5,y=0.985)
fig.text(0.5,0.045,"Schedule-based: MTA subway + Manhattan/Bronx/MTA Bus Co. bus GTFS (service date 2026-11-18). Walk 4.8 km/h on NYC Centerline streets; no curb ramps modelled; all buses and bus stops assumed usable.\nArea = land within 100 m of streets reached in <=30 min. In ② and ④ only ADA subway stations may be used for boarding, alighting and transfers; ride-through at other stations is allowed. Subway elevator outages ignored.",ha="center",fontsize=7.2,color="#444")
fig.tight_layout(rect=(0,0.085,1,0.965)); fig.savefig(O+"nyp_isochrone_bus_4scenarios.png",dpi=150); print("saved")
