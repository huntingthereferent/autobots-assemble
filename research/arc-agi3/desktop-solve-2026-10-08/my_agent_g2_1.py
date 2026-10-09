"""ARC3 direct G2.1 — latent explorer + evidence-gated visual schemas."""
from __future__ import annotations
from typing import Any
from arcengine import GameAction, GameState
from my_agent_g2 import MyAgent as G2Base
from schemas import detect_reference_palette_fill

class MyAgent(G2Base):
    def __init__(self,*args:Any,**kwargs:Any):
        super().__init__(*args,**kwargs)
        self.schema_plan=[]
        self.schema_level=None
        self.schema_name=None

    @property
    def name(self):
        return f"{super().name}.schema-g2-1"

    def _schema_action(self, latest_frame):
        level=int(getattr(latest_frame,"levels_completed",0))
        if self.schema_level != level:
            self.schema_plan=[]
            self.schema_level=level
            self.schema_name=None
            found=detect_reference_palette_fill(latest_frame)
            if found:
                self.schema_plan=list(found["plan"])
                self.schema_name=found["schema"]

        if not self.schema_plan:
            return None

        aname,data=self.schema_plan.pop(0)
        action=getattr(GameAction,aname)
        tok=self.tok(action,data)
        if action is GameAction.ACTION6 and data is not None:
            x,y=data
            action.set_data({"x":int(x),"y":int(y)})
            action.reasoning={
                "policy":"schema-g2-1",
                "schema":self.schema_name,
                "why":"visible reference/palette/slot relation",
                "x":int(x),"y":int(y),
            }
        else:
            action.reasoning={
                "policy":"schema-g2-1",
                "schema":self.schema_name,
                "why":"evaluate completed visible relation",
            }
        return action,tok

    def choose_action(self,frames,latest_frame):
        self.learn(latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED,GameState.GAME_OVER):
            self.last_frame=None
            self.last_token=None
            self.force_backtrack=False
            self.schema_plan=[]
            self.schema_level=None
            self.schema_name=None
            a=GameAction.RESET
            a.reasoning={"policy":"schema-g2-1","why":"start/recover"}
            return a

        schema=self._schema_action(latest_frame)
        if schema is not None:
            a,t=schema
            self.last_frame=latest_frame
            self.last_token=t
            return a

        a,t,data,why=self.choose(latest_frame)
        self.last_frame=latest_frame
        self.last_token=t
        if a is GameAction.ACTION6 and data is not None:
            x,y=data
            a.set_data({"x":int(x),"y":int(y)})
            a.reasoning={"policy":"schema-g2-1","why":why,"x":int(x),"y":int(y)}
        else:
            a.reasoning={"policy":"schema-g2-1","why":why}
        return a
