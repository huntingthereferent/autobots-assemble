"""B9 proposal-only routing with scoped *historical* observations.

Fixture evidence is deliberately not a source-native production witness.
No source worker is admitted or executed by this example.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from systems.workspace.workstation_construction import (
    ObservationalDetermination, WorkstationConstruction,
)


def demonstrate() -> dict:
    with TemporaryDirectory() as tmp:
        builder = WorkstationConstruction(Path(tmp))
        goal = builder.goal("Ship a playable game with a verifiable receipt", provenance="example:requested-result")
        native = builder.candidate(goal, "Reuse existing native verification input", provenance="example:path-a",
                                   path_role="ALTERNATIVE")
        adapter = builder.candidate(goal, "Transform browser receipt to canonical input", provenance="example:path-b",
                                    path_role="ALTERNATIVE")
        source = builder.candidate(native, "Inspect available receipt shape", provenance="example:source-need")
        builder.propose_connection(source, adapter, reason="explore whether the receipt also fits adapter input")
        observer = ObservationalDetermination(builder,
            verify_native_receipt=lambda r: r.native_source == "fixture-only")
        observer.record(observer.receipt_for(
            native, verdict="CONTRADICTED", native_source="fixture-only",
            relation_scope="prior verifier input edition did not fit browser receipt",
            witness_ref="fixture:replay-old-input", source_report_sha256="a" * 64))
        observer.record(observer.receipt_for(
            adapter, verdict="UNKNOWN", native_source="fixture-only",
            relation_scope="canonical adapter mapping not independently determined",
            witness_ref="fixture:adapter-unresolved", source_report_sha256="b" * 64))
        builder.suggest_source(adapter, worker_id="candidate-adapter-worker",
            edition_ref="source-edition-unverified", source_locator="example://possible-adapter",
            reason="possible source fit, no native admission")
        result = builder.next_construction_handoffs(goal)
        frontier = result["construction_handoffs"]
        assert len(frontier) == 1
        paths = frontier[0]["routes_with_observational_context"]
        return {
            "required_result": result["required_result"],
            "number_of_candidate_routes": len(paths),
            "routes": [
                {"requirements": [s["candidate_requirement"] for s in route["steps"]],
                 "route_state": route["historical_route_state"],
                 "possible_next_movement": route["next_construction_movement"],
                 "intermediate_scopes": [
                     {"requirement": s["candidate_requirement"],
                      "scopes": [r["relation_scope"] for r in s["historical_determinations"]],
                      "contract_state": s["contract_state"],
                      "relation_origin": s["relation_origin"]}
                     for s in route["steps"]],
                 "whole_route_verified": route["whole_route_verified"],
                 "execution_authorized": route["execution_authorized"]}
                for route in paths
            ],
            "native_worker_executed": False,
            "demonstration_scope": "synthetic historical claims; candidate construction only",
        }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2))
