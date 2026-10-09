"""A/B trace machine with all minimal witness sources preserved."""

from dataclasses import dataclass
from collections import defaultdict
from ab_family_all_minima import ab_family_all,separator_values,predictive_class_map

@dataclass
class ABTraceState:
    referent: object
    minimal_sources: tuple
    source_maps: tuple

@dataclass
class ABTraceModelV2:
    states: dict

    def predict(self, occurrence):
        s=self.states[occurrence.referent]
        preds=[]
        for subset,m in s.source_maps:
            key=separator_values(occurrence,subset)
            if key in m:
                preds.append(m[key])
        if not preds:
            raise ValueError(("no witnessed source applies",occurrence.referent))
        first=preds[0]
        if any(p!=first for p in preds[1:]):
            raise ValueError(("minimal witness sources disagree",occurrence.referent,preds))
        return first

def build_ab_model_all_sources(occurrences):
    fam=ab_family_all(occurrences)
    groups=defaultdict(list)
    for o in occurrences:groups[o.referent].append(o)
    states={}
    for ref,fs in fam.items():
        maps=predictive_class_map(groups[ref],fs)
        states[ref]=ABTraceState(ref,fs.minimal_separator_sets,maps)
    model=ABTraceModelV2(states)
    for o in occurrences:
        assert model.predict(o)==o.future
    return model

def summarize(model):
    n_plain=sum(1 for s in model.states.values() if s.minimal_sources==((),))
    n_split=len(model.states)-n_plain
    source_counts=defaultdict(int)
    for s in model.states.values():source_counts[s.minimal_sources]+=1
    return {
        "referents":len(model.states),
        "plain":n_plain,
        "split":n_split,
        "source_families":dict(source_counts),
    }
