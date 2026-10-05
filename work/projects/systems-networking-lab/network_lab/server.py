from __future__ import annotations

import socket
import threading

from .protocol import recv_frame, send_frame


class EchoServer:
    def __init__(self, host: str = "127.0.0.1") -> None:
        self.host = host
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind((host, 0))
        self._listener.listen()
        self.port = self._listener.getsockname()[1]
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def close(self) -> None:
        self._stop.set()
        try:
            socket.create_connection((self.host, self.port), timeout=0.2).close()
        except OSError:
            pass
        self._thread.join(timeout=2)
        self._listener.close()

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                connection, _ = self._listener.accept()
            except OSError:
                break

            with connection:
                while not self._stop.is_set():
                    try:
                        payload = recv_frame(connection)
                    except (ConnectionError, OSError):
                        break
                    send_frame(connection, payload)


class SilentServer:
    def __init__(self, host: str = "127.0.0.1") -> None:
        self.host = host
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.bind((host, 0))
        self._listener.listen(1)
        self.port = self._listener.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._release = threading.Event()

    def start(self) -> None:
        self._thread.start()

    def close(self) -> None:
        self._release.set()
        self._thread.join(timeout=2)
        self._listener.close()

    def _serve(self) -> None:
        connection, _ = self._listener.accept()
        with connection:
            self._release.wait(timeout=2)
