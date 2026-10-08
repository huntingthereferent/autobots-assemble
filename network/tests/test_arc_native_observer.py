"""Integration checks for observed ARC movement through the existing service."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import os
import unittest

from runtime.arc_native_observer import ARCFrameObservationProvider
from runtime.service import EcosystemService


def frame(color, *, index=36 * 64 + 36):
    board = [0] * 4096
    board[index] = color
    return SimpleNamespace(frame=[board], levels_completed=0)


class ARCNativeProviderIntegrationTests(unittest.TestCase):
    def test_service_registers_actual_native_provider_only_when_supplied(self):
        with TemporaryDirectory() as tmp:
            observer = ARCFrameObservationProvider("ft09")
            service = EcosystemService(data_dir=tmp, native_observer=observer)
            self.assertTrue(service.connections()["agents"]["ab_evaluator_connected"])
            self.assertFalse(service.connections()["agents"]["autonomous_worker_running"])
            start = service.activate_agent({
                "surface": "begin comparison", "actor_id": "james",
                "instance_id": "arc-native", "referent": "ft09 current board",
            })
            root = start["root"]
            self.assertEqual(start["ready"], [root])
            # No native step => do not consume the handoff or fabricate UNKNOWN.
            self.assertEqual(service.agent_lineage.step(root).executed, ())
            self.assertEqual(service.runtime.state(root).status, "READY")
            observer.record_native_step(
                handoff_id=root, referent="ft09 current board",
                before=frame(9), after=frame(8),
                action="ACTION6 click(36,36)", x=36, y=36,
                predicted_after={"cell_color": 8, "levels_completed": 0},
            )
            move = service.agent_lineage.step(root)
            self.assertEqual(move.executed, (root,))
            state = service.runtime.state(root)
            self.assertEqual(state.status, "COMPLETE")
            self.assertEqual(state.output["ab_state"], "MOVE")
            self.assertEqual(state.output["survived"], {"levels_completed": 0})
            self.assertEqual(state.output["changed"]["cell_color"]["before"], 9)
            self.assertEqual(state.output["changed"]["cell_color"]["after"], 8)
            self.assertEqual(len(state.evidence), 1)
            self.assertTrue(state.evidence[0].ref.startswith("arc://ft09/native-frame/sha256:"))
            self.assertEqual(service.agent_lineage.step(root).executed, ())
            other = service.activate_agent({
                "surface": "begin comparison", "actor_id": "james",
                "instance_id": "other-run", "referent": "ft09 current board",
            })
            self.assertEqual(other["ready"], [other["root"]])
            with self.assertRaisesRegex(ValueError, "already captured"):
                observer.record_native_step(
                    handoff_id=root, referent="ft09 current board",
                    before=frame(9), after=frame(8),
                    action="ACTION6", x=36, y=36,
                )
            restarted = EcosystemService(data_dir=tmp, native_observer=observer)
            self.assertEqual(restarted.runtime.state(root).status, "COMPLETE")
            self.assertEqual(restarted.agent_lineage.step(root).executed, ())

    def test_provider_mismatch_and_incomplete_native_data(self):
        observer = ARCFrameObservationProvider("ft09")
        with self.assertRaisesRegex(ValueError, "64x64"):
            observer.record_native_step(
                handoff_id="one", referent="board",
                before=SimpleNamespace(frame=[[9]], levels_completed=0),
                after=frame(8), action="ACTION6", x=36, y=36,
            )
        observer.record_native_step(
            handoff_id="one", referent="wrong board",
            before=frame(9), after=frame(8), action="ACTION6", x=36, y=36,
            predicted_after={"cell_color": 8, "levels_completed": 0},
        )
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp, native_observer=observer)
            root = service.activate_agent({
                "surface": "begin comparison", "actor_id": "james",
                "instance_id": "wrong-source", "referent": "correct board",
            })["root"]
            self.assertEqual(service.runtime.state(root).status, "READY")
            observer._captured[root] = observer._captured.pop("one")
            service.agent_lineage.step(root)
            self.assertEqual(service.runtime.state(root).status, "UNKNOWN")
            self.assertEqual(service.runtime.state(root).evidence, ())

    @unittest.skipUnless(os.environ.get("CONTINUITY_ARC_NATIVE_TESTS") == "1",
                         "explicit opt-in required for real ARC game movement")
    def test_actual_ft09_sdk_step_to_service_lineage(self):
        from arc_agi import Arcade, OperationMode
        from arcengine import GameAction
        arcade = Arcade(operation_mode=OperationMode.NORMAL)
        game = arcade.make("ft09")
        before = game.observation_space
        import numpy as np
        old_color = int(np.asarray(before.frame[-1]).reshape(-1)[36 * 64 + 36])
        after = game.step(GameAction.ACTION6, data={"x": 36, "y": 36})
        new_color = int(np.asarray(after.frame[-1]).reshape(-1)[36 * 64 + 36])
        self.assertNotEqual(old_color, new_color)
        observer = ARCFrameObservationProvider("ft09")
        with TemporaryDirectory() as tmp:
            service = EcosystemService(data_dir=tmp, native_observer=observer)
            root = service.activate_agent({
                "surface": "begin comparison", "actor_id": "james",
                "instance_id": "actual-ft09", "referent": "ft09 current board",
            })["root"]
            observer.record_native_step(
                handoff_id=root, referent="ft09 current board",
                before=before, after=after,
                action="ACTION6 click(36,36)", x=36, y=36,
                predicted_after={"cell_color": new_color,
                                 "levels_completed": int(after.levels_completed)},
            )
            self.assertEqual(service.agent_lineage.step(root).executed, (root,))
            self.assertEqual(service.runtime.state(root).status, "COMPLETE")
            self.assertEqual(service.runtime.state(root).output["ab_state"], "MOVE")


if __name__ == "__main__":
    unittest.main()
