"""
Same layer, architecture-vs-drift experiment.
We are NOT solving by search here. We compare ways the created structure
constrains what may happen after a witnessed relation.
"""
from dataclasses import dataclass
@dataclass
class Outcome:
    architecture:str; status:str; reason:str; allowed:int

def frontier_model(rel):
    # known bad control: every resulting state becomes new room
    return Outcome("frontier","DRIFT","novelty creates permission to expand",6)

def guard_model(rel):
    # prior guardrails: prose/rules constrain, but chooser remains outside
    return Outcome("guard","DRIFT","external chooser can reinterpret relation",len(rel.get("actions",())))

def reciprocal_model(rel):
    inv=rel.get("reciprocal")
    if inv is None:
        return Outcome("reciprocal","STOP","relation supplies no reciprocal",0)
    return Outcome("reciprocal","BOUND","only witnessed reciprocal may execute",1)

def paired_return_model(rel):
    inv=rel.get("reciprocal")
    invariant=rel.get("invariant")
    if inv is None or invariant is None:
        return Outcome("paired_return","STOP","cannot form completed local return",0)
    # completed pair is returned; child states are no longer selectable space
    return Outcome("paired_return","RETURN","oscillation collapses to invariant",1)

def ownership_model(rel):
    # strongest current variant: the created relation owns both continuation
    # and its completion test. No caller choice exists inside child oscillation.
    if not rel.get("owns_next",False):
        return Outcome("ownership","STOP","continuation would come from outside child",0)
    if not rel.get("owns_completion",False):
        return Outcome("ownership","STOP","completion would be judged externally",0)
    return Outcome("ownership","RETURN","child owns oscillation and closure",1)

# ARC evidence-shaped fixtures; not claims that action IDs have permanent meaning.
fixtures=[
 {"name":"8_to_0","actions":(1,2,3,4,5,7),"reciprocal":2,"invariant":"structured_color_relation","owns_next":True,"owns_completion":True},
 {"name":"8_to_16","actions":(1,2,3,4,5,7),"reciprocal":1,"invariant":"replacement_block_relation","owns_next":True,"owns_completion":True},
 {"name":"marker_8_to_21","actions":(1,2,3,4,5,7),"reciprocal":5,"invariant":"marker_representation_relation","owns_next":True,"owns_completion":True},
 {"name":"unresolved","actions":(1,2,3,4,5,7),"reciprocal":None,"invariant":None,"owns_next":False,"owns_completion":False},
]
models=[frontier_model,guard_model,reciprocal_model,paired_return_model,ownership_model]
for f in fixtures:
 print("\nREL",f["name"])
 for m in models:
  o=m(f);print(o.architecture,o.status,"allowed",o.allowed,"-",o.reason)
