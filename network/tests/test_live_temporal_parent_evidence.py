"""Independent live-temporal source parent is not historical owner W13."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import json
import unittest
from systems.workspace.live_temporal_parent_evidence import (
    ORIGINAL_SEVEN, OWNER_W13, require_isolated_source_lineage, source_witness)
from systems.workspace.game_temporal_bridge import JOB_ID


class IndependentLiveTemporalSourceTests(unittest.TestCase):
    def test_seven_job_source_lineage_is_distinct_from_owner_w13(self):
        require_isolated_source_lineage(tuple(ORIGINAL_SEVEN))
        for old in OWNER_W13:
            with self.assertRaisesRegex(ValueError,"seven exact"):
                require_isolated_source_lineage(tuple(ORIGINAL_SEVEN)+(old,))
        self.assertNotIn("game-w13-github-001",ORIGINAL_SEVEN)
        self.assertNotIn("game-native-verifier-github-001",ORIGINAL_SEVEN)
        self.assertIn(JOB_ID,ORIGINAL_SEVEN)

    def test_no_parent_result_or_browser_proof_cannot_be_imagined(self):
        with TemporaryDirectory() as tmp:
            d=Path(tmp)
            with self.assertRaisesRegex(ValueError,"journal, stack report and browser proof"):
                source_witness(data_dir=d,output_dir=d)
            for name,content in (
                ("runtime.jsonl",""),
                ("game-temporal-complete-stack.json",json.dumps({
                    "schema":"complete-stack-live-temporal-game/v1",
                    "source_owned_jobs":7,"new_native_build":JOB_ID,
                    "game_temporal_browser":"NOT_RUN","synthetic_only":True
                })),
                ("game-temporal-witness.json",json.dumps({"game_solved":True})),
            ):
                (d/name).write_text(content)
            with self.assertRaisesRegex(ValueError,"browser/CP boundary incomplete"):
                source_witness(data_dir=d,output_dir=d)

    def test_source_witness_has_no_job_admission_or_execution(self):
        source=inspect.getsource(source_witness)
        for forbidden in (".execute(", ".admit(", ".copy_source(", ".submit("):
            self.assertNotIn(forbidden,source)
        self.assertIn("reverify_local(",source)
        self.assertIn("owner_w13_child_journal_present",source)
        self.assertIn("game_worker_ready_witnessed",source)


if __name__=="__main__":
    unittest.main()
