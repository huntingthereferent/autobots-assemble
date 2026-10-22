"""Offline control tests for one public OpenNeuro GraphQL snapshot."""
import json
import unittest
from pathlib import Path

from snapshot_metadata import DATASET, DOI, ENDPOINT, QUERY, SNAPSHOT, classify, probe


def payload(*, version=SNAPSHOT, doi=DOI, dataset=DATASET):
    return json.dumps({"data": {
        "dataset": {"id": dataset, "name": "Public named dataset"},
        "snapshot": {"id": dataset + ":" + version, "tag": version,
                     "description": {"Name": "Public named dataset", "DatasetDOI": doi}},
    }}).encode()


class FakeResponse:
    status = 200
    def __init__(self, raw):
        self.raw = raw
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return None
    def read(self, n):
        return self.raw[:n]


class FakeOpener:
    def __init__(self, raw):
        self.raw = raw
        self.calls = []
    def open(self, req, timeout):
        self.calls.append({"url": req.full_url, "method": req.get_method(),
                           "body": req.data, "accept": req.get_header("Accept"),
                           "timeout": timeout})
        return FakeResponse(self.raw)


class NeuroMetadataTests(unittest.TestCase):
    def test_exact_public_snapshot_identity(self):
        result = classify(payload())
        self.assertEqual(result["dataset_id"], "ds000224")
        self.assertEqual(result["snapshot_tag"], "1.0.1")
        self.assertEqual(result["doi"], DOI)
        self.assertFalse(result["source_data_admitted"])
        self.assertFalse(result["scientific_results_tested"])

    def test_one_frozen_read_only_graphql_query(self):
        fake = FakeOpener(payload())
        receipt = probe(opener=fake)
        self.assertEqual(receipt["state"], "PUBLIC_SNAPSHOT_METADATA_OBSERVED")
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(fake.calls[0]["url"], ENDPOINT)
        self.assertEqual(fake.calls[0]["method"], "POST")
        self.assertEqual(fake.calls[0]["accept"], "application/json")
        self.assertEqual(fake.calls[0]["timeout"], 15)
        body = json.loads(fake.calls[0]["body"])
        self.assertEqual(body, {"query": QUERY})
        self.assertNotIn("files", QUERY.lower())
        self.assertNotIn("subject", QUERY.lower())
        self.assertFalse(receipt["human_imaging_fetched"])
        self.assertFalse(receipt["source_data_archived"])
        self.assertEqual(receipt["scientific_status"], "NOT_TESTED")
        self.assertEqual(receipt["rights_review"], "REQUIRED_PER_RECORD")
        self.assertEqual(len(receipt["raw_response_sha256"]), 64)

    def test_snapshot_version_mismatch_is_wall(self):
        r = probe(opener=FakeOpener(payload(version="1.0.2")))
        self.assertEqual(r["state"], "SOURCE_WALL")
        self.assertEqual(r["error_class"], "ValueError")
        self.assertNotIn("raw_response_sha256", r)

    def test_dataset_id_mismatch_is_wall(self):
        with self.assertRaises(ValueError):
            classify(payload(dataset="ds000001"))

    def test_doi_mismatch_is_wall(self):
        with self.assertRaises(ValueError):
            classify(payload(doi="10.0000/bad"))

    def test_missing_snapshot_is_wall(self):
        raw = json.dumps({"data": {"dataset": {"id": DATASET, "name": "Dataset"},
                                  "snapshot": None}}).encode()
        self.assertEqual(probe(opener=FakeOpener(raw))["state"], "SOURCE_WALL")

    def test_graphql_errors_are_wall(self):
        raw = json.dumps({"errors": [{"message": "Denied"}]}).encode()
        self.assertEqual(probe(opener=FakeOpener(raw))["state"], "SOURCE_WALL")

    def test_html_is_not_metadata(self):
        r = probe(opener=FakeOpener(b"<html>OpenNeuro Playground</html>"))
        self.assertEqual(r["state"], "SOURCE_WALL")
        self.assertEqual(r["error_class"], "JSONDecodeError")

    def test_size_ceiling_retains_wall(self):
        r = probe(opener=FakeOpener(b"a" * 60001))
        self.assertEqual(r["state"], "SOURCE_WALL")
        self.assertEqual(r["error_class"], "ValueError")
        self.assertFalse(r["human_imaging_fetched"])

    def test_archived_public_receipt_never_promotes_science(self):
        path = Path(__file__).parent / "observations" / "2026-10-22-run-39782507005.json"
        evidence = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["run_id"], 39782507005)
        self.assertEqual(evidence["observation"]["state"], "PUBLIC_SNAPSHOT_METADATA_OBSERVED")
        self.assertEqual(evidence["observation"]["identity"]["snapshot_tag"], "1.0.1")
        self.assertEqual(evidence["observation"]["identity"]["doi"], DOI)
        self.assertEqual(evidence["observation"]["raw_response_sha256"],
                         "1cfc7ea2a470186ac613ebd8887ed6578bf0f1d83647a3979d3f500715f1f875")
        self.assertEqual(evidence["neuro_parent_lane_scientific_state"], "NOT_TESTED")
        self.assertEqual(evidence["neuro_parent_lane_dataset_admission"], "REQUIRED")
        self.assertFalse(evidence["observation"]["source_data_archived"])
        self.assertFalse(evidence["observation"]["human_imaging_fetched"])

    def test_no_user_supplied_ids_or_data_fetch(self):
        self.assertEqual(ENDPOINT, "https://openneuro.org/crn/graphql")
        self.assertEqual(DATASET, "ds000224")
        self.assertEqual(SNAPSHOT, "1.0.1")
        self.assertEqual(QUERY.count("snapshot("), 1)


if __name__ == "__main__":
    unittest.main()
