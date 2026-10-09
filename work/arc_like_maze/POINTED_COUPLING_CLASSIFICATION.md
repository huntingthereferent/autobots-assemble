# Pointed conjugacy classification across both fifth-coordinate trace families

[Common mathematical interface](pointed_coupling_classification.py) · [14 focused tests](../../network/tests/test_arc_like_pointed_coupling_classification.py) · [independent complete matrix reconciliation](pointed_coupling_independent_audit.py) · [formal terminology](TERMINOLOGY.md)

## Current referent and definition of solved

Two previous finite-field cohomological classification results have different admissibility and cyclic-order behavior:

- [Nonzero-trace fourth-coordinate systems](VARIABLE_FOURTH_LIFT.md): lower centralizer map has order nine. All admissible fifth-coordinate extensions retain order nine. The induced 27-state graph is connected.
- [Zero-trace fourth-coordinate systems](ZERO_TRACE_LIFT.md): lower centralizer map has order three. An admissible fifth-coordinate extension may have order three or nine; in some disconnected graphs both are possible for the **same coupling table**, depending on the correction constants.

The present movement is **not** a new universal conjugacy theorem. It builds a common *witness-preserving mathematical interface* over both already proved families and tests whether their distinct results survive conversion and pointed-arrow composition.

A solved interface must report **four independent pieces of mathematical information**: (1) coupling admission or obstruction; (2) graph component count and constraint rank; (3) exact set of available cyclic orders; and (4) the actual correction and distinguished-point transport selected by the constructor.

## Declared coupling law

A `CouplingLaw(g,Q,k,q2)` describes the complete fixed triangular generating transformations, over `F3`, with the two previously admitted lower-coupling tables `q0(g)`:

```text
A: x0 -> x0+1 (other coordinates unchanged)

B: x1 -> x1+g*(x0+1)
   x2 -> x2+q0(x0,x1)
   x3 -> x3+Q(phi(x1,x2))+k(x1)
   x4 -> x4+q2(x2,x3)
   xi -> xi                      for i>=5

g in {1,2}
Q:F3 -> F3
k:F3 -> F3, k(0)=0
q2:F3² -> F3
phi(v,z)=z+alpha_g(v).
```

Every increment reads the original coordinates. Every finite-dimensional generating transformation is invertible, and its projections are coherent. The **lower order** is determined by the trace `sum Q mod 3`, not inferred from the label in a calling context.

There are **486** distinct configured fourth-coordinate laws before q2 is chosen: two gains, 27 quotient functions Q, and nine normalized row-offset choices k.

## Separate mathematical objects

The [common interface](pointed_coupling_classification.py) deliberately uses different objects rather than flattening their meanings.

| Object | What is retained |
|---|---|
| `CouplingLaw` | Underlying generating transformations and their actual coupling tables |
| `AdmissionCertificate` | The trace branch; yes/no admission; 27-vertex component count; constraint rank; number of admitted tables for that fourth-coordinate configuration; possible orders; original obstruction certificate if rejected |
| `SelectedSymmetry` | **Chosen 27-value correction**, explicit connected-component constants, and **verified exact cyclic order** |
| `PointedSystem` | The selected symmetry **and** a distinguished five-coordinate state, with zero higher tail |
| `PointedConjugacy` | Exact source and target pointed systems, plus the complete ordered exponent-factor list |

Importantly, `CouplingLaw` and `SelectedSymmetry` are not interchangeable. A coupling table may admit multiple commuting corrections, including different cyclic orders. The interface may not count those corrections as new underlying laws.

Similarly, a map that moves the distinguished point is not an automorphism **fixing the originally chosen point**. `PointedConjugacy` requires the exact equation `F(source.mark)=target.mark` and refuses composition through different pointed intermediate objects.

## How the interface preserves the original proof

For `sum Q=0`, `inspect_coupling` retains the exact zero-trace graph component labels, normalized potential, compatible-order result, and original [signed-cycle obstruction](zero_trace_lift.py).

For `sum Q != 0`, it retains the exact nonzero-trace compatibility rank, the normalized 27-value potential from the [previous voltage graph](variable_fourth_lift.py), its connected single component, the proved order-nine result, and the original obstruction.

The obstruction wrapper does **not replace** the proof with a new text label. It retains the original object and can replay every actual signed edge using its respective branch's verification method.

A selected admissible symmetry is then checked again against **all 81 defining commutation equations**, its complete three- and nine-turn orbits on the 27 lower-coordinate states, and its chosen component constants. Only then can the exact all-dimensional triangular map be built.

The map changes x2 by +1, changes x3 by the previously proved primitive `Q(phi)-Q(0)`, and changes x4 by the selected 27-value potential. Higher coordinates remain fixed. This explicit formula and the 27-state checks prove commutation and the stated finite cyclic order at every dimension of this declared family.

## Combined classification without double-counting

| Property | Zero trace | Nonzero trace | Combined |
|---|---:|---:|---:|
| Fourth-coordinate configurations | 162 | 324 | **486** |
| Admitted (configuration, q2) combinations | 22,410 | 8,100 | **30,510** |
| Available order-three combinations | 11,106 | 0 | **11,106** |
| Available order-nine combinations | 12,492 | 8,100 | **20,592** |
| Combinations allowing both orders | 1,188 | 0 | **1,188** |
| One-component graph configurations | 144 | 324 | **468** |
| Three-component graph configurations | 18 | 0 | **18** |

The order-three and order-nine availability counts overlap for 1,188 combinations. The disjoint admitted categories are therefore:

- **9,918** combinations allowing only order three;
- **19,404** allowing only order nine;
- **1,188** allowing both orders.

They sum to 30,510, and they are **not** counts of distinct conjugacy classes or distinct state maps. Coupling admission remains a separate property from the choice of correction.

The overall q2-constraint rank histogram, across both traces, is:

```text
rank 3:  14 fourth-coordinate configurations
rank 4:  28
rank 5: 100
rank 6: 128
rank 7: 216
----------------
total:   486
```

### Example: the same law, two different pointed symmetries

For gain one, quotient `Q=(1,0,2)`, offsets `k=(0,0,0)`, and the **same zero fifth-coordinate coupling q2**, the induced compatibility graph has three connected components. One exact choice of correction-component constants yields an order-three centralizer symmetry; another yields an order-nine one.

Those transformations have the same `CouplingLaw`, but **different `SelectedSymmetry` objects**, corrections, and pointed trajectories. They are not silently composed as if they were the same cyclic subgroup. The interface preserves the actual chosen constants and refuses an arrow with a mismatched target mark or intervening symmetry.

## Independent verification and its boundary

The executable [independent full-matrix audit](pointed_coupling_independent_audit.py) imports none of the branch classifiers, the adapter or the interpreter. It constructs the **81 equations in 36 unknowns** for each of all **486** fourth-coordinate configurations, computes each F3 nullspace, separates the genuine q2 basis from independent correction-component gauge vectors, and checks all three- or nine-turn trace equations on the lower state space.

Its expected mathematical certificate is:

```text
486 configurations
30,510 admitted coupling combinations
11,106 permitting order three
20,592 permitting order nine
1,188 permitting both orders
468 one-component graphs
18 three-component graphs
1,440 independent q2 basis vectors
522 component-gauge basis vectors
52,974 complete lower-state trace evaluations
```

The [14 new regression tests](../../network/tests/test_arc_like_pointed_coupling_classification.py) exercise all 486 configurations with the zero fifth coupling, both original obstruction verifiers, exact agreement on representative full-state transformations, explicit component-constant selection, inverse and composite pointed arrows, and false-root or unsupported-order rejection.

**Evidence status:** the new module, tests, and independent audit were committed to GitHub. The predecessor mathematical results and their independent arithmetic checks support these combined counts. **Do not claim that the newly committed regression suite or the standalone independent audit has run successfully on GitHub until a workflow run is observed.** Full repository CI integration remains open.

Run from repository root:

```bash
python -m unittest network.tests.test_arc_like_pointed_coupling_classification -v
python -m work.arc_like_maze.pointed_coupling_independent_audit
```

## Boundary, preservation, next referent

**Closed as a mathematical interface:** the specification and explicitly witnessed selection for the two established fifth-coordinate additive-lift families, without conflating admission, connectedness, available cyclic orders, and distinguished-point transport.

**Preserved:** the original zero-trace and nonzero-trace theorem scopes; complete 27-state corrections; the original signed-cycle obstruction objects; true finite-field generating transformations; and all pointed-arrow exponent factors.

**Unknown:** a general conjugacy decision procedure for arbitrary state maps, non-admitted q0 systems, other higher-coordinate correction forms, unrestricted infinite tails, universal inverse construction, and native ARC execution.

**Next:** construct one additional higher-coordinate rule using the same explicit witness protocol, or examine whether the two *selected* symmetry generators can be meaningfully composed without confusing their different pointed objects. Either way, require an actual algebraic action or a verified obstruction rather than assuming commutation or closure.
