"""A/B refinement when formerly equivalent minimal witness sources diverge later."""
from dataclasses import dataclass
from collections import defaultdict
from ab_family_all_minima import Occurrence,ab_family_all

@dataclass(frozen=True)
class SourcePath:
    names: tuple
    values: tuple

@dataclass(frozen=True)
class ProvenanceState:
    referent: object
    continuation_class: object
    source_paths: tuple

def source_occurrences(state, future_by_path):
    out=[]
    for p in state.source_paths:
        future=future_by_path[p]
        rel=(
            ("source_names",p.names),
            ("source_values",p.values),
        )
        out.append(Occurrence(state,rel,future))
    return out

def refine_sources(state,future_by_path):
    return ab_family_all(source_occurrences(state,future_by_path))[state]
