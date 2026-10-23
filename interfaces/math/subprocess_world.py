"""Subprocess observation adapter for Unstupid.

Protocol: invoke an external program once per probe, send one JSON request on
stdin, parse one JSON response from stdout. A fresh process per probe provides
an explicit reset boundary. This adapter does not trust the program's claims.
"""
import json
import subprocess
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SubprocessWorld:
    command: tuple[str, ...]
    depth: int
    timeout_seconds: float = 10.0

    def __post_init__(self):
        if not self.command:
            raise ValueError("command is required")
        if self.depth < 2:
            raise ValueError("depth must be at least two")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout must be positive")

    def __call__(self, actions: str) -> tuple[int, ...]:
        if any(a not in "AB" for a in actions):
            raise ValueError("only A and B actions are admitted")
        request = {"protocol": "unstupid-world-v1", "reset": True, "actions": actions}
        result = subprocess.run(
            self.command, input=json.dumps(request) + "\n", text=True,
            capture_output=True, timeout=self.timeout_seconds, check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"world process failed with code {result.returncode}")
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("world returned invalid JSON") from exc
        if not isinstance(response, dict) or response.get("protocol") != "unstupid-world-v1":
            raise ValueError("world protocol mismatch")
        if response.get("reset_confirmed") is not True:
            raise ValueError("world did not confirm reset")
        state = response.get("state")
        if not isinstance(state, list) or len(state) != self.depth:
            raise ValueError("world returned invalid state dimension")
        if any(type(value) is not int or value not in range(3) for value in state):
            raise ValueError("world returned non-F3 state")
        return tuple(state)
