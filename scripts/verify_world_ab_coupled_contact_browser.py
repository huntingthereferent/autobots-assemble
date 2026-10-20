"""Real Chromium independently computes and selects all 1330 coupled modes."""
import argparse,json,threading
from pathlib import Path
from hashlib import sha256
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from systems.workspace.world_ab_coupled_contact_modes import run
from systems.workspace.world_ab_two_contact_stress import run as stress
from network.tests.test_world_ab_coupled_contact_modes import check
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE="docs/world_ab_coupled_contact_modes.html"

def verify(output_dir):
    from playwright.sync_api import sync_playwright
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    native=run();check(native)
    upstream=stress()
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={"width":1220,"height":850})
                page.on("pageerror",lambda error:errors.append(str(error)))
                page.goto("http://127.0.0.1:"+str(server.server_port)+"/"+PAGE,wait_until="load")
                if page.evaluate("typeof window.worldTrial13")!="object":
                    raise ValueError("Trial13 source failed to parse: "+repr(errors))
                if page.evaluate("window.worldTrial13.receipt()") is not None:
                    raise ValueError("Trial13 prefabricated physics without original source")
                page.wait_for_function("""() => !!document.getElementById('source')?.contentWindow?.worldTrial09""")
                page.locator("#run").click()
                actual=page.evaluate("window.worldTrial13.receipt()")
                if actual is None:
                    raise ValueError("Trial13 independent JS failed: "+page.locator("#status").inner_text()+" "+repr(errors))
                prior=page.evaluate("window.worldTrial13.upstream()")
                subset={k:upstream[k] for k in (
                    "schema","original_source_geometry","incoming_angle_grid","surface_rotation_grid",
                    "speed","controlled_contact_lead","cases","counts",
                    "original_surface_modified","rotated_faces_are_original_source",
                    "general_two_contact_physics_proven","frictional_manifold_solved")}
                if not source_equivalent(prior,subset):
                    raise ValueError("unchanged Trial09 Chromium source changed")
                if not source_equivalent(actual,native):
                    for i,(ac,ex) in enumerate(zip(actual.get("scenarios",[]),native["scenarios"])):
                        if not source_equivalent(ac,ex):
                            for j,(ag,eg) in enumerate(zip(ac.get("groups",[]),ex["groups"])):
                                if not source_equivalent(ag,eg):
                                    for k,(ao,eo) in enumerate(zip(ag["options"],eg["options"])):
                                        if not source_equivalent(ao,eo):
                                            fields=[(key,ao.get(key),eo.get(key)) for key in ao if not source_equivalent(ao.get(key),eo.get(key))]
                                            raise ValueError(f"native/Chromium mismatch case={i}, group={j}, mode={k}: "+repr(fields)[:2500])
                                    raise ValueError(f"group {i}/{j} differs")
                            raise ValueError(f"case {i} differs")
                    raise ValueError("global schema or aggregate mismatch "+repr((actual.get("aggregate"),native["aggregate"])))
                for i in range(35):
                    page.locator("#case").select_option(str(i))
                    for j in range(6):
                        page.locator("#parameter").select_option(str(j))
                        for k in range(len(native["scenarios"][i]["groups"][j]["options"])):
                            page.locator("#mode").select_option(str(k))
                            if page.evaluate("window.worldTrial13.selection()")!={"case":i,"parameter":j,"mode":k,"frame":0}:
                                raise ValueError("mode selection was not source bound")
                page.locator("#case").select_option("16")
                page.locator("#parameter").select_option("0")
                page.locator("#mode").select_option("0")
                for _ in range(30):page.locator("#next").click()
                if page.evaluate("window.worldTrial13.selection().frame")!=30:
                    raise ValueError("virtual motion cursor inoperable")
                if "PHYSICAL CONTACT NOT OBSERVED" not in page.locator("#status").inner_text():
                    raise ValueError("hypothesis promoted to physical event")
                page.screenshot(path=str(output_dir/"world_trial13_chromium.png"),full_page=True)
                (output_dir/"world_trial13_browser.json").write_text(json.dumps(actual,sort_keys=True,indent=2)+"\n")
                page.locator("#reset").click()
                if page.evaluate("window.worldTrial13.receipt()") is not None:
                    raise ValueError("reset retained a fictional result")
                if errors:raise ValueError("actual page errors "+repr(errors))
            finally:browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
    (output_dir/"world_trial13_native.json").write_text(json.dumps(native,sort_keys=True,indent=2)+"\n")
    result={"schema":"world-ab-coupled-modes-chromium-witness/v1",
       "original_trial09_source_replayed_unchanged":True,
       "all_1330_modes_independently_computed":True,
       "aggregate":native["aggregate"],
       "material_collision_measured":False,
       "simultaneous_friction_manifold_proven":False,
       "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (output_dir/"world_trial13_verification.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    verify(p.parse_args().output_dir)
