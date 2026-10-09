# Regression facts for the public-only CN04 semantic-discovery layer.
# These are intentionally small and do not read latent engine masks.

H1={'a0':0,'a1':0,'b0':1,'b1':0,'c0':0,'c1':1}
H2={'a0':0,'a1':1,'b0':0,'b1':0,'c0':1,'c1':0}

success_pairs=[('a0','b1'),('a1','c0'),('b0','c1')]
discriminating_pairs=[('a0','b0'),('a1','c0'),('b1','c1')]

def compatible(H,pairs):
    return all(H[a]==H[b] for a,b in pairs)

assert compatible(H1,success_pairs)
assert compatible(H2,success_pairs)
assert not compatible(H1,discriminating_pairs)
assert compatible(H2,discriminating_pairs)

# Public experiment outcome for the discriminating configuration was failure,
# so H2 is eliminated and H1 survives.
observed_discriminating_success=False
survivors=[H for H in (H1,H2) if compatible(H,discriminating_pairs)==observed_discriminating_success]
assert survivors==[H1]
print("PASS public-only semantic hypothesis refinement")
