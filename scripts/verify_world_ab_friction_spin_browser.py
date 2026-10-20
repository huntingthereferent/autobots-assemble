"""Real Chromium and independent Python finite friction-spin candidate comparison."""
import argparse,json,threading
from pathlib import Path
from hashlib import sha256
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from systems.workspace.world_ab_friction_spin_trial import run
from systems.workspace.world_ab_active_set_trial import run as prior
from systems.workspace.world_ab_two_contact_stress import run as stress
from network.tests.test_world_ab_friction_spin_trial import oracle
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE="docs/world_ab_friction_spin_trial.html"

def replay(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    native=run();oracle(native)
    parent=prior();upstream=stress()
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start();errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={"width":1230,"height":840})
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto("http://127.0.0.1:"+str(server.server_port)+"/"+PAGE,wait_until="load")
                if page.evaluate("typeof window.worldTrial12")!="object":
                    raise ValueError("Trial12 page parse failure: "+repr(errors))
                if page.evaluate("window.worldTrial12.receipt()") is not None:
                    raise ValueError("fabricated physics before source execution")
                page.wait_for_function("""() => {
                  const fr=document.getElementById('source')?.contentWindow;
                  return !!fr?.worldTrial10&&!!fr.document.getElementById('source')?.contentWindow?.worldTrial09;
                }""")
                page.locator("#run").click()
                actual=page.evaluate("window.worldTrial12.receipt()")
                if actual is None:raise ValueError("browser source/control failure: "+page.locator("#status").inner_text()+"; "+repr(errors))
                original_browser=page.evaluate("window.worldTrial12.upstream()")
                old_browser=page.evaluate("window.worldTrial12.parent()")
                original_subset={k:upstream[k] for k in (
                    "schema","original_source_geometry","incoming_angle_grid",
                    "surface_rotation_grid","speed","controlled_contact_lead",
                    "cases","counts","original_surface_modified",
                    "rotated_faces_are_original_source",
                    "general_two_contact_physics_proven","frictional_manifold_solved")}
                if not source_equivalent(original_browser,original_subset):
                    raise ValueError("unaltered source Trial09 Chromium diverged from Python")
                if not source_equivalent(old_browser,parent):
                    raise ValueError("unaltered Trial10 Chromium diverged from Python")
                if not source_equivalent(actual,native):
                    for i,(x,y) in enumerate(zip(actual.get("cases",[]),native["cases"])):
                        if not source_equivalent(x,y):
                            for j,(c,d) in enumerate(zip(x.get("options",[]),y.get("options",[]))):
                                if not source_equivalent(c,d):
                                    diffs=[(k,c.get(k),d.get(k)) for k in c if not source_equivalent(c.get(k),d.get(k))]
                                    raise ValueError("candidate case "+str(i)+" option "+str(j)+" mismatch "+repr(diffs)[:2100])
                            raise ValueError("case "+str(i)+" source or provenance mismatch")
                    raise ValueError("global comparison schema or count mismatch: "+repr((actual.get("by_parameter"),native["by_parameter"])))
                for case in range(35):
                    page.locator("#case").select_option(str(case))
                    for selection in range(12):
                        page.locator("#candidate").select_option(str(selection))
                        if page.evaluate("window.worldTrial12.selection()")!={"case":case,"candidate":selection,"frame":0}:
                            raise ValueError("browser selection changed source identity")
                page.locator("#case").select_option("16")
                page.locator("#candidate").select_option("0")
                for _ in range(30):page.locator("#next").click()
                if page.evaluate("window.worldTrial12.selection().frame")!=30:
                    raise ValueError("finite observation controls not working")
                if "NOT OBSERVED" not in page.locator("#status").inner_text():
                    raise ValueError("UI presents hypothesized contact as real event")
                page.screenshot(path=str(folder/"world_trial12_chromium.png"),full_page=True)
                (folder/"world_trial12_browser.json").write_text(json.dumps(actual,indent=2,sort_keys=True)+"\n")
                page.locator("#reset").click()
                if page.evaluate("window.worldTrial12.receipt()") is not None:
                    raise ValueError("reset retained phantom evidence")
                if errors:raise ValueError("real browser page errors: "+repr(errors))
            finally:browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
    (folder/"world_trial12_native.json").write_text(json.dumps(native,sort_keys=True,indent=2)+"\n")
    witness={"schema":"world-ab-friction-spin-chromium-witness/v1",
        "source_trial09_trial10_replayed_unchanged":True,
        "all_420_controls_independently_reconstructed":True,
        "by_parameter":native["by_parameter"],
        "frictional_simultaneous_contact_solved":False,
        "actual_active_contacts_measured":False,
        "physical_blueprint_generated":False,
        "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (folder/"world_trial12_verification.json").write_text(json.dumps(witness,indent=2,sort_keys=True)+"\n")
    print(json.dumps(witness,sort_keys=True))
    return witness

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",required=True)
    replay(ap.parse_args().output_dir)
