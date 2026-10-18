"""Run a Phase 1 temporal evidence frontier IN the original playable W13/NIH world.

Replays the original 12-job stack with live Chromium, then launches a separate
read-only view backed by the exact original emitted temporal_query.py and actual
game actions. The new overlay is a presentation experiment, NOT a source-owned
thirteenth job, a rewritten prototype, a new NIH checkpoint, or clinical data.
Independent host oracle reads original Phase 1 scope, not HTML output.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_benchmark_temporal_join import join as original_twelve
from .nih_prototype_native import oracle, invoke
from .nih_scope_native import validate_scope
from .controls import reverify_job

SCHEMA = "nih-phase1-original-w13-world-frontier/v1"
PROTOTYPE_JOB = "nih-prototype-001"
GAME_JOB = "build-game-room-v1"
OBSERVATION_JOB = "live-game-temporal-001"
BENCHMARK_JOB = "nih-p2-benchmark-001"

OVERLAY = r"""
<script id="phase1-world-frontier-source">
(() => {
  const native = document.querySelector("#temporal-panel");
  if (!native || !document.querySelector("#grid")) throw Error("original world absent");
  const panel = document.createElement("section");
  panel.id = "phase1-frontier";
  panel.setAttribute("aria-label", "Phase 1 observed temporal evidence frontier");
  panel.style.cssText = "background:#121f29;color:#edf0f3;border:1px solid #76889a;padding:15px;margin:12px 0;font-family:monospace;line-height:1.5";
  panel.innerHTML = '<h2 style="margin:0 0 8px;font-size:16px">Phase 1 / observed frontier</h2>' +
    '<p id="phase1-frontier-summary">Reading native temporal source...</p>' +
    '<p style="margin:8px 0 0">Synthetic source only. Status is derived from the original emitted Python query on each game turn. No real registry version or clinical conclusion.</p>';
  native.insertAdjacentElement("afterend", panel);
  let sequence = 0;
  async function refresh() {
    const turn = Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g, ""));
    const ticket = ++sequence;
    const response = await fetch("/api/query?turn=" + encodeURIComponent(turn), {cache:"no-store"});
    if (!response.ok) throw Error("original temporal executable query unavailable");
    const result = await response.json();
    if (ticket !== sequence) return;
    if (result.kind !== "synthetic-bitemporal-query/v1" || result.clinical_verdict !== "NOT_EVALUATED") {
      throw Error("not the source-owned bounded synthetic answer");
    }
    const visible = result.temporal_ids.join(",");
    const withheld = result.future_leakage_ids.join(",");
    const allValid = result.static_snapshot_ids.join(",");
    panel.dataset.turn = String(turn);
    panel.dataset.known = result.known_at;
    panel.dataset.target = result.target_at;
    panel.dataset.visible = visible;
    panel.dataset.withheld = withheld;
    panel.dataset.static = allValid;
    panel.dataset.querySha = result.prototype_sha256;
    panel.dataset.clinical = result.clinical_verdict;
    document.querySelector("#phase1-frontier-summary").textContent =
      "Turn " + turn + " | Q(known=" + result.known_at + ", valid=" + result.target_at + ")" +
      " | T: " + (visible || "none") +
      " | S: " + (allValid || "none") +
      " | L: " + (withheld || "none");
  }
  for (const name of ["up", "down", "left", "right", "interact", "reset"]) {
    document.querySelector("#" + name).addEventListener("click", () => {
      refresh().catch(e => { panel.dataset.error = e.message; });
    });
  }
  document.addEventListener("keyup", () => {
    refresh().catch(e => { panel.dataset.error = e.message; });
  });
  refresh().catch(e => { panel.dataset.error = e.message; });
})();
</script>
"""


def digest(content):
    if type(content) is bytes:
        return sha256(content).hexdigest()
    if type(content) is not str:
        raise ValueError("source witness needs exact text or bytes")
    return sha256(content.encode("utf8")).hexdigest()


def overlay_html(original_html):
    if (type(original_html) is not str or
            original_html.count("</body>") != 1 or
            original_html.count('id="native-temporal-client"') != 1 or
            "phase1-world-frontier-source" in original_html):
        raise ValueError("not the exact original live temporal world")
    return original_html.replace("</body>", OVERLAY + "</body>")


def check_frame(frame, *, turn, known, target, source_sha, expected):
    """Host verifies browser-observed evidence against independent native scope."""
    if (type(frame) is not dict or set(frame) != {
            "turn", "known", "target", "visible", "withheld", "static",
            "query_sha", "clinical"}):
        raise ValueError("browser frontier frame fields changed")
    if (type(turn) is not int or turn < 0 or
            frame["turn"] != str(turn) or frame["known"] != known or
            frame["target"] != target or frame["query_sha"] != source_sha or
            frame["clinical"] != "NOT_EVALUATED"):
        raise ValueError("browser frame no longer refers to original temporal source")
    for key, expected_key in (
        ("visible", "temporal_ids"), ("withheld", "future_leakage_ids"),
        ("static", "static_snapshot_ids")):
        if frame[key] != ",".join(expected[expected_key]):
            raise ValueError(f"browser {key} disagrees with independently reconstructed scope")
    visible, withheld, static = (set(expected[k]) for k in (
        "temporal_ids", "future_leakage_ids", "static_snapshot_ids"))
    if not visible.isdisjoint(withheld) or visible | withheld != static:
        raise ValueError("temporal and withheld evidence do not partition static eligible evidence")
    return {
        "turn": turn, "known_at": known, "target_at": target,
        "visible_ids": sorted(visible), "future_withheld_ids": sorted(withheld),
        "static_ids": sorted(static),
        "source_program_sha256": source_sha,
        "independent_scope_agreement": True,
    }


def read_frame(page):
    panel = page.locator("#phase1-frontier")
    return {
        "turn": panel.get_attribute("data-turn"),
        "known": panel.get_attribute("data-known"),
        "target": panel.get_attribute("data-target"),
        "visible": panel.get_attribute("data-visible"),
        "withheld": panel.get_attribute("data-withheld"),
        "static": panel.get_attribute("data-static"),
        "query_sha": panel.get_attribute("data-query-sha"),
        "clinical": panel.get_attribute("data-clinical"),
    }


def check_sequence(frames, *, expected_cutover):
    if (type(frames) is not list or len(frames) < 3 or
            [r["turn"] for r in frames] != list(range(len(frames)))):
        raise ValueError("every original real game turn must have a distinct observed frame")
    if type(expected_cutover) is not int or not 1 <= expected_cutover < len(frames):
        raise ValueError("source game cutover outside actual frame observations")
    if not any(x["future_withheld_ids"] for x in frames[:expected_cutover]):
        raise ValueError("no future-hidden evidence before original game cutover")
    if any(x["future_withheld_ids"] for x in frames[expected_cutover:]):
        raise ValueError("original source did not reveal evidence after cutover")
    for left, right in zip(frames, frames[1:]):
        if left["target_at"] != right["target_at"]:
            raise ValueError("world sequence changed valid target during monotonicity trial")
        if left["known_at"] > right["known_at"]:
            raise ValueError("world knowledge cutoff regressed")
        if not set(left["visible_ids"]).issubset(right["visible_ids"]):
            raise ValueError("evidence visibility not monotone across same static source")
        if set(left["static_ids"]) != set(right["static_ids"]):
            raise ValueError("original world unexpectedly replaced source/valid target")
    return True


def run_world(*, data_dir, output_dir, parent=original_twelve):
    from playwright.sync_api import sync_playwright

    data, out = Path(data_dir), Path(output_dir)
    data.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    native = parent(data_dir=data, output_dir=out)
    if (native["native_jobs"] != 12 or
            native["NIH_P2_BENCHMARK"] != "WITNESSED" or
            native["NIH_P2_TEST"] != "WITNESSED" or
            native["synthetic_only"] is not True):
        raise ValueError("original twelve-job phase 2 world is not native-witnessed")
    for jid in (PROTOTYPE_JOB, OBSERVATION_JOB, BENCHMARK_JOB):
        if reverify_job(data_dir=data, job_id=jid)["status"] != "COMPLETE":
            raise ValueError("source-owned original witness changed")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
    if len(runtime.snapshot()) != 12:
        raise ValueError("new experiment would invent a native job")
    scope = validate_scope(runtime.get("nih-scope-001").inputs)
    proto = runtime.state(PROTOTYPE_JOB).output["prototype"]
    source = proto["python_source"]
    program_sha = digest(source)
    file_map = {
        name: (out / name).read_text(encoding="utf8")
        for name in (
            "temporal-game.html", "temporal_bridge_server.py",
            "temporal_query.py", "temporal_dataset.json",
            "game-temporal-config.json",
        )
    }
    if file_map["temporal_query.py"] != source:
        raise ValueError("original emitted program file disagrees with native source owner")
    if json.loads(file_map["temporal_dataset.json"])["observations"] != scope["observations"]:
        raise ValueError("original game dataset changed from original Phase 1 scope")
    if file_map["temporal_game.html"] if False else False:
        raise AssertionError("unreachable")
    config = json.loads(file_map["game-temporal-config.json"])
    if config.get("synthetic") is not True:
        raise ValueError("browser game is not synthetic")
    plan = runtime.state(GAME_JOB).output["build"]["plan"]
    if not isinstance(plan, list) or not 2 <= len(plan) <= 30:
        raise ValueError("bounded actual playable route required")
    timepoints = (config["known_at_before"], config["known_at_after"])
    if timepoints[0] >= timepoints[1]:
        raise ValueError("world cutover must advance knowledge")
    before = {name: (data / name).read_bytes() for name in (
        "runtime.jsonl", "coordinator-windows.jsonl")}
    parent_log = (out / "game-temporal-query-events.jsonl").read_bytes()
    frames = []
    with TemporaryDirectory(prefix="phase1-world-frontier-") as temporary:
        root = Path(temporary)
        for name, content in file_map.items():
            (root / name).write_text(
                overlay_html(content) if name == "temporal-game.html" else content,
                encoding="utf8")
        server = subprocess.Popen(
            [sys.executable, "-I", str(root / "temporal_bridge_server.py"),
             str(root), "0"],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            port = server.stdout.readline().strip()
            if not port.isdecimal():
                raise ValueError("original loopback server did not start")
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    def witness(turn):
                        known = timepoints[1] if turn >= config["cutover_turn"] else timepoints[0]
                        page.wait_for_function(
                            "document.querySelector('#phase1-frontier')?.dataset.turn === "
                            + json.dumps(str(turn)), timeout=15000)
                        page.wait_for_function(
                            "document.querySelector('#temporal-panel')?.dataset.turn === "
                            + json.dumps(str(turn)), timeout=15000)
                        observed = read_frame(page)
                        expected = oracle(scope, json.loads(file_map["temporal_dataset.json"])[
                            "functional_predicates"], known=known, target=config["target_at"])
                        result = check_frame(
                            observed, turn=turn, known=known, target=config["target_at"],
                            source_sha=program_sha, expected=expected)
                        if (page.locator("#temporal-panel").get_attribute("data-query-sha") !=
                                program_sha):
                            raise ValueError("original game client did not call original Python")
                        frames.append(result)
                    witness(0)
                    for i, action in enumerate(plan, 1):
                        if action not in ("up", "down", "left", "right", "interact"):
                            raise ValueError("original path uses unsupported action")
                        page.locator("#" + action).click()
                        witness(i)
                    if page.locator("body").get_attribute("data-solved") != "true":
                        raise ValueError("playable W13 original world was not solved")
                    page.screenshot(path=str(out / "nih-phase1-frontier-live-world.png"),
                                    full_page=True)
                finally:
                    browser.close()
        finally:
            server.terminate()
            try:
                server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate()
        generated_log = root / "game-temporal-query-events.jsonl"
        events = [json.loads(line) for line in generated_log.read_text().splitlines()]
        if len(events) < len(frames):
            raise ValueError("real game issued too few original Python requests")
        for frame in frames:
            if not any(e["turn"] == frame["turn"] and
                       e["result"]["prototype_sha256"] == program_sha and
                       e["result"]["temporal_ids"] == frame["visible_ids"] and
                       e["result"]["future_leakage_ids"] == frame["future_withheld_ids"]
                       for e in events):
                raise ValueError("browser frame not backed by logged original executable call")
        # Additional same-source boundaries execute unchanged native executable,
        # independently compared with the Phase 1 scope oracle.
        comparisons = []
        for known in ("2026-01-04", "2026-01-05", "2026-01-06"):
            for target in ("2026-01-04", "2026-01-10", "2026-01-11"):
                query = {"known_at": known, "target_at": target}
                actual = invoke(root / "temporal_query.py",
                                root / "temporal_dataset.json", query)
                expected = oracle(
                    scope,
                    json.loads(file_map["temporal_dataset.json"])["functional_predicates"],
                    known=known, target=target)
                if actual != expected:
                    raise ValueError("real original temporal Python diverged from independent scope")
                comparisons.append({"query": query, "exact_match": True,
                                    "temporal_ids": actual["temporal_ids"],
                                    "withheld_future_ids": actual["future_leakage_ids"],
                                    "outside_validity_ids": actual["outside_validity_ids"]})
        (out / "nih-phase1-frontier-world.html").write_text(
            (root / "temporal-game.html").read_text(), encoding="utf8")
    check_sequence(frames, expected_cutover=config["cutover_turn"])
    if ({name: (data / name).read_bytes() for name in before} != before or
            (out / "game-temporal-query-events.jsonl").read_bytes() != parent_log):
        raise ValueError("the research overlay altered original native journals or browser history")
    report = {
        "schema": SCHEMA, "original_native_jobs": 12,
        "original_NIH_P2_BENCHMARK": "WITNESSED",
        "original_NIH_P1_PACKET": "PARENT_WITNESSED_IN_NATIVE_GRAPH",
        "original_temporal_program_sha256": program_sha,
        "original_world_html_sha256": digest(file_map["temporal-game.html"]),
        "original_runtime_journal_sha256": digest(before["runtime.jsonl"]),
        "original_browser_log_sha256": digest(parent_log),
        "actual_world_actions": len(plan),
        "browser_frames": frames,
        "new_actual_python_query_log_entries": len(events),
        "additional_boundary_queries": comparisons,
        "browser_world_solved": True,
        "independent_scope_oracle_agreed": True,
        "future_evidence_withheld_then_revealed": True,
        "fixed_source_knowledge_monotonicity_observed": True,
        "historical_publication_time_authenticated": False,
        "synthetic_only": True, "clinical_verdict": "NOT_EVALUATED",
        "new_native_job_created": False, "new_NIH_checkpoint_claimed": False,
        "official_NIH_submission": False,
    }
    (out / "nih-phase1-original-world-frontier.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_world(data_dir=args.data_dir, output_dir=args.output_dir)
    print(json.dumps({
        "schema": result["schema"], "native_jobs": result["original_native_jobs"],
        "world_actions": result["actual_world_actions"],
        "actual_python_queries": result["new_actual_python_query_log_entries"],
        "extra_oracle_checks": len(result["additional_boundary_queries"]),
        "NIH_submission": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
