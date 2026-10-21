"""Native audio source movement through actual workstation editions and handoffs."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import struct
import unittest
import wave

from runtime.handoff import ExecutionResult
from systems.workspace.audio_motion_native import (expected_result, read_wav_request,
                                                     validate_input, content_sha)
from systems.workspace.audio_motion_bridge import (AudioMotionBridge, WORKER_ID,
                                                   copy_audio_source)
from systems.workspace import WorkspaceStore


def wav(path, frames=2048):
    signal = [int(9000 * math.sin(2 * math.pi * i / 41)) for i in range(frames)]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(struct.pack("<" + "h"*len(signal), *signal))
    return signal


class AudioNativeWorkstationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.wav = self.dir / "sample.wav"
        self.samples = wav(self.wav)
        self.data = self.dir / "private"

    def setup_bridge(self):
        copy_audio_source(self.data, "v1", allow_copy=True)
        return AudioMotionBridge(self.data)

    def test_explicit_copy_and_execute_gates(self):
        with self.assertRaises(PermissionError):
            copy_audio_source(self.data, "v1")
        bridge = self.setup_bridge()
        data = read_wav_request(self.wav, target_note=67)
        job = bridge.admit("v1", data, from_actor="owner")
        self.assertEqual(bridge.runtime.state(job.handoff_id).status, "READY")
        with self.assertRaises(PermissionError):
            bridge.execute(job.handoff_id)
        self.assertEqual(bridge.runtime.state(job.handoff_id).status, "READY")

    def test_real_copy_child_native_replay_and_workspace_continuation(self):
        bridge = self.setup_bridge()
        data = read_wav_request(self.wav, target_note=67, reverse=True)
        self.assertEqual(data["source_sha256"], sha256(self.wav.read_bytes()).hexdigest())
        job = bridge.admit("v1", data, from_actor="owner")
        state = bridge.execute(job.handoff_id, allow_local_execution=True)
        self.assertEqual(state.status, "COMPLETE")
        self.assertEqual(state.output["result"], expected_result(data))
        receipt = bridge.reverify(job.handoff_id)
        self.assertEqual(receipt["pcm_sha256"], content_sha(state.output["result"]["pcm"]))
        movement = bridge.record_movement(job.handoff_id)
        self.assertTrue(movement["movement_recorded"])
        self.assertFalse(bridge.record_movement(job.handoff_id)["movement_recorded"])
        exported = self.dir / "result.wav"
        report = bridge.export(job.handoff_id, exported)
        with wave.open(str(exported), "rb") as w:
            self.assertEqual((w.getnchannels(), w.getsampwidth(), w.getframerate()), (1, 2, 16000))
            self.assertEqual(w.getnframes(), len(self.samples))
        self.assertEqual(report["pcm_sha256"], receipt["pcm_sha256"])
        restored = AudioMotionBridge(self.data)
        self.assertTrue(restored.reverify(job.handoff_id)["reverified"])
        store = WorkspaceStore(self.data / "workspace.jsonl")
        self.assertEqual(store.get_lane("creative-audio-motion").movements, 1)
        self.assertEqual(len([e for e in store.history("creative-audio-motion")
                              if e["event_type"] == "LANE_MOVED"]), 1)
        self.assertEqual(restored.runtime.state(job.handoff_id).status, "COMPLETE")

    def test_host_rejects_fabricated_output_and_source_mutation(self):
        bridge = self.setup_bridge()
        job = bridge.admit("v1", read_wav_request(self.wav, target_note=65), from_actor="owner")
        bridge.execute(job.handoff_id, allow_local_execution=True)
        state = bridge.runtime.state(job.handoff_id)
        forged = dict(state.output)
        forged["result"] = dict(forged["result"])
        forged["result"]["pcm"] = list(forged["result"]["pcm"])
        forged["result"]["pcm"][7] += 1
        with self.assertRaises(ValueError):
            bridge._verify(job, ExecutionResult(status="COMPLETE", output=forged, evidence=state.evidence))
        source = self.data / "workstation" / WORKER_ID / "v1" / "motion_worker.py"
        source.write_text(source.read_text() + "\n# altered after admission\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            bridge.reverify(job.handoff_id)
        with self.assertRaises(ValueError):
            bridge.export(job.handoff_id, self.dir/"forged.wav")

    def test_malformed_input_and_non_pcm_file_fail_closed(self):
        valid = read_wav_request(self.wav, target_note=72)
        for key, new in (("target_note", 73), ("sample_rate", 0),
                         ("root_note", True), ("reverse", 1), ("source_sha256", "not-a-hash")):
            row = dict(valid)
            row[key] = new
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_input(row)
        bad = dict(valid)
        bad["pcm"] = valid["pcm"] + [0] * 10000
        with self.assertRaises(ValueError):
            validate_input(bad)
        path = self.dir/"unknown.wav"
        path.write_bytes(b"not an audio file")
        with self.assertRaises(ValueError):
            read_wav_request(path)
        with self.assertRaises(ValueError):
            read_wav_request(self.wav, root_note=5, target_note=60)


if __name__ == "__main__":
    unittest.main()
