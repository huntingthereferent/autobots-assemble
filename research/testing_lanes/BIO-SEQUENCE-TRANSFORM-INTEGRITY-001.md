# BIO-SEQUENCE-TRANSFORM-INTEGRITY-001 — reference sequence transformation integrity

**Question:** For one pinned public nucleotide reference, do deterministic reverse-complement transformations preserve the declared sequence invariants and restore the exact original sequence after two applications?

- Reference: NCBI Nucleotide accession `NC_012920.1` (human mitochondrial reference sequence)
- Retrieval: one bounded FASTA record from NCBI E-utilities; 100 KB response cap
- Transform: reverse complement over A/C/G/T/N
- Predeclared checks: accession identity, alphabet, bounded length, reverse-complement involution, length preservation and GC-count preservation
- Receipt: retrieval time, source-byte SHA-256, sequence hashes, counts and check outcomes
- Negative controls: unsupported symbols, multiple FASTA records and wrong accession

## Evidence boundary

This is a sequence-processing integrity check, not a biological discovery. It does not test gene function, pathogenicity, evolutionary claims, expression, clinical relevance or a universal mechanism. The test suite uses synthetic offline fixtures; the live workflow separately fetches the pinned reference record and emits a receipt for that snapshot. Reference content and annotations may change, so the receipt hash identifies the retrieved bytes.

## Reproduction

```sh
python -m unittest discover -s research/testing_lanes -p 'test_bio_sequence_transform_integrity.py' -v
python research/testing_lanes/bio_sequence_transform_integrity.py --output BIO-SEQUENCE-TRANSFORM-INTEGRITY-001.json
```
