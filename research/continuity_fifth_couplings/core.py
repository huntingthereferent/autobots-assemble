"""Portable, dependency-free, exact five-coordinate A/B coupling-action mathematics.

This does not import the repository or earlier prototype. The identity of
its finite group and classification apply ONLY to the declared grammar.
All generator words act from left to right. A/a and B/b are inverses.
"""
from collections import Counter, deque
from itertools import product

F3=(0,1,2)
STATES=tuple(product(F3, repeat=5))
INDEX={x:i for i,x in enumerate(STATES)}
N=243
LAWS=3**9
A=tuple(INDEX[((u+1)%3,v,z,y,t)] for u,v,z,y,t in STATES)
STATE_R=tuple(INDEX[(u,v,(z+1)%3,(y+int(z==2))%3,t)] for u,v,z,y,t in STATES)
STATE_S=tuple(INDEX[(u,v,z,y,(2*t)%3)] for u,v,z,y,t in STATES)
B_BASE=tuple(INDEX[(u,(v+u+1)%3,(z+int(v==2))%3,
                           (y+int(v==2 and z==2))%3,0)] for u,v,z,y,t in STATES)
FIFTH=tuple(x[-1] for x in STATES)
COUPLING_INPUT=tuple(3*x[2]+x[3] for x in STATES)
SELECTED_FEATURES=(
    ('BAB','Ab','A'),
    ('ABab','ABBabbbb','B'),
    ('ABA','ABBabbbb','AB'),
    ('ABBabbbb','ABBB','b'),
)


def valid_law(q):
    if len(q)!=9 or any(type(v)!=int or v not in F3 for v in q):
        raise ValueError('law must have nine F3 table entries')
    return tuple(q)


def B(q):
    q=valid_law(q)
    return tuple(B_BASE[i]+((FIFTH[i]+q[COUPLING_INPUT[i]])%3) for i in range(N))


def inverse(p):
    out=[-1]*len(p)
    for i,v in enumerate(p):
        if out[v]>=0:raise ValueError('generator not bijective')
        out[v]=i
    if any(i<0 for i in out):raise ValueError('generator not surjective')
    return tuple(out)


def R(q):
    q=valid_law(q)
    out=[None]*9
    for z,y in product(F3,repeat=2):
        out[3*((z+1)%3)+(y+int(z==2))%3]=q[3*z+y]
    return tuple(out)


def S(q):return tuple(2*x%3 for x in valid_law(q))


def orbit_RS(q):
    points=set();now=valid_law(q)
    for _ in range(9):
        points.add(now);points.add(S(now));now=R(now)
    if now!=q:raise AssertionError('R is not order nine')
    return frozenset(points)


def word_map(steps,w):
    x=list(range(N))
    for char in w:
        edge=steps[char]
        x=[edge[i] for i in x]
    return tuple(x)


def orbit_masks(perm):
    out=[0]*len(perm)
    for root in range(len(perm)):
        if out[root]:continue
        x=root;mask=0
        while not out[x] and not ((mask>>x)&1):
            mask|=1<<x
            x=perm[x]
        if x!=root:raise ValueError('not a valid cyclic permutation')
        todo=mask
        while todo:
            one=todo & -todo;todo-=one
            out[one.bit_length()-1]=mask
    return tuple(out)


def fingerprint(q):
    b=B(q)
    steps={'A':A,'B':b,'a':inverse(A),'b':inverse(b)}
    words={word for p,q,r in SELECTED_FEATURES for word in (p,q,r)}
    perms={w:word_map(steps,w) for w in words}
    cycles={w:orbit_masks(perms[w]) for w in words}
    result=[]
    for p,q,r in SELECTED_FEATURES:
        left,right,shift=cycles[p],cycles[q],perms[r]
        result.append(tuple(sorted(Counter((left[i]&right[shift[i]]).bit_count()
                                           for i in range(N)).items())))
    return tuple(result)


def reach_count(q):
    edge=B(q)
    seen={0};queue=deque([0])
    while queue:
        x=queue.popleft()
        for nxt in (A[x],edge[x]):
            if nxt not in seen:seen.add(nxt);queue.append(nxt)
    return len(seen)


def find_conjugacy(source_q,target_q,rooted=False):
    """Complete origin-image search when both labeled actions are transitive.

    Returns an actual 243-point intertwiner or None, with trial count.
    Not valid as a general negative test for a nontransitive source action.
    """
    a=B(source_q);b=B(target_q)
    if reach_count(source_q)!=N or reach_count(target_q)!=N:
        raise ValueError('requires both A/B actions to be transitive')
    for tries,root_image in enumerate(((0,) if rooted else range(N)),start=1):
        mapping=[-1]*N;mapping[0]=root_image
        used={root_image};todo=deque([0]);good=True
        while todo and good:
            x=todo.popleft();y=mapping[x]
            for sx,ty in ((A[x],A[y]),(a[x],b[y])):
                if mapping[sx]!=-1:
                    if mapping[sx]!=ty:
                        good=False;break
                elif ty in used:
                    good=False;break
                else:
                    mapping[sx]=ty;used.add(ty);todo.append(sx)
        if good:
            assert len(used)==N
            assert all(mapping[A[i]]==A[mapping[i]] and
                       mapping[a[i]]==b[mapping[i]] for i in range(N))
            return tuple(mapping),tries
    return None,(1 if rooted else N)


def positive_transport_checks(q):
    """Independently checks both A/B intertwining equations for R,S."""
    b=B(q);br=B(R(q));bs=B(S(q))
    return all(STATE_R[A[i]]==A[STATE_R[i]] and
               STATE_S[A[i]]==A[STATE_S[i]] and
               STATE_R[b[i]]==br[STATE_R[i]] and
               STATE_S[b[i]]==bs[STATE_S[i]] for i in range(N))

ORIGINAL_CLOSURES=(('A','B','A'),('BA','ABBabbbb'),('ABab','BABa'))

def old_four(q):
    """The prior four-feature catalog: three orbit closures and one linked orbit."""
    b=B(q);steps={'A':A,'B':b,'a':inverse(A),'b':inverse(b)}
    ws={w for words in ORIGINAL_CLOSURES for w in words}|{'BAB','Ab','A'}
    pm={w:word_map(steps,w) for w in ws}
    om={w:orbit_masks(pm[w]) for w in ws}
    hist=[]
    for words in ORIGINAL_CLOSURES:
        roots=[1<<i for i in range(N)]
        for w in words:
            nxt=[]
            for mask in roots:
                expanded=0
                while mask:
                    low=mask & -mask;mask^=low
                    expanded|=om[w][low.bit_length()-1]
                nxt.append(expanded)
            roots=nxt
        hist.append(tuple(sorted(Counter(x.bit_count() for x in roots).items())))
    hist.append(tuple(sorted(Counter((om['BAB'][i]&om['Ab'][A[i]]).bit_count()
                                  for i in range(N)).items())))
    return tuple(hist)
