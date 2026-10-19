# Non-AI swallow: Box2D → A/B WORLD finite-surface topology

Source inspected: [Erin Catto's Box2D, revision `178495ba`](https://github.com/erincatto/box2d/tree/178495ba35695aefe9c321e569d2277f06db3b90) (MIT), in particular `docs/collision.md` sections **Ghost collisions**, **Chain segment**, **Time of impact**, and `src/distance.c`.

## Source relationship, not a transplanted solver

Box2D suppresses false internal collisions at the **shared endpoint of adjacent segments of a one-sided chain**, with adjacent ghost vertices and winding requirements. This is a useful distinction only when the input segments genuinely form an end-to-end chain.

The actual A/B WORLD 05/06/07/08 source is **not such a chain**. It combines two independently observed Trial 04B receiver segments. They cross at **finite interior locations**; Trial 06's swept-disc solver independently handles finite interior/endpoint arrivals, and Trial 07/08 explore a genuine two-surface tie. Applying chain-vertex suppression to that cross would silently replace the actual geometry and could erase a meaningful contact.

## Implemented bounded guard

`systems/workspace/world_ab_segment_topology.py` provides a read-only independent finite segment incidence classification:
- `interior-crossing`: two finite segment interiors intersect — **never a shared-endpoint chain**;
- `endpoint-interior`: one endpoint touches another segment's interior — also not the same chain boundary;
- `shared-endpoint`: only **eligible for additional** winding/ghost-neighbor validation, not automatic contact removal;
- `disjoint` or `parallel-or-unresolved`: no ghost-chain inference.

It returns actual intersection fractions, explicitly refuses invalid/nonfinite/degenerate geometry, and does not move a source endpoint, change a collision response, or execute any worker.

`network/tests/test_world_ab_segment_topology.py` independently compares this classification with `world_ab_connected_routing.assemble()`'s **actual** measured junction position, plus synthetic controls. Original physics remains untouched.

No Box2D code was copied, so the independent original A/B implementation keeps existing rights; Box2D MIT rights remain with its authors.

## Important limitations

This is a **topology-only** guard, not a full physics solver or verification of Earth physics. Box2D's more general rotating-shape TOI and contact manifold approaches are not justified for import while existing finite-disc source cases remain checked. Trial 08's frictionless two-contact candidate, the Trial 06 `mu=0.4` baseline, and all original native/Chromium receipts remain as they were.

Reproduce using the **Trial 08 branch**, not `main`:

```bash
python -m unittest -v network.tests.test_world_ab_segment_topology
```

Before applying any new physics, a separately source-matched native test and independent browser replay must support a specific claim. Nothing in this note upgrades the Trial 08 local candidate to a universal collision solution.
