"""Synthetic OECD dataflow source tests; no network or statistical data."""
import unittest
import json
from pathlib import Path
from dataflow_identity import URL, AGENCY, FLOW, VERSION, ACCEPT, MAX_BYTES, classify, observe

def xml(*, agency=AGENCY, flow=FLOW, version=VERSION, label="Trade in services", extra="", data=""):
    return (f"""<Structure xmlns="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
     <Structures><Dataflows><Dataflow id="{flow}" agencyID="{agency}" version="{version}">
     <Name>{label}</Name></Dataflow>{extra}</Dataflows></Structures>{data}</Structure>""").encode()

class Response:
    status = 200
    def __init__(self, raw): self.raw = raw
    def __enter__(self): return self
    def __exit__(self, *_): return None
    def read(self, length): return self.raw[:length]

class Transport:
    def __init__(self, raw): self.raw, self.calls = raw, []
    def open(self, request, timeout):
        self.calls.append((request.full_url, request.get_method(), request.get_header("Accept"), timeout))
        return Response(self.raw)

class OECDSourceTests(unittest.TestCase):
    def test_exact_flow_structure(self):
        r = classify(xml())
        self.assertEqual((r["agency"], r["dataflow"], r["version"]), (AGENCY, FLOW, VERSION))
        self.assertTrue(all(r["identity_checks"].values()))
        self.assertEqual(r["statistical_rows_read"], 0)

    def test_fixed_metadata_get(self):
        fake = Transport(xml())
        r = observe(opener=fake)
        self.assertEqual(r["state"], "PUBLIC_DATAFLOW_METADATA_OBSERVED")
        self.assertEqual(fake.calls, [(URL, "GET", ACCEPT, 15)])
        self.assertEqual(len(r["response_sha256"]), 64)
        self.assertFalse(r["raw_source_archived"])
        self.assertEqual(r["data_rows_downloaded"], 0)

    def test_wrong_agency(self):
        self.assertRaises(ValueError, classify, xml(agency="OTHER"))
    def test_wrong_flow(self):
        self.assertRaises(ValueError, classify, xml(flow="OTHER"))
    def test_wrong_version(self):
        self.assertRaises(ValueError, classify, xml(version="2.0"))
    def test_missing_name(self):
        self.assertRaises(ValueError, classify, xml(label=""))
    def test_multiple_flows(self):
        self.assertRaises(ValueError, classify, xml(extra="<Dataflow id='OTHER'/>"))
    def test_no_statistical_payload(self):
        self.assertRaises(ValueError, classify, xml(data="<DataSet><Series><Obs/></Series></DataSet>"))
    def test_error_xml(self):
        r = observe(opener=Transport(b"<Error>Invalid</Error>"))
        self.assertEqual(r["state"], "SOURCE_WALL")
        self.assertIn("sdmx_structure_root", r["failed_identity_checks"])
    def test_html_rejected(self):
        self.assertEqual(observe(opener=Transport(b"<html>No data</html>"))["state"], "SOURCE_WALL")
    def test_doctype_rejected(self):
        self.assertEqual(observe(opener=Transport(b"<!DOCTYPE Structure><Structure/>"))["state"], "SOURCE_WALL")
    def test_byte_ceiling(self):
        r = observe(opener=Transport(b"X" * (MAX_BYTES + 1)))
        self.assertEqual(r["state"], "SOURCE_WALL")
        self.assertNotIn("response_sha256", r)
    def test_archived_live_structure_never_claims_statistical_result(self):
        document = Path(__file__).parent / "observations" / "2026-10-22-run-39831994691.json"
        archived = json.loads(document.read_text(encoding="utf-8"))
        observation = archived["observation"]
        self.assertEqual(archived["source_run_id"], 39831994691)
        self.assertEqual(archived["source_code_commit"], "fc77da47fe928b31d555dd5b138dde6e4a5bbaa8")
        self.assertEqual(observation["state"], "PUBLIC_DATAFLOW_METADATA_OBSERVED")
        self.assertEqual(observation["source_url"], URL)
        self.assertEqual(observation["response_sha256"],
                         "c5e17eb631f9eba763e6baf2fec612a7841642be84fd217ecb0ade2687416109")
        self.assertTrue(all(observation["identity"]["identity_checks"].values()))
        self.assertEqual(observation["data_rows_downloaded"], 0)
        self.assertFalse(observation["raw_source_archived"])
        self.assertEqual(archived["science_status"], "NOT_TESTED")

    def test_safe_error_fields(self):
        r = observe(opener=Transport(xml(version="bad", label="")))
        self.assertEqual(r["failed_identity_checks"], ["exact_identity", "named_flow"])
        self.assertNotIn("raw", r)

if __name__ == "__main__":
    unittest.main()
