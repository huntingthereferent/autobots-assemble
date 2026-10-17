# A/B-led relational cluster — finite movement experiment

This is the **movement experiment** in which mathematical relationships decide where the next worker moves. It is deliberately different from distributing a fixed list of A/B calculations across CPUs.

The source is the existing [finite A/B World](../../work/arc_like_maze/math.py), with state in F3³, declared parameter phi=(0,1,2), and noncommuting labeled actions A and B. It is **not** a definition of James's language referent, a universal law about autonomous workers, or an external source-owner observation.

## What actually moves

The first local process starts from the origin. It evaluates **both** A and B, and the host independently recomputes each reported transition. A previously unseen state opens a new *worker trajectory* (a path that becomes eligible for the next wave), while a state reached by a second distinct path becomes a verified mathematical **connection between histories**.

There is no manually authored task list of future paths. The frontier is regenerated after each accepted wave. Separate OS processes execute the selected frontier paths concurrently when two or more are available. Only the parent can admit new paths or connections, and only after checking each mathematical transition without calling the worker's math implementation.

Example of a collision within the fixed F3 world:

~~~text
root --A--> A --A--> AA --A--> AAA
  ^                                  |
  +----- verified same state --------+
~~~

In this finite model, applying A three times returns to the origin. Its prior and new histories are preserved; the model does **not** infer broader correspondence or an owner-verified multi-system join from that fact.

## Run from repository root

~~~sh
python -m unittest -v network.tests.test_ab_relational_cluster

python -m systems.workspace.ab_relational_cluster --execute --workers 3 --data-dir runtime/data
python -m systems.workspace.ab_relational_cluster --execute --workers 3 --data-dir runtime/data
python -m systems.workspace.ab_relational_cluster --execute --workers 3 --data-dir runtime/data
python -m systems.workspace.ab_relational_cluster --inspect --data-dir runtime/data
~~~

Each explicit invocation carries out one wave, not a permanently running daemon. The durable private file is `runtime/data/ab_relational_cluster.jsonl` and carries an append-only SHA-256-chained trail of the selected prior frontier, independent process IDs, accepted transitions, branch outcomes and connected histories. Restart reconstructs the frontier **by replaying the complete original math**, not by trusting cached labels. The current math/adapter source SHA-256 must match its recorded source fingerprints.

Without `--execute` the command refuses to launch processes or create a journal. With `--depth 1` the experiment reaches an explicit shallow frontier wall. Workers are local processes, not Kubernetes nodes and not AI model agents. There is no shared-store multiwriter locking, externally authenticated proof, or malicious-actor-resistant journal signature. The graph has at most 27 finite states.

## Relationship to the existing Process Workstation

The [B2 continuation harness](WORKSTATION_CONTINUATION_B2.md) already preserves separately witnessed BRANCH and RELATION observations. This source-specific experiment provides an **actual mathematical example** of the event-producing side of that relationship: a checked output changes which computation is eligible next, and a collision creates evidence relating two histories.

Its mathematical journal is currently *separate from the native workstation journal*. No B2 or CP lane, W13 checkpoint, native owner admission, or agent execution is silently created. Routing these finite observations into the real B2 harness requires a dedicated adapter mapping exact source/witness identities into its existing admission contract and independently verifying each proposed cross-lane connection. The finite mathematical equality demonstrated here must not be generalized as proof of other research relationships.

This branch is intended to correct the direction of [PR #53](https://github.com/huntingthereferent/autobots-assemble/pull/53), which merely split pre-selected mathematical calculations between processes. This experiment instead tests **relationally determined continuation**.

## Tests

The targeted test suite checks real spawned processes and their distinct process IDs, unplanned frontier formation, algebraically verified reconvergence, persistent restart, noncommuting A/B paths, bounded depth, corrupted provenance, maliciously recomputed digests on fabricated edges, duplicate JSON keys and execution gating.

Repository-integrated CI must run independently before this branch can be called verified.
