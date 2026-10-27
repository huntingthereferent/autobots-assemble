#!/usr/bin/env bash
# Trusted default-branch runner only. Never execute or extract original artifacts.
set -euo pipefail
[[ "${GH_REPO:-}" == "huntingthereferent/autobots-assemble" ]] || {
  echo "Unexpected evidence repository" >&2
  exit 1
}
archive_one() {
  local run_id="$1"
  [[ "$run_id" =~ ^[1-9][0-9]*$ ]] || { echo "Invalid run ID" >&2; return 1; }
  local root="$RUNNER_TEMP/tracework-native/$run_id"
  mkdir -p "$root"
  gh api "repos/$GH_REPO/actions/runs/$run_id" > "$root/run.json"
  local attempt tag
  attempt="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["run_attempt"])' "$root/run.json")"
  [[ "$attempt" =~ ^[1-9][0-9]*$ ]] || return 1
  tag="tracework-native-run-$run_id-attempt-$attempt"
  if ! gh release view "$tag" --repo "$GH_REPO" >/dev/null 2>&1; then
    gh api "repos/$GH_REPO/actions/runs/$run_id/artifacts?per_page=100" > "$root/artifacts.json"
    local artifact_id
    artifact_id="$(python - "$root/run.json" "$root/artifacts.json" <<'PY'
import json,sys
from systems.workspace.github_native_evidence_archive import SOURCES
run=json.load(open(sys.argv[1]))
listing=json.load(open(sys.argv[2]))
spec=SOURCES.get(run.get("path"))
if spec is None: raise SystemExit("unapproved native workflow")
matches=[a for a in listing["artifacts"] if a.get("name")==spec[1]]
if len(matches)!=1: raise SystemExit("missing or ambiguous native artifact")
print(matches[0]["id"])
PY
)"
    [[ "$artifact_id" =~ ^[1-9][0-9]*$ ]] || return 1
    # GitHub API redirects to short-lived ZIP storage; curl saves exact bytes.
    # Authorization is not forwarded to a different redirect host.
    curl --fail --silent --show-error --location --retry 3 \
      --proto '=https' --proto-redir '=https' \
      --header "Accept: application/vnd.github+json" \
      --header "Authorization: Bearer $GH_TOKEN" \
      --output "$root/original.zip" \
      "https://api.github.com/repos/$GH_REPO/actions/artifacts/$artifact_id/zip"
    python -m systems.workspace.github_native_evidence_archive \
      --run "$root/run.json" --artifacts "$root/artifacts.json" \
      --zip "$root/original.zip" --output "$root/staged"
    gh release create "$tag" \
      "$root/staged/$tag.zip" "$root/staged/$tag.manifest.json" \
      --repo "$GH_REPO" --latest=false \
      --title "Tracework original native witness $run_id, attempt $attempt" \
      --notes "Original Actions artifact preserved with run, source revision, conclusion, and exact ZIP SHA-256. This archive is not a new native execution."
  fi
  mkdir -p "$root/verify"
  gh release download "$tag" --repo "$GH_REPO" --pattern "$tag*" --dir "$root/verify"
  python - "$root/verify" "$root/run.json" "$tag" <<'PY'
import json,sys
from hashlib import sha256
from pathlib import Path
from systems.workspace.github_native_evidence_archive import inspect_zip,SOURCES,SCHEMA
root=Path(sys.argv[1])
run=json.load(open(sys.argv[2]))
tag=sys.argv[3]
file=root/(tag+".zip")
receipt=root/(tag+".manifest.json")
if not file.is_file() or not receipt.is_file():
    raise SystemExit("release archive or manifest missing")
m=json.loads(receipt.read_text())
spec=SOURCES.get(run.get("path"))
raw=file.read_bytes()
if (not spec or m.get("schema")!=SCHEMA
    or m.get("run_id")!=run["id"]
    or m.get("run_attempt")!=run["run_attempt"]
    or m.get("source_commit")!=run["head_sha"]
    or m.get("original_conclusion")!=run["conclusion"]
    or m.get("workflow_name")!=run["name"]
    or m.get("artifact_name")!=spec[1]
    or m.get("archive_sha256")!=sha256(raw).hexdigest()
    or m.get("members")!=inspect_zip(raw,spec[2])):
    raise SystemExit("published evidence failed source/hash verification")
print("PRESERVED",tag,m["archive_sha256"])
PY
  echo "- Verified [original evidence $run_id](https://github.com/$GH_REPO/releases/tag/$tag)" >> "$GITHUB_STEP_SUMMARY"
}
if [[ "${1:-}" == "one" ]]; then
  archive_one "${2:-}"
  exit
fi
declare -a ids=()
if [[ "${EVENT_KIND:-}" == "workflow_run" ]]; then
  ids=("${COMPLETED_RUN_ID:-}")
elif [[ -n "${MANUAL_RUN_ID:-}" ]]; then
  ids=("$MANUAL_RUN_ID")
else
  ids=(39616395169 39636174534 39531157339 39000587000)
  for workflow in \
      arc3-sp80-stage3-right-catcher-edge.yml \
      arc4-sp80-stage4-clean-lateral-top.yml \
      world-ab-first-envelope-limit.yml \
      workstation-w13-independent-witness.yml; do
    mapfile -t recent < <(gh api "repos/$GH_REPO/actions/workflows/$workflow/runs?per_page=20" \
      --jq '.workflow_runs[].id')
    ids+=("${recent[@]}")
  done
fi
mkdir -p "$RUNNER_TEMP/tracework-native"
printf '%s\n' "${ids[@]}" | grep -E '^[1-9][0-9]*$' | sort -un \
  > "$RUNNER_TEMP/tracework-native/ids.txt"
failed=0
while IFS= read -r run_id; do
  if bash "$0" one "$run_id"; then
    :
  else
    echo "::error::Tracework failed to preserve original native run $run_id"
    failed=1
  fi
done < "$RUNNER_TEMP/tracework-native/ids.txt"
exit "$failed"
