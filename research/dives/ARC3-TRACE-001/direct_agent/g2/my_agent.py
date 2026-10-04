"""ARC3 direct G2.3 — typed recursive program induction + latent fallback."""
from __future__ import annotations
from typing import Any
from arcengine import GameAction,GameState
from my_agent_g2 import MyAgent as G2Base
from typed_program_schema import induce_typed_program

class MyAgent(G2Base):
    def __init__(self,*args:Any,**kwargs:Any):
        super().__init__(*args,**kwargs)
        self.program_plan=[]
        self.program_level=None
        self.program_meta=None

    @property
    def name(self):
        return f"{super().name}.typed-program-g2-3"

    def _program_action(self,latest_frame):
        level=int(getattr(latest_frame,"levels_completed",0))
        if self.program_level!=level:
            self.program_plan=[]
            self.program_level=level
            self.program_meta=induce_typed_program(latest_frame)
            if self.program_meta:
                self.program_plan=list(self.program_meta["plan"])

        if not self.program_plan:
            return None
        aname,data=self.program_plan.pop(0)
        action=getattr(GameAction,aname)
        tok=self.tok(action,data)
        reasoning={
            "policy":"typed-program-g2-3",
            "schema":"typed_recursive_program",
            "why":"synthesize visible typed program whose recursive expansion matches target",
        }
        if self.program_meta:
            reasoning["root"]=self.program_meta.get("root")
            reasoning["periodic_witness"]=self.program_meta.get("periodic_witness",False)
        if action is GameAction.ACTION6 and data is not None:
            x,y=data
            action.set_data({"x":int(x),"y":int(y)})
            reasoning["x"]=int(x);reasoning["y"]=int(y)
        action.reasoning=reasoning
        return action,tok

    def choose_action(self,frames,latest_frame):
        self.learn(latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED,GameState.GAME_OVER):
            self.last_frame=None
            self.last_token=None
            self.force_backtrack=False
            self.program_plan=[]
            self.program_level=None
            self.program_meta=None
            a=GameAction.RESET
            a.reasoning={"policy":"typed-program-g2-3","why":"start/recover"}
            return a

        p=self._program_action(latest_frame)
        if p is not None:
            a,t=p
            self.last_frame=latest_frame
            self.last_token=t
            return a

        a,t,data,why=self.choose(latest_frame)
        self.last_frame=latest_frame
        self.last_token=t
        if a is GameAction.ACTION6 and data is not None:
            x,y=data
            a.set_data({"x":int(x),"y":int(y)})
            a.reasoning={"policy":"typed-program-g2-3","why":why,"x":int(x),"y":int(y)}
        else:
            a.reasoning={"policy":"typed-program-g2-3","why":why}
        return a