# Read-only owner W13 next-checkpoint preflight

The [original owner-merged W13 computation](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39025574748) was reverified against its original GitHub artifact and exact research source in [run 39095851290](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39095851290). The [native owner-parent verifier admission](https://github.com/huntingthereferent/autobots-assemble/pull/112) is also merged.

These do **not** imply the next owner-native worker has been admitted. The preserved owner journal reports the parent `GAME-W13-WORLDS=WITNESSED`, next `GAME-NATIVE-VERIFIER=ADMISSIBLE` with an unstaffed planned slot, and `GAME-WORKER-READY=BLOCKED`.

`w13_owner_next_cp_preflight.py` reads the real original archive in a private temporary directory. It checks the GitHub owner-run/archive pins through the existing validators; freshly re-verifies the original native job and its Git-pinned research source; checks the exact original RESULT and fingerprint; verifies the separate existing native-witness worker source Git blob; and independently recomputes the existing coordinator CP frontier. It refuses a staged owner child authorization, a changed parent or worker source, and any already-admitted child.

Successful output is `SOURCE_VERIFIED_ADMISSIBLE_NOT_ADMITTED`, **not** a staffed verifier checkpoint. No source is copied, no handoff is admitted, no executable is launched, and neither journal nor inputs/outputs are published. The only future activation requires an owner-authorized request and a separate review/merge of its exact child worker source edition and execution scope; no authorization is introduced by this preflight.

The protected-main workflow authenticates the original GitHub run and artifact prior to downloading; PR jobs run only tests that don't access the original archive. The source artifact has finite retention; if it expires or changes, the preflight fails rather than fabricating a journal.

Run the local tests:

`python -m unittest -v network.tests.test_w13_owner_next_cp_preflight`

The real original archive preflight is only available on the owner-merged main CI run, or locally to an owner of the authenticated private evidence.
