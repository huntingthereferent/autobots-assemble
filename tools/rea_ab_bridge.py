"""Explicit local REA CLI -> preserved Evidence -> A/B reference handoff.

No REA code is vendored and no static source relationship is automatically
promoted to a mathematical A/B correspondence.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile

from tools.ab_math_workbench import inspect_rea_evidence

MAX_BYTES = 128 * 1024 * 1024


def scan_javascript_target(
    target: Path,
    evidence_output: Path,
    reference_output: Path,
    *,
    rea_executable: str = "rea",
    timeout: int = 600,
) -> dict:
    """Run the documented static REA workflow on a specifically chosen target."""
    target = target.resolve()
    evidence_output = evidence_output.resolve()
    reference_output = reference_output.resolve()
    if not (target.is_dir() or (target.is_file() and target.suffix.lower() == ".asar")):
        raise ValueError("REA JavaScript analysis requires an existing directory or .asar file")
    if evidence_output == reference_output or evidence_output.exists() or reference_output.exists():
        raise ValueError("evidence/reference destinations must be distinct and must not already exist")
    if not evidence_output.parent.is_dir() or not reference_output.parent.is_dir():
        raise ValueError("output parent directories must already exist")
    executable = shutil.which(rea_executable)
    if executable is None:
        raise ValueError("REA CLI not installed: see https://github.com/morluto/rea")
    if timeout < 1 or timeout > 3600:
        raise ValueError("timeout must be between 1 and 3600 seconds")
    temp_path = None
    try:
        with NamedTemporaryFile(mode="wb", dir=evidence_output.parent,
                                prefix=".rea-evidence-", suffix=".json", delete=False) as dest:
            temp_path = Path(dest.name)
            try:
                result = subprocess.run(
                    [executable, "analyze-javascript-application", str(target), "--json"],
                    stdout=dest,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise ValueError("REA analysis timed out without publishing partial Evidence") from exc
        if result.returncode != 0:
            reason = result.stderr[-800:].decode("utf-8", errors="replace")
            raise ValueError(f"REA analysis failed with exit {result.returncode}: {reason}")
        if temp_path.stat().st_size > MAX_BYTES:
            raise ValueError("REA Evidence exceeds 128 MiB bridge limit; use REA's own inspect-analysis-view")
        # Parse and validate before publishing the evidence or the smaller reference.
        reference = inspect_rea_evidence(temp_path)
        os.replace(temp_path, evidence_output)
        temp_path = None
        reference["evidence_path"] = str(evidence_output)
        reference["scan_target"] = str(target)
        reference["scan_command"] = "rea analyze-javascript-application TARGET --json"
        reference["mathematical_correspondence"] = None
        reference["status"] = "REA_EVIDENCE_SAVED_MATH_WITNESS_OPEN"
        reference_output.write_text(json.dumps(reference, indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8")
        return reference
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local REA static analysis; preserve original Evidence for later mathematical questions")
    parser.add_argument("target", type=Path)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--reference-output", type=Path, required=True)
    parser.add_argument("--rea", default="rea", help="REA CLI executable (installed separately)")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args(argv)
    try:
        response = scan_javascript_target(
            args.target, args.evidence_output, args.reference_output,
            rea_executable=args.rea, timeout=args.timeout,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"WALL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": response["status"],
        "evidence_id": response["evidence_id"],
        "sha256": response["sha256"],
        "evidence_path": response["evidence_path"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
