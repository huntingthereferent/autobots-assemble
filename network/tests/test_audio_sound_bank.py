"""Batch sound-bank sources must get real independent native worker receipts."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import math
import struct
import unittest
import wave

from systems.workspace.audio_sound_bank import build_sound_bank
from systems.workspace.audio_motion_bridge import AudioMotionBridge
from systems.workspace.store import WorkspaceStore


def write_wave(path, f=220):
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        values=[round(11000*math.sin(i*2*math.pi*f/16000)) for i in range(2048)]
        w.writeframes(struct.pack("<"+"h"*len(values),*values))


class SwallowSoundsTests(unittest.TestCase):
    def test_four_sources_move_through_real_workstation(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);src=root/"input";src.mkdir()
            for name,freq in zip(("miso","mochi","nori","bean"),(210,420,160,330)):
                write_wave(src/(name+".wav"),freq)
            data=root/"private";out=root/"bank"
            with self.assertRaises(PermissionError):
                build_sound_bank(data_dir=data,source_dir=src,output_dir=out,version="native-1")
            receipt=build_sound_bank(data_dir=data,source_dir=src,output_dir=out,version="native-1",
                move_semitones=5,allow_copy=True,allow_execute=True)
            self.assertEqual(len(receipt["assets"]),4)
            self.assertEqual(len({item["job_id"] for item in receipt["assets"]}),4)
            self.assertTrue(all(item["native_reverified"] for item in receipt["assets"]))
            bridge=AudioMotionBridge(data)
            for item in receipt["assets"]:
                self.assertTrue(bridge.reverify(item["job_id"])["reverified"])
                self.assertTrue((out/item["output_filename"]).is_file())
            self.assertEqual(WorkspaceStore(data/"workspace.jsonl").get_lane("creative-audio-motion").movements,4)
            saved=json.loads((out/"sound-bank-manifest.json").read_text())
            self.assertEqual(saved,receipt)

    def test_refuse_unbounded_source_or_unsafe_destination(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);src=root/"input";src.mkdir()
            write_wave(src/"stranger.wav")
            with self.assertRaises(ValueError):
                build_sound_bank(data_dir=root/"private",source_dir=src,output_dir=root/"out",
                    version="v1",allow_copy=True,allow_execute=True)
            (src/"stranger.wav").rename(src/"miso.wav")
            with self.assertRaises(ValueError):
                build_sound_bank(data_dir=root/"private",source_dir=src,output_dir=src/"output",
                    version="v1",allow_copy=True,allow_execute=True)
            with self.assertRaises(ValueError):
                build_sound_bank(data_dir=root/"private",source_dir=src,output_dir=root/"out",
                    version="v1",move_semitones=15,allow_copy=True,allow_execute=True)
