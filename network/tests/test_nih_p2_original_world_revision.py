"""Pure negative control tests; fixtures are never counted as game-world evidence."""
from copy import deepcopy
import unittest

from scripts.nih_p2_original_world_revision import (
    snapshots,independent_oracle,validate_frames,apply_overlay,SNAPSHOTS,frame_for_verifier)

BASE={
    "kind":"temporal-scope/v1","synthetic":True,"case_id":"synthetic-interval",
    "application":"research-evidence",
    "question":"Which synthetic source observations were known by the selected date?",
    "query_at":"2026-01-04","target_at":"2026-01-04",
    "observations":[
        {"id":"delayed-result","subject":"study-alpha",
         "predicate":"has-status","object":"synthetic-original-value",
         "valid_from":"2026-01-03","valid_to":"2026-01-08",
         "known_at":"2026-01-05","source_ref":"synthetic-late-source"},
        {"id":"prior-note","subject":"study-alpha",
         "predicate":"has-status","object":"synthetic-prior-value",
         "valid_from":"2026-01-02","valid_to":"2026-01-10",
         "known_at":"2026-01-01","source_ref":"synthetic-first-source"},
    ],
}
def sources():
    from systems.workspace.nih_scope_native import validate_scope
    scope=validate_scope(BASE)
    dataset={"synthetic":True,"observations":scope["observations"],
        "functional_predicates":["has-status"]}
    return snapshots(scope,dataset)

def frames():
    versions=sources()
    rows=[]
    for turn in range(5):
        known="2026-01-04" if turn<2 else "2026-01-06"
        for name in SNAPSHOTS:
            result=independent_oracle(versions[name],known=known,target="2026-01-04")
            rows.append(frame_for_verifier(
                turn=turn,snapshot=name,known=known,result=result,
                program="d"*64,
                edition={"baseline":"a"*64,"corrected":"b"*64,"withdrawn":"c"*64}[name]))
    return rows

class RevisionWorldTests(unittest.TestCase):
    def test_01_snapshot_facts_have_distinct_ownership(self):
        versions=sources()
        self.assertEqual(tuple(versions),SNAPSHOTS)
        self.assertEqual(len(versions["baseline"]["observations"]),2)
        self.assertEqual(len(versions["withdrawn"]["observations"]),1)
        self.assertEqual({r["id"] for r in versions["corrected"]["observations"]},
                         {"prior-note","corrected-result"})
        self.assertEqual({r["id"] for r in versions["baseline"]["observations"]},
                         {"prior-note","delayed-result"})
        b=independent_oracle(versions["baseline"],known="2026-01-06",target="2026-01-04")
        c=independent_oracle(versions["corrected"],known="2026-01-06",target="2026-01-04")
        w=independent_oracle(versions["withdrawn"],known="2026-01-06",target="2026-01-04")
        self.assertIn("delayed-result",b["temporal_ids"])
        self.assertIn("corrected-result",c["temporal_ids"])
        self.assertNotIn("delayed-result",c["temporal_ids"])
        self.assertEqual(w["temporal_ids"],["prior-note"])
        self.assertNotEqual(b["visible_source_refs"],c["visible_source_refs"])

    def test_02_fixed_source_monotonic_but_revision_breaks_merged_ids(self):
        rows=frames()
        report=validate_frames(rows,actions=4,cutover=2,program="d"*64,
            editions={"baseline":"a"*64,"corrected":"b"*64,"withdrawn":"c"*64})
        self.assertEqual([r["source_snapshot"] for r in report],list(SNAPSHOTS))
        self.assertEqual([r["game_turn"] for r in report],[2,2,3])
        self.assertEqual(report[-1]["visible"],["prior-note"])

    def test_03_reject_drift_duplicates_missing_or_fake_withdrawal(self):
        base=frames()
        for idx,changes in (
            (0,{"original_program_sha256":"f"*64}),
            (1,{"snapshot_dataset_sha256":"f"*64}),
            (3,{"known_at":"2026-01-06"}),
            (4,{"independent_host_agreement":False}),
            (6,{"temporal_ids":["prior-note"]}),
            (7,{"temporal_ids":["prior-note"]}),
            (8,{"temporal_ids":["delayed-result","prior-note"]}),
            (11,{"temporal_ids":["corrected-result","prior-note"]}),
        ):
            corrupted=deepcopy(base)
            corrupted[idx].update(changes)
            with self.subTest(idx=idx),self.assertRaises(ValueError):
                validate_frames(corrupted,actions=4,cutover=2,program="d"*64,
                    editions={"baseline":"a"*64,"corrected":"b"*64,"withdrawn":"c"*64})
        for corrupted in (deepcopy(base[:-1]),deepcopy(base)):
            if len(corrupted)==len(base):corrupted[1]=deepcopy(corrupted[0])
            with self.assertRaises(ValueError):
                validate_frames(corrupted,actions=4,cutover=2,program="d"*64,
                    editions={"baseline":"a"*64,"corrected":"b"*64,"withdrawn":"c"*64})

    def test_04_requires_prior_game_not_replace_it(self):
        html='<script id="phase1-world-two-clock"></script><script id="phase1-world-frontier-source"></script></body>'
        modified=apply_overlay(html)
        self.assertEqual(modified.count('id="nih-p2-revision-world"'),1)
        self.assertIn("nihRevisionProbe",modified)
        with self.assertRaises(ValueError):apply_overlay(modified)
        with self.assertRaises(ValueError):apply_overlay("<body></body>")

if __name__=="__main__":
    unittest.main()
