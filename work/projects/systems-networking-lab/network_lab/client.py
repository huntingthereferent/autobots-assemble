from __future__ import annotations

from dataclasses import asdict, dataclass
import socket
import time

from .protocol import recv_frame, send_frame


@dataclass(frozen=True)
class ProbeResult:
    status: str
    latency_ms: float | None = None
    bytes_round_trip: int = 0
    throughput_mib_s: float | None = None
    error_type: str | None = None


def echo_probe(
    host: str,
    port: int,
    payload: bytes,
    *,
    timeout: float = 1.0,
) -> ProbeResult:
    started = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            send_frame(sock, payload)
            echoed = recv_frame(sock)
    except ConnectionRefusedError as exc:
        return ProbeResult(status="refused", error_type=type(exc).__name__)
    except socket.timeout as exc:
        return ProbeResult(status="timeout", error_type=type(exc).__name__)

    elapsed = time.perf_counter() - started
    if echoed != payload:
        return ProbeResult(status="protocol_error", error_type="PayloadMismatch")

    total_bytes = len(payload) * 2
    throughput = (total_bytes / (1024 * 1024)) / elapsed if elapsed else None
    return ProbeResult(
        status="ok",
        latency_ms=elapsed * 1000,
        bytes_round_trip=total_bytes,
        throughput_mib_s=throughput,
    )


def to_dict(result: ProbeResult) -> dict:
    return asdict(result)
