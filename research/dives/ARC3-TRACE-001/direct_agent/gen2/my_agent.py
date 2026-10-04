from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
import sys
from typing import Any

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from latent import latent_key, exact_key, delta_signature, click_candidates, grid
from grammar import solve_visible_program


DIRS=(GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4)


def legal(frame:FrameData)->list[GameAction]:
    raw=set(getattr(frame,"available_actions",[]) or [])
    out=[]
    for a in GameAction:
        if a is GameAction.RESET:
            continue
        if not raw or a in raw or a.value in raw:
            out.append(a)
    return out


def token(action:GameAction,data:tuple[int,int]|None=None)->tuple:
    if data is None:
        return (action.name,)
    return (action.name,int(data[0]),int(data[1]))


class MyAgent(Agent):
    MAX_ACTIONS=600

    def __init__(self,*args:Any,**kwargs:Any)->None:
        super().__init__(*args,**kwargs)
        self.last_frame:FrameData|None=None
        self.last_token:tuple|None=None
        self.last_level=0

        self.tried:defaultdict[tuple,set[tuple]]=defaultdict(set)
        self.transitions:dict[tuple[tuple,tuple],dict[str,Any]]={}
        self.visits:Counter[tuple]=Counter()
        self.action_stats:defaultdict[str,Counter[str]]=defaultdict(Counter)
        self.known_progress:dict[tuple,tuple]={}

        self.recent_latent:deque[tuple]=deque(maxlen=64)
        self.structural_edits_since_eval=0
        self.effect_classes:defaultdict[str,Counter[tuple]]=defaultdict(Counter)
        self.action_uses:Counter[str]=Counter()
        self.last_action_name:str|None=None
        self.same_action_streak=0

        # A queued plan is created only when a visual relation is parsed directly
        # from the current frame. It contains no game-id or banked solution data.
        self.visual_plan:deque[tuple[GameAction,tuple[int,int]|None,str]]=deque()
        self.visual_plan_level:int|None=None

    @property
    def name(self)->str:
        return f"{super().name}.solve-whole-g2"

    def is_done(self,frames:list[FrameData],latest_frame:FrameData)->bool:
        return latest_frame.state is GameState.WIN

    def _learn(self,latest:FrameData)->None:
        if self.last_frame is None or self.last_token is None:
            self.last_level=int(getattr(latest,"levels_completed",0))
            return

        before=self.last_frame
        sig=delta_signature(before,latest)
        lk0=latent_key(before)
        lk1=latent_key(latest)
        level=int(getattr(latest,"levels_completed",self.last_level))
        dl=level-self.last_level
        terminal_bad=latest.state is GameState.GAME_OVER and dl<=0

        rec={
            "next":lk1,
            "exact_changed":sig["exact_changed"],
            "latent_changed":sig["latent_changed"],
            "shape_changed":sig["shape_changed"],
            "bbox":sig["bbox"],
            "level_delta":dl,
            "terminal_bad":terminal_bad,
        }
        self.transitions[(lk0,self.last_token)]=rec
        self.tried[lk0].add(self.last_token)

        aname=self.last_token[0]
        self.action_uses[aname]+=1
        bbox=sig["bbox"]
        if bbox is None:
            bw=bh=0
        else:
            bw=bbox[2]-bbox[0]+1
            bh=bbox[3]-bbox[1]+1
        n=sig["exact_changed"]
        if n==0:
            mag="none"
        elif n<=2:
            mag="micro"
        elif n<=16:
            mag="small"
        elif n<=128:
            mag="medium"
        else:
            mag="large"
        effect_class=(bool(sig["latent_changed"]),bool(sig["shape_changed"]),mag,min(bw,16),min(bh,16))
        self.effect_classes[aname][effect_class]+=1

        if dl>0:
            self.action_stats[aname]["progress"]+=1
            self.known_progress[lk0]=self.last_token
            self.structural_edits_since_eval=0
        elif terminal_bad:
            self.action_stats[aname]["death"]+=1
        elif sig["latent_changed"]:
            self.action_stats[aname]["structural"]+=1
            if aname=="ACTION6":
                self.structural_edits_since_eval+=1
        elif sig["exact_changed"]>0:
            self.action_stats[aname]["status_only"]+=1
        else:
            self.action_stats[aname]["noop"]+=1

        if aname=="ACTION5":
            self.structural_edits_since_eval=0

        self.last_level=level

    def _candidates(self,frame:FrameData)->list[tuple[GameAction,tuple]]:
        acts=legal(frame)
        out=[]
        for a in acts:
            if a is GameAction.ACTION7:
                continue
            if a is GameAction.ACTION6:
                for xy in click_candidates(frame):
                    out.append((a,token(a,xy)))
            else:
                out.append((a,token(a)))
        return out

    def _score(self,lk:tuple,tok:tuple)->float:
        name=tok[0]
        stats=self.action_stats[name]
        score=0.0

        uses=max(1,self.action_uses[name])
        informative=stats["structural"]
        status=stats["status_only"]
        noop=stats["noop"]
        bad=stats["death"]

        # Reward demonstrated progress, but use rates—not cumulative counts—
        # for ordinary effects so one early structural action cannot snowball forever.
        score += 120.0*stats["progress"]
        score += 14.0*(informative/uses)
        score -= 14.0*(status/uses)
        score -= 18.0*(noop/uses)
        score -= 50.0*(bad/uses)

        # Global information value diminishes as an action family is repeatedly sampled.
        if self.action_uses[name]==0:
            score += 35.0
        else:
            score -= min(28.0, 3.0*(self.action_uses[name]**0.5))

        # Distinct observed effect classes are useful evidence; repeated samples of
        # the same class are not increasingly valuable.
        score += min(8.0, 2.0*len(self.effect_classes[name]))

        tr=self.transitions.get((lk,tok))
        if tr is None:
            score += 20.0
        else:
            if tr["level_delta"]>0:
                score += 500.0
            elif tr["terminal_bad"]:
                score -= 200.0
            elif tr["latent_changed"]:
                score += 15.0 - 2.0*self.visits[tr["next"]]
            elif tr["exact_changed"]>0:
                score -= 12.0
            else:
                score -= 30.0

        # Cheap calibration prior for directional controls.
        if name in {"ACTION1","ACTION2","ACTION3","ACTION4"}:
            score += 2.0

        # ACTION5 is treated as an evaluator/commit candidate only after
        # multiple structural edits have accumulated.
        if name=="ACTION5":
            if self.structural_edits_since_eval>=2:
                score += 25.0
            else:
                score -= 25.0

        return score

    def _pick(self,frame:FrameData)->tuple[GameAction,tuple,str]:
        lk=latent_key(frame)
        self.visits[lk]+=1
        self.recent_latent.append(lk)

        if lk in self.known_progress:
            tok=self.known_progress[lk]
            for a,t in self._candidates(frame):
                if t==tok:
                    return a,t,"known latent level-up edge"

        candidates=self._candidates(frame)
        if not candidates:
            return GameAction.RESET,("RESET",),"no candidates"

        # Prefer untried structural hypotheses at this latent state.
        scored=[]
        for a,t in candidates:
            s=self._score(lk,t)
            if t not in self.tried[lk]:
                s+=15.0
            # A long same-action streak is direct evidence that local novelty is
            # overpowering level-wide information coverage.
            if t[0]==self.last_action_name and self.same_action_streak>=3:
                s-=min(35.0,5.0*self.same_action_streak)
            scored.append((s,a,t))
        scored.sort(key=lambda x:(x[0],x[2]),reverse=True)

        # If every ordinary candidate is exhausted here and undo exists,
        # backtrack rather than looping.
        if all(t in self.tried[lk] for _,t in candidates) and GameAction.ACTION7 in legal(frame):
            return GameAction.ACTION7,("ACTION7",),"latent state exhausted; backtrack"

        s,a,t=scored[0]
        return a,t,"maximize structural novelty/progress"

    def _queue_visual_program(self,latest_frame:FrameData)->bool:
        plan,_why=solve_visible_program(grid(latest_frame))
        if plan is None:
            return False
        pairs=plan.get("click_pairs") or []
        if not pairs:
            return False
        level=int(getattr(latest_frame,"levels_completed",0))
        self.visual_plan.clear()
        for select,slot in pairs:
            self.visual_plan.append((GameAction.ACTION6,select,"visual grammar: select inferred symbol"))
            self.visual_plan.append((GameAction.ACTION6,slot,"visual grammar: assign inferred symbol"))
        self.visual_plan.append((GameAction.ACTION5,None,"visual grammar: execute synthesized program"))
        self.visual_plan_level=level
        return True

    def choose_action(self,frames:list[FrameData],latest_frame:FrameData)->GameAction:
        self._learn(latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED,GameState.GAME_OVER):
            self.last_frame=None
            self.last_token=None
            self.structural_edits_since_eval=0
            self.visual_plan.clear()
            self.visual_plan_level=None
            action=GameAction.RESET
            action.reasoning={"policy":"solve-whole-g2","why":"start/recover"}
            return action

        level=int(getattr(latest_frame,"levels_completed",0))
        if self.visual_plan_level is not None and level!=self.visual_plan_level:
            self.visual_plan.clear()
            self.visual_plan_level=None

        if not self.visual_plan:
            self._queue_visual_program(latest_frame)

        if self.visual_plan:
            action,data,why=self.visual_plan.popleft()
            if action is GameAction.ACTION6 and data is not None:
                x,y=data
                tok=("ACTION6",int(x),int(y))
                action.set_data({"x":int(x),"y":int(y)})
            else:
                tok=(action.name,)
            self.last_frame=latest_frame
            self.last_token=tok
            action.reasoning={
                "policy":"solve-whole-g2-visual-grammar",
                "why":why,
                "remaining_plan_actions":len(self.visual_plan),
            }
            return action

        action,tok,why=self._pick(latest_frame)
        aname=tok[0]
        if aname==self.last_action_name:
            self.same_action_streak+=1
        else:
            self.last_action_name=aname
            self.same_action_streak=1
        self.last_frame=latest_frame
        self.last_token=tok

        if action is GameAction.ACTION6 and len(tok)==3:
            _,x,y=tok
            action.set_data({"x":int(x),"y":int(y)})
            action.reasoning={
                "policy":"solve-whole-g2",
                "why":why,
                "latent_visits":self.visits[latent_key(latest_frame)],
                "structural_edits_since_eval":self.structural_edits_since_eval,
                "x":int(x),"y":int(y),
            }
        else:
            action.reasoning={
                "policy":"solve-whole-g2",
                "why":why,
                "latent_visits":self.visits[latent_key(latest_frame)],
                "structural_edits_since_eval":self.structural_edits_since_eval,
            }
        return action
