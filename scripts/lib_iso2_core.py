import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso_core.py")).read())
import scipy.sparse as sp, time
WT_MAX=300.0; SNAP_MAX=150.0
# ---- edge snapping index (bus stops sit mid-block)
nE=len(eu); nS=np.ceil(el/15).astype(int)+1; rep=np.repeat(np.arange(nE),nS); off=np.cumsum(nS)-nS; kk=np.arange(nS.sum())-np.repeat(off,nS); frac=kk/(nS[rep]-1)
sx=nx[eu[rep]]+(nx[ev[rep]]-nx[eu[rep]])*frac; sy=ny[eu[rep]]+(ny[ev[rep]]-ny[eu[rep]])*frac
etree=cKDTree(np.c_[sx,sy]); print("edge samples",len(sx))
ORIG=(40.8409780,-73.9407016); on,od=snap(*ORIG); on=int(on[0]); od=float(od[0])
d0=dijkstra(G[:N,:N],directed=True,indices=on,limit=TLIM+1)
parents_idx=list(parents.index); pnodes,pdist=snap(parents.lat.values,parents.lon.values)
def prep_bus(T0h):
    B=pickle.load(open(S+f"bus_{T0h}.pkl","rb")); stopinfo={}; pats=[]
    for feed,dct in B.items():
        s=dct["stops"].set_index("id")
        for (rt,sl,pk,dr),tl in dct["pat"].items():
            for x in sl: 
                if x not in stopinfo: stopinfo[x]=(float(s.loc[x,"stop_lat"]),float(s.loc[x,"stop_lon"]))
            pats.append((rt,sl,np.array(sorted(tl,key=lambda a:a[0])),np.array(pk),np.array(dr)))
    ids=sorted(stopinfo); base=len(kids); bidx={x:base+i for i,x in enumerate(ids)}
    lat=np.array([stopinfo[x][0] for x in ids]); lon=np.array([stopinfo[x][1] for x in ids]); X,Y=xy(lat,lon)
    d,i=etree.query(np.c_[X,Y]); e=rep[i]; f=frac[i]; ok=d<=SNAP_MAX
    BUS=dict(ids=ids,idx=bidx,lat=lat,lon=lon,e=e,f=f,snap=d,ok=ok,pats=[(rt,[bidx[x] for x in sl],M,pk,dr) for rt,sl,M,pk,dr in pats])
    print(f"bus stops served in window {len(ids)} | snapped within {SNAP_MAX:.0f} m: {ok.sum()} | patterns {len(pats)}")
    # walking transfers
    ne_u=eu[e]; ne_v=ev[e]; off_u=f*el[e]; off_v=(1-f)*el[e]
    ends=collections.defaultdict(list)       # node -> [(unit, offset_s)]
    for j in range(len(ids)):
        if not ok[j]: continue
        u_=("b",j); ends[int(ne_u[j])].append((u_,(d[j]+off_u[j])/WALK)); ends[int(ne_v[j])].append((u_,(d[j]+off_v[j])/WALK))
    for k,P in enumerate(parents_idx):
        if pdist[k]<=SNAP_MAX: ends[int(pnodes[k])].append((("s",P),pdist[k]/WALK))
    nodes=np.array(sorted(ends)); isE=np.zeros(N,bool); isE[nodes]=True; NB={}
    t0=time.time()
    for b0 in range(0,len(nodes),150):
        batch=nodes[b0:b0+150]; D=dijkstra(G[:N,:N],directed=True,indices=batch,limit=WT_MAX); r,c=np.nonzero(np.isfinite(D)&isE[None,:])
        for rr,cc in zip(r,c): NB.setdefault(int(batch[rr]),[]).append((int(cc),float(D[rr,cc])))
    print("node-pair search %.0fs, endpoint nodes %d"%(time.time()-t0,len(nodes)))
    W=collections.defaultdict(dict)
    for na,lst in ends.items():
        for (ua,oa) in lst:
            for (nb,dd) in NB.get(na,[]):
                for (ub,ob) in ends[nb]:
                    if ua==ub or (ua[0]=="s" and ub[0]=="s"): continue
                    t=oa+dd+ob
                    if t<=WT_MAX and t<W[ua].get(ub,1e9): W[ua][ub]=t
    # same-edge direct walking between bus stops
    byedge=collections.defaultdict(list)
    for j in range(len(ids)):
        if ok[j]: byedge[int(e[j])].append(j)
    for eidx,js in byedge.items():
        for a in js:
            for b in js:
                if a<b:
                    t=(abs(f[a]-f[b])*el[eidx]+d[a]+d[b])/WALK
                    if t<=WT_MAX:
                        for x,y in ((("b",a),("b",b)),(("b",b),("b",a))):
                            if t<W[x].get(y,1e9): W[x][y]=t
    print("walking-transfer units",len(W),"pairs",sum(len(v) for v in W.values()))
    # origin walk to bus stops
    wob={}
    for j in range(len(ids)):
        if not ok[j]: continue
        tu=d0[ne_u[j]]+off_u[j]/WALK; tv=d0[ne_v[j]]+off_v[j]/WALK; t=od/WALK+d[j]/WALK+min(tu,tv)
        if t<=TLIM: wob[j]=t
    BUS.update(W=dict(W),ne_u=ne_u,ne_v=ne_v,off_u=off_u,off_v=off_v,walk_origin=wob)
    return BUS
def raptor2(T0,ada_only,BUS,use_bus,K=7):
    al=np.r_[ALLOW[ada_only],np.ones(len(BUS["ids"]),bool)] if use_bus else ALLOW[ada_only]
    nst=len(al); INF=1e9; best=np.full(nst,INF); tau=np.full(nst,INF); marked=set()
    pats=[(a,b,m_,None,None) for a,b,m_ in PATS]+(BUS["pats"] if use_bus else []); sp_=collections.defaultdict(list)
    for pi,(rt,sl,M,_cb,_ca) in enumerate(pats):
        for pos,s in enumerate(sl): sp_[s].append((pi,pos))
    sid_list=list(kids.stop_id)
    # walking to subway parents (as before)
    pw={}
    for k,P in enumerate(parents_idx):
        t=(od+d0[pnodes[k]]*WALK+pdist[k])/WALK
        if t<=TLIM: pw[P]=t
    def relax(s,t,tgt):
        if al[s] and t<best[s] and t<=T0+TLIM: best[s]=t; tau[s]=t; tgt.add(s)
    for P,wt in pw.items():
        for c in children.get(P,[]): relax(sidx[c],T0+wt,marked)
    if use_bus:
        for j,wt in BUS["walk_origin"].items(): relax(len(kids)+j,T0+wt,marked)
    def unit_stops(u):
        if u[0]=="b": return [len(kids)+u[1]]
        return [sidx[c] for c in children.get(u[1],[])]
    for k in range(K):
        new=set(); Qp={}
        for s in marked:
            for pi,pos in sp_.get(s,[]):
                if pi not in Qp or pos<Qp[pi]: Qp[pi]=pos
        prev=tau.copy()
        for pi,pos0 in Qp.items():
            rt,sl,M,cb,ca=pats[pi]; cur=None
            for pos in range(pos0,len(sl)):
                s=sl[pos]
                if cur is not None:
                    a=M[cur,pos]
                    if al[s] and (ca is None or ca[pos]) and a<best[s] and a<=T0+TLIM: best[s]=a; tau[s]=a; new.add(s)
                if al[s] and (cb is None or cb[pos]) and prev[s]<INF:
                    j=int(np.searchsorted(M[:,pos],prev[s],side="left"))
                    if j<M.shape[0] and (cur is None or j<cur): cur=j
        tn=set(new); parr={}
        for s in new:
            if s<len(kids): P=par_of[sid_list[s]]; parr[("s",P)]=min(parr.get(("s",P),INF),tau[s])
            elif use_bus: parr[("b",s-len(kids))]=tau[s]
        for u,t in parr.items():
            if u[0]=="s":
                for (P2,mt) in TR.get(u[1],[]):
                    if P2 in children:
                        for c in children[P2]: relax(sidx[c],t+mt,tn)
            if use_bus:
                for ub,wt in BUS["W"].get(u,{}).items():
                    for s2 in unit_stops(ub): relax(s2,t+wt,tn)
        marked=tn
        if not marked: break
    return best
def street_from(best,T0,BUS,use_bus):
    best_rel=best-T0; parr={}
    for i,s in enumerate(kids.stop_id):
        if best_rel[i]<1e8: P=par_of[s]; parr[P]=min(parr.get(P,1e9),best_rel[i])
    src=[(on,od/WALK)]
    for P,t in parr.items():
        if t<=TLIM: k=parents_idx.index(P); src.append((int(pnodes[k]),t+pdist[k]/WALK))
    nbus=0
    if use_bus:
        for j in range(len(BUS["ids"])):
            t=best_rel[len(kids)+j]
            if t<=TLIM and BUS["ok"][j]:
                nbus+=1; src.append((int(BUS["ne_u"][j]),t+(BUS["snap"][j]+BUS["off_u"][j])/WALK)); src.append((int(BUS["ne_v"][j]),t+(BUS["snap"][j]+BUS["off_v"][j])/WALK))
    nodes=np.array([a for a,_ in src]); vals=np.array([max(b,1e-3) for _,b in src]); mn=np.full(N,np.inf); np.minimum.at(mn,nodes,vals); nz=np.flatnonzero(np.isfinite(mn))
    Gs=G+sp.csr_matrix((mn[nz],(np.full(len(nz),N),nz)),shape=G.shape)
    dist=dijkstra(Gs,directed=True,indices=N,limit=TLIM+1)[:N]
    return dist,{k:v for k,v in parr.items() if v<=TLIM},nbus
