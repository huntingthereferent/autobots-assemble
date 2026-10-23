"""Scripted finite-world arena demonstration; no live AI agents."""
import json
from dataclasses import asdict
from interfaces.math.constructive_harness import demonstration

if __name__ == "__main__":
    print(json.dumps(asdict(demonstration()), indent=2))
