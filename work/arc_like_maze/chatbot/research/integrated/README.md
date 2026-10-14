# Integrated source restoration — checkpoints 20–30

This folder is a **byte-for-byte recovery of the original integrated finite correspondence sources**, not a new construction, a second mathematical research branch, or a claim that every historical test was independently rerun.

It repairs the missing integrated-source baseline described in `../README.md`. The original flat archives are retained in the user's ChatGPT file library; this layout keeps their **281 original files** as one **201-file CP20 baseline plus ten eight-file deltas**, with a manifest of each byte's SHA-256 and historical stage.

All material here is historical source/evidence. Current GitHub research/checkpoint pages remain the public entry points; none should be replaced by these old flat archive file names. A built checkpoint's files are emitted into a fresh temporary output directory, preserving original sibling imports.

## Verify and reconstruct

Run from this folder after it is installed in an authorized repository clone:

```sh
python verify.py
python assemble.py --stage 20 --out /tmp/correspondence-cp20
python assemble.py --stage 30 --out /tmp/correspondence-cp30
cd /tmp/correspondence-cp30
python -m pip install 'cryptography>=45,<47'
python -m unittest -q test_finite_two_hop_transport test_finite_single_route_task test_finite_multi_task_dependency test_finite_shared_route_certificate test_finite_certificate_handoff test_finite_process_attestation
```

`--stage` supports all integers **20 through 30**. Each stage yields exactly `201 + 8*(stage-20)` files and keeps earlier stages byte-identical.

## Verification boundaries

- Recovery package SHA-256s for original archives are recorded in `MANIFEST.json`, but archive ZIP serialization is not reconstructed; the **individual 281 bytestrings** are reconstructed, not the historical ZIP bitstream.
- The original CP20 ZIP includes preceding unnumbered experiments. Their contents are preserved here without inventing checkpoint numbers 1–19.
- Checkpoint 30's signed scopes are synthetic and do not enroll or authenticate external owners.
- These restored executable files may be run locally only after reviewing the source and environment. Do not execute untrusted ZIP scripts blindly.
- A full owner-backed historical test-suite pass is *not* asserted; run targeted tests in the required Python environment and record the actual result.
- A source archive hash is an integrity identifier, not a download link or proof of external authorship.

## Private workstation source editions

The [Process Workstation source-copy entry](../../../../../../systems/workspace/INTEGRATED_CORRESPONDENCE_SOURCE.md) independently checks the published manifest and copies any selected CP20–CP30 reconstructed flat source into a new, isolated local edition. It makes **no execution, agent, or owner-authentication claim** and does not change historical source. A separate native task adapter is required before admitting an integrated worker job.
