"""Generic trace -> A/B predictive-state constructor."""

from dataclasses import dataclass
from collections import defaultdict
from ab_family_closure import Occurrence,ab_family,project

@dataclass
class ABTraceModel:
    states: dict
    table: dict

    def encode(self, occurrence):
        return project(occurrence,self.states[occurrence.referent])

    def predict(self, occurrence):
        key=self.encode(occurrence)
        vals=self.table[key]
        if len(vals)!=1:
            raise ValueError(("non-closed A/B state",key,vals))
        return next(iter(vals))

def build_ab_model(occurrences):
    states=ab_family(occurrences)
    table=defaultdict(set)
    for o in occurrences:
        table[project(o,states[o.referent])].add(o.future)
    bad={k:v for k,v in table.items() if len(v)>1}
    if bad:
        raise ValueError(("A/B closure failed",bad))
    return ABTraceModel(states,dict(table))

def summarize(model):
    raw=len(model.states)
    refined=len(model.table)
    split={r:s for r,s in model.states.items() if s.retained_names}
    relation_sets=defaultdict(int)
    for s in model.states.values():
        relation_sets[s.retained_names]+=1
    return {
        "raw_referents":raw,
        "ab_states":refined,
        "extra_states":refined-raw,
        "split_referents":len(split),
        "relation_sets":dict(relation_sets),
    }
