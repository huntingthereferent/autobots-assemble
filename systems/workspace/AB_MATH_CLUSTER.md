# Finite A/B mathematical cluster — local, witnessed computation

This opt-in experiment executes the **existing nine finite-field A/B worlds**
across distinct, real local Python worker processes. It computes the complete
reachable three-coordinate state graphs (both labeled A and B actions), then
checks every returned graph with a separately implemented finite enumeration
in the parent process. Only verified graphs enter an exhaustive, rooted
labeled-transition correspondence comparison.

**The language referent / A/B is not a cluster, dispatcher, or scheduler.**
Here **A** and **B** are the *locally defined finite operators* from
[the original source](../../work/arc_like_maze/math.py), operating on
the constructed family with parameter phi=(0,a,b) over F3.
This experiment does not assert a physical two-step, solve ARC, or establish
any universal correspondence theorem.

## Run

From the repository root, with standard Python 3.11+:

~~~sh
python -m unittest -v network.tests.test_ab_math_cluster
python -m systems.workspace.ab_math_cluster --execute --workers 3 --data-dir runtime/data
python -m systems.workspace.ab_math_cluster --inspect --data-dir runtime/data
~~~

Without the **--execute** flag the command does not start workers or create files.
Workers are distinct **local OS processes**, using Python's spawn context.
No distributed hosts, containers, Kubernetes, continuously running agent,
model inference, or background scheduler are created.

The path **runtime/data/ab_math_cluster.jsonl** is an **append-only,
source-specific mathematical receipt**. It records the worker/driver source
SHA-256, selected finite parameters, complete worker graphs, independently
recomputed alignment classes, observed process IDs, and previous/receipt hashes.
The receipt is replayed and rechecked before a matching request can be reused
after restart. Hash chaining protects against accidental edits, not a malicious
actor who can rewrite the whole journal. It is not a source-owner signature
or a native workstation job receipt.

## What can move, and what remains separate

- The existing nine worlds split into **five rooted A/B relational classes**
  when complete reachable graphs are compared under both action labels.
- Processes may compute different worlds simultaneously; only the parent
  verifies and joins their results, never accepting a class just because
  worker reports have identical names.
- A forged edge, missing world, duplicate JSON key, changed saved class,
  conflicting world identity, or missing/changed source fails closed.
- Repeating an identical, source-pinned request reads the checked receipt
  without launching workers or duplicating the result.
- A new admitted finite subset appends a new receipt with the prior hash.
  Writers must be serialized; **there is no multi-process journal lock**.

**Boundary:** This is a mathematical compute cluster on one computer, *not*
the Process Workstation's native worker admission, CP verification, W13
evidence promotion, authenticated cross-worker relationships, or a live
distributed cluster. It intentionally writes **no runtime.jsonl events**,
admits no native handoffs, and cannot automatically spawn new research agents.
An explicit source-owned adapter and native independent verifier would be
needed before these receipts could authorize a workstation movement.

## Reproduction and test boundary

~~~sh
python -m unittest -v network.tests.test_ab_math_cluster
~~~

The focused tests cover multiple real child process IDs, nine fully verified
graphs, five exact classes, source-pinned restart reuse, two chained subsets,
explicit execution gating, malformed inputs, a falsified finite edge,
rewritten claimed classes with recalculated digest, and duplicated JSON keys.

The local process and journal code were tested independently of GitHub
before the PR. GitHub CI supplies the separate repository-integrated check;
do not infer CI PASS until that workflow actually succeeds.
