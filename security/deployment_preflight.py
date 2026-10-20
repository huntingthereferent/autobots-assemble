"""Read-only, conservative gate for a disposable local security pilot.

This DOES NOT launch a service or authorize a production deployment. It
inspects the exact service instance and source trust state the operator gives
it. A real outside review, key custody and independently stored checkpoint
are not properties that software can infer from a local directory alone.
"""
from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from runtime.service import EcosystemService
from .journal_checkpoint import verify_checkpoint
from .sealed_journal import SealedRuntimeJournal


@dataclass(frozen=True)
class StagingPreflight:
    ready_for_isolated_local_test: bool
    findings: tuple[str, ...]
    scope: str = "local_staging_only"

    def __bool__(self):
        # Do not allow a pass to be silently treated as deployment approval.
        raise TypeError("inspect ready_for_isolated_local_test; never treat as production approval")


def check_staged_local_security(
    service: EcosystemService, *,
    independently_retained_checkpoint: dict | None,
    trusted_checkpoint_public_key: Ed25519PublicKey | None,
    listener_host: str = "127.0.0.1",
) -> StagingPreflight:
    """Check key/runtime coupling and continuity WITHOUT writing or starting work."""
    findings = []
    if not isinstance(service, EcosystemService):
        raise TypeError("existing native EcosystemService required")
    if listener_host not in ("127.0.0.1", "::1", "localhost"):
        findings.append("BLOCK: staging listener must be loopback-only")
    if not isinstance(service.runtime.event_store, SealedRuntimeJournal):
        findings.append("BLOCK: native HandoffRuntime is not using the sealed journal")
    if (service.data_dir / "runtime.jsonl").exists():
        findings.append("BLOCK: plaintext native runtime history present")

    entries = service._security_ingresses
    if not all(role in entries for role in ("submit", "result")):
        findings.append("BLOCK: both operator-pinned submit and result ingress are required")
    else:
        from .runtime_ingress import AuthenticatedHandoffIngress
        submit, result = entries["submit"], entries["result"]
        for role, entry in (("submit", submit), ("result", result)):
            if (not isinstance(entry, AuthenticatedHandoffIngress)
                    or entry.runtime is not service.runtime):
                findings.append(f"BLOCK: {role} does not point at this native runtime")
                continue
            try:
                if entry.authority.operator_pin_ledger is None:
                    raise PermissionError("operator ledger absent")
                entry.authority.require_current_operator_pin()
            except (PermissionError, ValueError, OSError) as exc:
                findings.append(f"BLOCK: {role} signing key is not currently operator-enrolled ({type(exc).__name__})")
        if (isinstance(submit, AuthenticatedHandoffIngress)
                and isinstance(result, AuthenticatedHandoffIngress)):
            a, b = submit.authority, result.authority
            if (a.lane != b.lane or a.signer_actor != b.receiver_actor
                    or a.receiver_actor != b.signer_actor):
                findings.append("BLOCK: signed handoff and return must use one reciprocal actor/lane scope")
            if submit.ledger.path == result.ledger.path:
                # Same ledger is OK: both lanes share event IDs in one store.
                pass
            for role, entry in (("submit", submit), ("result", result)):
                if entry.ledger.path == service.runtime.event_store.path:
                    findings.append(f"BLOCK: {role} replay database must not be the encrypted journal")

    if independently_retained_checkpoint is None or not isinstance(
            trusted_checkpoint_public_key, Ed25519PublicKey):
        findings.append("BLOCK: independently retained signed checkpoint and pinned public key required")
    elif isinstance(service.runtime.event_store, SealedRuntimeJournal):
        try:
            verify_checkpoint(service.runtime.event_store,
                              independently_retained_checkpoint,
                              trusted_checkpoint_public_key)
        except (ValueError, TypeError, OSError) as exc:
            findings.append(f"BLOCK: journal checkpoint mismatch ({type(exc).__name__})")

    if not findings:
        findings.append("PASS: isolated local test prerequisites are consistent (NOT a deployment authorization)")
    return StagingPreflight(not any(x.startswith("BLOCK:") for x in findings),
                            tuple(findings))
