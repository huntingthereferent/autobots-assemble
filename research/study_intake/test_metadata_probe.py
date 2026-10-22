"""Offline/source-isolated regression tests. No network access."""
import copy
import json
import unittest
from urllib.error import URLError

from metadata_probe import (
    MAX_RESPONSE_BYTES,
    canonical_doi,
    fetch_one,
    normalized_title,
    parse_metadata,
    probe,
    read_study,
    reconcile,
    source_url,
)

STUDY = read_study()


def crossref_payload(doi=STUDY["doi"], title=STUDY["title"], year=2015):
    return {"message": {"DOI": doi, "title": [title],
            "published": {"date-parts": [[year, 8, 28]]},
            "deposited": {"date-time": "2026-10-01T00:00:00Z"},
            "abstract": "A deliberately excluded abstract"}}


def openalex_payload(doi=STUDY["doi"], title=STUDY["title"], year=2015):
    return {"doi": "https://doi.org/" + doi, "title": title, "publication_year": year,
            "updated_date": "2026-10-01T00:00:00Z", "abstract_inverted_index": {"excluded": [1]}}


class FakeResponse:
    status = 200

    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, maximum):
        return self.data[:maximum]


class FakeOpener:
    def __init__(self, replies):
        self.replies = list(replies)
        self.requested = []

    def open(self, request, timeout=None):
        self.requested.append((request.full_url, timeout))
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return FakeResponse(item)


class MetadataProbeTests(unittest.TestCase):
    def test_frozen_study_identity(self):
        self.assertEqual(STUDY["doi"], "10.1126/science.aac4716")
        self.assertEqual(STUDY["scientific_evidence_status"], "NOT_REPRODUCED")
        self.assertFalse(STUDY["study_data_ingested"])

    def test_offline_is_default(self):
        receipt = probe(STUDY)
        self.assertEqual(receipt["identity_comparison"]["state"], "UNOBSERVED")
        self.assertEqual(receipt["source_receipts"], [])

    def test_known_doi_has_only_fixed_hosts(self):
        self.assertEqual(
            source_url("crossref", STUDY["doi"]),
            "https://api.crossref.org/works/10.1126/science.aac4716")
        self.assertEqual(
            source_url("openalex", STUDY["doi"]),
            "https://api.openalex.org/works/https://doi.org/10.1126/science.aac4716")
        with self.assertRaises(ValueError):
            source_url("external", STUDY["doi"])
        with self.assertRaises(ValueError):
            source_url("crossref", "../example?evil=true")

    def test_normalization_is_limited_to_identity(self):
        self.assertEqual(canonical_doi("https://doi.org/10.1126/SCIENCE.aac4716"),
                         STUDY["doi"])
        self.assertEqual(normalized_title("A: B!"), "a b")
        self.assertIsNone(canonical_doi("https://example.org/fake"))

    def test_crossref_whitelisted_fields(self):
        record = parse_metadata("crossref", crossref_payload())
        self.assertEqual(record["year"], 2015)
        self.assertEqual(record["doi"], STUDY["doi"])
        self.assertNotIn("abstract", record)

    def test_openalex_whitelisted_fields(self):
        record = parse_metadata("openalex", openalex_payload())
        self.assertEqual(record["year"], 2015)
        self.assertEqual(record["doi"], STUDY["doi"])
        self.assertNotIn("abstract_inverted_index", record)

    def test_two_sources_match_is_only_metadata_match(self):
        client = FakeOpener([crossref_payload(), openalex_payload()])
        receipt = probe(STUDY, live=True, opener=client)
        self.assertEqual(len(client.requested), 2)
        self.assertTrue(all(t == 15 for u, t in client.requested))
        self.assertEqual(receipt["identity_comparison"]["state"], "MATCH")
        self.assertEqual(receipt["scientific_evidence_status"], "NOT_REPRODUCED")
        self.assertTrue(all(len(x["response_sha256"]) == 64 for x in receipt["source_receipts"]))
        self.assertTrue(all(x["raw_body_archived"] is False for x in receipt["source_receipts"]))

    def test_mismatch_is_not_promoted_to_match(self):
        client = FakeOpener([crossref_payload(), openalex_payload(year=2016)])
        receipt = probe(STUDY, live=True, opener=client)
        self.assertEqual(receipt["identity_comparison"]["state"], "MISMATCH")

    def test_missing_source_yields_unknown(self):
        client = FakeOpener([crossref_payload(), URLError("blocked")])
        receipt = probe(STUDY, live=True, opener=client)
        self.assertEqual(receipt["identity_comparison"]["state"], "UNKNOWN")
        self.assertEqual(len(receipt["errors"]), 1)
        self.assertEqual(receipt["errors"][0]["error_type"], "URLError")

    def test_duplicate_source_yields_unknown(self):
        record = {"source": "crossref", "metadata": parse_metadata("crossref", crossref_payload())}
        self.assertEqual(reconcile(STUDY, [record, record])["state"], "UNKNOWN")

    def test_empty_source_payload_fails(self):
        with self.assertRaises(ValueError):
            parse_metadata("crossref", {})

    def test_response_bound_is_fixed(self):
        self.assertLessEqual(MAX_RESPONSE_BYTES, 2_000_000)


if __name__ == "__main__":
    unittest.main()
