"""Source-first catalog controls; no network requests or research claims."""
import json
import unittest

from source_admission import (
    ALLOWED_HOSTS, MANUAL, catalog, inspect_shape, probe_one
)


class Response:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, n):
        return self.payload[:n]


class FakeOpener:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []
        self.requests = []

    def open(self, request, timeout=None):
        self.calls.append((request.full_url, timeout))
        self.requests.append(request)
        return Response(self.payload)


class SourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = catalog()

    def test_each_registered_source_has_one_source_card(self):
        self.assertEqual(len(self.cards), 18)
        self.assertEqual(len(ALLOWED_HOSTS), 13)
        self.assertEqual(len(MANUAL), 5)

    def test_all_sources_begin_unobserved(self):
        for sid, card in self.cards.items():
            with self.subTest(source=sid):
                self.assertEqual(card["observation_status"], "NOT_RUN")
                self.assertEqual(card["scientific_outcome"], "NOT_TESTED")
                self.assertEqual(card["rights_review"], "REQUIRED_PER_RECORD")

    def test_manual_sources_do_not_trigger_network(self):
        for sid in MANUAL:
            r = probe_one(sid, self.cards)
            self.assertEqual(r["state"], "ACCESS_WALL")
            self.assertNotIn("body_sha256", r)

    def test_unknown_source_is_rejected(self):
        with self.assertRaises(ValueError):
            probe_one("not-registered", self.cards)

    def test_probe_only_uses_fixed_host(self):
        bad = dict(self.cards)
        bad["crossref"] = dict(self.cards["crossref"])
        bad["crossref"]["probe"] = dict(bad["crossref"]["probe"], url="https://example.net/bad")
        with self.assertRaises(ValueError):
            probe_one("crossref", bad)

    def test_crossref_single_get_observation(self):
        payload = json.dumps({"message": {"DOI": "10.1126/science.aac4716"}}).encode()
        transport = FakeOpener(payload)
        receipt = probe_one("crossref", self.cards, opener=transport)
        self.assertEqual(receipt["state"], "METADATA_OBSERVED")
        self.assertFalse(receipt["scientific_claim_verified"])
        self.assertFalse(receipt["source_data_archived"])
        self.assertEqual(len(receipt["body_sha256"]), 64)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.calls[0][1], 15)

    def test_wrong_doi_is_structure_wall(self):
        payload = json.dumps({"message": {"DOI": "10.1000/wrong"}}).encode()
        receipt = probe_one("crossref", self.cards, opener=FakeOpener(payload))
        self.assertEqual(receipt["state"], "STRUCTURE_WALL")

    def test_unparseable_source_is_wall(self):
        receipt = probe_one("crossref", self.cards, opener=FakeOpener(b"not valid json"))
        self.assertEqual(receipt["state"], "SOURCE_WALL")
        self.assertEqual(receipt["error_class"], "JSONDecodeError")

    def test_response_length_is_bounded(self):
        receipt = probe_one("crossref", self.cards, opener=FakeOpener(b"a" * 300001))
        self.assertEqual(receipt["state"], "SOURCE_WALL")
        self.assertEqual(receipt["error_class"], "ValueError")

    def test_pubmed_identifier_is_explicit(self):
        good = {"esearchresult": {"idlist": ["26315443"]}}
        bad = {"esearchresult": {"idlist": ["123"]}}
        self.assertTrue(inspect_shape("pubmed", json.dumps(good).encode(), "json")["semantic_record_verified"])
        self.assertFalse(inspect_shape("pubmed", json.dumps(bad).encode(), "json")["semantic_record_verified"])

    def test_pubchem_cid_is_explicit(self):
        good = {"PropertyTable": {"Properties": [{"CID": 962, "MolecularFormula": "H2O"}]}}
        self.assertTrue(inspect_shape("pubchem", json.dumps(good).encode(), "json")["semantic_record_verified"])

    def test_gwosc_fixed_endpoint_uses_json_and_one_result(self):
        source = self.cards["gwosc"]
        self.assertEqual(source["probe"]["expected_format"], "json")
        self.assertTrue(source["probe"]["url"].endswith("?format=json&pagesize=1"))
        transport = FakeOpener(json.dumps({
            "results": [{"shortName": "GW150914-v3"}],
            "results_count": 1, "results_per_page": 1,
        }).encode())
        receipt = probe_one("gwosc", self.cards, opener=transport)
        self.assertEqual(receipt["state"], "METADATA_OBSERVED")
        self.assertEqual(transport.requests[0].get_header("Accept"), "application/json")
        self.assertFalse(receipt["scientific_claim_verified"])

    def test_gwosc_browsable_html_cannot_be_admitted_as_json(self):
        receipt = probe_one("gwosc", self.cards,
                            opener=FakeOpener(b"<html>GWOSC browsable API</html>"))
        self.assertEqual(receipt["state"], "SOURCE_WALL")
        self.assertEqual(receipt["error_class"], "JSONDecodeError")
        self.assertNotIn("body_sha256", receipt)

    def test_gwosc_v2_event_catalog_is_distinct_from_waveform(self):
        outcome = inspect_shape("gwosc", json.dumps({"results": [], "results_count": 0}).encode(), "json")
        self.assertTrue(outcome["semantic_record_verified"])
        self.assertEqual(outcome["record_shape"], "expected_structure")

    def test_gwosc_html_is_not_an_event_witness(self):
        outcome = inspect_shape("gwosc", b"<html>public API documentation</html>", "html")
        self.assertFalse(outcome["semantic_record_verified"])

    def test_every_probe_url_is_provider_scoped(self):
        for sid, host in ALLOWED_HOSTS.items():
            with self.subTest(sid=sid):
                self.assertIn(host, self.cards[sid]["probe"]["url"])


if __name__ == "__main__":
    unittest.main()
