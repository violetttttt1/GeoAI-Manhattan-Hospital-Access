import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
import json, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, PathPatch
from matplotlib.path import Path
exec(open((S+"study.py")).read().split("# ===== 1 elevators")[0])
O=O
gj=json.load(open(R+"borough_boundaries/boroughs.geojson"))
def rings(f):
    g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    out=[]
    for poly in polys:
        for ring in poly[:1]:
            a=np.array(ring); X,Y=xy(a[:,1],a[:,0]); out.append(np.c_[X,Y])
    return out
B={f["properties"]["boroname"]:rings(f) for f in gj["features"]}
fig,ax=plt.subplots(figsize=(7.2,11)); 
for nme,col in [("Bronx","#ececec"),("Queens","#ececec"),("Brooklyn","#ececec")]:
    for r in B[nme]: ax.add_patch(MPoly(r,closed=True,fc=col,ec="#b8b8b8",lw=0.6))
man=[]
for r in B["Manhattan"]:
    if len(r)<50: continue
    p=MPoly(r,closed=True,fc="#f3f3f3",ec="#555",lw=0.9); ax.add_patch(p); man.append(r)
# study area shading = north of 110 St line, clipped to Manhattan
f=np.load(S_+"fit.npy"); c0=f[:2]; nrm=f[2:]; dirv=np.array([nrm[1],-nrm[0]])
big=3e4; q=np.array([c0-dirv*big,c0+dirv*big,c0+dirv*big+nrm*big,c0-dirv*big+nrm*big])
def clip_half(poly):
    out=[]; n=len(poly)
    sd=lambda P:(P-c0)@nrm
    for i in range(n):
        a,b=poly[i],poly[(i+1)%n]; sa,sb=sd(a),sd(b)
        if sa>=0: out.append(a)
        if (sa>=0)!=(sb>=0): out.append(a+(b-a)*(sa/(sa-sb)))
    return np.array(out)
for r in man:
    cl=clip_half(r)
    if len(cl)>2: ax.add_patch(MPoly(cl,closed=True,fc="#fbd98a",ec="#c98a00",lw=0.8,zorder=2))
_a,_b=c0-dirv*6000,c0+dirv*6000; ax.plot([_a[0],_b[0]],[_a[1],_b[1]],color="#1f5fa8",lw=1.4,ls="--",zorder=3)
ax.text(*(c0-dirv*2650+nrm*60),"110 St (fitted line)",rotation=np.degrees(np.arctan2(dirv[1],dirv[0])),color="#1f5fa8",fontsize=8,ha="center",va="bottom",zorder=6)
# hospitals
cols={"Harlem Hospital":"#d62728","NYP/CUIMC":"#d62728","Mount Sinai Morningside":"#d62728"}
lab={"Harlem Hospital":"Harlem Hospital\n(506 Lenox Ave)","NYP/CUIMC":"NYP / Columbia Irving\nMedical Center (622 W 168th St)","Mount Sinai Morningside":"Mount Sinai Morningside\n(1111 Amsterdam Ave)"}
off={"Harlem Hospital":(700,-60,"left"),"NYP/CUIMC":(-640,0,"right"),"Mount Sinai Morningside":(-600,-80,"right")}
for k,(la,lo) in HOSP.items():
    x,y=xy(la,lo); ax.add_patch(Circle((x,y),400,fc="#d62728",alpha=0.14,ec="#d62728",lw=1.4,zorder=4))
    ax.plot(x,y,marker="P",ms=11,color="#d62728",mec="white",mew=0.8,zorder=7)
    dx,dy,ha=off[k]; ax.annotate(lab[k],(x,y),xytext=(x+dx,y+dy),fontsize=8.5,ha=ha,va="center",zorder=8,arrowprops=dict(arrowstyle="-",color="#d62728",lw=0.8),bbox=dict(fc="white",ec="#d62728",lw=0.6,boxstyle="round,pad=0.25"))
# ADA stations in study area (from station_table.csv)
T=pd.read_csv(O+"station_table.csv",dtype=str)
for _,s in T.iterrows():
    x,y=xy(float(s.lat),float(s.lon)); ax.plot(x,y,"^",ms=7,color="#2a7d3f",mec="white",mew=0.6,zorder=6)
ax.plot([],[],"^",color="#2a7d3f",ms=7,label="ADA subway station in study area (10)")
ax.plot([],[],"P",color="#d62728",ms=9,label="Hospital (400 m radius circle)")
ax.add_patch(plt.Rectangle((0,0),0,0,fc="#fbd98a",ec="#c98a00",label="Land north of 110 St (Manhattan)"))
ax.legend(loc="upper left",fontsize=8,frameon=True)
xa,ya=xy(np.array([40.783,40.884]),np.array([-73.985,-73.900])); 
ax.set_xlim(xa[0],xa[1]*0+ (xy(40.8,-73.903)[0])); ax.set_ylim(ya[0],ya[1]); ax.set_aspect("equal")
# scale bar
x0,y0=xa[0]+300,ya[0]+300; ax.plot([x0,x0+1000],[y0,y0],"k",lw=2); ax.text(x0+500,y0+60,"1 km",ha="center",fontsize=8)
ax.annotate("N",xy=(xa[0]+300,ya[0]+1700),xytext=(xa[0]+300,ya[0]+1000),arrowprops=dict(arrowstyle="-|>",color="k"),ha="center",fontsize=10)
ax.set_title("Study area: Manhattan north of 110 St + 400 m around three hospitals",fontsize=11); ax.set_xticks([]); ax.set_yticks([])
ax.set_facecolor("#e8f1f8"); ax.text(0.01,0.005,"Boundaries: NYC Open Data borough boundaries. Hospital points geocoded from street addresses (OSM Nominatim).",transform=ax.transAxes,fontsize=6,va="bottom",color="#444")
fig.tight_layout(); fig.savefig(O+"hospitals_map.png",dpi=170); print("saved")
