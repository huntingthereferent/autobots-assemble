# Engine 1 — bounded inverse mathematical construction

**Current referent:** build the *first* mathematical engine to construct versions
of a *second*, changing mathematical engine. This is not the public ARC service,
not an A/B redefinition, and not software/factory orchestration.

## Already-existing mathematics used

- [48-law two-predecessor family](WINDOW_COMBINED.md): complete full-state
  conjugacy classification, distinct pointed-root classification, action-word
  obstructions, and actual parameter-construction operators.
- [Independent coupling towers](third_coupling.py): finite families of 9,
  81, 729, and 6,561 parameter systems, exact rooted-orbit graph classifiers,
  algebraic full-state diagonal witnesses in admitted cases, and
  complete-state fixed-B invariants.
- [Pointed arrows](WINDOW_MARKED_ARROWS.md): origin-moving state maps do not
  become origin-preserving maps by declaration.

The 48-law family is not the same set as the 48 reversible affine
**operators** on the initial nine-law space. Nor are the 9/81/729/6,561
towers a single common equivalence quotient. Incompatible mathematical
contracts remain separate.

## Mathematical operation

For one declared finite construction family F, and required equations
R over its proved invariants, define the inverse candidate set

~~~text
Inv_F(R) = { W in F : W satisfies every equation in R }.
~~~

No uniqueness is asserted. Engine 1 exhausts the declared family, then
selects the first candidate in documented family order for an initial version.

For a changing constructed law W, only an **admitted construction path**
W --C1--> ... --Cn--> W' qualifies for a successor. The search checks the
mathematical relation between W and W' *and* preserves the evidence of each
intermediate edge, not just a single endpoint status.

~~~text
constructed_law(version n, law W, witnesses P)
  + equation and relation requirements R
  -> Engine 1 inverse search over an explicitly admitted grammar
  -> verified path and mathematical witnesses
  -> constructed_law(version n+1, law W', previous P + witnesses)
       OR explicit WALL
~~~

Engine 1 itself is the stable inverse-construction and evidence-admission
mechanism for this declared implementation. The resulting law is the concrete
mathematical transformation system, with evolving transition law A/B.
The output can enter the same operation again, preserving its witnesses.

### Window-family constructors

The exact existing operations are: cyclic coefficient shear, increasing
support until its wall, admitting a pulse once, and admitting a balanced edit
once. No imaginary downward support, erase-pulse, or wraparound edit.

For each candidate, [window_combined.py](window_combined.py) supplies
one of:

1. ROOTED_FULL — exact full-state, origin-preserving labeled conjugacy.
2. FULL_UNROOTED — exact full-state labeled conjugacy with changed origin
   and explicit root-word collision.
3. FULL_OBSTRUCTED — complete-state fixed-word-count obstruction to
   full-state labeled conjugacy.

The builder independently checks every proposed positive state-conjugacy
square at dimension three and checks the root witness, while relying on
the already proven formulas for each all-depth statement.

### Coupling-tower constructors

A same-depth turn may change **one** complete coupling table. An extension
may append one independent coupling rule, keeping the entire old prefix.
Other jumps are not automatically admitted.

- ROOTED_FULL needs an *explicit projective scaling witness*, plus
  the checked exact rooted graph at the declared finite depth.
- ROOTED_REACHABLE means only the origin-reachable graphs are
  exactly isomorphic. A dormant coupling may hide different full-state
  dynamics; this is **not** a full-state conjugacy claim.
- FULL_OBSTRUCTED needs different complete-space fixed-B counts.
- ROOTED_OBSTRUCTED records an exact rooted graph difference but
  states full-state equivalence remains UNKNOWN if fixed-B counts agree.
- PROJECTION means every A/B transition commutes with dropping the
  added coordinate; this is **not** a bijective state conjugacy.

A candidate is never treated as proven equivalent merely because two
selected invariants happen to match.

### Inverse construction of an executable changing-law recurrence

After selecting a law, Engine 1 can call its own `construct_cycle(seed)` to construct a *witnessed*, independently executable changing-law recurrence. The result calls `tick()` without calling Engine 1 each turn. Its transition law changes, its previous witnesses remain reachable, and the cycle returns only after its proven period.

- In the 48-law window family, this is the proved **three-turn nonlinear shear**: three concretely different transition laws, each step with full-state, origin-preserving conjugacy.
- In the triangular coupling towers, this is the existing **chosen finite rooted-class rotation**. Some turns have full-state diagonal witnesses; dormant-root turns are only origin-reachable equivalences. No full-state claim is silently promoted.
- A singleton rooted class is a **WALL** for a nontrivial class-rotation cycle.

This is construction of *one declared changing-law recurrence*, not an unrestricted self-modifying engine. The periodic update law is itself part of the returned mathematical object, rather than requiring James to manually choose a new law each turn.

### Selection

A next engine is selected by **fewest admitted construction operations**,
with the existing family enumeration used for deterministic ties.
This is an explicit engineering choice, not an alleged unique mathematical
inverse. All qualifying candidates are counted; a fresh seed chooses the
first matching law and records that uniqueness has not been established.
No satisfying candidate or unadmitted cross-family movement returns WALL.

## Reproduce

From the repository root:

~~~bash
python -m unittest network.tests.test_arc_like_engine_one -v
python -m unittest network.tests.test_arc_like_window_combined network.tests.test_arc_like_third_coupling -v
~~~

Programmatic example:

~~~python
from work.arc_like_maze.engine_one import (
    ConstructedEngine, InverseConstructionEngine, Requirements,
)
from work.arc_like_maze.window_combined import CombinedWorld

builder = InverseConstructionEngine()
first = ConstructedEngine(CombinedWorld(0, 0, 1, 0), version=0)
next_result = first.evolve(
    builder,
    Requirements("window48", relation="FULL_UNROOTED"),
)
assert next_result.status == "CONSTRUCTED"
assert next_result.engine.history[-1].kind == "FULL_UNROOTED"
assert next_result.engine.history[-1].source_mark == (0, 0, 0)
assert next_result.engine.history[-1].target_mark != (0, 0, 0)

# Engine 1 also constructs a self-ticking mathematical recurrence.
cyclic = builder.construct_cycle(first)
assert cyclic.status == "CONSTRUCTED"
after_one_turn = cyclic.engine.tick()
assert after_one_turn.law != cyclic.engine.law
assert after_one_turn.tick().tick().law == cyclic.engine.law
~~~

## Cyclic Action Engine native B-continuation entry

The [separate continuation witness contract](CYCLIC_ACTION_CONTINUATION.md)
uses actual five-coordinate [WindowProcess](window_two.py) laws and
the existing ConstructedEngine handoff:

~~~python
from work.arc_like_maze.engine_one import ConstructedEngine
from work.arc_like_maze.window_two import WindowProcess

left = ConstructedEngine(WindowProcess(1, (q0, q1, q2_left), (zero,)), 0)
right = ConstructedEngine(WindowProcess(1, (q0, q1, q2_right), (zero,)), 0)
witness = left.watch_B_against(right)
saved = witness.advance(8).snapshot()
reentered = witness.reenter(saved, left_engine=left, right_engine=right)
~~~

The watch_B_against method admits only the declared 81-state
B-invariant fiber with the existing three-rule/zero-tail window grammar.
It verifies and replays every earlier periodic-count observation and
keeps UNKNOWN distinct from witnessed B-only nonconjugacy or B-only
conjugacy. It makes no simultaneous A/B claim.

This is a **Cyclic Action Engine research entrance**, not an additional Engine 1
inverse-construction grammar. InverseConstructionEngine.construct
returns **WALL** if supplied one of these WindowProcess research laws as
its predecessor; it does not coerce it into the 48-law or
coupling-tower construction families. The input laws are explicitly
constructed, not claimed to originate from the old Engine 1 grammar.

[Focused 18-test regression](../../network/tests/test_arc_like_cyclic_action_continuation.py)
and [dedicated workflow](../../.github/workflows/cyclic-action-continuation.yml)
are committed. Local proof-of-concept tests passed previously;
a successful run of the new repository test module must be confirmed
independently.

## Verified versus unknown

**Implemented:** an inverse search over two explicit existing
construction grammars, a versioned changing law, witnessed admitted
construction paths, and explicit walls when the relation is unsupported.

**Does not establish:** arbitrary inverse A/B, automatic selection of
unlimited new operator grammars, a universal mathematical update theorem,
a live background executor or an unrestricted self-extending mathematical system, live ARC execution, or
customer-ready reports.

**Next referent:** provide an independently proved *inter-grammar*
constructor, or an independently justified rule for admitting new
construction operators. Test its witness contract before allowing
the constructed law to cross that mathematical boundary. Do not invent a connector
by calling different finite families "the same".
