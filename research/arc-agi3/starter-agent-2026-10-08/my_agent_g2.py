"""ARC3 direct G2 — latent-state explorer/planner.

Generic only:
- no game IDs or banked solutions;
- exact pixels remain witness through latent.effect;
- planning/exploration uses structural object state;
- tiny border/status mutations are not treated as structural progress.
"""
from __future__ import annotations
from collections import Counter, defaultdict, deque
from typing import Any
import numpy as np

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent
from latent import perceive, effect, grid

DIRS=(GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4)

def legal(frame):
    vals=set(getattr(frame,"available_actions",[]) or [])
    out=[]
    for a in GameAction:
        if a is GameAction.RESET: continue
        if not vals or a in vals or a.value in vals:
            out.append(a)
    return out

def structural_key(frame):
    s=perceive(frame)
    # Ignore tiny border objects likely to be status/evaluation indicators.
    objs=[]
    for o in s.objects:
        touches=o.x0==0 or o.y0==0 or o.x1==63 or o.y1==63
        if touches and o.size<=4:
            continue
        objs.append((o.shape,o.center2))
    return tuple(objs)

def click_candidates(frame):
    s=perceive(frame)
    g=grid(frame)
    if g.size==0:return []
    freq=Counter(int(v) for v in g.ravel())
    ranked=[]
    for o in s.objects:
        # Don't click tiny border indicators.
        touches=o.x0==0 or o.y0==0 or o.x1==63 or o.y1==63
        if touches and o.size<=4: continue
        if o.size>256: continue
        rarity=1.0/max(1,freq[o.color])
        density=o.size/max(1,(o.x1-o.x0+1)*(o.y1-o.y0+1))
        score=20*rarity+2/max(1,o.size)+density
        pts=[(o.center2[0]//2,o.center2[1]//2)]
        if o.size>=12:
            pts += [(o.x0,o.y0),(o.x1,o.y0),(o.x0,o.y1),(o.x1,o.y1)]
        for x,y in pts:
            ranked.append((score,max(0,min(63,x)),max(0,min(63,y))))
    ranked.sort(reverse=True)
    seen=set(); out=[]
    for _,x,y in ranked:
        p=(x,y)
        if p not in seen:
            seen.add(p); out.append(p)
    return out[:48]

class MyAgent(Agent):
    MAX_ACTIONS=600
    def __init__(self,*args:Any,**kwargs:Any):
        super().__init__(*args,**kwargs)
        self.last_frame=None
        self.last_token=None
        self.last_level=0
        self.tried=defaultdict(set)        # latent_key -> action tokens
        self.edges={}                     # (state,token) -> (next,eclass,dl,bad)
        self.effect_stats=defaultdict(Counter)
        self.visits=Counter()
        self.progress_edges={}
        self.force_backtrack=False

    @property
    def name(self):
        return f"{super().name}.latent-g2"

    def is_done(self,frames,latest_frame):
        return latest_frame.state is GameState.WIN

    def tok(self,a,data=None):
        return (a.name,) if data is None else (a.name,int(data[0]),int(data[1]))

    def candidates(self,frame):
        out=[]
        for a in legal(frame):
            if a is GameAction.ACTION7:
                continue
            if a is GameAction.ACTION6:
                for p in click_candidates(frame):
                    out.append((a,self.tok(a,p),p))
            else:
                out.append((a,self.tok(a),None))
        return out

    def learn(self,latest):
        if self.last_frame is None or self.last_token is None:
            self.last_level=int(getattr(latest,"levels_completed",0))
            return
        if grid(self.last_frame).size==0 or grid(latest).size==0:
            self.last_level=int(getattr(latest,"levels_completed",self.last_level))
            return
        sk=structural_key(self.last_frame)
        nk=structural_key(latest)
        e=effect(self.last_frame,latest)
        lvl=int(getattr(latest,"levels_completed",self.last_level))
        dl=lvl-self.last_level
        bad=latest.state is GameState.GAME_OVER and dl<=0
        self.tried[sk].add(self.last_token)
        self.edges[(sk,self.last_token)]=(nk,e.class_name,dl,bad,e.changed_pixels)
        self.effect_stats[self.last_token[0]][e.class_name]+=1
        if dl>0:
            self.progress_edges[sk]=self.last_token
            self.force_backtrack=False
        elif nk==sk and e.class_name in ("status_like","tiny_local","noop"):
            # This action did not change structural state. Don't mistake it for progress.
            self.force_backtrack=False
        elif self.visits[nk]>0:
            self.force_backtrack=True
        self.last_level=lvl

    def token_score(self,sk,tok):
        # Strongly reward exact known level edge.
        edge=self.edges.get((sk,tok))
        if edge:
            nk,cls,dl,bad,pix=edge
            if dl>0:return 10000.0
            if bad:return -1000.0
            if cls=="structural_motion": base=30
            elif cls in ("local_structural","global_structural"): base=20
            elif cls=="tiny_local": base=-8
            elif cls=="status_like": base=-20
            elif cls=="noop": base=-30
            else: base=0
            base-=3*self.visits[nk]
            return base

        # Untried token: use learned class tendency of its action type only as weak prior.
        stats=self.effect_stats[tok[0]]
        structural=stats["structural_motion"]+stats["local_structural"]+stats["global_structural"]
        nuisance=stats["status_like"]+stats["noop"]+stats["tiny_local"]
        return 12.0 + 3.0*structural - 2.0*nuisance

    def choose(self,frame):
        sk=structural_key(frame)
        self.visits[sk]+=1
        acts=legal(frame)

        if sk in self.progress_edges:
            tok=self.progress_edges[sk]
            for a,t,d in self.candidates(frame):
                if t==tok:return a,t,d,"replay exact latent progress edge"

        if self.force_backtrack and GameAction.ACTION7 in acts:
            self.force_backtrack=False
            return GameAction.ACTION7,self.tok(GameAction.ACTION7),None,"backtrack from visited structural state"

        cand=self.candidates(frame)
        if not cand:
            return GameAction.RESET,self.tok(GameAction.RESET),None,"no candidates"

        # First exhaust genuinely untried actions in this latent state.
        untried=[x for x in cand if x[1] not in self.tried[sk]]
        pool=untried if untried else cand

        ranked=[]
        for a,t,d in pool:
            score=self.token_score(sk,t)
            # Cheap cardinal grounding gets only a tie-break, not dominance.
            if a in DIRS: score+=0.5
            # Complex clicks cost more unless their action type has shown structural effects.
            if a is GameAction.ACTION6 and not self.effect_stats[a.name]["structural_motion"]                and not self.effect_stats[a.name]["local_structural"]                and not self.effect_stats[a.name]["global_structural"]:
                score-=0.5
            ranked.append((score,-len(t),a.name,a,t,d))
        ranked.sort(reverse=True,key=lambda z:(z[0],z[1],z[2]))
        _,_,_,a,t,d=ranked[0]

        # If state exhausted and undo exists, prefer backtracking over known nuisance loop.
        if not untried and GameAction.ACTION7 in acts and self.token_score(sk,t)<=0:
            return GameAction.ACTION7,self.tok(GameAction.ACTION7),None,"latent state exhausted"
        return a,t,d,"latent novelty/effect-class choice"

    def choose_action(self,frames,latest_frame):
        self.learn(latest_frame)
        if latest_frame.state in (GameState.NOT_PLAYED,GameState.GAME_OVER):
            self.last_frame=None; self.last_token=None; self.force_backtrack=False
            a=GameAction.RESET
            a.reasoning={"policy":"latent-g2","why":"start/recover"}
            return a

        a,t,data,why=self.choose(latest_frame)
        self.last_frame=latest_frame
        self.last_token=t
        if a is GameAction.ACTION6 and data is not None:
            x,y=data
            a.set_data({"x":int(x),"y":int(y)})
            a.reasoning={"policy":"latent-g2","why":why,"x":int(x),"y":int(y)}
        else:
            a.reasoning={"policy":"latent-g2","why":why}
        return a
