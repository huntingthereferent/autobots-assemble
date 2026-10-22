"""Offline controls for SEC-CVE-METADATA-001."""
import unittest

from sec_cve_metadata import CVE_ID, validate_payload


def valid_payload():
    return {
        "totalResults": 1,
        "vulnerabilities": [{
            "cve": {
                "id": CVE_ID,
                "published": "2021-12-10T10:15:09.143",
                "lastModified": "2025-01-01T00:00:00.000",
                "descriptions": [{"lang": "en", "value": "synthetic fixture"}],
                "metrics": {"cvssMetricV31": []},
                "weaknesses": [{"description": [{"lang": "en", "value": "CWE-502"}]}]
            }
        }]
    }


class NvdMetadataTests(unittest.TestCase):
    def test_accepts_one_matching_record(self):
        result = validate_payload(valid_payload())
        self.assertEqual(result["cve_id"], CVE_ID)
        self.assertEqual(result["description_languages"], ["en"])
        self.assertEqual(result["cvss_metric_families"], ["cvssMetricV31"])
        self.assertEqual(result["cwe_ids"], ["CWE-502"])

    def test_rejects_wrong_record_identity(self):
        payload = valid_payload()
        payload["vulnerabilities"][0]["cve"]["id"] = "CVE-1900-0001"
        with self.assertRaisesRegex(ValueError, "identity"):
            validate_payload(payload)

    def test_rejects_empty_or_ambiguous_result(self):
        payload = valid_payload()
        payload["totalResults"] = 0
        payload["vulnerabilities"] = []
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_payload(payload)

    def test_rejects_missing_provenance_fields(self):
        payload = valid_payload()
        del payload["vulnerabilities"][0]["cve"]["published"]
        with self.assertRaisesRegex(ValueError, "timestamp"):
            validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
