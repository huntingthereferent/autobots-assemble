"""Synthetic NOAA NCEI catalog checks, no network."""
import unittest
import json
from pathlib import Path
from catalog_identity import URL, TITLE, ID, DSI, LIMIT, classify, observe


def page(*, title=TITLE, dataset_id=ID, dsi=DSI,
         publisher="NOAA National Centers for Environmental Information",
         lineage="successor dataset to the Global Summary of the Day",
         version="SSODv2"):
    return f"""<html><body><h1>Dataset Overview</h1><h1>{title}</h1>
      <h2>{version}</h2><p>{publisher}</p>
      <p>Dataset Identifiers: {dsi}; {dataset_id}</p>
      <p>SSOD is the {lineage}</p></body></html>""".encode()


class Response:
    status = 200
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *_): return None
    def read(self, n): return self.body[:n]


class Transport:
    def __init__(self, body):
        self.body = body
        self.calls = []
    def open(self, request, timeout):
        self.calls.append((request.full_url, request.get_method(), request.get_header("Accept"), timeout))
        return Response(self.body)


class NOAAIdentityTests(unittest.TestCase):
    def test_exact_publisher_source_identity(self):
        data = classify(page())
        self.assertEqual(data["dataset_id"], ID)
        self.assertEqual(data["edition"], "Version 2")
        self.assertTrue(all(data["identity_checks"].values()))
        self.assertEqual(data["observation_rows_read"], 0)
        self.assertEqual(data["station_records_downloaded"], 0)

    def test_exact_one_read_only_public_metadata_request(self):
        t = Transport(page())
        result = observe(opener=t)
        self.assertEqual(result["state"], "PUBLIC_DATASET_METADATA_OBSERVED")
        self.assertEqual(t.calls, [(URL, "GET", "text/html", 15)])
        self.assertEqual(len(result["response_sha256"]), 64)
        self.assertFalse(result["observations_downloaded"])
        self.assertFalse(result["station_files_downloaded"])
        self.assertFalse(result["raw_html_archived"])
        self.assertEqual(result["scientific_status"], "NOT_TESTED")

    def test_superseded_gsod_title_rejected(self):
        self.assertRaises(ValueError, classify, page(title="Global Surface Summary of the Day - GSOD"))

    def test_wrong_noaa_dataset_id_rejected(self):
        self.assertRaises(ValueError, classify, page(dataset_id="gov.noaa.ncdc:C00516"))

    def test_wrong_data_series_id_rejected(self):
        self.assertRaises(ValueError, classify, page(dsi="NCEI DSI 3505"))

    def test_publisher_spoof_rejected(self):
        self.assertRaises(ValueError, classify, page(publisher="Unknown archive"))

    def test_missing_succession_evidence_rejected(self):
        self.assertRaises(ValueError, classify, page(lineage="unknown provenance"))

    def test_wrong_version_label_rejected(self):
        self.assertRaises(ValueError, classify, page(version="GSODv1"))

    def test_javascript_cannot_forge_catalog_page(self):
        raw = b"<html><script>" + page() + b"</script><h1>Unknown</h1></html>"
        self.assertEqual(observe(opener=Transport(raw))["state"], "SOURCE_WALL")

    def test_missing_metadata_reports_named_failed_predicates(self):
        response = observe(opener=Transport(page(dataset_id="bad", version="bad")))
        self.assertEqual(response["state"], "SOURCE_WALL")
        self.assertEqual(response["failed_identity_checks"],
                         ["current_version_label", "dataset_catalog_id"])
        self.assertNotIn("response_sha256", response)

    def test_ceiling_holds_without_archiving(self):
        result = observe(opener=Transport(b"x" * (LIMIT + 1)))
        self.assertEqual(result["state"], "SOURCE_WALL")
        self.assertEqual(result["error_class"], "ValueError")
        self.assertNotIn("response_sha256", result)

    def test_historical_source_receipt_not_a_weather_observation(self):
        record = Path(__file__).parent / "observations" / "2026-10-22-run-39830318184.json"
        archive = json.loads(record.read_text(encoding="utf-8"))
        receipt = archive["observation"]
        self.assertEqual(archive["github_run_id"], 39830318184)
        self.assertEqual(archive["source_code_commit"], "2ec0c0cd3d6eb370766c92dbf499ebf4b24e882d")
        self.assertEqual(receipt["state"], "PUBLIC_DATASET_METADATA_OBSERVED")
        self.assertEqual(receipt["source_url"], URL)
        self.assertEqual(receipt["response_sha256"],
                         "4ed866a8fbbfbe08ddfeb4ee0fc2dbeb6accc8f978d284a847b891fb192fdd51")
        self.assertTrue(all(receipt["identity"]["identity_checks"].values()))
        self.assertEqual(receipt["identity"]["station_records_downloaded"], 0)
        self.assertFalse(receipt["observations_downloaded"])
        self.assertFalse(receipt["raw_html_archived"])
        self.assertEqual(archive["rights_review"], "REQUIRED_PER_RECORD")
        self.assertEqual(archive["scientific_status"], "NOT_TESTED")

    def test_invalid_utf8_is_source_wall(self):
        result = observe(opener=Transport(b"\xff"))
        self.assertEqual(result["state"], "SOURCE_WALL")
        self.assertFalse(result["station_files_downloaded"])


if __name__ == "__main__":
    unittest.main()
