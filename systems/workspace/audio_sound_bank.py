"""Meow Lab 2 sound intake: opt-in batch admission from audio files into native workstation movement.

This is a source-owning adapter, not an API bridge to Suno. Each accepted WAV
gets a separate actual HandoffRuntime job and independent host PCM verification.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from .audio_motion_bridge import AudioMotionBridge, copy_audio_source
from .audio_motion_native import read_wav_request

SLOTS = ("miso", "mochi", "nori", "bean")


def build_sound_bank(*, data_dir: str | Path, source_dir: str | Path,
                     output_dir: str | Path, version: str, move_semitones: int = 0,
                     allow_copy: bool = False, allow_execute: bool = False) -> dict:
    if not allow_copy or not allow_execute:
        raise PermissionError("explicit source copy and execution required")
    if type(move_semitones) is not int or not -12 <= move_semitones <= 12:
        raise ValueError("bounded semitone movement must be within +/-12")
    source = Path(source_dir)
    destination = Path(output_dir)
    if source.is_symlink() or not source.is_dir() or destination.resolve().is_relative_to(source.resolve()):
        raise ValueError("ordinary input folder and separate output folder required")
    sources = sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() == ".wav")
    if not sources or len(sources) > len(SLOTS):
        raise ValueError("one to four named PCM16 WAV files required")
    unknown = [p for p in sources if p.stem not in SLOTS]
    if unknown or len({p.stem for p in sources}) != len(sources):
        raise ValueError("files must be miso.wav, mochi.wav, nori.wav, bean.wav (up to four)")
    # Validate all inputs before any source copy, handoff, or export.
    payloads = [(p, read_wav_request(p, root_note=60, target_note=60+move_semitones)) for p in sources]
    copy_audio_source(data_dir, version, allow_copy=True)
    bridge = AudioMotionBridge(data_dir)
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for path, payload in payloads:
        job = bridge.admit(version, payload, from_actor="workstation-operator")
        state = bridge.execute(job.handoff_id, allow_local_execution=True)
        if state.status != "COMPLETE":
            raise ValueError("native worker did not return COMPLETE")
        receipt = bridge.record_movement(job.handoff_id)
        saved = bridge.export(job.handoff_id, destination/(path.stem+".wav"))
        records.append({"slot": path.stem, "job_id": job.handoff_id,
                        "source_name": path.name, "original_sha256": payload["source_sha256"],
                        "processed_pcm_sha256": receipt["pcm_sha256"],
                        "output_filename": path.stem+".wav", "export_sha256": sha256(Path(saved["path"]).read_bytes()).hexdigest(),
                        "movement_event": receipt["return_event"],
                        "native_reverified": True, "semitones": move_semitones,
                        "sample_rate": receipt["frames"] and saved["sample_rate"], "frames": saved["frames"]})
    manifest = {"schema": "ab-workstation/cat-sound-bank/v1",
                "kind": "local-native-reverified-receipt",
                "worker": "audio-pcm-motion", "version": version,
                "native_verifier": "workstation:audio-motion-native/v1",
                "assets": records, "source_policy": "user-selected PCM16; file rights not inferred"}
    (destination/"sound-bank-manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2)+"\n", encoding="utf8")
    return manifest


def main():
    p=argparse.ArgumentParser(description="Ingest up to four user-selected WAVs through the real private workstation")
    p.add_argument("--data-dir",default="runtime/data")
    p.add_argument("--source-dir",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--version",default="meow-sounds-v1")
    p.add_argument("--semitones",type=int,default=0)
    p.add_argument("--copy-source",action="store_true")
    p.add_argument("--execute",action="store_true")
    args=p.parse_args()
    print(json.dumps(build_sound_bank(data_dir=args.data_dir,source_dir=args.source_dir,
        output_dir=args.output_dir,version=args.version,move_semitones=args.semitones,
        allow_copy=args.copy_source,allow_execute=args.execute),indent=2))


if __name__ == "__main__":
    main()
