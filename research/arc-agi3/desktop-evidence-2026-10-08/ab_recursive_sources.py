"""Recursive A/B over prior A/B states with multiple minimal source families."""
from dataclasses import dataclass
from collections import defaultdict
from ab_family_all_minima import Occurrence,ab_family_all

@dataclass(frozen=True)
class PriorAB:
    referent: object
    continuation_class: object
    sources: tuple

def lift_prior(prior,relations,future):
    # Prior A/B output is itself the referent.
    # Source family remains provenance, not flattened into relation names.
    rel=(("prior_sources",prior.sources),)+tuple(relations)
    return Occurrence(prior,rel,future)

def recursive_family(occurrences):
    return ab_family_all(occurrences)
