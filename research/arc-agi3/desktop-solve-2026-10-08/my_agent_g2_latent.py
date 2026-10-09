"""ARC3 G2: generic latent-state induction from observable action deltas.

No game IDs, source inspection, or public solution paths.
Pixels remain the witness; decisions use an earned compact state.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Any
import numpy as np
from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent

DIRS=(GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4)

def grid(frame):
    a=np.asarray(frame.frame)
    if a.size==0:
        return np.empty((0,0),dtype=np.int8)
    if a.ndim==3:
        a=a[-1]
    return a.reshape(64,64).astype(np.int8,copy=False)

def legal(frame):
    raw=set(getattr(frame,"available_actions",[]) or [])
    out=[]
    for a in GameAction:
        if a is GameAction.RESET:
            continue
        if not raw or a in raw or a.value in raw:
            out.append(a)
    return out

def components(g):
    if g.size==0:
        return []
    h,w=g.shape
    seen=np.zeros((h,w),dtype=bool)
    raw=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]:
                continue
            color=int(g[y,x]); stack=[(y,x)]; seen[y,x]=True; pts=[]
            while stack:
                cy,cx=stack.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==color:
                        seen[ny,nx]=True; stack.append((ny,nx))
            ys=[q[0] for q in pts]; xs=[q[1] for q in pts]
            raw.append({
                "color":color,"size":len(pts),
                "x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),
                "cx2":min(xs)+max(xs),"cy2":min(ys)+max(ys),
                "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,
            })
    if not raw:
        return []
    dominant=max(range(len(raw)),key=lambda i:raw[i]["size"])
    return [c for i,c in enumerate(raw) if i!=dominant]

def shape(c):
    return (c["color"],c["size"],c["w"],c["h"])

def match_components(before,after):
    bb=defaultdict(list); aa=defaultdict(list)
    for c in before: bb[shape(c)].append(c)
    for c in after: aa[shape(c)].append(c)
    matches=[]; removed=[]; added=[]
    for sig in set(bb)|set(aa):
        left=list(aa.get(sig,[])); used=set()
        for b in bb.get(sig,[]):
            choices=[]
            for j,a in enumerate(left):
                if j not in used:
                    dist=abs(a["cx2"]-b["cx2"])+abs(a["cy2"]-b["cy2"])
                    choices.append((dist,j,a))
            if choices:
                _,j,a=min(choices,key=lambda z:z[0]); used.add(j); matches.append((sig,b,a))
            else:
                removed.append((sig,b))
        for j,a in enumerate(left):
            if j not in used:
                added.append((sig,a))
    return matches,removed,added

def effect(before_frame,after_frame):
    bg=grid(before_frame); ag=grid(after_frame)
    if bg.size==0 or ag.size==0:
        return {"kind":"empty","changed":0,"moved":[],"added":[],"removed":[]}
    ys,xs=np.where(bg!=ag)
    changed=int(len(xs))
    bbox=None if changed==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
    matches,removed,added=match_components(components(bg),components(ag))
    moved=[]
    for sig,b,a in matches:
        dx2=a["cx2"]-b["cx2"]; dy2=a["cy2"]-b["cy2"]
        if dx2 or dy2:
            moved.append((sig,dx2,dy2))
    if changed==0:
        kind="noop"
    elif changed<=4 and not moved:
        # Exact-pixel witness dominates component bookkeeping at this scale.
        # Tiny add/remove artifacts are status unless a real object translation is observed.
        kind="status"
    elif moved and not added and not removed:
        kind="translation"
    else:
        kind="structural"
    return {"kind":kind,"changed":changed,"bbox":bbox,"moved":moved,
            "added":[s for s,_ in added],"removed":[s for s,_ in removed]}

def row_groups(frame):
    groups=defaultdict(list)
    for c in components(grid(frame)):
        groups[(c["cy2"],c["size"],c["w"],c["h"])].append(c)
    rows=[]
    for key,vals in groups.items():
        if 3<=len(vals)<=10:
            vv=sorted(vals,key=lambda c:c["cx2"])
            rows.append({
                "key":key,
                "y":key[0],
                "colors":[c["color"] for c in vv],
                "comps":vv,
            })
    return rows

def detect_ordered_match(frame):
    """Find a source-free ordered-token relation from visible row structure.

    Contract:
    - two aligned rows carry the same multiset of mostly-distinct colors;
    - a third aligned row of equal placeholders lies between them;
    - causal probing later decides which colored row is source vs target.
    """
    rows=row_groups(frame)
    hypotheses=[]
    for i,a in enumerate(rows):
        for j,b in enumerate(rows):
            if j<=i or len(a["colors"])!=len(b["colors"]):
                continue
            if Counter(a["colors"])!=Counter(b["colors"]):
                continue
            n=len(a["colors"])
            if n<3 or len(set(a["colors"]))<max(2,n-1):
                continue
            lo,hi=sorted((a["y"],b["y"]))
            for k,s in enumerate(rows):
                if k in (i,j) or len(s["colors"])!=n:
                    continue
                if not (lo<s["y"]<hi):
                    continue
                if len(set(s["colors"]))!=1:
                    continue
                # Prefer compact, horizontally aligned triples.
                span_a=a["comps"][-1]["cx2"]-a["comps"][0]["cx2"]
                span_b=b["comps"][-1]["cx2"]-b["comps"][0]["cx2"]
                span_s=s["comps"][-1]["cx2"]-s["comps"][0]["cx2"]
                align_penalty=abs(span_a-span_b)+abs(span_a-span_s)
                score=100*n-align_penalty
                hypotheses.append((score,a,b,s))
    if not hypotheses:
        return None
    _,a,b,s=max(hypotheses,key=lambda x:x[0])
    return {"A":a,"B":b,"slots":s}

def _same_color_points(g,x,y):
    color=int(g[y,x])
    q=[(y,x)]
    seen={(y,x)}
    while q:
        cy,cx=q.pop()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<64 and 0<=nx<64 and (ny,nx) not in seen and int(g[ny,nx])==color:
                seen.add((ny,nx)); q.append((ny,nx))
    return color,seen

def _program_boxes(g,target_y,palette_y):
    vals,counts=np.unique(g,return_counts=True)
    bg=int(vals[np.argmax(counts)])
    runs=[]
    for y in range(64):
        x=0
        while x<64:
            color=int(g[y,x]); x0=x
            while x+1<64 and int(g[y,x+1])==color:
                x+=1
            n=x-x0+1
            if color!=bg and n>=20:
                runs.append((y,color,x0,x))
            x+=1

    boxes=[]
    seen=set()
    for y0,color,x0,x1 in runs:
        for y1 in range(y0+6,min(64,y0+14)):
            seg=g[y1,x0:x1+1]
            if float(np.mean(seg==color))<0.70:
                continue
            if np.mean(g[y0:y1+1,x0]==color)<0.55:
                continue
            if np.mean(g[y0:y1+1,x1]==color)<0.55:
                continue
            center=(y0+y1)/2
            if not (target_y<center<palette_y):
                continue
            key=(color,x0,x1,y0)
            if key not in seen:
                seen.add(key)
                boxes.append({"color":color,"x0":x0,"x1":x1,"y0":y0,"y1":y1})
            break
    return sorted(boxes,key=lambda b:b["y0"])

def detect_program_plan(frame):
    """Parse a visible target/palette/program-call relation into literal placements."""
    g=grid(frame)
    if g.size==0:
        return None

    rs=row_groups(frame)
    pairs=[]
    for i,a in enumerate(rs):
        for j,b in enumerate(rs):
            if j<=i or len(a["colors"])!=len(b["colors"]):
                continue
            if Counter(a["colors"])!=Counter(b["colors"]):
                continue
            n=len(a["colors"])
            if n<3 or len(set(a["colors"]))<n-1:
                continue
            above=a if a["y"]<b["y"] else b
            below=b if a["y"]<b["y"] else a
            pairs.append((above,below))
    if not pairs:
        return None
    target,palette=max(
        pairs,
        key=lambda ab:(len(ab[0]["colors"]),ab[1]["y"]-ab[0]["y"])
    )
    target_y=target["y"]/2
    palette_y=palette["y"]/2

    boxes=_program_boxes(g,target_y,palette_y)
    if not boxes:
        return None

    cs=components(g)
    xs=[]
    for box in boxes:
        for c in cs:
            cx=c["cx2"]/2; cy=c["cy2"]/2
            if (
                box["x0"]<cx<box["x1"]
                and box["y0"]<cy<box["y1"]
                and c["w"]<=6 and c["h"]<=6
            ):
                xs.append(int(round(cx)))
    xs=sorted(set(xs))
    if len(xs)<2:
        return None
    diffs=[b-a for a,b in zip(xs,xs[1:]) if b>a]
    if not diffs:
        return None
    step=min(diffs)
    if step<=1:
        return None
    slot_xs=list(range(min(xs),max(xs)+1,step))

    sampled=[]
    for box in boxes:
        box["yc"]=(box["y0"]+box["y1"])//2
        box["slots"]=[(x,box["yc"]) for x in slot_xs if box["x0"]<x<box["x1"]]
        sampled.extend(int(g[y,x]) for x,y in box["slots"])
    if not sampled:
        return None
    placeholder=Counter(sampled).most_common(1)[0][0]

    for i,box in enumerate(boxes):
        typed=[]
        for x,y in box["slots"]:
            call=None
            for j,child in enumerate(boxes):
                if j==i or child["y0"]<=box["y0"]:
                    continue
                cc=child["color"]
                connected=False
                for yy in range(max(0,y-3),min(64,y+4)):
                    for xx in range(max(0,x-3),min(64,x+4)):
                        if int(g[yy,xx])!=cc:
                            continue
                        _,pts=_same_color_points(g,xx,yy)
                        if any(
                            (child["y0"],bx) in pts
                            for bx in range(child["x0"],child["x1"]+1)
                        ):
                            connected=True; break
                    if connected:
                        break
                if connected:
                    call=j; break
            if call is not None:
                typed.append(("call",call))
                continue

            color=int(g[y,x])
            if color==placeholder:
                typed.append(("leaf",x,y))
            else:
                typed.append(("literal",color))
        box["typed"]=typed

    root=min(range(len(boxes)),key=lambda i:boxes[i]["y0"])
    flat=[]
    def walk(i,stack=()):
        if i in stack:
            raise ValueError("cyclic visible call graph")
        for item in boxes[i]["typed"]:
            if item[0]=="call":
                walk(item[1],stack+(i,))
            else:
                flat.append(item)
    try:
        walk(root)
    except ValueError:
        return None

    target_colors=list(target["colors"])
    if len(flat)!=len(target_colors):
        return None

    required=[]
    for want,item in zip(target_colors,flat):
        if item[0]=="literal":
            if item[1]!=want:
                return None
        else:
            required.append((want,item[1],item[2]))

    palette_colors=list(palette["colors"])
    if Counter(c for c,_,_ in required)!=Counter(palette_colors):
        return None

    sources=defaultdict(list)
    for c in palette["comps"]:
        sources[c["color"]].append((c["cx2"]//2,c["cy2"]//2))
    placements=[]
    for color,tx,ty in required:
        if not sources[color]:
            return None
        sx,sy=sources[color].pop(0)
        placements.append({
            "color":color,
            "source":(sx,sy),
            "target":(tx,ty),
        })

    return {
        "placements":placements,
        "target":target_colors,
        "box_count":len(boxes),
        "leaf_count":len(flat),
    }

class MyAgent(Agent):
    MAX_ACTIONS=700

    def __init__(self,*args:Any,**kwargs:Any)->None:
        super().__init__(*args,**kwargs)
        self.last_frame=None
        self.last_action=None
        self.last_level=0
        self.active_shapes=set()
        self.effect_votes=defaultdict(Counter)
        self.motion_votes=defaultdict(Counter)
        self.click_shape_effect=defaultdict(Counter)
        self.tried=defaultdict(set)
        self.latent_visits=Counter()
        self.transition_votes=defaultdict(Counter)
        self.progress_edges={}
        self.structural_edits_since_eval=0
        self.last_effect=None

        # High-confidence visible program/call-graph relation.
        self.program=None
        self.program_failed_levels=set()

        # Generic ordered-token relation hypothesis.
        self.pattern=None
        self.pattern_failed_levels=set()

    @property
    def name(self):
        return f"{super().name}.solve-whole-g2-latent"

    def is_done(self,frames,latest_frame):
        return latest_frame.state is GameState.WIN

    def _component_latent(self,frame):
        cs=components(grid(frame))
        if not self.active_shapes:
            inv=Counter(shape(c) for c in cs)
            return ("inventory",tuple(sorted(inv.items())))
        vals=[]
        for c in cs:
            sig=shape(c)
            if sig in self.active_shapes:
                vals.append((sig,c["cx2"],c["cy2"]))
        return ("active",tuple(sorted(vals)))

    def latent(self,frame):
        comp=self._component_latent(frame)
        small=[]
        for c in components(grid(frame)):
            if c["size"]<=4:
                small.append((shape(c),c["cx2"],c["cy2"]))
        return (comp,tuple(sorted(small)))

    def _clicked_shape(self,frame,xy):
        x,y=xy
        hits=[]
        for c in components(grid(frame)):
            if c["x0"]<=x<=c["x1"] and c["y0"]<=y<=c["y1"]:
                hits.append(c)
        if not hits:
            return None
        return shape(min(hits,key=lambda c:c["size"]))

    def _token(self,action,data,frame=None):
        if action is GameAction.ACTION6 and data is not None:
            sig=self._clicked_shape(frame,data) if frame is not None else None
            return (action.name,sig,data[0],data[1])
        return (action.name,)

    def learn(self,frames,latest):
        if self.last_frame is None or self.last_action is None:
            self.last_level=int(getattr(latest,"levels_completed",0))
            return
        if grid(self.last_frame).size==0 or grid(latest).size==0:
            self.last_level=int(getattr(latest,"levels_completed",self.last_level))
            return

        before=self.last_frame
        action,data=self.last_action
        e=effect(before,latest)
        self.last_effect=e
        aid=action.value
        self.effect_votes[aid][e["kind"]]+=1

        for sig,dx2,dy2 in e["moved"]:
            self.active_shapes.add(sig)
            self.motion_votes[aid][(sig,dx2,dy2)]+=1

        if action is GameAction.ACTION6 and data is not None:
            sig=self._clicked_shape(before,data)
            if sig is not None:
                self.click_shape_effect[sig][e["kind"]]+=1
                if e["kind"] in ("translation","structural"):
                    self.active_shapes.add(sig)

        if e["kind"] in ("translation","structural"):
            self.structural_edits_since_eval+=1

        lb=self.latent(before); la=self.latent(latest)
        token=self._token(action,data,before)
        self.tried[lb].add(token)
        self.transition_votes[(lb,token)][la]+=1

        level=int(getattr(latest,"levels_completed",self.last_level))
        level_delta=level-self.last_level
        if level_delta>0:
            self.progress_edges[lb]=token
            self.structural_edits_since_eval=0

        # Feed the exact observed consequence back into active relational hypotheses.
        self._program_feedback(e,level_delta)
        self._pattern_feedback(e,level_delta)
        if level_delta>0:
            self.program=None
            self.pattern=None

        self.last_level=level



    def _fail_program(self):
        self.program_failed_levels.add(self.last_level)
        self.program=None

    def _program_feedback(self,e,level_delta):
        p=self.program
        if p is None:
            return
        awaiting=p.get("awaiting")
        if awaiting is None:
            return
        p["awaiting"]=None

        if level_delta>0:
            self.program=None
            return

        if awaiting=="select":
            if e["changed"]>0:
                p["stage"]="apply"
            else:
                self._fail_program()
            return

        if awaiting=="apply":
            if e["changed"]<=0:
                self._fail_program()
                return
            p["idx"]+=1
            if p["idx"]>=len(p["placements"]):
                p["stage"]="evaluate"
            else:
                p["stage"]="select"
            return

        if awaiting=="evaluate":
            self._fail_program()

    def _program_choice(self,frame):
        level=int(getattr(frame,"levels_completed",self.last_level))
        if level in self.program_failed_levels:
            return None

        if self.program is None:
            plan=detect_program_plan(frame)
            if plan is None:
                return None
            self.program={
                **plan,
                "idx":0,
                "stage":"select",
                "awaiting":None,
            }

        p=self.program
        stage=p["stage"]

        if stage=="select":
            if p["idx"]>=len(p["placements"]):
                p["stage"]="evaluate"
                stage="evaluate"
            else:
                item=p["placements"][p["idx"]]
                p["awaiting"]="select"
                return (
                    GameAction.ACTION6,
                    item["source"],
                    f"select literal {item['color']} for flattened leaf {p['idx']}"
                )

        if stage=="apply":
            item=p["placements"][p["idx"]]
            p["awaiting"]="apply"
            return (
                GameAction.ACTION6,
                item["target"],
                f"apply literal {item['color']} to flattened leaf {p['idx']}"
            )

        if stage=="evaluate":
            simple=[
                x for x in legal(frame)
                if x not in (GameAction.ACTION6,GameAction.ACTION7)
            ]
            if not simple:
                self._fail_program(); return None
            status=[x for x in simple if self._effect_class(x)=="status"]
            if status:
                action=status[0]
            elif len(simple)==1:
                action=simple[0]
            else:
                self._fail_program(); return None
            p["awaiting"]="evaluate"
            return (
                action,
                None,
                f"evaluate parsed call graph with {p['box_count']} boxes/{p['leaf_count']} leaves"
            )

        return None

    def _row_pos_for_color(self,row,color):
        for c in row["comps"]:
            if c["color"]==color:
                return (c["cx2"]//2,c["cy2"]//2)
        return None

    def _slot_pos(self,row,index):
        c=row["comps"][index]
        return (c["cx2"]//2,c["cy2"]//2)

    def _fail_pattern(self):
        self.pattern_failed_levels.add(self.last_level)
        self.pattern=None

    def _pattern_feedback(self,e,level_delta):
        p=self.pattern
        if p is None:
            return
        awaiting=p.get("awaiting")
        if awaiting is None:
            return
        p["awaiting"]=None

        if level_delta>0:
            self.pattern=None
            return

        if awaiting=="probe_a":
            if e["changed"]>0:
                p["source"]="A"; p["target"]="B"; p["idx"]=0; p["stage"]="apply"
            else:
                p["stage"]="probe_b"
            return

        if awaiting=="probe_b":
            if e["changed"]>0:
                p["source"]="B"; p["target"]="A"; p["idx"]=0; p["stage"]="apply"
            else:
                self._fail_pattern()
            return

        if awaiting=="select":
            if e["changed"]>0:
                p["stage"]="apply"
            else:
                self._fail_pattern()
            return

        if awaiting=="apply":
            if e["changed"]<=0:
                self._fail_pattern()
                return
            p["idx"]+=1
            n=len(p[p["target"]]["colors"])
            if p["idx"]>=n:
                p["stage"]="evaluate"
            else:
                p["stage"]="select"
            return

        if awaiting=="evaluate":
            # No level-up means the visible ordered-match hypothesis was insufficient.
            self._fail_pattern()

    def _pattern_choice(self,frame):
        level=int(getattr(frame,"levels_completed",self.last_level))
        if level in self.pattern_failed_levels:
            return None

        if self.pattern is None:
            if GameAction.ACTION6 not in legal(frame):
                return None
            found=detect_ordered_match(frame)
            if found is None:
                return None
            self.pattern={
                **found,
                "stage":"probe_a",
                "awaiting":None,
                "source":None,
                "target":None,
                "idx":0,
            }

        p=self.pattern
        stage=p["stage"]

        if stage=="probe_a":
            # If A is the source, select exactly the color needed for B slot 0.
            color=p["B"]["colors"][0]
            xy=self._row_pos_for_color(p["A"],color)
            if xy is None:
                self._fail_pattern(); return None
            p["awaiting"]="probe_a"
            return GameAction.ACTION6,xy,"probe colored row A as token source"

        if stage=="probe_b":
            # If B is the source, select exactly the color needed for A slot 0.
            color=p["A"]["colors"][0]
            xy=self._row_pos_for_color(p["B"],color)
            if xy is None:
                self._fail_pattern(); return None
            p["awaiting"]="probe_b"
            return GameAction.ACTION6,xy,"probe colored row B as token source"

        if stage=="select":
            target=p[p["target"]]
            source=p[p["source"]]
            idx=p["idx"]
            color=target["colors"][idx]
            xy=self._row_pos_for_color(source,color)
            if xy is None:
                self._fail_pattern(); return None
            p["awaiting"]="select"
            return GameAction.ACTION6,xy,f"select token for ordered slot {idx}"

        if stage=="apply":
            idx=p["idx"]
            xy=self._slot_pos(p["slots"],idx)
            p["awaiting"]="apply"
            return GameAction.ACTION6,xy,f"apply selected token to ordered slot {idx}"

        if stage=="evaluate":
            simple=[
                a for a in legal(frame)
                if a not in (GameAction.ACTION6,GameAction.ACTION7)
            ]
            if not simple:
                self._fail_pattern(); return None
            # Prefer an already-observed status/evaluator action. If there is only one
            # non-click action, testing it is the smallest remaining discriminator.
            status=[a for a in simple if self._effect_class(a)=="status"]
            if status:
                action=status[0]
            elif len(simple)==1:
                action=simple[0]
            else:
                self._fail_pattern(); return None
            p["awaiting"]="evaluate"
            return action,None,"evaluate completed visible ordered match"

        return None

    def _effect_class(self,action):
        votes=self.effect_votes.get(action.value)
        if not votes:
            return "unknown"
        return votes.most_common(1)[0][0]

    def _click_candidates(self,frame):
        cs=components(grid(frame))
        ranked=[]
        for c in cs:
            if c["size"]>256:
                continue
            sig=shape(c)
            votes=self.click_shape_effect.get(sig,Counter())
            structural=votes["structural"]+votes["translation"]
            status=votes["status"]
            score=100*structural-25*status+4/max(1,c["size"])
            if not votes:
                score+=12
            ranked.append((score,c["cx2"]//2,c["cy2"]//2,sig))
        ranked.sort(reverse=True)
        out=[]; seen=set()
        for _,x,y,sig in ranked:
            pt=(max(0,min(63,x)),max(0,min(63,y)))
            if pt not in seen:
                seen.add(pt); out.append((pt,sig))
        return out[:40]

    def candidates(self,frame):
        out=[]
        for action in legal(frame):
            if action is GameAction.ACTION7:
                continue
            if action is GameAction.ACTION6:
                for xy,sig in self._click_candidates(frame):
                    out.append((action,xy,self._token(action,xy,frame)))
            else:
                out.append((action,None,self._token(action,None,frame)))
        return out

    def choose(self,frame):
        lk=self.latent(frame)
        self.latent_visits[lk]+=1
        acts=legal(frame)

        if lk in self.progress_edges:
            tok=self.progress_edges[lk]
            for a,data,t in self.candidates(frame):
                if t==tok:
                    return a,data,"replay witnessed level-up edge"

        cand=self.candidates(frame)
        untried=[x for x in cand if x[2] not in self.tried[lk]]

        # Status-like actions are treated as evaluators, not structural moves.
        filtered=[]
        for a,data,tok in untried:
            cls=self._effect_class(a)
            if cls=="status" and self.structural_edits_since_eval<3:
                continue
            filtered.append((a,data,tok))
        if filtered:
            untried=filtered

        if untried:
            def score(item):
                a,data,tok=item
                cls=self._effect_class(a)
                class_score={"translation":35,"structural":30,"unknown":15,"status":-10,"noop":-30}.get(cls,0)
                votes=self.transition_votes.get((lk,tok))
                novel=0
                if votes:
                    nxt=votes.most_common(1)[0][0]
                    novel=-self.latent_visits[nxt]
                click_bonus=0
                if a is GameAction.ACTION6 and data is not None:
                    sig=self._clicked_shape(frame,data)
                    vv=self.click_shape_effect.get(sig,Counter())
                    click_bonus=20*(vv["structural"]+vv["translation"])-10*vv["status"]
                return (class_score+click_bonus,novel)
            a,data,tok=max(untried,key=score)
            return a,data,f"latent-untried; effect={self._effect_class(a)}"

        viable=[]
        for a,data,tok in cand:
            cls=self._effect_class(a)
            if cls=="noop":
                continue
            votes=self.transition_votes.get((lk,tok))
            if votes:
                nxt=votes.most_common(1)[0][0]
                cost=self.latent_visits[nxt]
            else:
                cost=999
            if cls=="status" and self.structural_edits_since_eval<3:
                cost+=500
            viable.append((cost,a,data,tok))
        if viable:
            viable.sort(key=lambda z:z[0])
            _,a,data,tok=viable[0]
            return a,data,"least-visited learned latent successor"

        if GameAction.ACTION7 in acts:
            return GameAction.ACTION7,None,"latent state exhausted; undo"
        return GameAction.RESET,None,"no latent move"

    def choose_action(self,frames,latest_frame):
        self.learn(frames,latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED,GameState.GAME_OVER):
            self.last_frame=None
            self.last_action=None
            self.structural_edits_since_eval=0
            a=GameAction.RESET
            a.reasoning={"policy":"g2-latent","why":"start/recover"}
            return a

        special=self._program_choice(latest_frame)
        if special is None:
            special=self._pattern_choice(latest_frame)

        if special is not None:
            a,data,why=special
        else:
            a,data,why=self.choose(latest_frame)

        self.last_frame=latest_frame
        self.last_action=(a,data)

        if a is GameAction.ACTION6 and data is not None:
            x,y=data
            a.set_data({"x":int(x),"y":int(y)})
        a.reasoning={
            "policy":"g2-latent",
            "why":why,
            "active_shapes":len(self.active_shapes),
            "structural_edits_since_eval":self.structural_edits_since_eval,
        }
        return a
