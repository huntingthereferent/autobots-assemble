import socket

from network_lab.client import echo_probe
from network_lab.measure import build_report, reserve_closed_port
from network_lab.protocol import recv_frame, send_frame
from network_lab.server import EchoServer


def test_frame_round_trip_over_socketpair():
    left, right = socket.socketpair()
    try:
        send_frame(left, b"abc" * 1000)
        assert recv_frame(right) == b"abc" * 1000
    finally:
        left.close()
        right.close()


def test_multiple_requests_share_one_tcp_connection():
    server = EchoServer()
    server.start()
    try:
        with socket.create_connection(("127.0.0.1", server.port), timeout=1) as sock:
            sock.settimeout(1)
            for payload in (b"one", b"two", b"three"):
                send_frame(sock, payload)
                assert recv_frame(sock) == payload
    finally:
        server.close()


def test_probe_records_latency_and_throughput():
    server = EchoServer()
    server.start()
    try:
        result = echo_probe("127.0.0.1", server.port, b"x" * (256 * 1024))
    finally:
        server.close()

    assert result.status == "ok"
    assert result.latency_ms is not None
    assert result.latency_ms > 0
    assert result.bytes_round_trip == 512 * 1024
    assert result.throughput_mib_s is not None
    assert result.throughput_mib_s > 0


def test_refused_connection_is_classified():
    result = echo_probe("127.0.0.1", reserve_closed_port(), b"x", timeout=0.2)

    assert result.status == "refused"
    assert result.error_type == "ConnectionRefusedError"


def test_report_contains_success_and_failure_witnesses():
    report = build_report()

    assert report["small_round_trip"]["status"] == "ok"
    assert report["one_mib_round_trip"]["status"] == "ok"
    assert report["one_mib_round_trip"]["bytes_round_trip"] == 2 * 1024 * 1024
    assert report["refused_connection"]["status"] == "refused"
    assert report["read_timeout"]["status"] == "timeout"
