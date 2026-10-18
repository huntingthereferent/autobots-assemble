"""A/B release assembler: ship a source-verified A/B tool, NOT the source repo.

Provenance is independently grounded against original native command log bytes.
The original referent's files and its license stay in its separately pinned
upstream checkout. The resulting bundle is our A/B distribution and license.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import shutil
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile

from .ab_tool import PIN, STAGES, ABEvidenceError

VERSION = "0.1.0"
BUNDLE = f"ab-tool-{VERSION}-release.zip"
DIST_NAMES = (f"ab_tool-{VERSION}-py3-none-any.whl", f"ab_tool-{VERSION}.tar.gz")
RECEIPT = "source-absorption-receipt.json"
PROVENANCE = "source-provenance.json"
NATIVE_LOGS = ("native-rea-tests.log", "rea-typecheck.log", "source-diff-check.log")
DOC_FILES = ("README.md", "CHANGELOG.md", "LICENSE", "THIRD_PARTY_NOTICES.md")
GUIDES = ("quickstart.md", "swallow-repo-lane.md", "release.md", "swallow.md", "cli.md", "evidence.md", "visual.md")
SITE_FILE = "index.html"
PREVIEW = ("source-provenance.html", "graph.json", "ancestry.json")
COMPARISON = ("baseline.json", "original-vitest.json", "original-vitest.log",
              "regrounded-vitest.json", "regrounded-vitest.log", "comparison.json",
              "comparison.md")


def _safe_file(root: Path, name: str) -> Path:
    if not name or Path(name).name != name:
        raise ABEvidenceError("nonlocal release source path: " + str(name))
    p = root / name
    if not p.is_file() or p.is_symlink():
        raise ABEvidenceError("missing or symlinked release source: " + str(p))
    return p

def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _check_log(evidence: Path, row: dict, expected: str) -> None:
    if not isinstance(row, dict) or row.get("returncode") != 0 or row.get("timed_out") is not False:
        raise ABEvidenceError("source-native execution did not pass: " + expected)
    path = _safe_file(evidence, row.get("log"))
    if path.name != expected or _hash(path) != row.get("sha256"):
        raise ABEvidenceError("native source evidence hash mismatch: " + expected)

def validate_evidence(evidence: Path) -> dict:
    receipt = json.loads(_safe_file(evidence, RECEIPT).read_text(encoding="utf-8"))
    graph = json.loads(_safe_file(evidence, PROVENANCE).read_text(encoding="utf-8"))
    if (receipt.get("kind") != "ab-tool/real-rea-source-edition-v1" or
        receipt.get("upstream") != "morluto/rea" or
        receipt.get("upstream_commit") != PIN or receipt.get("result") != "PASS"):
        raise ABEvidenceError("a passing source-edition receipt at the pinned referent is required")
    stages = receipt.get("stages")
    if not isinstance(stages, list) or [s.get("name") for s in stages] != [x[0] for x in STAGES]:
        raise ABEvidenceError("missing original ordered source-correction stages")
    for stage in stages:
        label = stage["name"]
        for action in ("prepare", "apply"):
            _check_log(evidence, stage.get(action), f"{label}-{action}.log")
    final = stages[-1]
    if final.get("result") != "PASS":
        raise ABEvidenceError("the final source stage was never native-verified")
    _check_log(evidence, final.get("native"), NATIVE_LOGS[0])
    _check_log(evidence, final.get("typecheck"), NATIVE_LOGS[1])
    _check_log(evidence, final.get("source_diff_check"), NATIVE_LOGS[2])
    if (graph.get("schema_version") != 1 or
        [r.get("provenance_id") for r in graph.get("provenance_links", [])] !=
        [f"ab-source-{n}-{name}" for n, (name, _) in enumerate(STAGES, 1)]):
        raise ABEvidenceError("source ancestry not grounded in executed source editions")
    if graph.get("traces") != []:
        raise ABEvidenceError("unknown trace claims in source-level provenance")
    return receipt

def _archive_license(name: str, archive: Path, expected: str) -> None:
    """The A/B license must be physically present in each Python distribution."""
    try:
        if name.endswith(".whl"):
            with ZipFile(archive) as z:
                members = [m for m in z.namelist() if m.endswith("/LICENSE")]
                if len(members) != 1 or sha256(z.read(members[0])).hexdigest() != expected:
                    raise ABEvidenceError("wheel does not carry the original A/B product license")
        else:
            import tarfile
            with tarfile.open(archive, "r:gz") as tar:
                members = [m for m in tar.getmembers() if m.name.endswith("/LICENSE")]
                if len(members) != 1 or not members[0].isfile():
                    raise ABEvidenceError("source distribution must carry A/B license")
                extracted = tar.extractfile(members[0])
                if extracted is None or sha256(extracted.read()).hexdigest() != expected:
                    raise ABEvidenceError("source distribution license is not identical to A/B")
    except (BadZipFile, OSError, ValueError) as exc:
        raise ABEvidenceError("bad or unreadable distribution: " + name) from exc

def validate_reference_comparison(evidence: Path) -> dict:
    folder = evidence / "comparison"
    for name in COMPARISON:
        _safe_file(folder, name)
    frozen = json.loads((folder / "baseline.json").read_text(encoding="utf-8"))
    paired = json.loads((folder / "comparison.json").read_text(encoding="utf-8"))
    if (frozen.get("kind") != "ab/original-REA-before-correction-v1" or
        frozen.get("pin") != PIN or
        paired.get("kind") != "ab/paired-reference-verdict-v1" or
        paired.get("upstream_pin") != PIN or
        paired.get("verdict") != "PARTIAL_NATIVE_MATCH" or
        paired.get("full_REA_reconstructed") is not False or
        paired.get("baseline_sha256") != _hash(folder / "baseline.json") or
        paired.get("original_native_json_sha256") != _hash(folder / "original-vitest.json") or
        paired.get("regrounded_native_json_sha256") != _hash(folder / "regrounded-vitest.json") or
        frozen.get("native", {}).get("json_sha256") != _hash(folder / "original-vitest.json") or
        frozen.get("native", {}).get("log_sha256") != _hash(folder / "original-vitest.log") or
        not isinstance(frozen.get("original_test_cases"), list) or
        not len(frozen["original_test_cases"]) or
        paired.get("before_assertions") != len(frozen["original_test_cases"]) or
        paired.get("after_assertions") != len(frozen["original_test_cases"]) or
        paired.get("capability_coverage", {}).get("original_cli_mcp_binary_android_and_other_providers", {}).get("status") != "NOT_RECONSTRUCTED" or
        paired.get("capability_coverage", {}).get("license", {}).get("status") != "SEPARATE_RIGHTS"):
        raise ABEvidenceError("original-vs-A/B comparison missing, tampered or claiming full REA equivalence")
    return paired

def ship(*, repo: Path, evidence: Path, dist: Path, out: Path) -> dict:
    repo, evidence, dist, out = (p.resolve() for p in (repo, evidence, dist, out))
    tool = repo / "tools" / "ab-provenance"
    if out.exists():
        raise ABEvidenceError("never overwrite a previously shipped result")
    if out == repo or not (repo / "LICENSE").is_file():
        raise ABEvidenceError("original A/B product license is unavailable")
    if repo.joinpath("runtime", "data").resolve() not in out.parents:
        raise ABEvidenceError("shipped bundle must be placed in the private runtime data area")
    receipt = validate_evidence(evidence)
    comparison = validate_reference_comparison(evidence)
    ab_license = _safe_file(tool, "LICENSE")
    if _hash(ab_license) != _hash(repo / "LICENSE"):
        raise ABEvidenceError("A/B product license diverged from original repository")
    for name in (*DOC_FILES,):
        _safe_file(tool, name)
    for name in GUIDES:
        _safe_file(tool / "docs", name)
    _safe_file(tool / "site", SITE_FILE)
    for name in (*DIST_NAMES,):
        candidate = _safe_file(dist, name)
        _archive_license(name, candidate, _hash(ab_license))
    for name in (*PREVIEW, *NATIVE_LOGS, RECEIPT, PROVENANCE):
        _safe_file(evidence, name)
    out.mkdir(parents=True)
    files = {}
    def add(src: Path, arc: str):
        if src.is_symlink() or arc in files:
            raise ABEvidenceError("unsafe or duplicate distribution member")
        files[arc] = {"sha256": _hash(src), "bytes": src.stat().st_size}
        with ZipFile(out / BUNDLE, "a", compression=ZIP_DEFLATED, compresslevel=9) as z:
            z.write(src, arcname=arc)
    for name in DOC_FILES:
        add(tool / name, name)
    for name in GUIDES:
        add(tool / "docs" / name, "docs/" + name)
    add(tool / "site" / SITE_FILE, "docs-site/" + SITE_FILE)
    for name in DIST_NAMES:
        add(dist / name, "dist/" + name)
    for name in PREVIEW:
        add(evidence / name, "evidence/" + name)
    for name in (*NATIVE_LOGS, RECEIPT, PROVENANCE):
        add(evidence / name, "evidence/" + name)
    for name in COMPARISON:
        add(evidence / "comparison" / name, "comparison/" + name)
    manifest = {
        "schema_version": 1, "kind": "ab-tool/release-candidate-v1",
        "product": "A/B", "version": VERSION,
        "product_license": "A/B All Rights Reserved (included as LICENSE)",
        "source_referent": {"repository": "morluto/rea", "pin": PIN,
                            "included_in_ab_distribution": False,
                            "license_not_adopted_as_product_license": True},
        "verification": {"source_stage_count": len(STAGES),
                         "native_tests_and_typecheck": "source-verified PASS",
                         "source_receipt_sha256": _hash(evidence / RECEIPT)},
        "paired_reference_result": {
            "verdict": comparison["verdict"],
            "original_upstream_assertions": comparison["before_assertions"],
            "regrounded_assertions": comparison["after_assertions"],
            "full_original_REA_reconstructed": False
        },
        "scope": "A/B tool with first supported source-correction adapter for real REA JS investigations",
        "unclaimed": "complete REA providers, native hidden state, global equivalent behavior",
        "files": files,
    }
    blob = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with ZipFile(out / BUNDLE, "a", compression=ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("release-manifest.json", blob)
    (out / "release-manifest.json").write_bytes(blob)
    return {"status": "RELEASE_CANDIDATE_READY", "bundle": str(out / BUNDLE),
            "sha256": _hash(out / BUNDLE),
            "files": len(files), "license": "A/B All Rights Reserved",
            "source_referent_included": False}
