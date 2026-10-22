"""Metadata-only OpenNeuro source boundary and negative controls; no network."""
import json
import unittest

from snapshot_metadata import ENDPOINT, QUERY, parse_metadata, request_metadata


def source(**changes):
    row = {
        "id": "ds000224:1.0.1", "tag": "1.0.1",
        "description": {
            "Name": "The Midnight Scan Club (MSC) dataset",
            "DatasetDOI": "10.18112/openneuro.ds000224.v1.0.1",
        },
    }
    row.update(changes)
    return json.dumps({"data": {"snapshot": row}}).encode()


class FakeResponse:
    status = 200
    def __init__(self, body, url=ENDPOINT):
        self.body, self.url = body, url
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return None
    def geturl(self):
        return self.url
    def read(self, limit):
        return self.body[:limit]


class FakeOpener:
    def __init__(self, body, url=ENDPOINT):
        self.body, self.url = body, url
    def open(self, request, timeout=20):
        assert request.full_url == ENDPOINT
        assert request.method == "POST"
        data = json.loads(request.data)
        assert "query" in data
        assert "mutation" not in data["query"].lower()
        assert "snapshot(" in data["query"]
        return FakeResponse(self.body, self.url)


class MetadataTests(unittest.TestCase):
    def test_frozen_identity(self):
        r = parse_metadata(source())
        self.assertEqual((r["dataset_id"], r["snapshot"]), ("ds000224", "1.0.1"))
        self.assertEqual(r["doi"], "10.18112/openneuro.ds000224.v1.0.1")

    def test_no_participant_data_or_file_fields_requested(self):
        for term in ["files", "subjects", "mutation", "download", "participants", "volumes"]:
            self.assertNotIn(term, QUERY.lower())

    def test_successful_single_metadata_request(self):
        self.assertEqual(parse_metadata(request_metadata(FakeOpener(source())))["snapshot"], "1.0.1")

    def test_exact_https_response_required(self):
        with self.assertRaisesRegex(ValueError, "exact HTTPS"):
            request_metadata(FakeOpener(source(), "https://other.example/graphql"))

    def test_strict_response_limit(self):
        with self.assertRaisesRegex(ValueError, "bounded limit"):
            request_metadata(FakeOpener(b"x" * 16001))

    def test_missing_dataset_is_source_wall(self):
        with self.assertRaisesRegex(ValueError, "snapshot not found"):
            parse_metadata(b'{"data":{"snapshot":null}}')

    def test_wrong_dataset_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "version"):
            parse_metadata(source(id="ds000225:1.0.1"))

    def test_wrong_tag_rejected(self):
        with self.assertRaisesRegex(ValueError, "version"):
            parse_metadata(source(tag="1.0.2"))

    def test_wrong_doi_rejected(self):
        with self.assertRaisesRegex(ValueError, "DOI"):
            parse_metadata(source(description={"Name":"X","DatasetDOI":"fake-doi"}))

    def test_missing_name_rejected(self):
        with self.assertRaisesRegex(ValueError, "name"):
            parse_metadata(source(description={"Name":"","DatasetDOI":"10.18112/openneuro.ds000224.v1.0.1"}))

    def test_graphql_errors_never_masquerade_as_success(self):
        with self.assertRaisesRegex(ValueError, "GraphQL"):
            parse_metadata(b'{"data":null,"errors":[{"message":"access denied"}]}')

    def test_disallow_unexpected_schema(self):
        with self.assertRaises(ValueError):
            parse_metadata(b"[]")


if __name__ == "__main__":
    unittest.main()
