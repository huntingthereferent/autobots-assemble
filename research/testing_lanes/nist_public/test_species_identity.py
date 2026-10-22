"""Offline NIST species identity tests. Every HTTP response is synthetic."""
import unittest
from species_identity import URL, CAS, INCHI_KEY, MAX_BYTES, classify, observe


def page(*, h1="Water", cas=CAS, formula="H<sub>2</sub>O",
         key=INCHI_KEY, webbook="NIST Chemistry WebBook"):
    return (f"""<!doctype html><html><body><header>{webbook}</header>
      <h1>{h1}</h1>
      <ul><li>Formula: {formula}</li>
        <li>Molecular weight: 18.0153</li>
        <li>IUPAC Standard InChIKey: {key}</li>
        <li>CAS Registry Number: {cas}</li></ul>
      </body></html>""").encode("utf-8")


class Response:
    status = 200
    def __init__(self, raw):
        self.raw = raw
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return None
    def read(self, n):
        return self.raw[:n]


class Transport:
    def __init__(self, raw):
        self.raw = raw
        self.calls = []
    def open(self, request, timeout):
        self.calls.append((request.full_url, request.get_method(),
                           request.get_header("Accept"), timeout))
        return Response(self.raw)


class NistIdentityTests(unittest.TestCase):
    def test_canonical_species_identity(self):
        x = classify(page())
        self.assertEqual(x["species"], "Water")
        self.assertEqual(x["cas_registry_number"], CAS)
        self.assertEqual(x["molecular_formula"], "H2O")
        self.assertEqual(x["inchi_key"], INCHI_KEY)
        self.assertTrue(all(x["metadata_identity_checks"].values()))
        self.assertEqual(x["scientific_measurements_admitted"], 0)
        self.assertFalse(x["property_tables_copied"])

    def test_one_fixed_https_metadata_request(self):
        fake = Transport(page())
        x = observe(opener=fake)
        self.assertEqual(x["state"], "PUBLIC_SPECIES_METADATA_OBSERVED")
        self.assertEqual(fake.calls, [(URL, "GET", "text/html", 15)])
        self.assertEqual(x["response_status"], 200)
        self.assertEqual(len(x["body_sha256"]), 64)
        self.assertFalse(x["measurements_downloaded"])
        self.assertFalse(x["data_compilation_copied"])
        self.assertEqual(x["rights_review"], "REQUIRED_PER_RECORD")
        self.assertEqual(x["scientific_status"], "NOT_TESTED")

    def test_other_compound_title_fails(self):
        self.assertRaises(ValueError, classify, page(h1="Hydrogen peroxide"))

    def test_different_cas_fails(self):
        self.assertRaises(ValueError, classify, page(cas="1111-11-1"))

    def test_incorrect_formula_fails(self):
        self.assertRaises(ValueError, classify, page(formula="H<sub>2</sub>O<sub>2</sub>"))

    def test_incorrect_inchikey_fails(self):
        self.assertRaises(ValueError, classify, page(key="WRONGKEY"))

    def test_missing_nist_publisher_identity_fails(self):
        self.assertRaises(ValueError, classify, page(webbook="Another catalog"))

    def test_javascript_cannot_impersonate_page(self):
        bad = b"<html><script>" + page() + b"</script><h1>Unknown</h1></html>"
        self.assertEqual(observe(opener=Transport(bad))["state"], "SOURCE_WALL")

    def test_missing_source_identity_is_wall(self):
        self.assertEqual(observe(opener=Transport(b"<html>Forbidden</html>"))["state"], "SOURCE_WALL")

    def test_bounded_size_rejected_without_hash(self):
        x = observe(opener=Transport(b"a" * (MAX_BYTES + 1)))
        self.assertEqual(x["state"], "SOURCE_WALL")
        self.assertEqual(x["error_class"], "ValueError")
        self.assertNotIn("body_sha256", x)

    def test_invalid_encoding_is_wall(self):
        x = observe(opener=Transport(b"\xff\xfe\xfa"))
        self.assertEqual(x["state"], "SOURCE_WALL")
        self.assertEqual(x["error_class"], "ValueError")


if __name__ == "__main__":
    unittest.main()
