"""Native Cyclic Action Engine witness admission through the existing HandoffRuntime.

The runtime transports referents and evidence; it does not prove mathematics.
This adapter persists native snapshots separately, replays them with the actual
CyclicActionContinuation code, and enforces the requested claim at the handoff
boundary. Its digest checks are local integrity checks, not authentication.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff, HandoffState
from .cyclic_action_continuation import CyclicActionContinuation, ContinuationWitness


VERIFIER_ID = "cyclic-action.restricted-B.v1"
B_CONJUGATE = "B_ONLY_CONJUGACY"
B_DISTINGUISHED = "B_ONLY_NONCONJUGACY"
AB_CONJUGATE = "SIMULTANEOUS_AB_CONJUGACY"
CLAIMS = (B_CONJUGATE, B_DISTINGUISHED, AB_CONJUGATE)


class CyclicActionHandoff:
    """Source-owned snapshot archive and verifier for an existing handoff runtime."""

    def __init__(self, runtime: HandoffRuntime, archive_dir: str | Path):
        self.runtime = runtime
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.runtime.register_evidence_verifier(VERIFIER_ID, self._verify_result)

    def _save(self, witness: ContinuationWitness) -> str:
        witness.verify()
        snapshot = witness.snapshot()
        ref = sha256(snapshot.encode("utf-8")).hexdigest()
        path = self.archive_dir / (ref + ".json")
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(snapshot)
        except FileExistsError:
            if path.read_text(encoding="utf-8") != snapshot:
                raise ValueError("existing witness archive content differs")
        return ref

    def _load(self, handoff: Handoff) -> ContinuationWitness:
        if handoff.metadata.get("native_evidence_verifier") != VERIFIER_ID:
            raise ValueError("handoff is not registered for this native verifier")
        ref = handoff.inputs.get("native_witness_ref")
        if not isinstance(ref, str) or re.fullmatch(r"[0-9a-f]{64}", ref) is None:
            raise ValueError("missing or malformed native witness reference")
        snapshot = (self.archive_dir / (ref + ".json")).read_text(encoding="utf-8")
        if sha256(snapshot.encode("utf-8")).hexdigest() != ref:
            raise ValueError("stored witness content changed")
        witness = CyclicActionContinuation.reenter(snapshot)
        if witness.source_identity != handoff.inputs.get("native_source_identity"):
            raise ValueError("source identity changed across handoff")
        return witness

    def submit(
        self,
        witness: ContinuationWitness,
        *,
        handoff_id: str,
        claim: str,
        previous_handoff_id: str | None = None,
    ) -> HandoffState:
        if claim not in CLAIMS:
            raise ValueError("unsupported requested mathematical relation")
        witness.verify()
        provenance = ("Cyclic Action Engine native WindowProcess witness",)
        if previous_handoff_id is not None:
            previous_handoff = self.runtime.get(previous_handoff_id)
            previous_state = self.recover(previous_handoff_id)
            if previous_state.status not in ("UNKNOWN", "COMPLETE", "BLOCKED"):
                raise ValueError("previous handoff has no recoverable result")
            previous = self._load(previous_handoff)
            if (
                witness.source_identity != previous.source_identity
                or witness.observations[:len(previous.observations)] != previous.observations
                or witness.budgets[:len(previous.budgets)] != previous.budgets
            ):
                raise ValueError("continuation did not preserve prior mathematical observations")
            provenance += ("handoff:" + previous_handoff_id,)
        ref = self._save(witness)
        return self.runtime.submit(Handoff(
            handoff_id=handoff_id,
            referent="Cyclic Action Engine restricted B-action witness",
            from_actor="cyclic-action-engine",
            to_actor="continuity",
            required_relation=claim,
            inputs={
                "native_witness_ref": ref,
                "native_source_identity": witness.source_identity,
            },
            expected_output={"requested_claim": claim},
            required_witnesses=("native mathematical verification",),
            admissible_evidence={"native mathematical verification": ("native-replay",)},
            boundaries=(
                "B only on the 81-state x0=2 invariant fiber",
                "no simultaneous A/B conjugacy established",
            ),
            provenance=provenance,
            metadata={"native_evidence_verifier": VERIFIER_ID},
        ))

    def _expected_result(self, handoff: Handoff) -> ExecutionResult:
        witness = self._load(handoff)
        claim = handoff.required_relation
        if claim not in CLAIMS:
            raise ValueError("handoff requests an unrecognized relation")
        native = witness.status
        if claim == AB_CONJUGATE:
            status = "BLOCKED"
        elif native == "UNKNOWN":
            status = "UNKNOWN"
        elif ((claim == B_CONJUGATE and native == "EQUIVALENT_FOR_B_ONLY")
              or (claim == B_DISTINGUISHED and native == "DISTINGUISHED")):
            status = "COMPLETE"
        else:
            status = "BLOCKED"
        output = {
            "requested_claim": claim,
            "native_status": native,
            "watched_scope": "B_ONLY_ON_x0_EQ_2",
            "state_count": 81,
            "observed_through": len(witness.observations),
            "distinguishing_depth": witness.distinguishing_depth,
            "bijection_verified": witness.bijection is not None,
            "does_not_establish": "simultaneous A/B conjugacy",
        }
        evidence = (EvidenceRecord(
            condition="native mathematical verification",
            kind="native-replay",
            source="CyclicActionContinuation.reenter",
            ref=handoff.inputs["native_witness_ref"],
            depth="verified" if status == "COMPLETE" else "replayed",
            note="replayed the source laws, scope, budgets and observations",
        ),)
        return ExecutionResult(status=status, output=output, evidence=evidence)

    def _verify_result(self, handoff: Handoff, result: ExecutionResult) -> None:
        if result != self._expected_result(handoff):
            raise ValueError("reported result exceeds or contradicts native witness")

    def conclude(self, handoff_id: str) -> HandoffState:
        handoff = self.runtime.get(handoff_id)
        if self.runtime.state(handoff_id).status != "READY":
            raise ValueError("handoff is not ready for a first native result")
        return self.runtime.return_result(
            handoff_id, actor_id="cyclic-action-engine",
            result=self._expected_result(handoff),
        )

    def recover(self, handoff_id: str) -> HandoffState:
        """Re-verify after journal reload; a recorded result is not new proof."""
        handoff = self.runtime.get(handoff_id)
        state = self.runtime.state(handoff_id)
        expected = self._expected_result(handoff)
        if state.status in ("COMPLETE", "UNKNOWN", "BLOCKED"):
            if (state.status != expected.status or state.output != expected.output
                    or state.evidence != expected.evidence):
                raise ValueError("persistent handoff diverged from the native witness")
        return state
