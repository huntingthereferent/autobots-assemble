# Historical research archive reconciliation

This is an import receipt and recovery protocol, **not a claim that the original ZIP binaries are stored in this branch**.

## Verified local scope (10 October 2026)

The 15 relevant Continuity/Cyclic/finite-construction ZIP archives available in the research workspace were inspected using the new \`research.continuity_archive_import\` module.

- 15 ZIP archives read successfully.
- 304 non-cache archive members.
- 171 distinct member SHA-256 values (the other members have historically repeated content).
- A dry run found 304 pending members in an empty temporary checkout.
- A staged isolated run wrote and verified 304 members; a second dry run found **0 pending**.
- The extracted files in this check were **local temporary copies, not GitHub commits**.
- Existing imported research sources, the main B-only mathematical engine, and frozen research board checkpoints were untouched.

## Reconcile locally supplied archives

From the repository root:

\`\`\`bash
python -m research.continuity_archive_import --source /path/to/zip-archives --destination .
\`\`\`

This is a nonmutating report. With an explicit, verified local archive directory, stage all missing members under their historical archive namespace:

\`\`\`bash
python -m research.continuity_archive_import --source /path/to/zip-archives --destination . --stage --manifest /path/to/reconciliation.json
python -m unittest network.tests.test_research_continuity_archive_import -v
git status --short
\`\`\`

Inspect the staged tree before any Git commit. Files with conflicting content are **never overwritten**. Unsafe archive paths, duplicate members, and special-file entries are rejected.

## Known archive inventory

SHA-256 is the checksum of the original ZIP *bytes*, not an assertion that GitHub already contains those bytes. Counts exclude Python cache binaries.

| ZIP archive | Members | ZIP SHA-256 |
| --- | ---: | --- |
| CYCLIC_ACTION_CONJUGACY_EXPERIMENT.zip | 7 | 852ff142bda868c37313462bb84f3b808318b5944f0fd56887c38322e11e1e17 |
| CYCLIC_ACTION_FIFTH_COUPLING_EXPERIMENT.zip | 8 | ffed972f73a71b0163a81beea7c8788b8b0eb066b375b55fbd708f34d3c38230 |
| CYCLIC_ACTION_STABILIZER_CORRESPONDENCE_EXPERIMENT.zip | 8 | 7e75d4c8ac57037f1e94e34059ca3b38f35c8862f3a5262e2b039a0c2ac5deb8 |
| CYCLIC_ACTION_Y_DEPENDENT_EXPERIMENT.zip | 12 | f97ab120386324f70ca5a0ee972b2b9131b9dcf845b485dc73b1714470d7ec8d |
| Continuity_Engine_A_Invariant_Integration.zip | 40 | aee48dee736bdad85fa19d6fdcc098b358415a55df062b5daa0a7e6311929999 |
| Continuity_Engine_All_Fifth_Couplings_1098_Classes.zip | 19 | 928b031bdfb89a48419dbe94d55af0353cc29acb33787f847b7d5774c3b9d367 |
| Continuity_Engine_Board_Integration.zip | 7 | b8bca6d765c2f77159fbdf11b381a3735057b324d0d08ceb071bca224e991531 |
| Continuity_Engine_Cross_Scope_Handoff.zip | 30 | 4d4855baae64cfe24eec7a29a1a2d87b1221aa705614e352c65c8f771af9d5e6 |
| Continuity_Engine_E_Drive_Repo_Ready.zip | 12 | 35551cbd1f9dc254d7868b6bb722a574c5d4926f109a76275c7e9199bbe1db06 |
| Continuity_Engine_Full_AB_Correspondence_Integration.zip | 14 | 977fb2ddd9fea2bc9c316caf8b7387129384efb690114312d5c13b9eb1c35711 |
| Continuity_Engine_Invariant_Intersections.zip | 59 | 94a0193f7644989bd782bb60871283b812615ca8c393991438f2b94d2bd97ea0 |
| Continuity_Engine_Orbit_Incidence_39_Class_Integration.zip | 75 | 7c56331fe7f21f9f1b8ece67a378df47dcf5d70acf470221bfcf31b5afc20e11 |
| ENGINE_TWO_parallel_quotient_experiment.zip | 6 | e0d5f4110d101fe21cca8a9a010dfadb686773499486a79337e9a698093dd98c |
| ENGINE_TWO_transported_commutator_experiment.zip | 4 | 2fe94fc8cfcc0246883e09dfb35204b72dda4ebb9b90bf4f5336d3c7dc999589 |
| continuity_engine_prototype.zip | 3 | c5a8e71956e4381d20347ebea526d9377b66b540203ac27a25d391e32bde2470 |

The separate factory-store prototype has a different referent and is not included in these 15 research ZIPs.

## CI boundary

PR #18's \`protocol-tests\` job failed before reporting any steps on its initial attempt and on a single retry. The GitHub API reported two annotations but this connector did not permit retrieving their contents. This must **not** be reported as either test failure or success. The standalone 21 mathematical regression tests and independent 1,098-class checks passed in a local environment. The updated PR branch still requires an actual integrated test run before merging.

The mathematical classification is scoped to the declared five-coordinate family and does not establish native ARC execution or universal A/B closure.
