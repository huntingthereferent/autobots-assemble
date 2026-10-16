"""B12: explicitly deliver existing B3 native source returns into B11.

This selects *one real source-owned B3 return* and its exact job, lane,
opening and source edition. It reopens the original journal and invokes
branch_help.verify_return / native controls on every observation.

No new worker runs here. Private signing keys remain with the authorized
source-owner callback. This is a callable local integration, not a daemon,
external owner credential, or automatic source-identity enrollment.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.b11_native_local_delivery import (
    NativeLocalProof, SourceOwnedLocalDelivery, canonical_proof_bytes,
)
from systems.workspace.main_referent_selector import Capability, Witness
from systems.workspace.observed_event_journal import SourceAdapter
from systems.workspace.workstation_construction import WorkstationConstruction
from systems.workspace.workstation_native_feedback import (
    _ASSIGN_EVENT, _RETURN_EVENT, canonical_digest,
)
from systems.workspace.branch_help import verify_return
from systems.workspace.process_handoff import WORKER_ID

RELATION = "source-owned native finite return reverified"
SOURCE_NAME = "finite-source-native"
_LANE_SOURCE = "workstation-continuation-lane/v1"


@dataclass(frozen=True)
class B3ObservedReturn:
    """A fresh native recheck, not transferable owner identity or route proof."""
    opening_id: str
    coordination_handoff_id: str
    job_id: str
    edition_fingerprint: str
    output_sha256: str
    evidence_sha256: str
    native_receipt_ref: str
    native_receipt_sha256: str


class B3NativeLocalSource:
    """Read one source-pinned B3 return through the existing native controls."""

    def __init__(self, *, data_dir: str | Path, lane_handoff_id: str,
                 opening_id: str, job_id: str):
        if not all(isinstance(x, str) and 0 < len(x) <= 200 and x.strip() == x
                   for x in (lane_handoff_id, opening_id, job_id)):
            raise ValueError("exact native B3 lane, opening and job required")
        self.data_dir = Path(data_dir)
        self.lane_id = lane_handoff_id
        self.opening_id = opening_id
        self.job_id = job_id

    def _runtime(self) -> HandoffRuntime:
        return HandoffRuntime(event_store=RuntimeJournal(self.data_dir / "runtime.jsonl"))

    def inspect(self) -> B3ObservedReturn:
        """Source recheck, not B3 execution or hypothetical source discovery."""
        native = self._runtime()
        lane = native.get(self.lane_id)
        job = native.get(self.job_id)
        if lane.metadata.get("source_system") != _LANE_SOURCE:
            raise ValueError("not the recorded B3 continuation lane")
        edition = job.metadata.get("edition_fingerprint")
        if (job.metadata.get("worker_id") != WORKER_ID
                or not isinstance(edition, str) or len(edition) != 64
                or any(ch not in "0123456789abcdef" for ch in edition)):
            raise ValueError("native job lacks its registered B3 worker edition")
        events = native.event_store.for_handoff(self.lane_id)
        assigned = [e.data for e in events if e.event_type == _ASSIGN_EVENT]
        recorded = [e.data for e in events if e.event_type == _RETURN_EVENT]
        if (len(assigned) != 1 or len(recorded) != 1
                or assigned[0] != {"opening_id": self.opening_id,
                                   "job_id": self.job_id}):
            raise ValueError("missing or ambiguous source-owned native assignment")
        saved = recorded[0]
        if (set(saved) != {"opening_id", "job_id", "output_sha256",
                           "evidence_sha256", "source_fingerprint",
                           "claim_scope", "parent_cp_witnessed"}
                or saved["opening_id"] != self.opening_id
                or saved["job_id"] != self.job_id
                or saved["source_fingerprint"] != edition
                or saved["parent_cp_witnessed"] is not False
                or saved["claim_scope"] != "source-owned native finite helper return only"):
            raise ValueError("native B3 recorded return does not match exact source")
        # Native verifier checks current source bytes, admitted job, inputs and
        # its independently persisted result. It may persist HELP_RETURNED
        # using its existing native journaling contract on a first recheck.
        independently = verify_return(
            data_dir=self.data_dir, opening_id=self.opening_id,
        )
        if (independently.get("state") != "RETURN_RECORDED_REVERIFY_BEFORE_USE"
                or independently.get("parent_cp_witnessed") is not False
                or independently.get("child", {}).get("job_id") != self.job_id):
            raise ValueError("native B3 current return re-verification failed")
        renewed = self._runtime()
        current = renewed.state(self.job_id)
        refreshed_job = renewed.get(self.job_id)
        persisted = [e.data for e in renewed.event_store.for_handoff(self.lane_id)
                     if e.event_type == _RETURN_EVENT]
        if (current.status != "COMPLETE"
                or refreshed_job != job
                or persisted != [saved]
                or saved["output_sha256"] != canonical_digest(current.output)
                or saved["evidence_sha256"] != canonical_digest(
                    [asdict(e) for e in current.evidence])):
            raise ValueError("persisted B3 source evidence changed since native recheck")
        reference = "b3-native-return://" + self.opening_id + "/" + self.job_id
        scope = {
            "opening_id": self.opening_id, "lane_id": self.lane_id,
            "job_id": self.job_id, "edition_fingerprint": edition,
            "output_sha256": saved["output_sha256"],
            "evidence_sha256": saved["evidence_sha256"],
        }
        return B3ObservedReturn(
            opening_id=self.opening_id,
            coordination_handoff_id=self.lane_id,
            job_id=self.job_id,
            edition_fingerprint=edition,
            output_sha256=saved["output_sha256"],
            evidence_sha256=saved["evidence_sha256"],
            native_receipt_ref=reference,
            native_receipt_sha256=canonical_digest(scope),
        )


class B12B3LocalDelivery:
    """Bind real B3 native return -> B9 route -> B11 signed LOCAL_PASS.

    The operator MUST provide a key pin and signer independently, and approve
    the exact native job and delivery. Signer is never invoked on proposals.
    """

    def __init__(self, *, construction: WorkstationConstruction,
                 observed_journal_path: str | Path,
                 source: B3NativeLocalSource,
                 pinned_public_key: bytes,
                 sign_native_proof: Callable[[bytes], bytes],
                 confirm_source_job: str):
        if not isinstance(source, B3NativeLocalSource):
            raise TypeError("existing source-owned B3 native binding required")
        if not isinstance(construction, WorkstationConstruction):
            raise TypeError("B9 construction required")
        if confirm_source_job != source.job_id:
            raise PermissionError("explicit exact B3 native source job confirmation required")
        if not callable(sign_native_proof):
            raise TypeError("source-owned external signature callback required")
        snapshot = source.inspect()
        self.source = source
        self.edition = snapshot.edition_fingerprint
        self.source_locator = "b3-native://" + source.job_id
        self.sign_native_proof = sign_native_proof
        adapter = SourceAdapter(
            Capability(SOURCE_NAME, self.edition, (RELATION,), True),
            self._execute_read_only, self._observe_again,
        )
        self.delivery = SourceOwnedLocalDelivery(
            construction=construction,
            journal_path=observed_journal_path,
            adapters=(adapter,),
            pinned_public_keys={(SOURCE_NAME, self.edition): pinned_public_key},
            verify_native_current=self._current_native_proof,
        )
        self.bridge = self.delivery.bridge

    def _execute_read_only(self, cap: Capability) -> B3ObservedReturn:
        if (cap.name, cap.edition) != (SOURCE_NAME, self.edition):
            raise ValueError("source adapter called with wrong registered edition")
        return self.source.inspect()  # no native subprocess, reverify only

    def _observe_again(self, cap: Capability, returned: object) -> Witness:
        fresh = self.source.inspect()
        accepted = (isinstance(returned, B3ObservedReturn)
                    and fresh == returned
                    and cap.name == SOURCE_NAME and cap.edition == self.edition
                    and fresh.edition_fingerprint == self.edition)
        return Witness(
            "SUPPORTED" if accepted else "UNKNOWN", cap.edition,
            (RELATION,) if accepted else (),
            fresh.native_receipt_ref if accepted else "", accepted,
        )

    def _current_native_proof(self, proof: NativeLocalProof) -> bool:
        current = self.source.inspect()
        return (
            proof.source_name == SOURCE_NAME
            and proof.source_edition == self.edition
            and proof.required_relation == RELATION
            and proof.source_locator == self.source_locator
            and current.edition_fingerprint == self.edition
            and current.native_receipt_ref == proof.native_receipt_ref
            and current.native_receipt_sha256 == proof.native_receipt_sha256
        )

    def prepare(self, goal_id: str, candidate_id: str,
                *, route: tuple[str, ...]) -> str:
        """Only a matching B9 source suggestion can prepare the inert request."""
        return self.bridge.prepare(
            goal_id, candidate_id, route=route, worker_id=SOURCE_NAME,
            edition_ref=self.edition, source_locator=self.source_locator,
        )

    def deliver(self, request_id: str, *, confirm_request: str,
                allow_native_local_delivery: bool = False):
        """Recheck B3 source, sign externally, then enter native journal B11.

        Does NOT execute B3 or invent a B9 source hint. The reactor's native
        'attempt' independently reads the *same* persisted B3 return once more.
        """
        if allow_native_local_delivery is not True or confirm_request != request_id:
            raise PermissionError("explicit exact B10 request delivery approval required")
        handoff = HandoffRuntime(event_store=self.delivery.journal).get(request_id)
        if (handoff.metadata.get("source_locator") != self.source_locator
                or handoff.required_relation != RELATION
                or handoff.metadata.get("continuation_source_binding") !=
                   {"name": SOURCE_NAME, "edition": self.edition}):
            raise ValueError("prepared request differs from this source owner's B3 binding")
        current = self.source.inspect()
        proof = NativeLocalProof(
            handoff_id=request_id, source_name=SOURCE_NAME,
            source_edition=self.edition, required_relation=RELATION,
            candidate_spec_sha256=handoff.metadata["candidate_spec_sha256"],
            source_locator=self.source_locator,
            native_receipt_ref=current.native_receipt_ref,
            native_receipt_sha256=current.native_receipt_sha256,
        )
        signature = self.sign_native_proof(canonical_proof_bytes(proof))
        if not isinstance(signature, bytes) or len(signature) != 64:
            raise ValueError("native source signer must return one Ed25519 signature")
        return self.delivery.deliver(proof, signature_hex=signature.hex())
