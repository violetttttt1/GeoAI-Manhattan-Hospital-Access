import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso2_core.py")).read())
HOSP={"Harlem Hospital":(40.8147102,-73.9392782),"NYP/Columbia (CUIMC)":(40.8409780,-73.9407016),"Mount Sinai Morningside":(40.8052373,-73.9613875)}
TRrev=collections.defaultdict(list)
for a_,lst in TR.items():
    for (b_,mt_) in lst: TRrev[b_].append((a_,mt_))
def origin_state(latlon=None,node=None):
    if node is None: o,dd=snap(*latlon); o=int(o[0]); dd=float(dd[0])
    else: o=int(node); dd=0.0
    return dict(on=o,od=dd,d0=dijkstra(G[:N,:N],directed=True,indices=o,limit=TLIM+1))
def bus_walk(BUS,st):
    w={}
    for j in range(len(BUS["ids"])):
        if not BUS["ok"][j]: continue
        tu=st["d0"][BUS["ne_u"][j]]+BUS["off_u"][j]/WALK; tv=st["d0"][BUS["ne_v"][j]]+BUS["off_v"][j]/WALK; t=st["od"]/WALK+BUS["snap"][j]/WALK+min(tu,tv)
        if t<=TLIM: w[j]=t
    return w
def raptor_g(T0,ada_only,BUS,use_bus,st,rev=False,K=7):
    al=np.r_[ALLOW[ada_only],np.ones(len(BUS["ids"]),bool)] if use_bus else ALLOW[ada_only]
    nst=len(al); INF=1e9; best=np.full(nst,INF); tau=np.full(nst,INF); marked=set()
    if not rev:
        pats=[(a,b,m_,None,None) for a,b,m_ in PATS]+(BUS["pats"] if use_bus else []); TRm=TR
    else:
        pats=[]
        for a,b,m_ in PATS:
            M2=-m_[:,::-1]; M2=M2[np.argsort(M2[:,0],kind="stable")]; pats.append((a,b[::-1],M2,None,None))
        if use_bus:
            for a,b,m_,pk,dr in BUS["pats"]:
                M2=-m_[:,::-1]; M2=M2[np.argsort(M2[:,0],kind="stable")]; pats.append((a,b[::-1],M2,dr[::-1],pk[::-1]))
        TRm=TRrev
    sp_=collections.defaultdict(list)
    for pi,(rt,sl,M,_cb,_ca) in enumerate(pats):
        for pos,s in enumerate(sl): sp_[s].append((pi,pos))
    sid_list=list(kids.stop_id)
    pw={}
    for k,P in enumerate(parents_idx):
        t=(st["od"]+st["d0"][pnodes[k]]*WALK+pdist[k])/WALK
        if t<=TLIM: pw[P]=t
    def relax(s,t,tgt):
        if al[s] and t<best[s] and t<=T0+TLIM: best[s]=t; tau[s]=t; tgt.add(s)
    for P,wt in pw.items():
        for c in children.get(P,[]): relax(sidx[c],T0+wt,marked)
    if use_bus:
        for j,wt in bus_walk(BUS,st).items(): relax(len(kids)+j,T0+wt,marked)
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
                for (P2,mt) in TRm.get(u[1],[]):
                    if P2 in children:
                        for c in children[P2]: relax(sidx[c],t+mt,tn)
            if use_bus:
                for ub,wt in BUS["W"].get(u,{}).items():
                    for s2 in unit_stops(ub): relax(s2,t+wt,tn)
        marked=tn
        if not marked: break
    return best
def street_g(best,T0,BUS,use_bus,st):
    rel=best-T0; parr={}
    for i,s in enumerate(kids.stop_id):
        if rel[i]<1e8: P=par_of[s]; parr[P]=min(parr.get(P,1e9),rel[i])
    src=[(st["on"],st["od"]/WALK)]
    for P,t in parr.items():
        if t<=TLIM: k=parents_idx.index(P); src.append((int(pnodes[k]),t+pdist[k]/WALK))
    nbus=0
    if use_bus:
        for j in range(len(BUS["ids"])):
            t=rel[len(kids)+j]
            if t<=TLIM and BUS["ok"][j]:
                nbus+=1; src.append((int(BUS["ne_u"][j]),t+(BUS["snap"][j]+BUS["off_u"][j])/WALK)); src.append((int(BUS["ne_v"][j]),t+(BUS["snap"][j]+BUS["off_v"][j])/WALK))
    nodes=np.array([a for a,_ in src]); vals=np.array([max(b,1e-3) for _,b in src]); mn=np.full(N,np.inf); np.minimum.at(mn,nodes,vals); nz=np.flatnonzero(np.isfinite(mn))
    Gs=G+sp.csr_matrix((mn[nz],(np.full(len(nz),N),nz)),shape=G.shape)
    dist=dijkstra(Gs,directed=True,indices=N,limit=TLIM+1)[:N]
    return dist,{k:v for k,v in parr.items() if v<=TLIM},nbus
