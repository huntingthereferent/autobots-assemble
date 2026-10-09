from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, itertools, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
e=a.make('ar25'); r=None
for z in SOL+MEET:r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e)
def run(word):
    x=copy.deepcopy(root); rr=r
    for z in word: rr=x.step(GameAction.from_id(z),data={})
    return rr.levels_completed, rr.state.name, rr.frame[0].tobytes()
def classes(words):
    d={}
    for w in words:
        L,S,k=run(w); d.setdefault((L,S,k),[]).append(w)
    return sorted(d.values(), key=lambda g:(len(g[0]),g[0]))
print("ROOT",r.levels_completed,r.state.name,hashlib.sha1(r.frame[0].tobytes()).hexdigest()[:12])
for depth in [1,2,3]:
    ws=list(itertools.product(ACTS, repeat=depth))
    cs=classes(ws)
    print("DEPTH",depth,"WORDS",len(ws),"EXACT_CLASSES",len(cs))
    for g in cs:
        if len(g)>1 or depth==1: print("CLASS",g)
    for w in ws:
        L,S,k=run(w)
        if L>2: print("SOLVED",w,L,S); raise SystemExit
