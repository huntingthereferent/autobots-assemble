"""Horizon-normalized recursive A/B signatures.

A k-step signature is defined only when k witnessed continuation steps are
available for every nonterminal branch.  This prevents remaining sample depth
from becoming accidental state.
"""

def horizon_signatures(nodes,actions,max_horizon):
    memo={}
    def sig(path,k):
        key=(path,k)
        if key in memo:return memo[key]
        if path not in nodes:
            memo[key]=None;return None
        n=nodes[path]
        if k==0:
            out=("obs",n["obs"])
            memo[key]=out;return out

        pieces=[]
        for item in n["immediate"]:
            z,no,lc,st=item[:4]
            if z not in actions:continue
            if st!="NOT_FINISHED":
                pieces.append((z,no,lc,st,"terminal"))
                continue
            child=n["children"].get(z)
            if k==1:
                pieces.append((z,no,lc,st))
            else:
                cs=sig(child,k-1)
                if cs is None:
                    memo[key]=None;return None
                pieces.append((z,no,lc,st,cs))
        out=(n["obs"],tuple(pieces))
        memo[key]=out;return out

    result={}
    for k in range(max_horizon+1):
        result[k]={}
        for p in nodes:
            s=sig(p,k)
            if s is not None:result[k][p]=s
    return result
