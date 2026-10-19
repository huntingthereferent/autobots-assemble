"""Real Chromium source-owner (unchanged Trial09 iframe) + Trial10 enumeration."""
import argparse,json,threading
from pathlib import Path
from hashlib import sha256
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from systems.workspace.world_ab_active_set_trial import run
from systems.workspace.world_ab_two_contact_stress import run as prior
from network.tests.test_world_ab_active_set_trial import check
from network.tests.test_world_ab_two_contact_stress import check as check_prior
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE="docs/world_ab_active_set_trial.html"

def verify(output_dir):
    from playwright.sync_api import sync_playwright
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    native=run();check(native)
    original=prior();check_prior(original)
    handler=partial(SimpleHTTPRequestHandler,directory=str(ROOT))
    server=ThreadingHTTPServer(("127.0.0.1",0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={"width":1220,"height":840})
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto("http://127.0.0.1:"+str(server.server_port)+"/"+PAGE,wait_until="load")
                if page.evaluate("window.worldTrial10.receipt()") is not None:
                    raise ValueError("candidate prefilled without source experiment")
                page.frame_locator("#source").locator("#run").wait_for()
                page.locator("#run").click()
                actual=page.evaluate("window.worldTrial10.receipt()")
                if actual is None:
                    raise ValueError("browser experiment failed: "+page.locator("#status").inner_text()+" "+repr(errors))
                upstream=page.evaluate("window.worldTrial10.upstream()")
                if not source_equivalent(upstream,original):
                    raise ValueError("unaltered source page disagrees with original independent Trial09 Python")
                if not source_equivalent(actual,native):
                    if actual.get("counts")!=native["counts"]:
                        raise ValueError("classification counts mismatch: "+repr((actual.get("counts"),native["counts"])))
                    for i,(x,y) in enumerate(zip(actual.get("cases",[]),native["cases"])):
                        if not source_equivalent(x,y):
                            differences=[(k,x.get(k),y.get(k)) for k in x if not source_equivalent(x.get(k),y.get(k))]
                            raise ValueError("case "+str(i)+" browser/native disagreement: "+repr(differences)[:3000])
                    raise ValueError("source or experiment claims mismatched")
                for i in range(35):
                    page.locator("#case").select_option(str(i))
                    for k in range(3):
                        page.locator("#alternative").select_option(str(k))
                        if page.evaluate("window.worldTrial10.selected()")!={"case":i,"alternative":k,"frame":0}:
                            raise ValueError("displayed alternative inconsistent with source")
                page.locator("#case").select_option("16")
                page.locator("#alternative").select_option("0")
                for _ in range(30):page.locator("#next").click()
                if page.evaluate("window.worldTrial10.selected().frame")!=30:
                    raise ValueError("continuous observation frame was not reachable")
                if "physical outcome NOT determined" not in page.locator("#status").inner_text():
                    raise ValueError("ambiguity incorrectly reported resolved")
                page.screenshot(path=str(output_dir/"world_trial10_chromium.png"),full_page=True)
                (output_dir/"world_trial10_browser.json").write_text(json.dumps(actual,indent=2,sort_keys=True)+"\n")
                page.locator("#reset").click()
                if page.evaluate("window.worldTrial10.receipt()") is not None:
                    raise ValueError("reset kept a fabricated physical result")
                if errors:raise ValueError("Chromium page errors: "+repr(errors))
            finally:browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
    (output_dir/"world_trial10_native.json").write_text(json.dumps(native,indent=2,sort_keys=True)+"\n")
    result={"schema":"world-ab-active-set-browser-witness/v1",
            "source_trial09_unchanged":True,"all_35_active_sets_independently_replayed":True,
            "counts":native["counts"],"trial09_rejected_cases_with_local_alternatives":native["trial09_rejected_cases_with_local_alternatives"],
            "physical_active_contact_observed":False,"general_frictional_manifold_verified":False,
            "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (output_dir/"world_trial10_verification.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output-dir",required=True)
    verify(parser.parse_args().output_dir)
