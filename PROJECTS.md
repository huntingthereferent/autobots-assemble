# Project guide — current repository structure

*Documentation snapshot: October 22, 2026. This describes what is present in the repository, not which private workers are running at this moment.*

The repository holds research, implementations, test records, and creative applications. These are related by shared methods and infrastructure where specifically documented; they are not a single proved theory or one completed product.

**How to read this page:** “Implemented” means source exists, not that it is deployed. “Native test” means the named implementation was actually exercised in the cited evidence; it does not transfer to other projects. “Historical” means retained work, not an automatic instruction to resume it.

## Research and mathematical experiments

| Project | Purpose | What exists now / evidence boundary | Start here |
| --- | --- | --- | --- |
| Language Referent (earlier name: A/B) | Continue the inquiry into relationships observed, described and corrected through change. | Technical account and explicit evidence boundaries; not a universal equation or the definition of a software process. | [Language Referent](LANGUAGE_REFERENT.md) · [evidence contract](LANGUAGE_REFERENT_CONTRACT.md) |
| Finite mathematics | Construct finite-field transformation families and test exact correspondences, inverse construction and counterexamples. | Executable models, local mathematical contracts, audits and tests. Results belong to each model's stated domain. | [Finite construction](work/arc_like_maze/README.md) |
| Finite Correspondence Research | Test when a proposed correspondence is witnessed, preserved, revised or invalidated across selected sources. | Checkpoint research and archived integrated-source reconstruction. A specific process/worker implementation is narrower than the research. | [Research](work/arc_like_maze/chatbot/README.md) · [process vs. worker](work/arc_like_maze/chatbot/PROCESS.md) |
| ARC-AGI-3 | Investigate behavior in the original native ARC environment using action histories, observations and falsifiable hypotheses. | Saved native action observations, many scoped tests and counterexamples. An observed or replayed route is not an autonomous hidden-game win. | [ARC work and latest recorded boundaries](work/arc3/README.md) · [saved route evidence](research/arc_native_runs/README.md) |
| A/B WORLD | Record changing objects/relations and compare bounded world results against their original mathematical or simulated sources. | Construction/verification code and separate trial handoffs. A failed conservative clearance bound is not evidence of a real collision. | [World construction](work/ab_world/GENERAL_CONSTRUCTION.md) · [Trial 31 boundary](work/ab_world/TRIAL31_SOURCE_HANDOFF.md) |
| NIH source research | Compare public clinical-trial source editions, identifiers and status fields; investigate the limits of temporal and cross-source inference. | Source-specific ingestion and verification modules plus documented comparisons. Dataset differences do not prove the exact date a registry entry changed or any clinical outcome. | [AACT source comparison](systems/workspace/NIH_P2_TWO_AACT_SNAPSHOT_BOUNDARY.md) · [status-difference search](systems/workspace/NIH_P2_STATUS_DIFFERENCE_SEARCH.md) |
| Research dives and audits | Preserve source questions, findings, unsuccessful branches and return points. | Individual saved investigations, question records and evidence files; not a global completion scoreboard. | [Research](research/README.md) · [dives](research/dives/README.md) |

## Implementation and infrastructure

| Project | Purpose | Current boundary | Start here |
| --- | --- | --- | --- |
| Workspace continuity | Keep independent lanes, their recorded changes and return points inspectable without merging their underlying projects. | Append-only local lane journal and read-only projections; opening a lane does not create or execute a job. | [Workspace](systems/workspace/README.md) |
| Process Workstation | Make private, versioned copies of selected worker source; inspect changes, admit explicitly authorized jobs and preserve results. | Opt-in local implementation, not a public remote-control service. GitHub Pages cannot read its private journal. | [Process Workstation](systems/workspace/WORKSTATION.md) |
| Handoff runtime | Pass declared work between unlike systems while keeping inputs, evidence, events, outcomes and recovery links. | Executable bounded carrier/adapters. A handoff is not synonymous with a task or a general-purpose agent. | [Runtime](runtime/README.md) |
| Systems | Keep a system's local state separate from the shared handoff boundary. | School, calendar, personal operations, factory and other source-specific modules with different implementation depths. | [Systems](systems/README.md) |
| Program foundation | Preserve demonstrated software construction capability as evidence, not a manually assigned score. | Frozen foundation records and supporting implementations; do not call a design a deployment. | [Foundation](foundation/README.md) |
| Public data monitor | Ingest external sources, keep their identities, compare changes and expose source-linked results. | Local development code and read-only public projections. Local Compose setup is not a hardened public deployment. | [Monitor project](work/projects/public-data-monitor/README.md) · [world observations](views/world-continuity/README.md) |
| Visual provenance | Record why a design uses a particular visual grammar and how the local implementation adapts it. | Templates, surface bindings and checks. A source-linked design record is not a live execution result. | [Visual provenance](design/visual-provenance/README.md) |

## Public interfaces and creative projects

| Surface | What a visitor can do | What it does **not** imply | Open |
| --- | --- | --- | --- |
| Workstation viewer | Inspect published research projections and public GitHub Actions runs. | It cannot start private workers or prove findings outside the actual tests. | [Viewer](https://huntingthereferent.github.io/autobots-assemble/live/) · [source](docs/live/README.md) |
| Project data audit | Inspect source-pinned tests and JSON records and export a human assessment. | Viewing a declared assertion is not a witnessed pass. | [Audit](docs/live/audit.html) |
| WORLD48 | Explore original finite mathematical challenge worlds in a browser. | Playable challenges are not the native ARC game or measured physical worlds. | [Play](docs/game/index.html) · [worker evidence](work/arc3/WORLD48_WORKER_HANDOFF.md) |
| Meow Lab 2 | Play, import user-selected sounds, edit beat/chord/melody layers and use browser-based music tools. | Browser sound import is separate from a native, independently reverified worker run. | [Studio](docs/live/cat-keyboard.html) · [project notes](work/projects/cat-keyboard/README.md) |
| Audio intake | Inspect user-supplied audio/MIDI, work with local waveform and direction tools and export supported results. | It is not a Suno account integration, source-code copy or generative music model. | [Audio intake](docs/live/suno-intake.html) · [scope](work/projects/suno-export-intake/README.md) |
| Pony Trail | Play the standalone horse-riding browser game. | Game progress is not workstation execution or research evidence. | [Play](docs/live/pony-trail.html) · [scope](work/projects/horse-riding/README.md) |

## External opportunities and products

[Money](money/README.md) contains [reusable product candidates](money/products/README.md) and [prize/challenge work](money/challenges/INDEX.md). It does not designate paid work as more authoritative than research and does not restore the retired `jobs/` directory. A candidate product is not a confirmed sale; a submitted challenge is not automatically an award.

## Where to look for actual status

- **A project's state and next supported test:** the project-specific README, source report or dated experiment.
- **Actual public execution:** the named [GitHub Actions run](https://github.com/huntingthereferent/autobots-assemble/actions), including its jobs, steps and artifacts.
- **Historical saved observations:** `research/`, `evidence/` and source-owned records; these do not automatically describe a running process.
- **Local worker state:** the authorized local Process Workstation and its private journal, not the public GitHub Pages viewer.
- **Selected work notes:** [TASKS.md](TASKS.md), which is not an exhaustive live queue.
- **Meaning of repeated technical words:** [reading guide](docs/READING_GUIDE.md) and the relevant project contracts.

Do not turn the largest number, latest commit, simulation, visual animation or passed unrelated workflow into a claim that a separate scientific question is solved.
