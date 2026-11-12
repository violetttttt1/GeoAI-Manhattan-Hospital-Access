import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import pickle, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.lines import Line2D
exec(open((S+"iso_core.py")).read().split("# ---------- street graph")[0])
O=O
P=pickle.load(open(S+"iso_res.pkl","rb")); M=pickle.load(open(S+"iso_masks.pkl","rb")); res=P["res"]
x0,x1,y0,y1=M["x0"],M["x1"],M["y0"],M["y1"]; ext=[x0,x1,y0,y1]
T=pd.read_csv(O+"nyp_isochrone_summary.csv",dtype={"departure":str}); g=lambda d,gp,b=100: T[(T.departure==d)&(T.group==gp)&(T.buffer_m==b)].iloc[0]
fig,ax=plt.subplots(figsize=(8.2,11.8)); ax.set_facecolor("#e8f1f8")
for r in M["boro"]: ax.add_patch(MPoly(r,closed=True,fc="#f2f2f2",ec="#9a9a9a",lw=0.5))
def layer(mask,rgb,alpha):
    a=np.zeros(mask.shape+(4,)); a[mask]=list(rgb)+[alpha]; ax.imshow(a,extent=ext,origin="upper",interpolation="nearest",zorder=3)
layer(M["masks"][(8,False)],(0.99,0.65,0.20),0.75); layer(M["masks"][(8,True)],(0.12,0.40,0.72),0.80)
ax.contour(np.linspace(x0,x1,M["W"]),np.linspace(y1,y0,M["H"]),M["masks"]["walk"].astype(float),levels=[0.5],colors="k",linewidths=0.8,linestyles="--",zorder=5)
_s=pd.read_csv(R+"gtfs/unz/stops.txt",dtype=str); _s["lat"]=_s.stop_lat.astype(float); _s["lon"]=_s.stop_lon.astype(float); parents_=_s[_s.location_type=="1"].set_index("stop_id"); px,py=xy(parents_.lat,parents_.lon); pos=dict(zip(parents_.index,zip(px,py)))
ord_st={k:v for k,v in res[(8,False)]["parr"].items() if v<=TLIM}; ada_st={k:v for k,v in res[(8,True)]["parr"].items() if v<=TLIM}
xs=[pos[k][0] for k in ord_st]; ys=[pos[k][1] for k in ord_st]; ax.plot(xs,ys,"o",ms=3.2,color="#555",zorder=6)
_lab=set()
for k in sorted(ada_st,key=ada_st.get):
    ax.plot(*pos[k],"^",ms=8,color="#1b7f3b",mec="white",mew=0.7,zorder=7)
    if parents_.stop_name[k] not in _lab:
        _lab.add(parents_.stop_name[k]); ax.annotate(parents_.stop_name[k],pos[k],xytext=(6,-3),textcoords="offset points",fontsize=6.3,zorder=8,color="#0b4a22")
ox,oy=xy(*P["orig"]); ax.plot(ox,oy,"*",ms=17,color="#d62728",mec="white",mew=0.9,zorder=9)
ax.set_xlim(x0,x1); ax.set_ylim(y0-250,y1); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("30-minute reach from NYP/Columbia Irving Medical Center\nweekday 08:00 departure, subway + street walking (no curb ramps modelled)",fontsize=10.5)
o=g("08:00","ordinary"); a=g("08:00","ADA-only"); w=g("-","walk only")
leg=[Line2D([0],[0],marker="s",ls="",color=(0.99,0.65,0.20),ms=11,label=f"Anyone: all stations   {o.area_km2:.1f} km²"),
     Line2D([0],[0],marker="s",ls="",color=(0.12,0.40,0.72),ms=11,label=f"ADA stations only   {a.area_km2:.1f} km²  ({100*a.area_km2/o.area_km2:.0f}% of 'anyone')"),
     Line2D([0],[0],ls="--",color="k",lw=1,label=f"Walking only (no subway)   {w.area_km2:.1f} km²"),
     Line2D([0],[0],marker="^",ls="",color="#1b7f3b",ms=8,label=f"ADA station reached ({len(ada_st)} station records)"),
     Line2D([0],[0],marker="o",ls="",color="#555",ms=4,label=f"Any station reached ({len(ord_st)} station records)"),
     Line2D([0],[0],marker="*",ls="",color="#d62728",ms=13,label="NYP/CUIMC (622 W 168th St)")]
ax.legend(handles=leg,loc="upper left",fontsize=7.4,framealpha=0.95)
ax.text(0.995,0.004,"Area = land within 100 m of walkable streets reached in <=30 min. Walk 4.8 km/h. Streets: NYC Centerline. Schedule: MTA subway GTFS.",transform=ax.transAxes,fontsize=5.6,ha="right",va="bottom",color="#444")
fig.tight_layout(); fig.savefig(O+"nyp_isochrone_30min.png",dpi=170); print("saved")
print("ADA-reached stations:",sorted((round(v/60,1),parents_.stop_name[k]) for k,v in ada_st.items()))
