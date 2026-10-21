"""Host-owned PCM16 movement contract and independent native replay.

Movement is from actual finite audio samples, not a Suno generation claim.
The host does not import executable code from the private copied worker.
"""
from __future__ import annotations

from hashlib import sha256
import math
from pathlib import Path
import re
import struct
import wave

SCHEMA = "ab-audio-motion/v1"
RESULT_SCHEMA = "ab-audio-motion-result/v1"
VERIFIER = "workstation:audio-motion-native/v1"
WITNESS = "host-owned pcm16 movement replay"
SOURCE_LOCATOR = "repo:systems/workspace/audio_motion_worker_source/motion_worker.py"


def validate_input(row: object) -> dict:
    names = {"schema", "sample_rate", "pcm", "root_note", "target_note", "source_sha256", "reverse"}
    if type(row) is not dict or set(row) != names or row["schema"] != SCHEMA:
        raise ValueError("invalid audio movement contract")
    pcm = row["pcm"]
    if (type(pcm) is not list or not 128 <= len(pcm) <= 8192
            or any(type(x) is not int or not -32768 <= x <= 32767 for x in pcm)):
        raise ValueError("expected bounded 16-bit mono PCM")
    rate, root, note = row["sample_rate"], row["root_note"], row["target_note"]
    if type(rate) is not int or not 8000 <= rate <= 96000:
        raise ValueError("unsupported sample rate")
    if (type(root) is not int or type(note) is not int
            or not 0 <= root <= 127 or not 0 <= note <= 127 or abs(note-root) > 12):
        raise ValueError("pitch movement must be within 12 semitones")
    if type(row["reverse"]) is not bool:
        raise ValueError("reverse must be boolean")
    if type(row["source_sha256"]) is not str or re.fullmatch("[0-9a-f]{64}", row["source_sha256"]) is None:
        raise ValueError("source hash required")
    return {k: row[k] if k != "pcm" else list(pcm) for k in sorted(names)}


def expected_result(raw: object) -> dict:
    row = validate_input(raw)
    values = row["pcm"]
    length = len(values)
    frequency_multiplier = math.pow(2, (row["target_note"] - row["root_note"]) / 12)
    result = []
    for frame in range(length):
        absolute = frame * frequency_multiplier
        whole = math.floor(absolute)
        frac = absolute - whole
        a, b = values[whole % length], values[(whole+1) % length]
        value = math.floor(a + (b-a)*frac + 0.5)
        result.append(min(32767, max(-32768, value)))
    if row["reverse"]:
        result = result[::-1]
    return {"schema": RESULT_SCHEMA, "pcm": result, "sample_rate": row["sample_rate"],
            "target_note": row["target_note"], "source_sha256": row["source_sha256"],
            "reverse": row["reverse"]}


def content_sha(pcm: list[int]) -> str:
    return sha256(struct.pack("<" + "h"*len(pcm), *pcm)).hexdigest()


def read_wav_request(filename: str | Path, *, root_note: int = 60,
                     target_note: int = 60, reverse: bool = False) -> dict:
    """Take only the first 8192 mono PCM16 frames; preserve full-file identity."""
    p = Path(filename)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > 20_000_000:
        raise ValueError("input must be ordinary WAV <=20MB")
    content = p.read_bytes()
    digest = sha256(content).hexdigest()
    try:
        with wave.open(str(p), "rb") as audio:
            if (audio.getnchannels() != 1 or audio.getsampwidth() != 2
                    or audio.getcomptype() != "NONE" or not 8000 <= audio.getframerate() <= 96000
                    or audio.getnframes() < 128):
                raise ValueError("only PCM16 mono WAV at 8–96kHz")
            rate = audio.getframerate()
            raw = audio.readframes(min(audio.getnframes(), 8192))
    except (wave.Error, EOFError) as exc:
        raise ValueError("invalid PCM WAV") from exc
    if len(raw) < 256 or len(raw) % 2:
        raise ValueError("truncated WAV")
    pcm = list(struct.unpack("<" + "h"*(len(raw)//2), raw))
    return validate_input({"schema": SCHEMA, "sample_rate": rate, "pcm": pcm,
                           "root_note": root_note, "target_note": target_note,
                           "source_sha256": digest, "reverse": reverse})


def write_verified_wav(path: str | Path, result: dict) -> dict:
    if result.get("schema") != RESULT_SCHEMA or type(result.get("pcm")) is not list:
        raise ValueError("not a native result")
    frames = result["pcm"]
    if not 128 <= len(frames) <= 8192 or any(type(x) is not int or not -32768 <= x <= 32767 for x in frames):
        raise ValueError("invalid PCM to export")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(result["sample_rate"])
        w.writeframes(struct.pack("<" + "h"*len(frames), *frames))
    return {"path": str(destination), "pcm_sha256": content_sha(frames),
            "frames": len(frames), "sample_rate": result["sample_rate"]}
