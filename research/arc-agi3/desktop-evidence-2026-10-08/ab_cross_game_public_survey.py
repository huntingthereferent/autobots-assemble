from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from itertools import product
from ab_family_closure import Occurrence,ab_family

GAMES=["bp35","cd82","cn04","dc22","ft09","g50t","ka59","lf52","lp85","ls20","m0r0","r11l","re86","s5i5","sb26","sc25","sk48","sp80","su15","tn36","tr87","tu93","vc33","wa30"]

def fh(r):
    if not getattr(r,"frame",None): return "EMPTY"
    try:
        arr=np.array(r.frame[0],dtype=np.int16)
    except:
        return hashlib.sha1(repr(r.frame).encode()).hexdigest()[:12]
    return hashlib.sha1(arr.tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)

# Deterministic probe families: repeated single actions and short alternating pairs.
probe_sequences=[]
for z in [1,2,3,4,5,7]:
    probe_sequences.append((f"rep{z}",[z]*12))
for x,y in [(1,2),(3,4),(4,5),(5,4),(1,5),(5,1)]:
    probe_sequences.append((f"alt{x}{y}",[x,y]*6))

for game in GAMES:
    observations=[]
    for pname,seq in probe_sequences:
        try:
            e=a.make(game)
        except Exception:
            continue
        hist=[]
        for t,z in enumerate(seq):
            # state observation is result of a no-op-like public action only when 7 is harmless
            # so instead use the frame returned by the previous required action; first state is synthetic START.
            if t==0:
                cur="START"
            else:
                cur=hist[-1][1]
            # full action-response vector from copies of current state
            outs=[]
            for az in [1,2,3,4,5]:
                q=copy.deepcopy(e)
                try:
                    rr=q.step(GameAction.from_id(az),data={})
                    outs.append((az,fh(rr),rr.levels_completed,rr.state.name))
                except Exception as ex:
                    outs.append((az,"ERR",type(ex).__name__,None))
            try:
                r=e.step(GameAction.from_id(z),data={})
            except Exception:
                break
            nxt=fh(r)
            observations.append((pname,t,cur,tuple(outs),tuple(h[1] for h in hist[-4:])))
            hist.append((z,nxt))
            if r.state.name!="NOT_FINISHED":
                break

    if not observations:
        print(game,"NO_DATA")
        continue

    # Build witnesses grouped by current public referent.
    occ=[]
    for pname,t,cur,future,prior in observations:
        rel=[]
        # prior is chronological oldest->newest within last <=4
        for i in range(1,5):
            v=prior[-i] if len(prior)>=i else None
            rel.append((f"prev{i}",v))
        rel.append(("probe",pname))
        occ.append(Occurrence(cur,tuple(rel),future))

    try:
        states=ab_family(occ)
    except Exception as ex:
        print(game,"AB_FAIL",type(ex).__name__,str(ex)[:120])
        continue

    raw=len(states)
    split={k:v for k,v in states.items() if v.retained_names}
    print(game,"RAW",raw,"SPLIT",len(split))
    for ref,s in list(split.items())[:8]:
        print(" ",ref,"=>",s.retained_names)
