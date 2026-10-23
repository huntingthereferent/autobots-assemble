"""BIO-SEQUENCE-TRANSFORM-INTEGRITY-001.

Fetches one pinned public reference sequence and checks deterministic,
reversible sequence transformations. This is an integrity experiment, not
a biological inference or a claim about function.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ACCESSION = "NC_012920.1"
ENDPOINT = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    f"?db=nuccore&id={ACCESSION}&rettype=fasta&retmode=text"
)
MAX_BYTES = 100_000
COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def parse_fasta(raw_text: str) -> tuple[str, str]:
    lines = raw_text.strip().splitlines()
    if len(lines) < 2 or not lines[0].startswith(">"):
        raise ValueError("expected one FASTA record with a header")
    if any(line.startswith(">") for line in lines[1:]):
        raise ValueError("multiple FASTA records are not accepted")
    header = lines[0][1:].strip()
    sequence = "".join(line.strip().upper() for line in lines[1:])
    if not sequence or re.fullmatch(r"[ACGTN]+", sequence) is None:
        raise ValueError("sequence contains unsupported or empty symbols")
    return header, sequence


def reverse_complement(sequence: str) -> str:
    if not sequence or re.fullmatch(r"[ACGTN]+", sequence) is None:
        raise ValueError("sequence must contain only A/C/G/T/N")
    return sequence.translate(COMPLEMENT)[::-1]


def measure(sequence: str) -> dict:
    return {
        "length": len(sequence),
        "A": sequence.count("A"),
        "C": sequence.count("C"),
        "G": sequence.count("G"),
        "T": sequence.count("T"),
        "N": sequence.count("N"),
        "gc_count": sequence.count("G") + sequence.count("C"),
    }


def build_receipt(raw: bytes) -> dict:
    header, sequence = parse_fasta(raw.decode("utf-8"))
    if ACCESSION not in header:
        raise ValueError("returned FASTA header does not match pinned accession")
    if not 10_000 <= len(sequence) <= 30_000:
        raise ValueError("sequence length outside configured mitochondrial-reference bounds")
    transformed = reverse_complement(sequence)
    restored = reverse_complement(transformed)
    original_metrics = measure(sequence)
    transformed_metrics = measure(transformed)
    if restored != sequence:
        raise AssertionError("reverse-complement involution failed")
    if len(transformed) != len(sequence):
        raise AssertionError("length invariant failed")
    if original_metrics["gc_count"] != transformed_metrics["gc_count"]:
        raise AssertionError("GC-count invariant failed")
    return {
        "schema_version": 1,
        "experiment_id": "BIO-SEQUENCE-TRANSFORM-INTEGRITY-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "INTEGRITY_CHECKS_PASSED",
        "source": {
            "provider": "NCBI Nucleotide E-utilities",
            "accession": ACCESSION,
            "endpoint": ENDPOINT,
            "raw_fasta_sha256": hashlib.sha256(raw).hexdigest(),
            "raw_bytes": len(raw),
            "header": header,
        },
        "measurements": {
            "original": original_metrics,
            "reverse_complement": transformed_metrics,
            "restored_sequence_sha256": hashlib.sha256(restored.encode("ascii")).hexdigest(),
            "original_sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
            "reverse_complement_is_involution": restored == sequence,
            "length_preserved": len(transformed) == len(sequence),
            "gc_count_preserved": original_metrics["gc_count"] == transformed_metrics["gc_count"],
        },
        "limits": [
            "One public reference record; no sample or population inference.",
            "Integrity checks do not establish gene function, clinical meaning, or biological mechanism.",
            "Reference records and annotations may be updated; receipt pins this retrieved byte snapshot.",
        ],
    }


def fetch_raw() -> bytes:
    request = Request(ENDPOINT, headers={"User-Agent": "bounded-research-witness/1.0 contact: research"})
    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"NCBI returned HTTP {response.status}")
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("FASTA response exceeded configured byte cap")
    return raw


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = build_receipt(fetch_raw())
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
