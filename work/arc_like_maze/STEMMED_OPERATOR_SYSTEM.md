# Finite-stem A/B operator closure

## Current referent

Operators on complete eventually periodic A/B coupling-rule streams, with explicit incoming boundary gains and verified scalar witnesses.

[Implementation](stemmed_operator_system.py) · [nine tests](../../network/tests/test_arc_like_stemmed_operator_system.py) · [previous layer](MARKED_OPERATORS.md)

## Construction

A gauge consists of an incoming unit, a finite sequence of scales, and a repeating tail. All scales are nonzero in F3. For every coupling index i and field element x:

```text
q_i(u_(i-1)*x) = u_i*p_i(x)
```

The transformed process retains the finite transient, including one extra coordinate to preserve the initial predecessor scale. This equation guarantees full-state, all-depth diagonal A/B alignment of the corresponding marked-root systems.

Gauges compose by pointwise multiplication and have pointwise inverses. A shift of k coupling rules carries the incoming scale u_(k-1), never silently resetting it to one. A verified arrow retains its exact witness tail; the solver is not rerun to choose a different witness.

## Operator normal form

A finite sequence of admitted gauge operations and forward shifts can be rearranged using the verified interchange relation:

```text
gauge; shift(k)  =  shift(k); shifted_gauge(k)
```

The result is **one total forward shift, then two endpoint gauges**. The implementation compares this normal form with direct step-by-step execution using complete rule streams, root gains and witness scalars. It does not recover discarded process stems, and a shift need not be invertible.

## Finite audit

| Evidence | Count |
|---|---:|
| Gauge schedules | 12 |
| Process templates | 81 |
| Gauge compositions | 11,664 |
| Gauge/shift interchange squares | 864 |
| Exhaustive mixed words of length 1–4 | 340 |
| Focused regression tests | 9 |

Tests also cover marked-state transitions, inverse gauges, witness ambiguity at zero rules, a longer seven-operation word, delayed root shifts and invalid input.

Run:

```bash
python -m unittest network.tests.test_arc_like_stemmed_operator_system -v
```

The nine focused tests passed locally using the existing marked-arrow/root-transport API fixture. The two committed Python files match their locally tested Git blob hashes. GitHub CI and full-repository integration remain unverified.

## Boundary and next movement

**Closed:** ultimately periodic F3-unit gauges and their witnessed interchange with forward root transport, under the declared diagonal A/B model.

**Open:** unrestricted coupling-rule addition, non-diagonal alignments, arbitrary nonperiodic rules and universal A/B closure.

**Next:** test new operator families with explicit full-state relation witnesses or preserved counterexamples, rather than repeatedly increasing finite schedule lengths.
