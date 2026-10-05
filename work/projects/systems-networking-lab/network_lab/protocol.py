from __future__ import annotations

import socket
import struct


HEADER = struct.Struct("!I")
MAX_FRAME = 8 * 1024 * 1024


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size

    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("peer closed before frame completed")
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def send_frame(sock: socket.socket, payload: bytes) -> None:
    if len(payload) > MAX_FRAME:
        raise ValueError("payload exceeds maximum frame size")
    sock.sendall(HEADER.pack(len(payload)) + payload)


def recv_frame(sock: socket.socket) -> bytes:
    header = recv_exact(sock, HEADER.size)
    (length,) = HEADER.unpack(header)
    if length > MAX_FRAME:
        raise ValueError("declared frame exceeds maximum frame size")
    return recv_exact(sock, length)
