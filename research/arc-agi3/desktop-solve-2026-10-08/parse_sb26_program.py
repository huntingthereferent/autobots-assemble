from collections import Counter,defaultdict,deque
import math
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,x,y):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"diag":"reach"})

def reach_l2(env):
    for sx,sy,tx,ty in [(35,58,22,29),(19,58,28,29),(43,58,34,29),(27,58,40,29)]:
        click(env,sx,sy); click(env,tx,ty)
    return env.step(GameAction.ACTION5,data={},reasoning={"diag":"eval"})

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(np.int16)

def comps(g):
    h,w=g.shape; seen=np.zeros((h,w),bool); raw=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); st=[(y,x)]; seen[y,x]=1; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            raw.append(dict(color=c,size=len(pts),x0=min(xs),x1=max(xs),y0=min(ys),y1=max(ys),
                            cx2=min(xs)+max(xs),cy2=min(ys)+max(ys),
                            w=max(xs)-min(xs)+1,h=max(ys)-min(ys)+1))
    dom=max(range(len(raw)),key=lambda i:raw[i]["size"])
    return [c for i,c in enumerate(raw) if i!=dom]

def rows(g):
    groups=defaultdict(list)
    for c in comps(g):
        groups[(c["cy2"],c["size"],c["w"],c["h"])].append(c)
    out=[]
    for k,v in groups.items():
        if 3<=len(v)<=12:
            vv=sorted(v,key=lambda c:c["cx2"])
            out.append(dict(y=k[0]/2,colors=[c["color"] for c in vv],comps=vv))
    return out

def find_boxes(g):
    vals,counts=np.unique(g,return_counts=True)
    bg=int(vals[np.argmax(counts)])
    tops=[]
    for y in range(64):
        x=0
        while x<64:
            c=int(g[y,x]); x0=x
            while x+1<64 and int(g[y,x+1])==c:x+=1
            n=x-x0+1
            if c!=bg and n>=20:
                tops.append((y,c,x0,x))
            x+=1
    boxes=[]
    for y0,c,x0,x1 in tops:
        for y1 in range(y0+6,min(64,y0+14)):
            seg=g[y1,x0:x1+1]
            frac=float(np.mean(seg==c))
            if frac<0.70: continue
            # border sides should substantially persist.
            left=np.mean(g[y0:y1+1,x0]==c)
            right=np.mean(g[y0:y1+1,x1]==c)
            if left<0.55 or right<0.55: continue
            boxes.append(dict(color=c,x0=x0,x1=x1,y0=y0,y1=y1))
    # remove duplicate nested candidates, prefer nearest matching bottom edge.
    uniq=[]
    seen=set()
    for b in sorted(boxes,key=lambda z:(z["y0"],z["y1"])):
        key=(b["color"],b["x0"],b["x1"],b["y0"])
        if key in seen: continue
        seen.add(key); uniq.append(b)
    return uniq

def same_color_component(g,x,y):
    c=int(g[y,x]); h,w=g.shape
    q=[(y,x)]; seen={(y,x)}
    while q:
        cy,cx=q.pop()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<h and 0<=nx<w and (ny,nx) not in seen and int(g[ny,nx])==c:
                seen.add((ny,nx)); q.append((ny,nx))
    return c,seen

def parse(g):
    rs=rows(g)

    # First identify the two visible ordered-color rows with the same multiset.
    # The program region must lie between them, so this also removes header-frame ambiguity.
    pairs=[]
    for i,a in enumerate(rs):
        for j,b in enumerate(rs):
            if j<=i or len(a["colors"])!=len(b["colors"]): continue
            if Counter(a["colors"])!=Counter(b["colors"]):continue
            if len(a["colors"])<3 or len(set(a["colors"]))<len(a["colors"])-1:continue
            above=a if a["y"]<b["y"] else b
            below=b if a["y"]<b["y"] else a
            pairs.append((above,below))
    if not pairs:
        print("NO TARGET PAIR");return None
    target,palette=max(pairs,key=lambda ab:(len(ab[0]["colors"]),ab[1]["y"]-ab[0]["y"]))
    print("TARGET",target["colors"],"PALETTE",palette["colors"])

    all_boxes=find_boxes(g)
    bs=[
        b for b in all_boxes
        if target["y"] < (b["y0"]+b["y1"])/2 < palette["y"]
    ]
    print("BOXES",bs)
    if not bs:return None

    # Infer slot x-grid from small components lying inside any box.
    xs=[]
    for b in bs:
        for c in comps(g):
            cx=c["cx2"]/2; cy=c["cy2"]/2
            if b["x0"]<cx<b["x1"] and b["y0"]<cy<b["y1"] and c["w"]<=6 and c["h"]<=6:
                xs.append(int(round(cx)))
    xs=sorted(set(xs))
    if len(xs)<2:
        print("NO SLOT GRID",xs);return None
    diffs=[b-a for a,b in zip(xs,xs[1:]) if b>a]
    step=min(diffs)
    # fill missing evenly-spaced positions within the observed range / box body.
    start=min(xs)
    end=max(xs)
    canonical=list(range(start,end+1,step))
    # If a box suggests one more equally spaced slot in a gap, canonical already fills it.
    print("SLOT_X",canonical)

    for b in bs:
        b["yc"]=(b["y0"]+b["y1"])//2
        b["slots"]=[(x,b["yc"]) for x in canonical if b["x0"]<x<b["x1"]]

    sampled=[]
    for b in bs:
        for x,y in b["slots"]:
            sampled.append(int(g[y,x]))
    placeholder=Counter(sampled).most_common(1)[0][0]
    print("PLACEHOLDER",placeholder,"SAMPLED",sampled)

    # identify calls by connected same-color path from a parent slot to a lower box border.
    by_index={i:b for i,b in enumerate(sorted(bs,key=lambda z:z["y0"]))}
    ordered=list(by_index.values())
    index_of={id(b):i for i,b in by_index.items()}
    for i,b in by_index.items():
        typed=[]
        for si,(x,y) in enumerate(b["slots"]):
            # A fixed call may be a colored ring/connector around a background center.
            # Search the local slot neighborhood for any lower-box color whose connected
            # component physically reaches that child box.
            call=None
            for j,child in by_index.items():
                if j==i or child["y0"]<=b["y0"]:
                    continue
                cc=child["color"]
                found_pts=None
                for yy in range(max(0,y-3),min(64,y+4)):
                    for xx in range(max(0,x-3),min(64,x+4)):
                        if int(g[yy,xx])!=cc:
                            continue
                        _,pts=same_color_component(g,xx,yy)
                        if any((child["y0"],bx) in pts for bx in range(child["x0"],child["x1"]+1)):
                            found_pts=pts; break
                    if found_pts is not None: break
                if found_pts is not None:
                    call=j; break
            if call is not None:
                typed.append(("call",call))
                continue

            color=int(g[y,x])
            if color==placeholder:
                typed.append(("leaf",x,y))
            else:
                typed.append(("literal",color))
        b["typed"]=typed
        print("FUNC",i,"color",b["color"],"typed",typed)

    root=min(by_index,key=lambda i:by_index[i]["y0"])
    flat=[]
    def walk(i,stack=()):
        if i in stack: raise RuntimeError("cycle")
        for item in by_index[i]["typed"]:
            if item[0]=="call":
                walk(item[1],stack+(i,))
            else:
                flat.append(item)
    walk(root)
    print("FLAT",flat)
    if len(flat)!=len(target["colors"]):
        print("LEN MISMATCH",len(flat),len(target["colors"]));return None

    required=[]
    for want,item in zip(target["colors"],flat):
        if item[0]=="literal":
            if item[1]!=want:
                print("FIXED MISMATCH",want,item);return None
        else:
            required.append((want,item[1],item[2]))
    print("REQUIRED",required)
    print("REQCOLORS",Counter(c for c,_,_ in required))
    print("PALCOLORS",Counter(palette["colors"]))
    return dict(target=target,palette=palette,boxes=bs,required=required)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
print("\n=== L1 ===")
parse(grid(env.observation_space))
reach_l2(env)
print("\n=== L2 ===")
parse(grid(env.observation_space))
