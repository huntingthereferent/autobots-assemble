"""Bounded audio-movement worker source, copied into a private workstation edition.

This executable is isolated from the verifier source. No calls to Suno or the
network. Reads one JSON request on stdin, returns one JSON observation on stdout.
"""
import json
import math
import os
import sys


def move(request):
    expected = {"schema", "sample_rate", "pcm", "root_note", "target_note", "source_sha256", "reverse"}
    if type(request) is not dict or set(request) != expected:
        raise ValueError("unexpected audio request")
    if request["schema"] != "ab-audio-motion/v1":
        raise ValueError("schema")
    src = request["pcm"]
    if (type(src) is not list or not 128 <= len(src) <= 8192
            or any(type(v) is not int or v < -32768 or v > 32767 for v in src)):
        raise ValueError("bounded PCM16 required")
    if (type(request["sample_rate"]) is not int or not 8000 <= request["sample_rate"] <= 96000
            or type(request["root_note"]) is not int or not 0 <= request["root_note"] <= 127
            or type(request["target_note"]) is not int or not 0 <= request["target_note"] <= 127
            or abs(request["target_note"]-request["root_note"]) > 12
            or type(request["reverse"]) is not bool):
        raise ValueError("invalid movement")
    n = len(src)
    ratio = 2.0 ** ((request["target_note"] - request["root_note"]) / 12.0)
    out = []
    for j in range(n):
        position = (j * ratio) % n
        lo = int(position)
        hi = (lo + 1) % n
        mix = position - lo
        value = math.floor(src[lo] * (1.0-mix) + src[hi] * mix + 0.5)
        out.append(max(-32768, min(32767, value)))
    if request["reverse"]:
        out.reverse()
    return {"schema": "ab-audio-motion-result/v1", "pcm": out,
            "sample_rate": request["sample_rate"], "target_note": request["target_note"],
            "source_sha256": request["source_sha256"], "reverse": request["reverse"]}


if __name__ == "__main__":
    request = json.load(sys.stdin)
    print(json.dumps({"result": move(request), "pid": os.getpid()}, separators=(",", ":")))
