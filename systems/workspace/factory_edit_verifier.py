"""Independent native behavioral verifier for edited factory worker edition.

An edited worker is executed only under an explicit trusted local invocation.
This runs actual code from the selected edition; Python -I is not an OS sandbox.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("expected exact worker source file path")
    source = Path(sys.argv[1])
    if source.name != "factory_machine_worker.py" or source.is_symlink() or not source.is_file():
        raise SystemExit("unsupported candidate source")
    spec = importlib.util.spec_from_file_location("candidate_factory_machine", source)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load candidate worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    good = {"product": "bolt", "quantity": 2, "material_state": "received"}
    expected = {"part": "bolt-part", "quantity": 2, "part_state": "machined"}
    if module.simulate(good) != expected:
        raise SystemExit("VALID_PRODUCT_REGRESSION")
    invalid = [
        {"product": "bolt", "quantity": True, "material_state": "received"},
        {"product": "bolt", "quantity": -1, "material_state": "received"},
        {"product": "bolt", "quantity": 1, "material_state": "missing"},
        {"product": "", "quantity": 1, "material_state": "received"},
    ]
    for case in invalid:
        try:
            module.simulate(case)
        except ValueError:
            pass
        else:
            raise SystemExit("NATIVE_INVALID_INPUT_ACCEPTED")
    try:
        module.simulate({"product": "   ", "quantity": 1, "material_state": "received"})
    except ValueError:
        pass
    else:
        print("BLANK_PRODUCT_ACCEPTED", file=sys.stderr)
        return 4
    print("FACTORY_NATIVE_BEHAVIOR_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
