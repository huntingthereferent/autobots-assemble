"""Construct a finite ROOTED equality-question plan for the ORIGINAL 48 laws.

Authoritative source: window_combined.CombinedWorld and rooted_conflict.
Mathematical *full-state* fixed-word counts do not supply a rooted experiment:
the original family has 14 full-state classes but SIXTEEN origin-preserving
classes, and some source conjugacies move the marked origin.

For every ordered pair of the 16 marked representative worlds, derive an
actual collision of two A/B words from the source-root BFS. Select a small
deterministic greedy cover of rooted equality/inequality questions that
separates all 16 signatures. Cross-check the 48 concrete worlds collapse
into exactly the 16 marked classes (three shear charts each).

This is a rooted MATHEMATICAL test plan only, not evidence ARC realizes it.
Native states, action assignments, and equality of hidden states require a
separate, source-owned native experiment. No ARC solver or game simulation.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path

from work.arc_like_maze.window_combined import (
    CombinedWorld, classify_pair, family, rooted_conflict,
)


ORIGIN = (0,0,0)


def representatives():
    """Canonical shear chart c=0 for each of the 16 rooted classes."""
    return tuple(CombinedWorld(k,0,e,t)
                 for k in range(4) for e in (0,1) for t in (0,1))


def parameters(w):
    return [w.support,w.coefficient,w.pulse,w.balanced]


def root_class_key(w):
    return (w.support,w.pulse,w.balanced)


def equality(w, question):
    a,b = question
    return w.apply(ORIGIN,a) == w.apply(ORIGIN,b)


def plan():
    sources = family()
    reps = representatives()
    if len(sources)!=48 or len(reps)!=16:
        raise AssertionError("original source/window class count changed")
    for w in reps:
        if w.coefficient != 0:
            raise AssertionError("rooted base charts were not fixed")

    # Literal rooted source collisions (not the source's unrooted Fix(word)
    # counts), generated for both ordered directions to avoid asymmetric
    # signatures hiding a class distinction.
    question_origins = {}
    for i,a in enumerate(reps):
        for j,b in enumerate(reps):
            if i==j:
                continue
            event=rooted_conflict(a,b)
            if event is None:
                raise AssertionError(
                    f"distinct marked classes {i},{j} lacked rooted counterexample")
            old,new,source_end,target_old,target_new=event
            if a.apply(ORIGIN,old)!=a.apply(ORIGIN,new):
                raise AssertionError("generated source collision is invalid")
            if b.apply(ORIGIN,old)==b.apply(ORIGIN,new):
                raise AssertionError("generated target split is invalid")
            if source_end!=a.apply(ORIGIN,old):
                raise AssertionError("source endpoint provenance changed")
            question=(old,new)
            question_origins.setdefault(question,[]).append([i,j])

    all_questions=sorted(question_origins,
                         key=lambda q:(max(map(len,q)),sum(map(len,q)),q))
    signatures={
        q: tuple(equality(w,q) for w in reps)
        for q in all_questions
    }
    pairs=set(combinations(range(16),2))
    uncovered=set(pairs)
    chosen=[]
    while uncovered:
        options=[]
        for q in all_questions:
            hits={p for p in uncovered if
                  signatures[q][p[0]] != signatures[q][p[1]]}
            if hits:
                options.append((
                    -len(hits),max(map(len,q)),sum(map(len,q)),q,hits
                ))
        if not options:
            raise AssertionError("original 16 rooted classes not distinguishable")
        _negative_count, _max_len, _total_len,q,hits=min(
            options,key=lambda x:x[:4])
        chosen.append({"words":list(q),
                       "representative_root_equalities":list(signatures[q]),
                       "new_class_pairs_separated":len(hits),
                       "source_ordered_pair_witnesses":question_origins[q]})
        uncovered-=hits

    chosen_q=[tuple(item["words"]) for item in chosen]
    marked_signatures={}
    for w in sources:
        key=root_class_key(w)
        sig=tuple(equality(w,q) for q in chosen_q)
        marked_signatures.setdefault(key,set()).add(sig)
    if len(marked_signatures)!=16:
        raise AssertionError("root classes did not cover original family")
    if any(len(values)!=1 for values in marked_signatures.values()):
        raise AssertionError("source shear charts unexpectedly split a rooted class")
    if len(set(next(iter(x)) for x in marked_signatures.values()))!=16:
        raise AssertionError("selected source questions did not separate rooted classes")

    examples=[]
    for k in (0,3):
        a=CombinedWorld(k,0,1,0)
        b=CombinedWorld(k,0,1,1)
        relation=classify_pair(a,b)
        if relation.root_preserving or relation.kind!="FIBER_SHIFT":
            raise AssertionError("original nonroot conjugacy boundary changed")
        sa=next(iter(marked_signatures[root_class_key(a)]))
        sb=next(iter(marked_signatures[root_class_key(b)]))
        if sa==sb:
            raise AssertionError("nonroot but full-conjugate worlds collapsed")
        contrast=[list(chosen_q[i]) for i in range(len(chosen_q))
                  if sa[i]!=sb[i]]
        examples.append({
            "support":k,
            "source_parameters":parameters(a),
            "target_parameters":parameters(b),
            "full_state_conjugacy_kind":relation.kind,
            "root_preserving":relation.root_preserving,
            "rooted_question_contrasts":contrast,
        })
    return {
        "kind":"ORIGINAL_WINDOW48_ROOTED_DISCRIMINATING_QUESTION_PLAN",
        "math_source":"work/arc_like_maze/window_combined.py",
        "worlds":48,
        "full_state_classes":14,
        "origin_preserving_classes":16,
        "representative_parameters":[parameters(x) for x in reps],
        "rooted_collision_candidate_pairs":len(all_questions),
        "ordered_source_pair_witnesses":16*15,
        "selection":"deterministic greedy finite cover; NOT a proven globally minimal test set",
        "questions":chosen,
        "questions_selected":len(chosen),
        "maximum_selected_word_length":max(
            len(word) for q in chosen_q for word in q),
        "source_class_rooted_signatures":[{
            "key":list(k),
            "equality_signature":list(next(iter(v))),
        } for k,v in sorted(marked_signatures.items())],
        "origin_moving_full_conjugacy_not_root_equivalent_examples":examples,
        "meaning":(
            "These equality questions separate exactly the 16 ROOTED classes "
            "of the original 48 mathematical laws; there is NO asserted "
            "native action correspondence, F3 quotient, ARC success, or "
            "hidden-state equivalence. Applying questions to native ARC "
            "requires independently established generator semantics. "
            "Visible equality alone cannot prove a hidden-state match."
        ),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/window48-rooted-questions.json"))
    args=parser.parse_args()
    result=plan()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print("WINDOW48_ROOTED_QUESTION_PLAN "+json.dumps({
        "concrete_source_laws":result["worlds"],
        "rooted_classes":result["origin_preserving_classes"],
        "full_state_classes":result["full_state_classes"],
        "source_candidate_word_pairs":result["rooted_collision_candidate_pairs"],
        "questions_selected":result["questions_selected"],
        "maximum_selected_word_length":result["maximum_selected_word_length"],
        "selected_word_pairs":[q["words"] for q in result["questions"]],
        "nonrooted_examples":[{
            "support":e["support"],
            "rooted_contrasts":e["rooted_question_contrasts"]
        } for e in result["origin_moving_full_conjugacy_not_root_equivalent_examples"]],
        "record":str(args.out),
    },sort_keys=True))


if __name__=="__main__":
    main()
