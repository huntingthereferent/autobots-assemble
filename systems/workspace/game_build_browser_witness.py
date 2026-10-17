"""Real Chromium WITNESS returns the generated game result to its native handoff.

Separate from BUILD's native verifier; no browser result is inferred from tests
or a green workflow status. Uses the actually emitted playable artifact.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from .controls import reverify_job
from .game_build_stack import JOB_ID
from .game_build_native import verify_build

EVENT = "GAME_BUILD_BROWSER_WITNESS_RETURNED"


def witness(*, data_dir: Path, output_dir: Path):
    from playwright.sync_api import sync_playwright
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    runtime = HandoffRuntime(event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
    job = runtime.get(JOB_ID)
    if job.metadata.get("stack_role") != "BUILD":
        raise ValueError("not a native WORLD/BUILD job")
    reverify_job(data_dir=data_dir, job_id=JOB_ID)
    build = runtime.state(JOB_ID).output["build"]
    proof = verify_build(job.inputs, build)
    html = output_dir / "built-world-room.html"
    if (not html.is_file() or html.is_symlink() or
            sha256(html.read_bytes()).hexdigest() != proof["html_sha256"]):
        raise ValueError("playable artifact does not match source-owned BUILD output")
    with sync_playwright() as browser_api:
        browser = browser_api.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(html.resolve().as_uri())
            spec = job.inputs["spec"]
            if (page.locator("#grid .tile").count() != spec["width"] * spec["height"]
                    or page.locator("body").get_attribute("data-solved") != "false"):
                raise ValueError("built browser geometry does not match WORLD")
            # Test an authentic reset before replaying the worker's W12-verified plan.
            page.locator("#reset").click()
            if page.locator("#turns").inner_text() != "Turns: 0":
                raise ValueError("built browser reset failed")
            for action in build["plan"]:
                page.locator("#" + action).click()
            if (page.locator("body").get_attribute("data-solved") != "true"
                    or "WORLD COMPLETE" not in page.locator("#status").inner_text()
                    or page.locator("#turns").inner_text() !=
                        "Turns: " + str(len(build["plan"]))):
                raise ValueError("actual newly built room failed Chromium gameplay")
            page.screenshot(path=str(output_dir / "built-world-browser-witness.png"),full_page=True)
        finally:
            browser.close()
    payload = {
        "job_id": JOB_ID,
        "html_sha256": proof["html_sha256"],
        "WORLD": job.inputs["world_id"],
        "browser": "chromium-played-real-generated-artifact",
        "W12_native_reverified": True,
        "controls": len(build["plan"]),
        "solved": True,
        "result_scope": "this bounded playable room only",
    }
    prior = [e for e in runtime.event_store.for_handoff(JOB_ID) if e.event_type == EVENT]
    if prior:
        if len(prior) != 1 or prior[0].data != payload:
            raise ValueError("conflicting browser witness return for this job")
        new = False
    else:
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=JOB_ID, event_type=EVENT, actor_id="independent-chromium-witness",
            data=payload,
            parents=(runtime.state(JOB_ID).last_event_id,),
        ))
        new = True
    result = {**payload, "native_journal_browser_return_recorded": True,
              "new_browser_event": new}
    (output_dir / "browser-witness.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    print(json.dumps(result, sort_keys=True))
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    a=p.parse_args(argv)
    witness(data_dir=a.data_dir,output_dir=a.output_dir)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
