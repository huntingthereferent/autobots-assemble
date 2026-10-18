"""Freshly inspect the ORIGINAL W13 evidence: pinned Git source -> native RESULT.

A caller supplies the original owner-authenticated GitHub artifact directory
and authenticated source-run metadata. The existing native verifier runs only
in a temporary restored runtime. No jobs are admitted/executed and no private
journal is published, uploaded or copied into the repository.
"""
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
from .github_w13_continuation import (
    ARTIFACT_ID, ORIGINAL_DIGEST, ORIGINAL_HEAD, RUN_ID, JOB_ID,
    _object, validate_archive_metadata, unpack_native_runtime)
from .native_research_join import verify_local_relation

RESEARCH_PATH = "research/dives/W13-NATIVE-RECEIPT-001/dive.json"


def verify_original(*, artifact_dir: Path, source_binding: Path,
                    repo_root: Path, research_commit: str) -> dict:
    if not isinstance(research_commit, str) or re.fullmatch("[0-9a-f]{40}",research_commit) is None:
        raise ValueError("exact committed research SHA required")
    root=Path(repo_root).resolve()
    origin=_object(Path(source_binding))
    if (origin.get("repository")!="huntingthereferent/autobots-assemble"
            or origin.get("run_id")!=RUN_ID or origin.get("artifact_id")!=ARTIFACT_ID
            or origin.get("attempt")!=1 or origin.get("head_sha")!=ORIGINAL_HEAD
            or origin.get("digest")!=ORIGINAL_DIGEST):
        raise ValueError("not the original owner-authorized W13 source")
    validate_archive_metadata(Path(artifact_dir),origin,repo_root=root)
    with TemporaryDirectory(prefix="original-w13-source-") as tmp:
        archive_hash=unpack_native_runtime(Path(artifact_dir),Path(tmp)/"runtime")
        original=json.loads((root/RESEARCH_PATH).read_text(encoding="utf8")).get("original_source")
        if (type(original) is not dict
                or (original.get("run_id"),original.get("artifact_id"),
                    original.get("artifact_digest"),original.get("head_sha"),
                    original.get("archive_sha256")) !=
                    (RUN_ID,ARTIFACT_ID,ORIGINAL_DIGEST,ORIGINAL_HEAD,archive_hash)):
            raise ValueError("research source and original native archive disagree")
        receipt=verify_local_relation(
            data_dir=Path(tmp)/"runtime",job_id=JOB_ID,repo_root=root,
            research_commit=research_commit,research_path=RESEARCH_PATH)
        if (receipt["relation"]!="EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH"
                or receipt["native_verified"] is not True
                or receipt["research_causality"]!="NOT_ESTABLISHED"):
            raise ValueError("original native result/source witness failed")
        return {
            "schema":"w13-original-research-source-witness/v1",
            "source_run_id":RUN_ID,"artifact_id":ARTIFACT_ID,
            "source_archive_digest":ORIGINAL_DIGEST,
            "research_commit":research_commit,
            "native_job_id":JOB_ID,
            "result_event_id":receipt["result_event_id"],
            "source_fingerprint":receipt["native_source_fingerprint"],
            "exact_native_result_reverified":True,
            "scientific_causality_proven":False,
            "private_journal_published":False,
            "new_native_job_executed":False
        }


def main(argv=None):
    p=ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir",type=Path,required=True)
    p.add_argument("--source-binding",type=Path,required=True)
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--research-commit",required=True)
    args=p.parse_args(argv)
    print(json.dumps(verify_original(
        artifact_dir=args.artifact_dir,source_binding=args.source_binding,
        repo_root=args.repo_root,research_commit=args.research_commit),
        sort_keys=True,indent=2))


if __name__=="__main__":
    main()
