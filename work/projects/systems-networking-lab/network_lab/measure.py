from __future__ import annotations

import json
from pathlib import Path
import socket

from .client import echo_probe, to_dict
from .server import EchoServer, SilentServer


def reserve_closed_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def build_report() -> dict:
    echo = EchoServer()
    echo.start()
    try:
        small = echo_probe("127.0.0.1", echo.port, b"hello-network")
        large = echo_probe("127.0.0.1", echo.port, b"x" * (1024 * 1024))
    finally:
        echo.close()

    refused = echo_probe(
        "127.0.0.1",
        reserve_closed_port(),
        b"test",
        timeout=0.2,
    )

    silent = SilentServer()
    silent.start()
    try:
        timed_out = echo_probe(
            "127.0.0.1",
            silent.port,
            b"timeout",
            timeout=0.1,
        )
    finally:
        silent.close()

    return {
        "protocol": "TCP / 4-byte big-endian length-prefixed frames",
        "small_round_trip": to_dict(small),
        "one_mib_round_trip": to_dict(large),
        "refused_connection": to_dict(refused),
        "read_timeout": to_dict(timed_out),
    }


def write_report(path: str | Path) -> dict:
    report = build_report()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
