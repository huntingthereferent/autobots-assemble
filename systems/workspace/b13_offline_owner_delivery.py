"""B13: explicit offline source-owner signing boundary for actual B12/B3 returns.

A public pin and an independent, operator-confirmed fingerprint must be
provisioned *outside* the signed envelope. This module never creates,
imports, saves, or invokes a private key. The source owner signs canonical
B11 bytes using their own process; the operator submits that signature back
through B11's original native-result verifier and journal.

This is an invoked single-writer local tool, NOT a daemon, key enrollment,
concurrent transaction, live third-party authentication, or automatic agent.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import argparse
import json
from pathlib import Path
from systems.workspace.b16_delivery_coordination import coordinated_operator_entry
from typing import Any, Mapping

from runtime.engine import HandoffRuntime
from systems.workspace.b11_native_local_delivery import (
    NativeLocalProof, PROTOCOL, canonical_proof_bytes,
)
from systems.workspace.b12_b3_native_delivery import (
    B12B3LocalDelivery, B3NativeLocalSource, RELATION, SOURCE_NAME,
)
from systems.workspace.workstation_construction import WorkstationConstruction

_MAX_ENVELOPE = 4096


def load_operator_pin(path: str | Path, *, expected_sha256: str) -> bytes:
    """Load only 32 raw Ed25519 public bytes; compare an OUT-OF-BAND pin digest.

    A public key supplied by the untrusted result or a digest copied out of
    the same envelope does not establish independent source identity.
    """
    p = Path(path)
    if (p.is_symlink() or not p.is_file() or p.stat().st_size != 32
            or not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise ValueError("operator must supply a pinned 32-byte public key and full SHA-256")
    key = p.read_bytes()
    if len(key) != 32 or sha256(key).hexdigest() != expected_sha256:
        raise ValueError("operator key does not match separately confirmed public-key digest")
    return key


def load_signed_envelope(path: str | Path) -> dict[str, Any]:
    """Read a strictly bounded, caller-supplied signed B11 response as data."""
    p = Path(path)
    if (p.is_symlink() or not p.is_file() or p.stat().st_size > _MAX_ENVELOPE
            or p.stat().st_size == 0):
        raise ValueError("signed envelope must be a bounded ordinary file")
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise ValueError("malformed source-owned signed envelope") from exc
    if (not isinstance(payload, dict)
            or set(payload) != {"protocol", "receipt", "signature"}
            or payload["protocol"] != PROTOCOL
            or not isinstance(payload["receipt"], dict)
            or set(payload["receipt"]) != set(NativeLocalProof.__dataclass_fields__)
            or not isinstance(payload["signature"], str)
            or len(payload["signature"]) != 128
            or any(c not in "0123456789abcdef" for c in payload["signature"])):
        raise ValueError("signed envelope does not meet the exact B11 protocol")
    return payload


class B13OfflineOwnerDelivery:
    """Two-process B3/B12/B11 flow with no private key in this process."""

    def __init__(self, *, construction_dir: str | Path,
                 native_data_dir: str | Path, observed_journal_path: str | Path,
                 lane_handoff_id: str, opening_id: str, job_id: str,
                 public_key: bytes, expected_public_key_sha256: str,
                 confirm_source_job: str,
                 operator_trust_ledger_path: str | Path):
        if (not isinstance(public_key, bytes) or len(public_key) != 32
                or not isinstance(expected_public_key_sha256, str)
                or sha256(public_key).hexdigest() != expected_public_key_sha256):
            raise ValueError("public key must be independently pinned by the operator")
        if confirm_source_job != job_id:
            raise PermissionError("operator must confirm the exact source-owned native job")
        # B10 already separates the observed journal from B9 construction.
        # Keep it separate from the ORIGINAL B3 runtime as well; mixing the
        # two append-only event schemas would corrupt the source/proof boundary.
        if (Path(observed_journal_path).resolve()
                == (Path(native_data_dir) / "runtime.jsonl").resolve()):
            raise ValueError("B13 observed journal must be separate from native B3 source")
        from .b14_operator_pin_ledger import OperatorPinLedger
        # Import at construction time to preserve B13/B14 module load order.
        # Every B13 host, not only the newer B14 CLI, requires the actual
        # current operator policy. No optional trust-check callback remains.
        if operator_trust_ledger_path is None:
            raise PermissionError("B15 requires an operator trust ledger")
        supplied_trust_path = Path(operator_trust_ledger_path)
        # Do not resolve away a symlink before OperatorPinLedger performs its
        # own no-symlink check. Trust policy aliases are not accepted.
        if supplied_trust_path.is_symlink():
            raise ValueError("B13 operator trust ledger must not be a symlink")
        trust_path = supplied_trust_path.resolve()
        scoped_paths = (
            trust_path, Path(observed_journal_path).resolve(),
            (Path(native_data_dir) / "runtime.jsonl").resolve(),
            (Path(construction_dir) / "runtime.jsonl").resolve(),
        )
        if len(set(scoped_paths)) != len(scoped_paths):
            raise ValueError("operator trust ledger must be separate from native and delivery journals")
        self._trust_path = trust_path
        self._observed_path = Path(observed_journal_path)
        # Constructor replay may start an already-authorized native attempt.
        # B17 takes the same B16 lock used by the CLI BEFORE opening a journal.
        with self._session():
            self.trust = OperatorPinLedger(trust_path)
            self.construction = WorkstationConstruction(construction_dir)
            self.source = B3NativeLocalSource(
                data_dir=native_data_dir, lane_handoff_id=lane_handoff_id,
                opening_id=opening_id, job_id=job_id,
            )
            edition = self.source.inspect().edition_fingerprint
            self.trust.require_current(SOURCE_NAME, edition, expected_public_key_sha256)

            def current_trust() -> bool:
                return self.trust.is_current(SOURCE_NAME, edition, expected_public_key_sha256)

            def no_private_key_here(_: bytes) -> bytes:
                raise PermissionError("B13 never signs: use a source-owned external signer")

            self._native_params = dict(
                construction=self.construction,
                observed_journal_path=observed_journal_path,
                source=self.source,
                pinned_public_key=public_key,
                sign_native_proof=no_private_key_here,
                confirm_source_job=confirm_source_job,
                verify_operator_pin_current=current_trust,
            )
            self._refresh()

    def _session(self):
        """Reuse a CLI lease or acquire the same two locks for direct callers."""
        return coordinated_operator_entry(
            trust_ledger=self._trust_path,
            observed_journal=self._observed_path,
        )

    def _refresh(self) -> None:
        """Reload durable B10/B11 state while the caller owns BOTH locks.

        An object instantiated before another process wrote a LOCAL_PASS
        must not continue against its stale in-memory journal. Recovery is
        permitted only inside the coordination lease.
        """
        self.b12 = B12B3LocalDelivery(**self._native_params)

    def prepare(self, *, goal_id: str, candidate_id: str,
                route: tuple[str, ...]) -> str:
        """Register ONE inert B10 request with a source-owned B3 adapter."""
        with self._session():
            self._refresh()
            return self.b12.prepare(goal_id, candidate_id, route=route)

    def _current_proof(self, request_id: str) -> NativeLocalProof:
        handoff = HandoffRuntime(event_store=self.b12.delivery.journal).get(request_id)
        if (handoff.metadata.get("source_locator") != self.b12.source_locator
                or handoff.required_relation != RELATION
                or handoff.metadata.get("continuation_source_binding")
                != {"name": SOURCE_NAME, "edition": self.b12.edition}):
            raise ValueError("request not bound to this B3 source edition and relation")
        current = self.source.inspect()
        return NativeLocalProof(
            handoff_id=request_id, source_name=SOURCE_NAME,
            source_edition=self.b12.edition, required_relation=RELATION,
            candidate_spec_sha256=handoff.metadata["candidate_spec_sha256"],
            source_locator=self.b12.source_locator,
            native_receipt_ref=current.native_receipt_ref,
            native_receipt_sha256=current.native_receipt_sha256,
        )

    def signing_request(self, request_id: str) -> dict[str, Any]:
        """Return the exact canonical bytes for an EXTERNAL native source signer.

        This emits a request, never a signature, LOCAL_PASS, or worker attempt.
        """
        with self._session():
            self._refresh()
            self.b12._check_pin()
            proof = self._current_proof(request_id)
            raw = canonical_proof_bytes(proof)
            return {
                "protocol": PROTOCOL,
                "receipt": asdict(proof),
                "canonical_bytes_hex": raw.hex(),
                "canonical_sha256": sha256(raw).hexdigest(),
                "signing_required_externally": True,
                "signature_provided": False,
            }

    def deliver(self, *, request_id: str, confirm_request: str,
                approved: bool, signed_envelope: Mapping[str, Any]):
        """Freshly recheck B3, compare exact proof, then invoke B11 delivery.

        Even a genuine signature on a different registered B9 route, source
        edition, candidate, or old native result must fail closed. The signed
        envelope cannot select or enroll its own public key.
        """
        with self._session():
            self._refresh()
            if approved is not True or confirm_request != request_id:
                raise PermissionError("explicit exact request delivery approval required")
            self.b12._check_pin()
            if (not isinstance(signed_envelope, Mapping)
                    or set(signed_envelope) != {"protocol", "receipt", "signature"}
                    or signed_envelope["protocol"] != PROTOCOL
                    or not isinstance(signed_envelope["receipt"], dict)):
                raise ValueError("B11 signed envelope required")
            proof = self._current_proof(request_id)
            if signed_envelope["receipt"] != asdict(proof):
                raise ValueError("signed proof differs from freshly verified B3 source")
            return self.b12.delivery.deliver(
                proof, signature_hex=signed_envelope["signature"],
            )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="B13 explicit B3 native-owner signing handoff (never signs or runs jobs)"
    )
    ap.add_argument("--trust-ledger", required=True, type=Path)
    ap.add_argument("--construction-dir", required=True, type=Path)
    ap.add_argument("--native-data-dir", required=True, type=Path)
    ap.add_argument("--observed-journal", required=True, type=Path)
    ap.add_argument("--lane-id", required=True)
    ap.add_argument("--opening-id", required=True)
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--confirm-source-job", required=True)
    ap.add_argument("--pinned-public-key", required=True, type=Path)
    ap.add_argument("--expected-public-key-sha256", required=True)
    sub = ap.add_subparsers(dest="action", required=True)
    sub.add_parser("inspect")
    p = sub.add_parser("prepare")
    p.add_argument("--goal-id", required=True)
    p.add_argument("--candidate-id", required=True)
    p.add_argument("--route-node", action="append", required=True)
    p = sub.add_parser("signing-request")
    p.add_argument("--request-id", required=True)
    p = sub.add_parser("deliver")
    p.add_argument("--request-id", required=True)
    p.add_argument("--confirm-request", required=True)
    p.add_argument("--approve-native-delivery", action="store_true")
    p.add_argument("--signed-envelope", type=Path, required=True)
    args = ap.parse_args(argv)
    # Lock BEFORE constructing the native journal: constructors perform
    # recovery that may invoke a live native observation.
    with coordinated_operator_entry(trust_ledger=args.trust_ledger, observed_journal=args.observed_journal):
        key = load_operator_pin(
            args.pinned_public_key, expected_sha256=args.expected_public_key_sha256,
        )
        host = B13OfflineOwnerDelivery(
            construction_dir=args.construction_dir,
            native_data_dir=args.native_data_dir,
            observed_journal_path=args.observed_journal,
            lane_handoff_id=args.lane_id,
            opening_id=args.opening_id,
            job_id=args.job_id,
            public_key=key,
            expected_public_key_sha256=args.expected_public_key_sha256,
            confirm_source_job=args.confirm_source_job,
            operator_trust_ledger_path=args.trust_ledger,
        )
        if args.action == "inspect":
            report = host.source.inspect()
            result = {"source": asdict(report), "native_worker_executed_now": False,
                      "private_key_loaded": False, "journal_modified_by_delivery": False}
        elif args.action == "prepare":
            result = {"request_id": host.prepare(
                goal_id=args.goal_id, candidate_id=args.candidate_id,
                route=tuple(args.route_node),
            ), "native_worker_executed_now": False,
                "local_pass_emitted": False, "private_key_loaded": False}
        elif args.action == "signing-request":
            result = host.signing_request(args.request_id)
        else:
            envelope = load_signed_envelope(args.signed_envelope)
            event = host.deliver(
                request_id=args.request_id,
                confirm_request=args.confirm_request,
                approved=args.approve_native_delivery,
                signed_envelope=envelope,
            )
            result = {"event_id": event.event_id, "request_id": event.handoff_id,
                      "state": host.b12.bridge.projection(event.handoff_id)["state"],
                      "whole_route_verified": False,
                      "native_b3_worker_executed_now": False}
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
