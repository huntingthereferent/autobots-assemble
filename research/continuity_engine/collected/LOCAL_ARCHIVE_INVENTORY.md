# Local artifact archive inventory — October 2026

The original local ZIP bundles are **not included as binary blobs in this
commit**. This inventory identifies them unambiguously so that a later
import can compare exact packages before adding more code. Hashes below are
the first 20 hex digits of SHA-256, not full authentication digests.

The imported text research snapshots live in `research/continuity_engine/collected/`.
The working fifth-coupling classifier is in `research/continuity_fifth_couplings/`.
The B-only Continuity handoff/board bridge is in `research/continuity_engine.py`
and `research/continuity_board_bridge.py`.

| Original ZIP filename | Text/data entries (excluding .pyc) | SHA256 prefix |
|---|---:|---|
| `CYCLIC_ACTION_CONJUGACY_EXPERIMENT.zip` | 7 | `852ff142bda868c37313` |
| `CYCLIC_ACTION_FIFTH_COUPLING_EXPERIMENT.zip` | 8 | `ffed972f73a71b0163a8` |
| `CYCLIC_ACTION_STABILIZER_CORRESPONDENCE_EXPERIMENT.zip` | 8 | `7e75d4c8ac57037f1e94` |
| `CYCLIC_ACTION_Y_DEPENDENT_EXPERIMENT.zip` | 12 | `f97ab120386324f70ca5` |
| `Continuity_Engine_A_Invariant_Integration.zip` | 40 | `aee48dee736bdad85fa1` |
| `Continuity_Engine_All_Fifth_Couplings_1098_Classes.zip` | 19 | `928b031bdfb89a48419d` |
| `Continuity_Engine_Board_Integration.zip` | 7 | `b8bca6d765c2f77159fb` |
| `Continuity_Engine_Cross_Scope_Handoff.zip` | 30 | `4d4855baae64cfe24eec` |
| `Continuity_Engine_E_Drive_Repo_Ready.zip` | 12 | `35551cbd1f9dc254d786` |
| `Continuity_Engine_Full_AB_Correspondence_Integration.zip` | 14 | `977fb2ddd9fea2bc9c31` |
| `Continuity_Engine_Invariant_Intersections.zip` | 59 | `94a0193f7644989bd782` |
| `Continuity_Engine_Orbit_Incidence_39_Class_Integration.zip` | 75 | `7c56331fe7f21f9f1b8e` |
| `ENGINE_TWO_parallel_quotient_experiment.zip` | 6 | `e0d5f4110d101fe21cca` |
| `ENGINE_TWO_transported_commutator_experiment.zip` | 4 | `2fe94fc8cfcc0246883e` |
| `continuity_engine_prototype.zip` | 3 | `c5a8e71956e4381d2034` |
| `continuity_engine_work/run_only.zip` | 2 | `398a197dc5bbb0618cd5` |
| `factory_store_bridge_prototype.zip` | 3 | `af4159f6fa2e0227fe5e` |

The ZIPs contain historical experiment code, local evidence, generated census
records, and many overlapping revisions. They were not silently folded into
the repository runtime. The full 1,574,298-byte fifth-coupling representative
census can be regenerated with:

```bash
python -m research.continuity_fifth_couplings.write_census
```

The batch import preserves research evidence, not a claim that every
historical implementation now runs from the repository. The independent
full A/B, A-invariant, and cross-scope adapters remain research-stage rather
than production entry points unless separately validated in the exact repo.
