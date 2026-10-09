"""
A/B completion-layer experiment.
The child space is allowed to oscillate, but it must RETURN once another
oscillation adds no new witnessed distinction.  The returned closure is then
the next evidence-bearing input; no semantic choice is inserted between them.
"""
from dataclasses import dataclass
from hashlib import sha256

@dataclass(frozen=True)
class Witness:
    state: bytes
    relation: tuple
    provenance: tuple

@dataclass
class Space:
    parent: Witness
    seen: dict
    frontier: list
    distinctions: set
    rounds_without_new: int = 0

def digest(board):
    return sha256(board.tobytes()).hexdigest()[:16]

def whole_witness(board, relation=(), provenance=()):
    return Witness(board.tobytes(), tuple(relation), tuple(provenance))

def oscillate(space, expand, completion_rounds=1):
    """
    One A/B child-space oscillation.
    Completion is structural: a full frontier oscillation produces no new
    whole-state distinction. It does NOT mean ARC level completion.
    """
    next_frontier=[]
    added=0
    for w in space.frontier:
        for move, board, env_result, relation in expand(w):
            k=digest(board)
            if k in space.seen:
                continue
            nw=whole_witness(board, relation, w.provenance+(move,))
            space.seen[k]=nw
            space.distinctions.add((relation,k))
            next_frontier.append(nw)
            added+=1
            if env_result.levels_completed:
                # environment completion remains evidence, never conflated
                # with child-space closure.
                pass
    space.frontier=next_frontier
    space.rounds_without_new = space.rounds_without_new+1 if added==0 else 0
    closed=space.rounds_without_new>=completion_rounds
    return closed, added

def return_completed(space):
    # Return the completed relational space itself one layer upward.
    # Do not pick a favorite member or summarize it into a heuristic.
    return {
        "parent": space.parent,
        "states": tuple(space.seen.values()),
        "distinctions": frozenset(space.distinctions),
        "closed": True,
    }

# Invariant:
#   child = AB(parent)
#   while not complete(child): child = AB(child)
#   parent_next = RETURN(child)
#   AB(parent_next)
#
# The critical difference from the previous guard file is executable ownership
# of oscillation/completion: the child space cannot silently become an
# unbounded search arena, and its closure cannot be replaced by my semantic
# interpretation before returning upward.
