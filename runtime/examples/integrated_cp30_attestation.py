"""Opt-in CP30 historical verifier demo using synthetic signing scopes only.

No real-world owner identity, independent trust enrollment or fresh route audit.
Source copy and one job are created only with the explicit --execute flag.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.integrated_source import WORKER_ID, verify_archive_source, copy_integrated_source
from systems.workspace.integrated_attestation_bridge import IntegratedCP30Bridge
from systems.workspace.workstation import ProcessWorkstation

ROOT = Path(__file__).resolve().parents[2]
VERSION = "recovered-cp30-001"
JOB = "integrated-cp30-synthetic-check-001"


def fixture():
    """Generate ephemeral private keys; persist only signed claims and public keys."""
    scopes = ("donor", "middle", "final")
    expected = {"challenge": "ab" * 24, "route": "left", "fingerprint": "12" * 32,
                "witness": "34" * 32,
                "source_digests": dict(zip(scopes, ("56" * 32, "78" * 32, "9a" * 32)))}
    trust, attestations = {}, []
    for scope in scopes:
        key = Ed25519PrivateKey.generate()
        trust[scope] = base64.b64encode(key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)).decode()
        claim = {"kind": "selected-route-source-attestation/v1", "scope": scope,
                 "challenge": expected["challenge"], "route": expected["route"],
                 "route_fingerprint": expected["fingerprint"],
                 "witness_sha256": expected["witness"],
                 "source_sha256": expected["source_digests"][scope]}
        signature = key.sign(json.dumps(claim, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=True).encode())
        attestations.append({"claim": claim, "signature": base64.b64encode(signature).decode()})
    return {"bundle": {"kind": "selected-route-source-bundle/v1", "attestations": attestations},
            "trust": trust, "expect": expected}


def run(*, data_dir: str | Path, allow_execute: bool = False) -> dict:
    if not allow_execute:
        raise PermissionError("CP30 synthetic local demo requires --execute")
    data = Path(data_dir).resolve()
    if data == ROOT or ROOT.is_relative_to(data):
        raise ValueError("data directory may not contain the repository")
    source = verify_archive_source(ROOT, stage=30)
    desk = ProcessWorkstation(data / "workstation")
    try:
        existing = desk.inspect(worker_id=WORKER_ID, version_id=VERSION)
    except KeyError:
        copy_integrated_source(repo_root=ROOT, data_dir=data, stage=30,
                               version_id=VERSION, allow_copy=True)
    else:
        if existing["current_fingerprint"] != source["fingerprint"]:
            raise ValueError("original CP30 demo edition changed; choose a new version")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
    bridge = IntegratedCP30Bridge(runtime=runtime, workstation=desk)
    if JOB not in runtime.snapshot():
        bridge.admit(version_id=VERSION, job_id=JOB, inputs=fixture(),
                     from_actor="synthetic-fixture", lane_id="finite-correspondence")
    state = runtime.state(JOB)
    if state.status == "READY":
        bridge.execute(JOB, allow_local_execution=True)
    elif state.status != "COMPLETE":
        raise ValueError("unresolved CP30 demo job needs an explicit recovery decision")
    bridge.reverify(JOB)
    result = runtime.state(JOB)
    return {"job_id": JOB, "worker_id": WORKER_ID, "worker_version": VERSION,
            "status": result.status, "signature_verdict": result.output["signature_verdict"],
            "verified_scopes": result.output["verified_scopes"], "reverified": True,
            "synthetic_only": True, "real_world_owner_authenticated": False,
            "fresh_route_audit_performed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(data_dir=args.data_dir, allow_execute=args.execute), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
