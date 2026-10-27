"""Source-bound validation for public Tracework original GitHub Actions artifacts.

This checks only original bytes and provenance. It does not run an experiment,
infer a success, or read private owner journals.
"""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

REPO = "huntingthereferent/autobots-assemble"
SCHEMA = "tracework-native-evidence-archive/v1"
MAX_ZIP = 12 * 1024 * 1024
MAX_EXPANDED = 64 * 1024 * 1024
SOURCES = {
 ".github/workflows/arc3-sp80-stage3-right-catcher-edge.yml":
   ("ARC3 original SP80 source right catcher edge contact",
    "original-sp80-stage3-right-catcher-edge",
    {"original-sp80-stage3-right-catcher-edge.json",
     "original-sp80-stage3-right-catcher-edge.npz"}),
 ".github/workflows/arc4-sp80-stage4-clean-lateral-top.yml":
   ("ARC4 original SP80 clean lateral plus top-left cup recovery",
    "original-sp80-stage4-clean-lateral-top",
    {"original-sp80-stage4-clean-lateral-top.json",
     "original-sp80-stage4-clean-lateral-top.npz"}),
 ".github/workflows/world-ab-first-envelope-limit.yml":
   ("WORLD 31 first conservative source envelope limit",
    "world31-original-first-envelope-limits",
    {"first_nominal_envelope_limits.json",
     "first_nominal_envelope_limits.sha256"}),
 ".github/workflows/workstation-w13-independent-witness.yml":
   ("workstation-w13-independent-witness",
    "w13-independent-witness-chromium-evidence", None),
}
BACKFILL = (39616395169, 39636174534, 39531157339, 39000587000)


def inspect_zip(data, expected):
    if not data or len(data) > MAX_ZIP:
        raise ValueError("missing or oversized original artifact")
    result = []
    with zipfile.ZipFile(BytesIO(data)) as z:
        info = z.infolist()
        names = [f.filename for f in info]
        if not 1 <= len(info) <= 128 or len(names) != len(set(names)):
            raise ValueError("invalid or duplicate archive entries")
        if expected is not None and set(names) != expected:
            raise ValueError("native artifact member contract changed")
        if expected is None and not (
            2 <= len(names) <= 32 and
            "witness_real_chromium_complete.png" in names and
            all(n.startswith("witness_") and n.endswith((".json", ".png"))
                for n in names)
        ):
            raise ValueError("unexpected W13 witness membership")
        expanded = 0
        for f in info:
            p = PurePosixPath(f.filename)
            if (p.is_absolute() or len(p.parts) != 1 or ".." in p.parts or
                "\\" in f.filename or f.is_dir() or
                (f.external_attr >> 16) & 0o170000 == 0o120000 or
                f.flag_bits & 1):
                raise ValueError("unsafe original archive member")
            expanded += f.file_size
            if expanded > MAX_EXPANDED:
                raise ValueError("unbounded extracted size")
            with z.open(f) as reader:
                digest = sha256(reader.read()).hexdigest()
            result.append({"path": f.filename, "bytes": f.file_size,
                           "sha256": digest})
    return sorted(result, key=lambda row: row["path"])


def prepare(run, listing, source_zip):
    """Require one owner-run, same-repository, named original witness."""
    if not isinstance(run, dict) or not isinstance(listing, dict):
        raise ValueError("original Actions API responses required")
    spec = SOURCES.get(run.get("path"))
    if not spec or run.get("name") != spec[0]:
        raise ValueError("unapproved workflow")
    if (run.get("repository", {}).get("full_name") != REPO or
        run.get("head_repository", {}).get("full_name") != REPO or
        run.get("actor", {}).get("login") != "huntingthereferent"):
        raise ValueError("untrusted execution source")
    if (run.get("status") != "completed" or
        run.get("event") not in {"pull_request", "push", "workflow_dispatch"} or
        run.get("conclusion") not in
          {"success", "failure", "cancelled", "timed_out"}):
        raise ValueError("no attributable terminal native run")
    commit = run.get("head_sha")
    if not isinstance(commit, str) or not re.fullmatch("[0-9a-f]{40}", commit):
        raise ValueError("native source commit missing")
    run_id, attempt = run.get("id"), run.get("run_attempt")
    if type(run_id) is not int or run_id <= 0 or type(attempt) is not int or attempt < 1:
        raise ValueError("invalid original run identity")
    arts = listing.get("artifacts")
    if (type(listing.get("total_count")) is not int or
        listing["total_count"] > 100 or not isinstance(arts, list)):
        raise ValueError("incomplete original artifact list")
    matches = [a for a in arts if a.get("name") == spec[1]]
    if len(matches) != 1 or matches[0].get("expired") is not False:
        raise ValueError("native artifact not uniquely recoverable")
    a = matches[0]
    if type(a.get("id")) is not int or a["id"] <= 0:
        raise ValueError("original artifact ID missing")
    members = inspect_zip(source_zip, spec[2])
    tag = f"tracework-native-run-{run_id}-attempt-{attempt}"
    manifest = {
        "schema": SCHEMA, "repository": REPO, "run_id": run_id,
        "run_attempt": attempt, "workflow_path": run["path"],
        "workflow_name": spec[0], "event": run["event"],
        "source_commit": commit, "original_conclusion": run["conclusion"],
        "run_url": run["html_url"], "artifact_id": a["id"],
        "artifact_name": a["name"], "artifact_expires_at": a.get("expires_at"),
        "archive_file": tag + ".zip", "archive_sha256": sha256(source_zip).hexdigest(),
        "archive_bytes": len(source_zip), "members": members,
        "claim": "copied original artifact; no new native execution or verification"
    }
    return tag, manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--artifacts", type=Path, required=True)
    p.add_argument("--zip", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    tag, manifest = prepare(
        json.loads(args.run.read_text()),
        json.loads(args.artifacts.read_text()),
        args.zip.read_bytes()
    )
    args.output.mkdir(parents=True, exist_ok=True)
    src = args.output / (tag + ".zip")
    dest = args.output / (tag + ".manifest.json")
    if src.exists() or dest.exists():
        raise ValueError("immutable evidence output must not be overwritten")
    src.write_bytes(args.zip.read_bytes())
    dest.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"tag": tag, "zip": str(src), "manifest": str(dest)}))


if __name__ == "__main__":
    main()
