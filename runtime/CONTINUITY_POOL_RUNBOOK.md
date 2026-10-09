# Original Continuity agent queue — live integration

The original 2026-10-08 tasks are **Finish Continuity site**, **Find things
to swallow**, and **Visual provenance min/max**. Their assignee is
`continuity-agent-pool`. Their native seed definitions live at
`systems/personal_operations/task_seeds/continuity_agent_tasks.json`.

This queue is **not** the four `TASKS.md` repository work entries previously
reported by James's Ohayo activation. Both remain preserved independently.

At startup, with `CONTINUITY_AGENT_POOL=1` and loopback `HOST=127.0.0.1`,
the HTTP service registers the existing recursive A/B loop as the **actual
`AgentLineage.evaluate` callback** scoped to `continuity-agent-pool`. It loads
the original task seeds, admits their Personal Operations handoffs idempotently
into the durable runtime, and executes one bounded A/B evaluation through
the original task agent. James's evaluator remains unassigned.

The resulting `AGENT_AB_OBSERVED` event contains real source paths,
SHA-256 witnesses, and a witnessed swallow-first attempt. It is a
nonterminal UNKNOWN outcome; the three tasks and agent stay READY. Source-relation
MOVEs do **not** mean the site, expansion research, or visual min/max tasks
are finished. No model-backed software worker or autonomous code editing
is installed by this connection; the native A/B worker can compare grounded
source relations but cannot invent implementation or render/inspect a
desktop/mobile browser without a separate, witnessed tool actor.

The original E: task journal may be copied (after a backup) to the live data
directory as `personal_operations.jsonl` to preserve original task IDs.
Never merge or overwrite the old E: working tree. Source and state are
distinct; the original task journal remains evidence.

## Local read-only checks

- `GET http://127.0.0.1:18540/api/agent-pool` — original task IDs, native
  A/B observation, agent readiness, honest worker status.
- `GET http://127.0.0.1:18540/api/monitor?actor=continuity-agent-pool` —
  three native task handoffs and the pool's one root agent.
- `GET http://127.0.0.1:18540/api/monitor?actor=james` —
  separate repository-work lane.
- `http://127.0.0.1:18540/monitor.html` defaults to the original pool;
  `?actor=james` preserves the other scope.

Reboots and repeated pool initialization are idempotent. `READY` means the
system can receive more native movement, not that an always-on model actor
is running. Never claim autonomous website completion without actual
implementation, tests, visual witnesses and user-visible deployment.


## One evaluator callback, two native evidence paths

The `AgentLineage.evaluate` slot is the single admission point.
`ContinuityPoolEvaluator` uses the recovered `ABLoop` for the three
original task/source relations, preserving UNKNOWN and swallow-first without
completing the tasks. `NativeABEvaluator`, already supplied by the ARC
native observation work, verifies independently captured before/after
transitions. When both are explicitly supplied in-process,
`RoutedEvaluator` uses the *original agent root owner* to route the two
existing evaluators through **one** callback. Unscoped arbitrary A/B
callbacks cannot register in that combined mode.

The HTTP server currently registers the original Continuity pool evaluator
only. With `CONTINUITY_LOCAL_MODEL=qwen3:4b-instruct` and a loopback Ollama
server, that same evaluator also requests one generative A/B source-selection
move and executes a bounded, read-only native source inspection. The proposed
move and independently measured file/hash witness enter the existing
`AGENT_AB_OBSERVED` event. The original tasks remain READY: this is neither
code editing nor autonomous completion. Without that env flag, the existing
native-only behavior is unchanged. If inference is unavailable, an explicit
UNKNOWN observation is recorded instead of fabricating movement.

Local Windows canary launch scripts:
`E:\Ollama\start-ollama.ps1` and `E:\Ollama\start-continuity-local-ai.ps1`.
The canary uses a separate journal and port 18541; it does not rewrite the
existing port 18540 journal. `network/tests/test_ollama_ab.py` verifies that
the model-selected source is actually read, traversal escapes are rejected,
and the same agent lineage receives the movement.

ARC has **no live capture provider registered in HTTP**. Trusted
in-process callers can supply a native observer to the same service as the
scoped task evaluator; no HTTP endpoint accepts captures. This does not
start an ARC game, website editor, or autonomous model worker.

Do not infer execution from evaluator registration. `AGENT_AB_OBSERVED`
is nonterminal and cannot satisfy the original agent's required movement
witness. ARC can record actual independently witnessed movement separately;
it must not be promoted to finishing Continuity's original site tasks.

The old extra `Native A/B source loop` dashboard connection row and
parallel `CONTINUITY_POOL_AB` event generator were removed. The monitor's
`A/B evaluator` line is now scoped to the requested agent. Historical
events in the journal remain preserved and are not rewritten.
