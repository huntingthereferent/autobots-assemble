"""Native SK48 phase: continuation witness carries invisible difference into same A/B agent."""
import sys,json,logging
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
sys.path.insert(0,r"C:\Users\teepa\continuity-live")
from runtime.observed_evaluator import ObservedTransition
from runtime.service import EcosystemService
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
l1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
old=json.loads((F/"sk48_l2_directional_phase_cross_source_ab.json").read_text())
e=next(v for v in old["examples"] if v["suffix"]==[1,1,1])
def sig(o):
 return "%d:%s:%s"%(o.levels_completed,o.state.name,
   sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20])
def trial(phase):
 g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in l1:
  o=g.step(GameAction.from_id(z),data={})
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 before=o
 if phase:o=g.step(GameAction.ACTION2,data={})
 pre=sig(o)
 suffix=[]
 for z in [1,1,1]:
  o=g.step(GameAction.from_id(z),data={})
  suffix.append(sig(o))
 return pre,suffix,sig(before)
b,trace0,root0=trial(0)
a,trace1,root1=trial(1)
assert b==a==root0==root1
assert trace0!=trace1
assert trace0==e["trajectories"]["0"]
assert trace1==e["trajectories"]["1"]
class Queue:
 def __init__(self):self.data={}
 def has_capture(self,root):return root in self.data
 def __call__(self,handoff,state):return self.data.get(handoff.handoff_id)
sink=Queue()
with TemporaryDirectory(prefix="ab_phase_compare_") as temp:
 svc=EcosystemService(data_dir=temp,native_observer=sink)
 ref="SK48 native same-frame phase distinction"
 root=svc.activate_agent({"surface":"begin comparison",
   "actor_id":"james","instance_id":"inverse-ab-phase-native-test",
   "referent":ref})["root"]
 def locator(trace):
  return "arc://sk48/native-future/sha256:"+sha256(json.dumps(trace).encode()).hexdigest()
 prior={"public_state":b,"future_111":trace0}
 actual={"public_state":a,"future_111":trace1}
 sink.data[root]=ObservedTransition(referent=ref,
  before=prior,after=actual,
  before_ref=locator(trace0),after_ref=locator(trace1),
  action="native L2 ACTION2; 111 holdout continuation",
  source="arc-agi-3:sk48:two-independent-native-continuation-replays",
  evidence_kind="measurement",
  predicted_after={"public_state":a,"future_111":e["trajectories"]["1"]})
 svc.agent_lineage.step(root)
 st=svc.runtime.state(root)
 assert st.status=="COMPLETE",(st.status,st.output)
 assert st.output["ab_state"]=="MOVE"
 assert st.output["prediction_matched"] is True
 assert "future_111" in st.output["changed"]
 assert "public_state" in st.output["survived"]
 assert len(st.evidence)==1
 result={"native_replays":2,"public_frame_identical":True,
  "forward_suffix":[1,1,1],"prior_witness_prediction_matched":True,
  "future_traces_distinct":True,"existing_agent_status":st.status,
  "ab_state":st.output["ab_state"],
  "surviving_state":"same public frame",
  "changed_relation":"witnessed three-step native continuation",
  "witness_kind":"measurement","repo_modified":False}
 dest=F/"AB_INVERSE_AGENT_NATIVE_PHASE_CORRECTION_2026-10-08.json"
 dest.write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("NATIVE_PHASE_A_B_CORRECTION_PASS",result,"SAVED",dest,flush=True)
