from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
A=np.array(e._game.xseexqzst.render(),dtype=int)
e.step(GameAction.from_id(5),data={})
B=np.array(e._game.xseexqzst.render(),dtype=int)

def graph(M):
    h,w=M.shape
    nodes=[(r,c) for r in range(h) for c in range(w)]
    adj={}
    for r,c in nodes:
        adj[(r,c)]={(rr,cc) for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<h and 0<=cc<w}
    val={(r,c):int(M[r,c]) for r,c in nodes}
    return nodes,adj,val

NA,AA,VA=graph(A); NB,AB,VB=graph(B)
cand={u:[v for v in NB if VA[u]==VB[v] and len(AA[u])==len(AB[v])] for u in NA}
order=sorted(NA,key=lambda u:(len(cand[u]),-len(AA[u])))
solutions=[]

def rec(i,m,used):
    if len(solutions)>=12:return
    if i==len(order):
        solutions.append(dict(m));return
    u=order[i]
    for v in cand[u]:
        if v in used:continue
        ok=True
        for u2,v2 in m.items():
            if ((u2 in AA[u]) != (v2 in AB[v])):
                ok=False;break
        if not ok:continue
        m[u]=v;used.add(v);rec(i+1,m,used);used.remove(v);del m[u]

rec(0,{},set())
print("A",A.shape,"B",B.shape,"ISOMORPHISMS",len(solutions))
for j,m in enumerate(solutions):
    pts=[(r,c,*m[(r,c)]) for r,c in NA]
    X=np.array([[r,c,1] for r,c,rr,cc in pts],dtype=float)
    yr=np.array([rr for r,c,rr,cc in pts],dtype=float)
    yc=np.array([cc for r,c,rr,cc in pts],dtype=float)
    br=np.linalg.lstsq(X,yr,rcond=None)[0]
    bc=np.linalg.lstsq(X,yc,rcond=None)[0]
    er=float(np.max(np.abs(X@br-yr)));ec=float(np.max(np.abs(X@bc-yc)))
    print("MAP",j,"ROW",np.round(br,8).tolist(),"ERR",round(er,10),"COL",np.round(bc,8).tolist(),"ERR",round(ec,10))
    print(" SAMPLE",sorted(m.items())[:10])
