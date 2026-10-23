"""Standalone three-coordinate finite-world protocol fixture.

This implementation does not import the project's World class.
"""
import argparse
import json
import sys


def transition(actions, phi, altered=False):
    x, y, z = 0, 0, 0
    for action in actions:
        if action == "A":
            x = (x + 1) % 3
        elif action == "B":
            old_y = y
            y = (y + x + (2 if altered else 1)) % 3
            z = (z + phi[old_y]) % 3
        else:
            raise ValueError("unsupported action")
    return [x, y, z]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phi", default="0,1,2")
    parser.add_argument("--mutant", action="store_true")
    args = parser.parse_args()
    phi = tuple(map(int, args.phi.split(",")))
    if len(phi) != 3 or any(v not in range(3) for v in phi):
        raise ValueError("invalid phi")
    request = json.loads(sys.stdin.readline())
    if request.get("protocol") != "unstupid-world-v1" or request.get("reset") is not True:
        raise ValueError("invalid request")
    actions = request.get("actions")
    if not isinstance(actions, str):
        raise ValueError("invalid actions")
    print(json.dumps({
        "protocol": "unstupid-world-v1",
        "reset_confirmed": True,
        "state": transition(actions, phi, args.mutant),
    }))


if __name__ == "__main__":
    main()
