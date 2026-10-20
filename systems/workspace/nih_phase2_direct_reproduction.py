"""NIH Phase 2 direct functional trial against the EXISTING W13 temporal executable.

This is NOT another historical source-intake experiment. We execute the real,
unchanged emitted W13/NIH temporal_query.py against realistic but wholly
fictional biomedical KG questions: state selection, future leakage, sequential
therapy inference, superseded research claims, and RDF entailment. Missing
capabilities are graded as failures, not replaced with imagined successful
worker results. A separately labeled graph profiler measures static/temporal
structural proxies; it is NOT an OWL consistency reasoner.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .game_construction import GameSpec, first_state, transition
from .nih_prototype_worker_source.prototype_worker import ENGINE

SCHEMA = "nih-phase2-direct-functional-reproduction-trial/v1"
EX = Namespace("https://example.org/ab-nih-phase2-rehearsal/")
MIN_DATE, MAX_DATE = "2026-01-01", "2026-02-01"


def obs(id, predicate, object, start, end, known, *, source, subject="fictional-cohort"):
    return dict(id=id, subject=subject, predicate=predicate, object=object,
                valid_from=start, valid_to=end, known_at=known, source_ref=source)


# These are explicitly fictional, synthetic population-level examples, not
# patient records or extracted real registry clinical outcomes.
BIOMED = [
    obs("therapy-alpha","receives-therapy","alpha","2026-01-04","2026-01-09",
        "2026-01-04",source="synthetic-care-sequence"),
    obs("response-poor","response","inadequate","2026-01-06","2026-01-20",
        "2026-01-06",source="synthetic-care-sequence"),
    obs("therapy-beta","receives-therapy","beta","2026-01-09","2026-01-31",
        "2026-01-09",source="synthetic-care-sequence"),
    obs("guide-old","recommended-therapy","alpha","2026-01-01","2026-01-12",
        "2026-01-01",source="synthetic-guideline",subject="fictional-guideline"),
    obs("guide-new","recommended-therapy","beta","2026-01-12","2026-02-01",
        "2026-01-12",source="synthetic-guideline",subject="fictional-guideline"),
    obs("claim-original","supports-claim","claim-z","2026-01-01","2026-02-01",
        "2026-01-02",source="synthetic-publication",subject="fictional-paper"),
    obs("claim-correction","retracts-claim","claim-z","2026-01-01","2026-02-01",
        "2026-01-10",source="synthetic-correction",subject="fictional-paper"),
]
SURVEILLANCE = [
    obs("surv-early","variant-status","variant-a","2026-01-01","2026-01-15",
        "2026-01-02",source="synthetic-surveillance",subject="fictional-region"),
    obs("surv-late","variant-status","variant-b","2026-01-15","2026-02-01",
        "2026-01-16",source="synthetic-surveillance",subject="fictional-region"),
]

# Independently declared practice-answer key. It is intentionally NOT
# generated from the W13 worker output. The tasks marked derived demand
# a value about the longitudinal PATH, not an input-record ID.
TASKS = [
    dict(id="care-early",domain="care",kind="fact",known="2026-01-05",
         target="2026-01-05",fact="therapy-alpha",expected=True),
    dict(id="care-late",domain="care",kind="fact",known="2026-01-11",
         target="2026-01-11",fact="therapy-beta",expected=True),
    dict(id="no-future-beta",domain="care",kind="fact",known="2026-01-07",
         target="2026-01-11",fact="therapy-beta",expected=False),
    dict(id="earlier-guideline",domain="guidelines",kind="fact",known="2026-01-08",
         target="2026-01-08",fact="guide-old",expected=True),
    dict(id="later-guideline",domain="guidelines",kind="fact",known="2026-01-15",
         target="2026-01-15",fact="guide-new",expected=True),
    dict(id="no-future-correction",domain="evidence",kind="fact",known="2026-01-07",
         target="2026-01-12",fact="claim-correction",expected=False),
    dict(id="correction-present",domain="evidence",kind="fact",known="2026-01-12",
         target="2026-01-12",fact="claim-correction",expected=True),
    # The original program only filters by known_at and valid_at; it cannot
    # retract a formerly visible claim after a later explicit correction.
    dict(id="superseded-claim-not-current",domain="evidence",kind="fact",
         known="2026-01-12",target="2026-01-12",
         fact="claim-original",expected=False),
    # Original native W13 selects *simultaneously valid snapshot records*,
    # not a longitudinal chain across different validity intervals.
    dict(id="infer-sequential-switch",domain="care",kind="derived",
         known="2026-01-11",target="2026-01-11",
         inference="therapy-alpha-then-poor-response-then-therapy-beta",expected=True),
    dict(id="no-premature-sequential-switch",domain="care",kind="derived",
         known="2026-01-07",target="2026-01-11",
         inference="therapy-alpha-then-poor-response-then-therapy-beta",expected=False),
    dict(id="no-backdated-sequential-switch",domain="care",kind="derived",
         known="2026-01-11",target="2026-01-07",
         inference="therapy-alpha-then-poor-response-then-therapy-beta",expected=False),
    # Biomed ontology support in the repo is a DIFFERENT earlier worker.
    # The emitted W13 query program cannot entail RDF class/property chains.
    dict(id="rdf-property-chain-inference",domain="interoperability",kind="rdf",
         known="2026-01-11",target="2026-01-11",
         inference="regimen-switch-chain-triple",expected=True),
    dict(id="surveillance-domain-transfer",domain="surveillance",kind="fact",
         known="2026-01-17",target="2026-01-17",fact="surv-late",expected=True),
]


def validated(data):
    if type(data) is not list or not 1 <= len(data) <= 1000:
        raise ValueError("bounded observation set required")
    used = set()
    for row in data:
        if set(row) != {"id","subject","predicate","object","valid_from","valid_to","known_at","source_ref"}:
            raise ValueError("exact source record shape required")
        if row["id"] in used:
            raise ValueError("duplicate source ID")
        used.add(row["id"])
        for key in ("valid_from","valid_to","known_at"):
            val=row[key]
            if type(val) is not str or len(val)!=10 or date.fromisoformat(val).isoformat()!=val:
                raise ValueError("invalid source clock")
        if not row["valid_from"] < row["valid_to"]:
            raise ValueError("invalid observed validity interval")
        for key in ("id","subject","predicate","object","source_ref"):
            v=row[key]
            if type(v) is not str or not 1<=len(v)<=70 or any(ord(c)<32 for c in v):
                raise ValueError("invalid source token")
    return data


def native_query(program: Path, dataset: Path, *, known: str, target: str) -> dict:
    command = subprocess.run([sys.executable,"-I",str(program),str(dataset)],
        input=json.dumps({"known_at":known,"target_at":target}),
        text=True,capture_output=True,timeout=8,check=True)
    report = json.loads(command.stdout)
    if report.get("kind")!="synthetic-bitemporal-query/v1":
        raise ValueError("unexpected actual original W13 source result")
    return report


def source_expected(records: list[dict], *, known: str, target: str) -> dict:
    """Separate host selection oracle for direct fact-filter observations."""
    available=set()
    static=set()
    for row in records:
        if row["valid_from"]<=target<row["valid_to"]:
            static.add(row["id"])
            if row["known_at"]<=known:
                available.add(row["id"])
    return {"temporal":sorted(available),"static":sorted(static)}


def graph_profile(records: list[dict], ids: list[str]) -> dict:
    """Quantitative *harness graph* structural proxies, NOT native OWL reasoning."""
    g=Graph()
    src={r["id"]:r for r in records}
    entity_subjects=set()
    for label in ids:
        row=src[label]
        statement=EX["statement-"+label]
        actor=EX["entity-"+row["subject"]]
        entity_subjects.add(actor)
        # Source evidence node, not a bare clinical fact asserted as true.
        g.add((statement,RDF.type,EX.SourceStatement))
        g.add((statement,EX.hasSubject,actor))
        g.add((statement,EX.predicateToken,Literal(row["predicate"])))
        g.add((statement,EX.objectToken,Literal(row["object"])))
        g.add((statement,EX.knownFrom,Literal(row["known_at"],datatype=XSD.date)))
        g.add((statement,EX.validFrom,Literal(row["valid_from"],datatype=XSD.date)))
        g.add((statement,EX.validTo,Literal(row["valid_to"],datatype=XSD.date)))
        g.add((statement,EX.sourceRef,EX["source-"+row["source_ref"]]))
    non_type=[(s,p,o) for s,p,o in g if p != RDF.type]
    preds={p for _,p,_ in non_type}
    object_preds={p for _,p,o in non_type if isinstance(o,URIRef)}
    subjects={s for s,_,_ in g}
    linked={s for s,p,o in non_type if isinstance(o,URIRef)}
    instantiations=sum(1 for _,p,_ in g if p==RDF.type)
    attrs=sum(1 for _,p,o in non_type if isinstance(o,Literal))
    return {
        "number_of_triples":len(g),
        "relationship_richness_object_predicate_share":round(len(object_preds)/len(preds),6) if preds else 0,
        "attribute_richness_literals_per_statement":round(attrs/len(ids),6) if ids else 0,
        "class_property_instantiation_ratio":round(instantiations/len(non_type),6) if non_type else 0,
        "interlinking_completeness_subjects_with_resource_links":round(len(linked)/len(subjects),6) if subjects else 0,
        "logical_inconsistencies_unsatisfiable_classes":"NOT_MEASURED_NO_OWL_REASONER",
        "measurement_owner":"phase2-rehearsal-profiler-not-native-W13",
        "serialize_turtle_sha256":sha256(g.serialize(format="nt").encode()).hexdigest()
    }


def trial(*, output_dir: Path) -> dict:
    records=validated(BIOMED+SURVEILLANCE)
    output_dir.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(prefix="nih-p2-direct-native-") as td:
        p=Path(td)
        program=p/"original_temporal_query.py"
        program.write_text(ENGINE,encoding="utf8")
        sources={
            "biomed":p/"fictional_biomed.json",
            "surveillance":p/"fictional_surveillance.json",
        }
        for key,path in sources.items():
            v=BIOMED if key=="biomed" else SURVEILLANCE
            path.write_text(json.dumps({
                "synthetic":True,"observations":v,
                "functional_predicates":["recommended-therapy","variant-status"],
            },sort_keys=True),encoding="utf8")
        results=[]
        for task in TASKS:
            is_surveillance=task["domain"]=="surveillance"
            rows=SURVEILLANCE if is_surveillance else BIOMED
            actual=native_query(program,sources["surveillance" if is_surveillance else "biomed"],
                known=task["known"],target=task["target"])
            expected_native=source_expected(rows,known=task["known"],target=task["target"])
            if actual["temporal_ids"]!=expected_native["temporal"] or actual["static_snapshot_ids"]!=expected_native["static"]:
                raise ValueError("original W13 actual executable disagreed with separate host factual oracle")
            if task["kind"]=="fact":
                native_answer=task["fact"] in actual["temporal_ids"]
                static_answer=task["fact"] in actual["static_snapshot_ids"]
                capability="direct-source-selection"
            else:
                # Crucially: DO NOT invent inference from merely seeing records.
                # The actual W13 executable exposes no path / RDF inference field.
                native_answer=actual.get("inferred_paths",{}).get(task["inference"]) if (
                    type(actual.get("inferred_paths")) is dict) else None
                static_answer=None
                capability="longitudinal-path-inference" if task["kind"]=="derived" else "rdf-entailment"
            passed=native_answer is not None and native_answer == task["expected"]
            static_passed=static_answer is not None and static_answer==task["expected"]
            results.append({
                "task":task["id"],"domain":task["domain"],"capability":capability,
                "kind":task["kind"],"known_at":task["known"],"valid_at":task["target"],
                "expected_answer":task["expected"],
                "native_answer":native_answer,"native_supported":native_answer is not None,
                "native_pass":passed,"static_answer":static_answer,
                "static_pass":static_passed,
                "original_native_temporal_ids":actual["temporal_ids"],
                "original_native_static_ids":actual["static_snapshot_ids"],
                "original_native_future_leakage_ids":actual["future_leakage_ids"],
            })
        # For an actual Phase 2 KG task, an unknown source posting interval
        # cannot be substituted with an invented exact known_at. Original W13
        # does not accept that record structure, so record a capability failure.
        unknown_publication_supported=False
        # RDF profiler run is an external evaluation harness, not an upgrade to W13.
        benchmark_query={"known":"2026-01-07","target":"2026-01-12"}
        baseline=source_expected(BIOMED,known=benchmark_query["known"],target=benchmark_query["target"])
        metrics={
            "query":benchmark_query,
            "static_KG":graph_profile(BIOMED,baseline["static"]),
            "temporal_KG_harness_only":graph_profile(BIOMED,baseline["temporal"]),
        }
    raw=len(results)
    native_pass=sum(r["native_pass"] for r in results)
    static_pass=sum(r["static_pass"] for r in results)
    by_kind={key:{
        "cases":sum(r["kind"]==key for r in results),
        "native_pass":sum(r["kind"]==key and r["native_pass"] for r in results),
        "static_pass":sum(r["kind"]==key and r["static_pass"] for r in results)}
        for key in ("fact","derived","rdf")}
    original_game_spec=GameSpec()
    before=first_state(original_game_spec)
    after,verdict=transition(original_game_spec,before,"right")
    return {
        "schema":SCHEMA,
        "question":"Does unchanged native W13 temporal executable reproduce Phase 2-style reasoning?",
        "NIH_public_judging_weights":{
            "demonstrated_temporal_reasoning":30,"correct_inference":30,
            "evaluation_rigor":20,"extensibility":20},
        "workload":"two fictional population-level biomedical domains, no PHI",
        "original_unmodified_source": "systems/workspace/nih_prototype_worker_source/prototype_worker.py:ENGINE",
        "original_engine_sha256":sha256(ENGINE.encode()).hexdigest(),
        "native_game_control":{
            "action":"right","result":verdict,
            "before":[before.x,before.y],"after":[after.x,after.y],
            "different_from_KG_reasoning":True,
        },
        "cases":results,"scored_cases":raw,
        "native_pass":native_pass,"native_fail":raw-native_pass,
        "static_pass":static_pass,"static_fail":raw-static_pass,
        "by_kind":by_kind,
        "static_future_leakage_queries":sum(bool(r["original_native_future_leakage_ids"]) for r in results),
        "tested_uncertain_source_publication_interval_supported":unknown_publication_supported,
        "RDF_output_produced_by_unchanged_native_temporal_executable":False,
        "RDF_structural_metrics":metrics,
        "real_clinical_benchmark":False,
        "official_NIH_shared_benchmark_used":False,
        "official_NIH_phase2_eligibility_or_award":False,
        "real_world_clinical_valid_at_authenticated":False,
        "full_OWL_reasoner_present":False,
        "all_official_Phase2_metrics_implemented":False,
        "W13_native_journal_mutated":False,
        "World48_required":False,
        "phase2_reproduced_in_full":False,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",required=True,type=Path)
    a=parser.parse_args()
    result=trial(output_dir=a.output_dir)
    dest=a.output_dir/"phase2-direct-functional-trial.json"
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({
        "native_pass":result["native_pass"],"native_fail":result["native_fail"],
        "scored_cases":result["scored_cases"],
        "by_kind":result["by_kind"],
        "full_phase2_reproduced":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
