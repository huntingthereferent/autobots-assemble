"""ARC-AGI-3 actual observation -> James AgentLineage, isolated integration test."""
from __future__ import annotations
import hashlib
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from runtime.activation import ActivationRegistry, ActivationRoute
from runtime.agent_lineage import AgentLineage
from runtime.engine import HandoffRuntime
from runtime.observed_evaluator import NativeABEvaluator, ObservedTransition


def obs(frame, x=36, y=36):
    grid=np.asarray(frame.frame[-1],dtype=np.int16).reshape((64,64))
    return {"cell_color": int(grid[y,x]), "levels_completed": frame.levels_completed}


def locator(frame):
    grid=np.asarray(frame.frame[-1],dtype=np.int16)
    return "arc://ft09/local/frame/" + hashlib.sha256(grid.tobytes()).hexdigest()[:24]


arc=Arcade(operation_mode=OperationMode.NORMAL)
game=arc.make("ft09")
before=game.observation_space
pre=obs(before)
pre_ref=locator(before)
after=game.step(GameAction.ACTION6,data={"x":36,"y":36})
post=obs(after)
post_ref=locator(after)
prediction=dict(pre,cell_color=(8 if pre["cell_color"]==9 else 9))
witness=ObservedTransition(
    referent="ft09 current board",
    source="local ARC-AGI-3 observed frame pair",
    action="ACTION6 click(36,36)",
    before=pre,
    after=post,
    predicted_after=prediction,
    before_ref=pre_ref,
    after_ref=post_ref,
)
reg=ActivationRegistry((ActivationRoute(
    activation_id="arc-ab-test",
    surfaces=("compare-arc",),
    actor_id="test",
    referent="ft09 current board",
    projection="agent_lineage",
),))
runtime=HandoffRuntime()
lineage=AgentLineage(
    runtime,reg,
    evaluate=NativeABEvaluator(lambda handoff,state:witness),
    allow_simulation=False,
)
root=lineage.activate("compare-arc",actor_id="test",instance_id="one")
move=lineage.step(root)
result=runtime.state(root)
assert result.status=="COMPLETE",result.output
assert result.output["observed"]==post
assert result.output["prediction_matched"] is True
assert result.evidence[0].ref==post_ref
assert move.executed==(root,)
assert lineage.step(root).executed==()
print("FT09_TO_JAMES_AB",{"before":pre,"after":post,
    "predicted":prediction,"lineage_status":result.status,
    "ab_state":result.output["ab_state"],
    "survived":result.output["survived"],
    "changed":result.output["changed"],
    "native_ref":result.evidence[0].ref,
    "repeat_does_not_reexecute":True})
