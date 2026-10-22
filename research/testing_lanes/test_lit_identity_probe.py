"""Offline controls for the fixed LIT DOI identity experiment."""
import json
import unittest

from lit_identity_probe import DOI, PMID, inspect_payloads, normalize_title


def crossref(doi=DOI, title="Estimating the reproducibility of psychological science"):
    return json.dumps({"message": {"DOI": doi, "title": [title]}}).encode()


def openalex(doi=f"https://doi.org/{DOI}", title="Estimating the reproducibility of psychological science."):
    return json.dumps({"doi": doi, "title": title}).encode()


def pubmed(doi=DOI, title="Estimating the reproducibility of psychological science.", pmid=PMID):
    return (
        "<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>" + pmid +
        "</PMID><Article><ArticleTitle>" + title +
        "</ArticleTitle></Article></MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType=\"doi\">" +
        doi + "</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"
    ).encode()


class LitIdentityProbeTests(unittest.TestCase):
    def test_three_sources_match_after_title_normalization(self):
        receipt = inspect_payloads({
            "crossref": crossref(), "openalex": openalex(), "pubmed": pubmed()
        })
        self.assertEqual(receipt["state"], "IDENTITY_MATCH")
        self.assertEqual(receipt["matched_fields"], ["DOI", "normalized title"])
        self.assertFalse(receipt["scientific_claim_tested"])
        self.assertFalse(receipt["full_text_fetched"])
        for source in receipt["sources"].values():
            self.assertEqual(len(source["response_sha256"]), 64)

    def test_wrong_doi_is_a_wall_not_a_match(self):
        receipt = inspect_payloads({
            "crossref": crossref("10.1000/wrong"), "openalex": openalex(), "pubmed": pubmed()
        })
        self.assertEqual(receipt["state"], "SOURCE_WALL")
        self.assertEqual(receipt["sources"]["crossref"]["state"], "IDENTITY_WALL")

    def test_title_conflict_is_preserved(self):
        receipt = inspect_payloads({
            "crossref": crossref(), "openalex": openalex(title="Different paper"), "pubmed": pubmed()
        })
        self.assertEqual(receipt["state"], "IDENTITY_CONFLICT")

    def test_missing_source_is_not_treated_as_zero_or_success(self):
        receipt = inspect_payloads({"crossref": crossref(), "openalex": openalex()})
        self.assertEqual(receipt["state"], "SOURCE_WALL")
        self.assertEqual(receipt["sources"]["pubmed"]["state"], "MISSING_INPUT")

    def test_invalid_xml_is_preserved_as_identity_wall(self):
        receipt = inspect_payloads({
            "crossref": crossref(), "openalex": openalex(), "pubmed": b"<broken"
        })
        self.assertEqual(receipt["state"], "SOURCE_WALL")
        self.assertEqual(receipt["sources"]["pubmed"]["error_class"], "ParseError")

    def test_normalization_only_removes_punctuation_and_case(self):
        self.assertEqual(
            normalize_title("A/B: TEST—Case!"),
            normalize_title("a b test case"),
        )

    def test_pinned_identifiers_are_explicit(self):
        self.assertEqual(DOI, "10.1126/science.aac4716")
        self.assertEqual(PMID, "26315443")


if __name__ == "__main__":
    unittest.main()
