"""Synthetic PhysioNet source admissions; the test suite does not use the network."""
import json
import unittest

from catalog_identity import (
    PAGE, SLUG, VERSION, DOI, LICENSE, MAX_BYTES, classify, observe
)


def page(*, title="MIT-BIH Arrhythmia Database", version=VERSION,
         doi=DOI, access="Database Open Access", license=LICENSE):
    return f"""<!doctype html><html><body>
    <div class="access">{access}</div><h1>{title}</h1>
    <span>Version {version}</span><p>DOI: {doi}</p><p>License {license}</p>
    </body></html>""".encode("utf-8")


class Response:
    status = 200
    def __init__(self, raw):
        self.raw = raw
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return None
    def read(self, length):
        return self.raw[:length]


class Transport:
    def __init__(self, raw):
        self.raw = raw
        self.requests = []
    def open(self, request, timeout):
        self.requests.append({
            "url": request.full_url,
            "method": request.get_method(),
            "accept": request.get_header("Accept"), "timeout": timeout,
        })
        return Response(self.raw)


class PhysioNetMetadataTests(unittest.TestCase):
    def test_expected_catalog_structure_without_recordings(self):
        data = classify(page())
        self.assertEqual(data["project_slug"], SLUG)
        self.assertEqual(data["version"], VERSION)
        self.assertEqual(data["version_doi"], DOI)
        self.assertEqual(data["published_license_label"], LICENSE)
        self.assertTrue(all(data["checks"].values()))
        self.assertFalse(data["recording_files_read"])
        self.assertFalse(data["scientific_experiment_completed"])

    def test_one_public_get_only_with_fixed_request(self):
        transport = Transport(page())
        receipt = observe(opener=transport)
        self.assertEqual(receipt["state"], "PUBLIC_CATALOG_METADATA_OBSERVED")
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.requests[0], {
            "url": PAGE, "method": "GET", "accept": "text/html", "timeout": 15
        })
        self.assertEqual(len(receipt["body_sha256"]), 64)
        self.assertFalse(receipt["recordings_fetched"])
        self.assertFalse(receipt["source_body_archived"])
        self.assertEqual(receipt["rights_review"], "REQUIRED_BEFORE_DATA_USE")
        self.assertEqual(receipt["scientific_status"], "NOT_TESTED")

    def test_html_scripts_cannot_fake_page_identity(self):
        raw = b"<html><script>" + page() + b"</script><p>Unknown resource</p></html>"
        self.assertEqual(observe(opener=Transport(raw))["state"], "SOURCE_WALL")

    def test_restricted_access_does_not_pass(self):
        self.assertRaises(ValueError, classify, page(access="Database Credentialed Access"))

    def test_wrong_doi_not_admitted(self):
        self.assertRaises(ValueError, classify, page(doi="10.0000/NOT-THIS"))

    def test_wrong_version_not_admitted(self):
        self.assertRaises(ValueError, classify, page(version="2.0.0"))

    def test_other_project_not_admitted(self):
        self.assertRaises(ValueError, classify, page(title="A different ECG repository"))

    def test_license_not_invented(self):
        self.assertRaises(ValueError, classify, page(license="No license information"))

    def test_empty_or_html_error_not_admitted(self):
        self.assertEqual(observe(opener=Transport(b"<html>Error</html>"))["state"], "SOURCE_WALL")

    def test_size_ceiling_stops_return_body(self):
        result = observe(opener=Transport(b"x" * (MAX_BYTES + 1)))
        self.assertEqual(result["state"], "SOURCE_WALL")
        self.assertNotIn("body_sha256", result)

    def test_non_utf8_is_a_wall(self):
        result = observe(opener=Transport(b"\xff\xfe"))
        self.assertEqual(result["state"], "SOURCE_WALL")
        self.assertEqual(result["error_class"], "ValueError")


if __name__ == "__main__":
    unittest.main()
