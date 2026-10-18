"""Inverse fixed-word observations for original 48 F3 window laws; NOT REA."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
from .window_combined import CombinedWorld, family, fixed_word_formula, classify_pair, rooted_conflict

WORDS=("B","BBB","AABAB","ABABAB")

@dataclass(frozen=True)
class Observation:
    word: str
    fixed: int
    def __post_init__(self):
        if self.word not in WORDS: raise ValueError("unsupported fixed-word invariant")
        if type(self.fixed) is not int or not 0 <= self.fixed <= 27:
            raise ValueError("fixed count must be 0..27")

@lru_cache(maxsize=192)
def measured(w:CombinedWorld,word:str)->int:
    if word not in WORDS:raise ValueError("unsupported word")
    return w.fixed_word(word,3)

def ident(w):
    return (w.support,w.coefficient,w.pulse,w.balanced)

@dataclass(frozen=True)
class Investigation:
    observations:tuple[Observation,...]=()
    def __post_init__(self):
        if any(not isinstance(x,Observation) for x in self.observations):
            raise ValueError("invalid evidence")
        if len({x.word for x in self.observations})!=len(self.observations):
            raise ValueError("duplicate word")
    def admit(self,observation:Observation)->"Investigation":
        if not isinstance(observation,Observation):raise TypeError("needs observation")
        previous={x.word:x.fixed for x in self.observations}
        if observation.word in previous:
            if previous[observation.word]!=observation.fixed:
                raise ValueError("conflicting observation")
            return self
        return Investigation(self.observations+(observation,))
    @property
    def candidates(self):
        return tuple(w for w in family() if all(measured(w,o.word)==o.fixed
                                                for o in self.observations))
    def next_probe(self):
        worlds=self.candidates
        if len(worlds)<2:return None
        used={o.word for o in self.observations}
        best=None
        for word in WORDS:
            if word in used:continue
            buckets={}
            for w in worlds:
                buckets.setdefault(measured(w,word),[]).append(ident(w))
            if len(buckets)<2:continue
            outcomes=tuple((value,tuple(members)) for value,members in sorted(buckets.items()))
            worst=max(map(len,buckets.values()))
            pairs=len(worlds)*(len(worlds)-1)//2
            remaining=sum(len(v)*(len(v)-1)//2 for v in buckets.values())
            key=(worst,remaining,len(word),word)
            if best is None or key<best[0]:
                best=(key,word,outcomes)
        return None if best is None else {
            "word":best[1],"worst_case_survivors":best[0][0],
            "separated_pairs":len(worlds)*(len(worlds)-1)//2-best[0][1],
            "possible_fixed_counts_NOT_OBSERVATIONS": [
                {"count":n,"laws":[list(p) for p in laws]} for n,laws in best[2]],
        }
    def root_obstruction(self):
        remaining=self.candidates
        if not remaining or self.next_probe() is not None:return None
        for a,b in combinations(remaining,2):
            classified=classify_pair(a,b)
            if classified.kind is None:
                raise AssertionError("counts failed existing full conjugacy classification")
            if classified.root_preserving:continue
            collision=rooted_conflict(a,b)
            if collision is None:raise AssertionError("expected rooted obstruction")
            w1,w2,same,first,second=collision
            origin=(0,0,0)
            if (a.apply(origin,w1)!=same or a.apply(origin,w2)!=same
                or b.apply(origin,w1)!=first or b.apply(origin,w2)!=second
                or first==second):
                raise AssertionError("source rooted witness invalid")
            return {"source":list(ident(a)),"target":list(ident(b)),
                    "same_source_words":[w1,w2],
                    "source_endpoint":list(same),
                    "distinct_target_endpoints":[list(first),list(second)],
                    "PREDICTED_mathematical_root_witness_not_external_observation":True}
        return None
    def receipt(self):
        candidates=self.candidates
        probe=self.next_probe()
        root=self.root_obstruction() if probe is None else None
        status=("CONTRADICTION" if not candidates else
                "NEXT_INVARIANT_PROPOSED" if probe is not None else
                "FULL_CLASS_KNOWN_ROOTED_DISTINCTION_OPEN" if root else
                "ROOTED_CLASS_IDENTIFIED_WITHIN_FAMILY")
        source=Path(__file__).resolve()
        return {"kind":"WINDOW48_INVERSE_FIXED_WORD_OBSERVATION",
                "status":status,
                "math_source_sha256":sha256(source.with_name("window_combined.py").read_bytes()).hexdigest(),
                "engine_source_sha256":sha256(source.read_bytes()).hexdigest(),
                "observations":[{"word":x.word,"fixed":x.fixed} for x in self.observations],
                "candidate_laws":[list(ident(w)) for w in candidates],
                "next":probe,"rooted_obstruction":root,
                "rooted_and_unpointed_NOT_interchangeable":True,
                "no_native_arc_or_universal_referent_claim":True}

def certify_partition():
    groups={}
    for w in family():
        signature=tuple(measured(w,word) for word in WORDS)
        groups.setdefault(signature,[]).append(w)
        for word,n in zip(WORDS,signature):
            if n!=fixed_word_formula(word,3,w.support,w.pulse,w.balanced):
                raise AssertionError("source and proved formula disagree")
    sizes=sorted(map(len,groups.values()))
    if len(groups)!=14 or sizes != [3]*12+[6]*2:
        raise AssertionError("full-state invariant partition not reproduced")
    nonroot=0
    roots=set()
    for laws in groups.values():
        for a,b in combinations(laws,2):
            relation=classify_pair(a,b)
            if relation.kind is None:
                raise AssertionError("identical signature lacks full-state map")
            if not relation.root_preserving:nonroot+=1
        roots.update((w.support,w.pulse,w.balanced) for w in laws)
    if len(roots)!=16 or nonroot!=18:
        raise AssertionError("rooted classes or obstructions changed")
    return {"status":"CLASSIFIED_DECLARED_WINDOW48",
            "laws":48,"full_state_classes":14,"rooted_classes":16,
            "full_class_sizes":sizes,"unpointed_nonroot_unordered_pairs":nonroot,
            "verified_formula_words":list(WORDS),
            "observations_are_only_declared_mathematical_invariants":True}

def main():
    import argparse
    p=argparse.ArgumentParser(description="A/B 48-law source inverse mathematical investigator")
    p.add_argument("--observe",action="append",default=[],help="WORD=COUNT")
    p.add_argument("--demo-law",help="SYNTHETIC k,c,pulse,balanced")
    p.add_argument("--certificate",action="store_true")
    args=p.parse_args()
    state=Investigation()
    for value in args.observe:
        word,sep,n=value.partition("=")
        if not sep:p.error("use WORD=COUNT")
        state=state.admit(Observation(word,int(n)))
    result={"initial":state.receipt()}
    if args.demo_law:
        world=CombinedWorld(*(int(x) for x in args.demo_law.split(",")))
        steps=[]
        while (probe:=state.next_probe()) is not None:
            number=measured(world,probe["word"])
            state=state.admit(Observation(probe["word"],number))
            steps.append({"word":probe["word"],"SYNTHETIC_count":number,
                          "remaining":len(state.candidates)})
        result["synthetic_math_demo"]={
            "source_law":list(ident(world)),"steps":steps,
            "final":state.receipt(),"not_native_arc":True}
    if args.certificate:result["certificate"]=certify_partition()
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
