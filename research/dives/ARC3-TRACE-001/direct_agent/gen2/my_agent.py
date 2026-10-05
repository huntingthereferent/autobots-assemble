"""G2 relational construction solver.

Generic visual mechanism discovered from live ARC interaction:
- detect a top reference strip;
- detect a bottom movable palette with the same color multiset;
- detect repeated empty construction slots in framed middle containers;
- infer colored links between frames;
- recursively traverse frames left-to-right;
- place palette objects into writable slots to realize the reference order.

No game IDs, fixed coordinates, fixed colors, or public action paths.
Falls back to simple exploration when the relational construction witness is absent.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any
import numpy as np

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent


def grid(frame: FrameData) -> np.ndarray:
    a=np.asarray(frame.frame)
    if a.size==0:
        return np.empty((0,0),dtype=np.int16)
    if a.ndim==3:
        a=a[-1]
    return a.reshape(64,64).astype(np.int16,copy=False)


def components(g: np.ndarray) -> list[dict[str,Any]]:
    if g.size==0: return []
    h,w=g.shape; seen=np.zeros((h,w),bool); out=[]
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
            out.append({
                "color":c,"size":len(pts),
                "x0":min(xs),"x1":max(xs),"y0":min(ys),"y1":max(ys),
                "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,
                "cx":(min(xs)+max(xs))/2.0,"cy":(min(ys)+max(ys))/2.0,
            })
    return out


def multiset(xs):
    return Counter(xs)


def click_action(x:int,y:int,why:str) -> GameAction:
    a=GameAction.ACTION6
    a.set_data({"x":int(x),"y":int(y)})
    a.reasoning={"policy":"g2-relational","why":why,"x":int(x),"y":int(y)}
    return a


class MyAgent(Agent):
    MAX_ACTIONS=700

    def __init__(self,*args:Any,**kwargs:Any)->None:
        super().__init__(*args,**kwargs)
        self.level_seen=-1
        self.queue:list[tuple[str,tuple[int,int]|None]]=[]
        self.last_parse:dict[str,Any]|None=None
        self.failed_parse_count=0

    @property
    def name(self)->str:
        return f"{super().name}.g2-relational"

    def is_done(self,frames:list[FrameData],latest_frame:FrameData)->bool:
        return latest_frame.state is GameState.WIN

    def _candidate_reference_groups(self,cs):
        # Reference tokens share an outer footprint, but their interior topology
        # may differ. Group by footprint/y rather than exact pixel count.
        groups=defaultdict(list)
        for c in cs:
            if c["cy"]>16 or not (5<=c["w"]<=8 and 5<=c["h"]<=8):
                continue
            if c["size"]<8 or c["size"]>40:
                continue
            groups[(c["w"],c["h"])].append(c)
        # Wrapped references are one sequence in row-major visual order.
        return [sorted(v,key=lambda z:(z["cy"],z["cx"])) for v in groups.values() if len(v)>=3]

    def _candidate_palette_groups(self,cs):
        # Palette tokens occupy equal cells; solid data tokens and hollow link
        # tokens may have different pixel counts inside the same footprint.
        groups=defaultdict(list)
        for c in cs:
            if c["cy"]<53 or not (3<=c["w"]<=5 and 3<=c["h"]<=5):
                continue
            if c["size"]<8 or c["size"]>30:
                continue
            groups[(c["w"],c["h"],round(c["cy"]))].append(c)
        return [sorted(v,key=lambda z:z["cx"]) for v in groups.values() if len(v)>=3]

    def _find_ref_palette(self,cs):
        refs=self._candidate_reference_groups(cs)
        pals=self._candidate_palette_groups(cs)
        best=None
        for r in refs:
            rc=[x["color"] for x in r]
            if len(set(rc))<2:
                continue
            for p in pals:
                pc=[x["color"] for x in p]
                overlap=sum((Counter(rc) & Counter(pc)).values())
                # Later graph levels can emit more values than there are physical
                # palette tokens because a shared child frame may be invoked twice.
                # Require strong vocabulary overlap, not equal multisets.
                if overlap < max(2, min(len(rc),len(pc))//2):
                    continue
                score=(overlap, len(r), len(p), -abs(len(r)-len(p)))
                if best is None or score>best[0]:
                    best=(score,r,p)
        return None if best is None else (best[1],best[2])

    def _find_slot_signature(self,cs,ref_colors):
        # Repeated tiny identical middle components not belonging to the reference/palette colors.
        sigs=defaultdict(list)
        for c in cs:
            if not (10<c["cy"]<52): continue
            if c["size"]>16: continue
            sig=(c["color"],c["size"],c["w"],c["h"])
            sigs[sig].append(c)
        ranked=[]
        for sig,v in sigs.items():
            if len(v)<3: continue
            # A slot family should occupy one or more horizontal rows.
            ys={round(c["cy"],1) for c in v}
            xs={round(c["cx"],1) for c in v}
            if len(xs)<3: continue
            ranked.append((len(v),len(ys),sig,v))
        if not ranked: return None
        ranked.sort(reverse=True,key=lambda z:(z[0],z[1]))
        return ranked[0][2], ranked[0][3]

    def _frame_rows(self,g,slots):
        # Empty slots lie on a regular x lattice, but multiple sibling frames may
        # share the same y. Detect each enclosing frame from its own top-border run.
        byy=defaultdict(list)
        for s in slots:
            byy[round(s["cy"],1)].append(s)
        if not byy:
            return None

        xvals=sorted({round(s["cx"],1) for s in slots})
        if len(xvals)<2:
            return None
        diffs=[round(xvals[i+1]-xvals[i],1) for i in range(len(xvals)-1) if xvals[i+1]>xvals[i]]
        if not diffs:
            return None
        step=Counter(diffs).most_common(1)[0][0]
        bg=Counter(int(v) for v in g.ravel()).most_common(1)[0][0]

        rows=[]
        for cy,ss in sorted(byy.items()):
            ytop=int(np.floor(cy))-4
            if not (0<=ytop<64):
                continue

            # Scan same-color horizontal runs on the expected top border.
            runs=[]
            x=0
            while x<64:
                color=int(g[ytop,x]); x0=x
                while x+1<64 and int(g[ytop,x+1])==color:
                    x+=1
                x1=x
                width=x1-x0+1
                if color!=bg and width>=int(2*step+4):
                    # Keep only runs enclosing at least one slot on this y.
                    enclosed=[s for s in ss if x0 < s["cx"] < x1]
                    if enclosed:
                        runs.append((x0,x1,color,enclosed))
                x+=1

            for x0,x1,color,enclosed in runs:
                # Frame grammar: first slot center is 4.5 cells inside border,
                # then slots repeat at the learned lattice spacing.
                lattice=[]
                cx=round(x0+4.5,1)
                limit=x1-4.5
                while cx<=limit+0.2:
                    lattice.append(round(cx,1))
                    cx+=step
                if len(lattice)<2:
                    continue
                rows.append({
                    "cy":cy,
                    "frame_color":color,
                    "lattice":lattice,
                    "empties":enclosed,
                    "x0":x0,
                    "x1":x1,
                })
        return rows or None

    def _parse_construction(self,frame:FrameData):
        g=grid(frame)
        if g.size==0: return None
        cs=components(g)
        rp=self._find_ref_palette(cs)
        if rp is None: return None
        ref,pal=rp
        ref_colors=[c["color"] for c in ref]

        slot_result=self._find_slot_signature(cs,set(ref_colors))
        if slot_result is None: return None
        slot_sig,slots=slot_result
        rows=self._frame_rows(g,slots)
        if not rows: return None

        # Target length need not equal physical palette length: reusable
        # child frames can emit the same constructed sub-sequence on multiple calls.

        # Map empty slots by rounded center.
        empty_by_pos={(round(s["cx"],1),round(s["cy"],1)):s for s in slots}

        frame_colors={r["frame_color"] for r in rows}
        row_by_color={}
        for r in rows:
            old=row_by_color.get(r["frame_color"])
            if old is None or len(r["empties"])>len(old["empties"]):
                row_by_color[r["frame_color"]]=r

        # Build ordered frame entries. A non-empty position can be:
        # - a fixed solid data item, which emits its color;
        # - a hollow/fused link item, which descends into the frame of that color.
        bg=Counter(int(v) for v in g.ravel()).most_common(1)[0][0]
        slot_color=slot_sig[0]
        for r in rows:
            entries=[]
            yi=int(round(r["cy"]))
            for cx in r["lattice"]:
                pos=(round(cx,1),round(r["cy"],1))
                dst=(int(round(cx)),yi)
                if pos in empty_by_pos:
                    entries.append(("slot",dst))
                    continue
                xi=int(round(cx))

                compact=[
                    c for c in cs
                    if c["w"]<=6 and c["h"]<=6 and c["size"]>=8
                    and abs(c["cx"]-cx)<=1.1 and abs(c["cy"]-r["cy"])<=1.1
                    and c["color"] not in (bg,slot_color)
                ]
                compact.sort(key=lambda c:(abs(c["cx"]-cx)+abs(c["cy"]-r["cy"]),-c["size"]))
                item=compact[0] if compact else None

                if item is not None:
                    hollow=item["size"] < item["w"]*item["h"]
                    if hollow and item["color"] in frame_colors and item["color"]!=r["frame_color"]:
                        entries.append(("link",item["color"]))
                    else:
                        entries.append(("data",item["color"]))
                    continue

                # Some fixed links visually connect to the child-frame border and
                # therefore merge into one large component. Recover those by local color.
                patch=g[max(0,yi-2):min(64,yi+3),max(0,xi-2):min(64,xi+3)]
                cnt=Counter(int(v) for v in patch.ravel())
                link=None
                for col,n in cnt.most_common():
                    if col in frame_colors and col!=r["frame_color"]:
                        link=col
                        break
                if link is not None:
                    entries.append(("link",link))
                else:
                    entries.append(("unknown",dst))
            r["entries"]=entries

        # Evaluation entry is the visually first frame.
        root=min(rows,key=lambda z:(z["cy"],z.get("x0",0)))

        # Palette tokens have equal footprints but may be solid data or hollow links.
        tokens={}
        for i,c in enumerate(pal):
            hollow=c["size"] < c["w"]*c["h"]
            kind="link" if hollow and c["color"] in row_by_color else "data"
            tokens[i]={
                "id":i,
                "kind":kind,
                "color":c["color"],
                "src":(int(round(c["cx"])),int(round(c["cy"]))),
            }

        # Assign each physical palette token to one physical empty slot exactly
        # once. Then evaluate the resulting frame graph as a reusable program.
        # A child frame may be invoked repeatedly, including bounded recursive calls;
        # the finite visible reference supplies the stopping witness.
        physical_slots=[]
        for r in rows:
            for i,(typ,val) in enumerate(r["entries"]):
                if typ=="slot":
                    physical_slots.append((r["frame_color"],i,val))
                elif typ=="unknown":
                    return None

        if len(physical_slots)!=len(tokens):
            return None

        token_sources=defaultdict(list)
        semantic_counts=Counter()
        for tok in tokens.values():
            sem=(tok["kind"],tok["color"])
            semantic_counts[sem]+=1
            token_sources[sem].append(tok["src"])
        for srcs in token_sources.values():
            srcs.sort()

        assignment={}
        solution_assignment=None
        tested=0
        max_assignments=500000

        def run_frame(frame_color,ti,depth):
            # The visible reference is a finite witness. Recursive/cyclic frame
            # calls are allowed, but execution succeeds as soon as the full target
            # sequence has been emitted. Depth cap rejects nonproductive loops.
            if ti>=len(ref_colors):
                return ti
            if frame_color not in row_by_color:
                return None
            if depth>max(16,len(ref_colors)*4):
                return None
            r=row_by_color[frame_color]
            for i,(typ,val) in enumerate(r["entries"]):
                if ti>=len(ref_colors):
                    return ti
                if typ=="data":
                    if ref_colors[ti]!=val:
                        return None
                    ti+=1
                elif typ=="link":
                    ti=run_frame(val,ti,depth+1)
                    if ti is None:
                        return None
                elif typ=="slot":
                    sem=assignment.get((frame_color,i))
                    if sem is None:
                        return None
                    kind,color=sem
                    if kind=="data":
                        if ref_colors[ti]!=color:
                            return None
                        ti+=1
                    else:
                        ti=run_frame(color,ti,depth+1)
                        if ti is None:
                            return None
                else:
                    return None
            return ti

        # Search semantic assignments instead of physical token identities, avoiding
        # duplicate permutations when several tokens have the same meaning.
        slot_order=list(physical_slots)

        def search_assignment(j):
            nonlocal solution_assignment,tested
            if solution_assignment is not None or tested>=max_assignments:
                return
            if j>=len(slot_order):
                tested+=1
                end_i=run_frame(root["frame_color"],0,0)
                if end_i==len(ref_colors):
                    solution_assignment=dict(assignment)
                return

            frame_color,entry_i,dst=slot_order[j]
            # Prefer direct next-reference colors, but retain links and alternatives.
            choices=[sem for sem,n in semantic_counts.items() if n>0]
            choices.sort(key=lambda sem:(
                0 if sem[0]=="data" and sem[1] in ref_colors else 1,
                0 if sem[0]=="link" else 1,
                sem[1],
            ))
            for sem in choices:
                semantic_counts[sem]-=1
                assignment[(frame_color,entry_i)]=sem
                search_assignment(j+1)
                del assignment[(frame_color,entry_i)]
                semantic_counts[sem]+=1
                if solution_assignment is not None:
                    return

        search_assignment(0)
        if solution_assignment is None:
            return None

        # Convert semantic assignment back to concrete source-token moves.
        available_sources={sem:list(srcs) for sem,srcs in token_sources.items()}
        placements=[]
        for frame_color,entry_i,dst in physical_slots:
            sem=solution_assignment[(frame_color,entry_i)]
            src=available_sources[sem].pop(0)
            placements.append((sem[1],src,dst))

        # Find a safe visible background pixel for animation ticks.
        bg=Counter(int(v) for v in g.ravel()).most_common(1)[0][0]
        safe=(63,63)
        for y in list(range(10,16))+list(range(45,51)):
            for x in list(range(55,62))+list(range(2,10)):
                if int(g[y,x])==bg:
                    safe=(x,y); break
            else: continue
            break

        return {
            "reference":ref_colors,
            "placements":placements,
            "safe":safe,
            "rows":[{"cy":r["cy"],"color":r["frame_color"],"entries":r["entries"]} for r in rows],
        }

    def _build_queue(self,frame:FrameData)->bool:
        parsed=self._parse_construction(frame)
        self.last_parse=parsed
        if parsed is None:
            return False
        q=[]
        for color,src,dst in parsed["placements"]:
            q.append(("click",src))
            q.append(("click",dst))
            # Animation settling: harmless background clicks. Seven is conservative
            # for the observed generic second-order move animation.
            for _ in range(7):
                q.append(("click",parsed["safe"]))
        q.append(("eval",None))
        self.queue=q
        return True

    def _fallback(self,latest:FrameData)->GameAction:
        raw=set(getattr(latest,"available_actions",[]) or [])
        # Minimal non-specialized fallback; G2 is being evaluated for the relational
        # construction witness, not claimed as full benchmark solver yet.
        for a in (GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4,GameAction.ACTION5):
            if not raw or a.value in raw or a in raw:
                a.reasoning={"policy":"g2-relational","why":"fallback legal simple action"}
                return a
        if not raw or GameAction.ACTION6.value in raw or GameAction.ACTION6 in raw:
            return click_action(32,32,"fallback center probe")
        return GameAction.RESET

    def choose_action(self,frames:list[FrameData],latest_frame:FrameData)->GameAction:
        level=int(getattr(latest_frame,"levels_completed",0))
        if latest_frame.state in (GameState.NOT_PLAYED,GameState.GAME_OVER):
            self.queue=[]
            self.level_seen=level
            a=GameAction.RESET
            a.reasoning={"policy":"g2-relational","why":"start/recover"}
            return a

        if level!=self.level_seen:
            self.level_seen=level
            self.queue=[]

        if not self.queue:
            if not self._build_queue(latest_frame):
                self.failed_parse_count+=1
                return self._fallback(latest_frame)

        kind,data=self.queue.pop(0)
        if kind=="click" and data is not None:
            return click_action(data[0],data[1],"execute inferred relational construction")
        if kind=="eval":
            a=GameAction.ACTION5
            a.reasoning={"policy":"g2-relational","why":"evaluate completed inferred construction"}
            return a
        return self._fallback(latest_frame)