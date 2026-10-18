"""A/B provenance CLI/package verification against existing repository contracts."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ab_prov import ProvenanceError, load_document, graph_summary, build_graph
from ab_prov.cli import main
from ab_prov.render import render_html
from ab_prov.ancestry import ancestors

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "tools" / "ab-provenance"
SAMPLE = PACKAGE / "examples" / "illustrative-provenance.json"
JOURNAL = PACKAGE / "examples" / "illustrative-journal.jsonl"

class ABProvenanceTests(unittest.TestCase):
    def test_real_existing_schema_compatibility(self):
        from jsonschema import Draft202012Validator
        data=json.loads(SAMPLE.read_text(encoding="utf-8"))
        linkschema=json.loads((ROOT/"protocols/core/provenance-link.schema.json").read_text())
        traceschema=json.loads((ROOT/"protocols/core/trace.schema.json").read_text())
        for row in data["provenance_links"]:
            Draft202012Validator(linkschema).validate(row)
        for row in data["traces"]:
            Draft202012Validator(traceschema).validate(row)

    def test_narrow_envelope_references_repo_native_schemas_instead_of_replacing(self):
        data=json.loads((PACKAGE/"schema/document.schema.json").read_text())
        self.assertEqual(data["properties"]["provenance_links"]["items"]["$ref"],
                         "../../../protocols/core/provenance-link.schema.json")
        self.assertEqual(data["properties"]["traces"]["items"]["$ref"],
                         "../../../protocols/core/trace.schema.json")

    def test_visual_design_contract_is_registered_and_only_a_candidate(self):
        registry=json.loads((ROOT/"design/visual-provenance/registry.json").read_text())
        template=json.loads((ROOT/"design/visual-provenance/templates/ab_provenance_graph_v1.json").read_text())
        binding=json.loads((PACKAGE/"visual-provenance.json").read_text())
        self.assertIn("ab_provenance_graph_v1",{x["template_id"] for x in registry["templates"]})
        self.assertEqual(template["status"],"candidate")
        self.assertEqual(binding["template_id"],template["template_id"])
        self.assertIn('name="visual-template" content="ab_provenance_graph_v1"',
                      (PACKAGE/"src/ab_prov/render.py").read_text())

    def test_projection_preserves_source_and_unresolved_counts(self):
        graph=load_document(SAMPLE)
        self.assertEqual(graph["kind"],"ab-provenance/graph-v1")
        self.assertEqual(len(graph["sources"]),1)
        self.assertEqual(len(graph["edges"]),5)
        self.assertEqual(len([e for e in graph["edges"] if e["state"]=="contested"]),1)
        self.assertGreaterEqual(graph_summary(graph)["unresolved"],2)
        relation=next(e for e in graph["edges"] if e["id"]=="prov:fixture-source-observation")
        self.assertEqual(relation["evidence_refs"],["fixture://witness-unchecked"])
        self.assertEqual(relation["survived"],["source identity"])
        self.assertEqual(relation["details"]["transformation"],"read-only example")
        self.assertFalse(graph_summary(graph)["independently_verified_by_this_tool"])

    def test_unresolved_reference_is_not_a_verified_event_or_created_worker(self):
        graph=load_document(SAMPLE)
        unresolved=[n for n in graph["nodes"] if n["kind"]=="unresolved"]
        self.assertTrue(unresolved)
        self.assertFalse(any(n["kind"]=="event" for n in graph["nodes"]))

    def test_original_runtimejournal_events_and_parents_are_preserved(self):
        graph=load_document(journal=JOURNAL)
        types={n["kind"] for n in graph["nodes"]}
        self.assertIn("handoff",types)
        self.assertIn("event",types)
        self.assertIn("evidence_reference",types)
        self.assertTrue(any(e["relation"]=="precedes" for e in graph["edges"]))
        self.assertTrue(any(e["relation"]=="cites_evidence_reference" for e in graph["edges"]))
        self.assertFalse(graph_summary(graph)["independently_verified_by_this_tool"])

    def test_workstation_missing_submission_stays_unresolved(self):
        orphan=[{"record_type":"EVENT","event":{
            "event_id":"orphan","handoff_id":"unprovided-handoff",
            "event_type":"NOTE","parents":["not-provided"],"evidence":[]}}]
        graph=build_graph([],[],orphan)
        self.assertTrue(any(n["kind"]=="unresolved" and n["id"]=="handoff:unprovided-handoff"
                            for n in graph["nodes"]))
        self.assertTrue(any(n["id"]=="unresolved-parent:not-provided" for n in graph["nodes"]))
        self.assertGreaterEqual(graph_summary(graph)["unresolved"],1)

    def test_duplicate_native_event_ids_rejected(self):
        item={"record_type":"EVENT","event":{
            "event_id":"same","handoff_id":"h","event_type":"NOTE","parents":[]}}
        with self.assertRaises(ProvenanceError):
            build_graph([],[],[item,item])

    def test_duplicate_cross_layer_identity_rejected(self):
        record=json.loads(SAMPLE.read_text())["provenance_links"][0]
        with self.assertRaises(ProvenanceError):
            build_graph([record,record],[],[])

    def test_duplicate_json_keys_rejected(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/"bad.json"
            path.write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(ProvenanceError):
                load_document(path)

    def test_dangling_and_invalid_input_rejected_without_fake_verification(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/"bad.json"
            path.write_text('{"schema_version":1,"provenance_links":[{"schema_version":1}]}')
            with self.assertRaises(ProvenanceError):
                load_document(path)
            self.assertFalse(any(n["kind"]=="evidence_verified" for n in load_document(SAMPLE)["nodes"]))

    def test_html_embeds_source_safely_instead_of_executing_it(self):
        graph=load_document(SAMPLE)
        graph["warnings"].append('</script><script>alert("arbitrary")</script>')
        html=render_html(graph)
        self.assertNotIn('</script><script>alert',html)
        self.assertIn("\\u003c/script\\u003e",html)
        self.assertIn("<svg",html)
        self.assertIn("textContent",html)
        self.assertIn("ab_provenance_graph_v1",html)
        self.assertNotIn("fetch(",html)

    def test_cli_renders_real_html_without_mutating_source(self):
        with TemporaryDirectory() as temp:
            target=Path(temp)/"research.html"
            before=SAMPLE.read_bytes()
            stdout=StringIO()
            with redirect_stdout(stdout):
                exitcode=main(["render",str(SAMPLE),"-o",str(target)])
            self.assertEqual(exitcode,0,stdout.getvalue())
            self.assertTrue(target.exists())
            self.assertIn("<svg",target.read_text())
            self.assertEqual(SAMPLE.read_bytes(),before)
            self.assertIn('"output"',stdout.getvalue())

    def test_cli_inspect_journal_and_graph_are_machine_readable(self):
        out=StringIO()
        with redirect_stdout(out):
            rc=main(["inspect","--journal",str(JOURNAL),"--graph"])
        self.assertEqual(rc,0)
        graph=json.loads(out.getvalue())
        self.assertIn("nodes",graph)
        self.assertIn("edges",graph)

    def test_cli_fail_closed_exit(self):
        output=StringIO()
        with redirect_stderr(output):
            result=main(["inspect","/path/that/does/not/exist.json"])
        self.assertEqual(result,2)
        self.assertIn("ab-prov:",output.getvalue())

    def test_backward_ancestry_preserves_recorded_source_and_contested_status(self):
        graph=load_document(SAMPLE)
        subset=ancestors(graph,"sample/provisional-claim")
        ids={e["id"] for e in subset["edges"]}
        self.assertIn("prov:fixture-source-observation",ids)
        self.assertIn("prov:fixture-contested",ids)
        self.assertNotIn("prov:fixture-open",ids)
        self.assertFalse(subset["truncated"])
        self.assertIn("prov:fixture-contested",subset["contested_edges"])
        self.assertFalse(any(e["state"]=="verified" for e in subset["edges"]))

    def test_backward_path_bounded_without_pretending_to_complete(self):
        graph=load_document(SAMPLE)
        subset=ancestors(graph,"sample/provisional-claim",max_hops=1)
        self.assertTrue(subset["truncated"])
        self.assertIn("Ancestry bounded at hop limit; upstream record may be missing.",
                      subset["warnings"])
        self.assertEqual(len(subset["edges"]),1)

    def test_backward_path_requires_unique_source_reference_or_id(self):
        graph=load_document(SAMPLE)
        with self.assertRaises(ProvenanceError):
            ancestors(graph,"nonexistent-source")
        with self.assertRaises(ProvenanceError):
            ancestors(graph,"sample/provisional-claim",max_hops=0)

    def test_cli_backward_query_and_focused_visual_export(self):
        with TemporaryDirectory() as temp:
            html=Path(temp)/"focused.html"
            stdout=StringIO()
            with redirect_stdout(stdout):
                rc=main(["ancestors",str(SAMPLE),"--target","sample/provisional-claim"])
            self.assertEqual(rc,0)
            view=json.loads(stdout.getvalue())
            self.assertEqual(view["kind"],"ab-provenance/ancestry-v1")
            with redirect_stdout(StringIO()):
                rc=main(["render",str(SAMPLE),"-o",str(html),
                         "--target","sample/provisional-claim"])
            self.assertEqual(rc,0)
            self.assertTrue(html.is_file())
            self.assertIn("prov:fixture-contested",html.read_text())
            self.assertNotIn("prov:fixture-open",html.read_text())


if __name__=="__main__":
    unittest.main()
