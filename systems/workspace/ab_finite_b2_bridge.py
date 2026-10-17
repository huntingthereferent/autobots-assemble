"""Read independently witnessed finite A/B worker relationships into existing B2.

No new worker, AI model, generic A/B claim, or independent relation-connector
registration. B2 can retain an OPEN_UNSTAFFED need for a real source owner.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

from .ab_relational_cluster import _pending, _strict_object, read_history
from .workstation_harness import WorkstationContinuationHarness


def _relation(state: tuple[int, int, int]) -> str:
    return "finite-F3-native-state:" + ",".join(str(x) for x in state)


def _load_source(path: Path, *, expected_head: str | None = None) -> tuple[dict, str, dict]:
    # The source-native verifier recomputes the ENTIRE finite trail and
    # rejects forged collisions even if the attacker recalculates JSON hashes.
    state, head = read_history(path)
    if (expected_head is not None and head != expected_head):
        raise ValueError("finite A/B journal head differs from authorized source")
    if (len(state["nodes"]) != 27 or state["connections"] != 28
            or state["events"] != 10 or _pending(state, 10)):
        raise ValueError("native finite source is not the complete witnessed frontier")
    records: dict[str, dict] = {}
    links = []
    # Source records are solely mathematical states/trajectories. No generic
    # identity, native owner, AI helper, or universal relation inferred here.
    for line in path.read_text(encoding="utf8").splitlines():
        row = json.loads(line, object_pairs_hook=_strict_object)
        for m in row["movements"]:
            word = m["word"]
            if word in records:
                raise ValueError("finite native worker reported duplicate trajectory word")
            records[word] = m
            if m["kind"] != "CONNECTION" or not m["existing_word"]:
                continue
            prior = records.get(m["existing_word"])
            if prior is None or prior["kind"] != "BRANCH":
                raise ValueError("native connection missing its prior branch movement")
            if m["word"][:1] not in ("A", "B") or prior["word"][:1] not in ("A", "B"):
                continue
            if m["word"][0] == prior["word"][0]:
                continue
            if m["to"] != prior["to"]:
                raise ValueError("native mathematical join lacks identical finite state")
            links.append((prior["word"], m["word"], tuple(m["to"])))
    if len(records) != 54 or len(links) != 8:
        raise ValueError("finite journal lost or gained cross-trajectory relationships")
    return state, head, {"records": records, "links": links}


class FiniteABSource:
    """Fresh native journal replay supplies existing B2's two witness callbacks."""

    def __init__(self, source_path: Path, *, expected_head: str):
        self.source_path = Path(source_path)
        if len(expected_head) != 64 or any(c not in "0123456789abcdef" for c in expected_head):
            raise ValueError("exact source-native SHA-256 journal head required")
        self.expected_head = expected_head
        _load_source(self.source_path, expected_head=expected_head)

    def _fresh(self):
        _, head, detail = _load_source(self.source_path, expected_head=self.expected_head)
        return head, detail

    def witness(self, word: str) -> str:
        return "finite-ab:" + self.expected_head + ":" + word

    def _movement(self, obs, source: dict) -> dict | None:
        prefix = "finite-ab:" + self.expected_head + ":"
        if (obs.kind != "RELATION" or obs.capability != ""
                or not obs.witness_ref.startswith(prefix)
                or obs.lane_id not in ("finite-A", "finite-B")):
            return None
        word = obs.witness_ref[len(prefix):]
        m = source["records"].get(word)
        if (not m or not word or obs.lane_id != "finite-" + word[0]
                or obs.relation != _relation(tuple(m["to"]))):
            return None
        return m

    def verify_observation(self, observation) -> bool:
        try:
            _, source = self._fresh()
            return self._movement(observation, source) is not None
        except (ValueError, KeyError, TypeError, OSError):
            return False

    def verify_connection(self, a, b) -> bool:
        try:
            _, source = self._fresh()
            x, y = self._movement(a, source), self._movement(b, source)
            if x is None or y is None:
                return False
            if x["to"] != y["to"] or x["word"][0] == y["word"][0]:
                return False
            return (x["word"], y["word"], tuple(x["to"])) in source["links"] or (
                y["word"], x["word"], tuple(x["to"])) in source["links"]
        except (ValueError, KeyError, TypeError, OSError):
            return False

    def import_into_workstation(self, data_dir: Path, *, origin: str) -> dict:
        """Record verified math relations without fabricating a B2 connecting worker."""
        data_dir = Path(data_dir)
        _, source = self._fresh()
        # Store a private copy of the authentic source journal with B2, so
        # future passes can revalidate without relying on a transient Actions ZIP.
        saved = data_dir / "finite-sources" / "ab_relational_cluster.jsonl"
        if not saved.exists():
            saved.parent.mkdir(parents=True, exist_ok=True)
            if self.source_path.resolve() != saved.resolve():
                shutil.copyfile(self.source_path, saved)
        if _load_source(saved, expected_head=self.expected_head)[1] != self.expected_head:
            raise ValueError("durable source copy failed exact native verification")
        evidence = FiniteABSource(saved, expected_head=self.expected_head)
        harness = WorkstationContinuationHarness(
            data_dir,
            verify_observation=evidence.verify_observation,
            verify_connection=evidence.verify_connection,
            worker_editions={},  # NO made-up relation-connector native worker.
        )
        harness.seed_lane("finite-A", "F3 finite mathematical trajectory starting with A")
        harness.seed_lane("finite-B", "F3 finite mathematical trajectory starting with B")
        for owner_word, other_word, target in source["links"]:
            relation = _relation(target)
            harness.observe(
                lane_id="finite-" + owner_word[0], kind="RELATION",
                relation=relation, witness_ref=evidence.witness(owner_word))
            harness.observe(
                lane_id="finite-" + other_word[0], kind="RELATION",
                relation=relation, witness_ref=evidence.witness(other_word))
        movement = harness.tick()
        snapshot = harness.inspect()
        # All eight newly witnessed cross-trajectory coincidences are
        # preserved in the original B2 journal. No source-owner native connector
        # is installed, so their connection assignments stay unstaffed.
        if (len(snapshot["lanes"]) != 2
                or len(snapshot["proposals"]) != len(source["links"])
                or any(p["kind"] != "OPEN_UNSTAFFED" for p in snapshot["proposals"])):
            raise ValueError("B2 finite relation intake changed source-owned boundaries")
        return {
            "schema": "finite-ab-to-existing-B2/v1",
            "source_journal_head": self.expected_head,
            "source_description": origin,
            "math_states_verified": 27,
            "math_transitions_verified": 54,
            "math_connections_verified": 28,
            "source_native_cross_trajectory_connections": len(source["links"]),
            "B2_relations_exposed": len(snapshot["proposals"]),
            "B2_new_unstaffed_openings": len(movement["open_unstaffed"]),
            "bounded_workers_executed_by_bridge": False,
            "model_helpers_used": False,
            "native_connector_available": False,
            "independently_rechecked": True,
            "source_journal_sha256": sha256(saved.read_bytes()).hexdigest(),
            "workstation_handoff_ids": [
                "finite-A", "finite-B",
            ],
            "example_connection": {
                "existing_path": source["links"][0][0],
                "new_path": source["links"][0][1],
                "finite_state": list(source["links"][0][2]),
            },
        }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-journal", required=True, type=Path)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--origin", default="source-owned finite mathematical worker")
    args = parser.parse_args(argv)
    report = FiniteABSource(args.source_journal, expected_head=args.source_head).import_into_workstation(
        args.data_dir, origin=args.origin)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
