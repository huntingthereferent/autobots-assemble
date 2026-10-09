"""Independent self-contained arithmetic witness for the completed F3 window.

Intentionally imports no repository construction/classifier modules. Verifies
48 concrete laws, 14 full-state classes versus 16 rooted classes, four
labeled-word invariants, and a nonrooted all-depth coordinate chart.

Run:
    python -m work.arc_like_maze.window_combined_arithmetic_audit

Finite checking is not universal A/B closure. All-depth proofs use explicit
triangular inverse, projection, and state-map algebra.
"""
from collections import Counter, deque
from itertools import product

PARAMETERS = tuple(product(range(4), range(2), range(2), range(3)))
WORDS = ("B", "BBB", "AABAB", "ABABAB")


def action(state, p, operation):
    k, e, t, c = p
    u, v, z, *tail = state
    if operation == "A":
        return ((u + 1) % 3, v, z, *tail)
    if operation != "B":
        raise ValueError("operation must be A/B")
    added = (
        int(u == 2 and v < k)
        + e * int(u == 0 and v == 0)
        + t * (int(u == 1 and v == 0) -
               int(u == 1 and v == 1))
        + c * ((v + u + 1)**2 - v**2)
    ) % 3
    return (u, (v + u + 1) % 3, (z + added) % 3, *tail)


def undo(state, p, operation):
    k, e, t, c = p
    u, v, z, *tail = state
    if operation == "A":
        return ((u - 1) % 3, v, z, *tail)
    if operation != "B":
        raise ValueError("operation must be A/B")
    old_v = (v - u - 1) % 3
    sub = (int(u == 2 and old_v < k)
           + e * int((u, old_v) == (0, 0))
           + t * (int((u, old_v) == (1, 0)) -
                  int((u, old_v) == (1, 1)))
           + c * ((old_v + u + 1)**2-old_v**2)) % 3
    return (u, old_v, (z - sub) % 3, *tail)


def shear(state, c):
    u, v, z, *tail = state
    return (u, v, (z+c*v*v) % 3, *tail)


def bridge(state, direction):
    """Bridge pulse-only and combined rule at support 0 or 3."""
    u, v, z, *tail = state
    if direction == 1:
        return (u, (v+2) % 3, (z+(2 if v == 1 else 0)) % 3,
                *tail)
    if direction == -1:
        old_v = (v+1) % 3
        return (u, old_v, (z-(2 if old_v == 1 else 0)) % 3,
                *tail)
    raise ValueError("unsupported bridge direction")


def map_state(state, source, target):
    if source[:3] == target[:3]:
        return shear(state, (target[3]-source[3]) % 3)
    if source[0] in (0, 3) and target[0] == source[0] \
            and source[1] == target[1] == 1 and \
            source[2] != target[2]:
        old = shear(state, (-source[3]) % 3)
        middle = bridge(old, 1 if source[2] == 0 else -1)
        return shear(middle, target[3])
    raise ValueError("no proven full-state conjugacy")


def word_image(state, p, word):
    for op in word:
        state = action(state, p, op)
    return state


def count_fixed(p, word, states):
    return sum(word_image(s, p, word) == s for s in states)


def category(source, target):
    k,e,t,c=source
    l,f,u,d=target
    if k!=l:return "B"
    if e!=f:return "BBB"
    if t!=u:
        if e==0:return "AABAB"
        return "nonroot" if k in (0,3) else "ABABAB"
    return "root"


def root_collision(source, target):
    zero = (0, 0, 0)
    reached = {zero: (zero, "")}
    queue = deque([(zero, zero, "")])
    while queue:
        a,b,path = queue.popleft()
        for label in "AB":
            x,y=action(a,source,label),action(b,target,label)
            if x in reached:
                former, word = reached[x]
                if y != former:
                    return word, path+label, x, former, y
            else:
                reached[x] = (y,path+label)
                queue.append((x,y,path+label))
    return None


def audit():
    states3 = tuple(product(range(3), repeat=3))
    signatures = {
        tuple(action(state, p, "B") for state in states3)
        for p in PARAMETERS
    }
    if len(signatures)!=48:
        raise AssertionError("worlds are not concretely distinct")
    counts=Counter()
    # Pairwise completeness: 2304 comparisons.
    for source in PARAMETERS:
        for target in PARAMETERS:
            kind=category(source,target)
            counts[kind]+=1
            if kind in ("B","BBB","AABAB","ABABAB"):
                if count_fixed(source,kind,states3) == count_fixed(target,kind,states3):
                    raise AssertionError(("failed word obstruction", source,target,kind))
            else:
                for state in states3:
                    image = map_state(state,source,target)
                    for op in "AB":
                        if map_state(action(state,source,op),source,target) != action(image,target,op):
                            raise AssertionError(("conjugacy mismatch",source,target,state,op))
                if kind=="root":
                    if map_state((0,0,0),source,target)!=(0,0,0):
                        raise AssertionError("rooted map moved root")
                else:
                    if map_state((0,0,0),source,target)==(0,0,0):
                        raise AssertionError("nonroot bridge unexpectedly fixes origin")
                    if root_collision(source,target) is None:
                        raise AssertionError("nonroot bridge lacks rooted counterexample")
                    counts["rooted_conflicts"]+=1
    expected_classes={"root":144,"nonroot":36,"B":1728,"BBB":288,
                      "AABAB":72,"ABABAB":36,"rooted_conflicts":36}
    if counts != expected_classes:
        raise AssertionError(("pair classification changed",dict(counts)))

    # Independent depth 3..6 state exhaustive arithmetic.
    totals=Counter()
    for p in PARAMETERS:
        base={}
        for depth in range(3,7):
            space=tuple(product(range(3), repeat=depth))
            for state in space:
                for op in "AB":
                    moved=action(state,p,op)
                    if undo(moved,p,op) != state:
                        raise AssertionError(("inverse",p,depth,state,op))
                    totals["inverses"]+=1
                    if depth>3:
                        if action(state[:-1],p,op)!=moved[:-1]:
                            raise AssertionError(("projection",p,depth,state,op))
                        totals["projections"]+=1
                    for target_chart in range(3):
                        newp=p[:3]+(target_chart,)
                        delta=(target_chart-p[3])%3
                        if shear(moved,delta)!=action(shear(state,delta),newp,op):
                            raise AssertionError(("shear",p,newp,depth,state,op))
                        totals["shear_conjugacies"]+=1
            for word in WORDS:
                value = count_fixed(p,word,space)
                if depth==3:
                    base[word]=value
                elif value != base[word]*3**(depth-3):
                    raise AssertionError(("fixed word formula",p,word,depth))
                totals["fixed_word_formulas"]+=1
    expect={"inverses":103680,"projections":101088,
            "shear_conjugacies":311040,"fixed_word_formulas":768}
    if totals!=expect:
        raise AssertionError(("unexpected arithmetic totals",dict(totals)))

    # Minimal new word-count obstruction for the two middle supports.
    for k in (1,2):
        source=(k,1,0,0)
        target=(k,1,1,0)
        for length in range(1,6):
            for word in product("AB",repeat=length):
                w="".join(word)
                if count_fixed(source,w,states3)!=count_fixed(target,w,states3):
                    raise AssertionError(("unexpected shorter witness",k,w))
        a=count_fixed(source,"ABABAB",states3)
        b=count_fixed(target,"ABABAB",states3)
        if (a,b)!=({1:(18,9),2:(9,0)}[k]):
            raise AssertionError(("six-letter witness failed",k,a,b))
    return {"status":"INDEPENDENT_BOUNDED_CHECKS_PASSED",
            "objects":48,"full_state_classes":14,
            "root_preserving_classes":16,
            "pairwise":dict(counts),"arithmetic":dict(totals)}


if __name__=="__main__":
    print(audit())
