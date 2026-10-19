"""WORLD Trial 11: real Chromium, unchanged Trial 10/09 nested originals."""
import argparse,json,threading
from pathlib import Path
from hashlib import sha256
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from systems.workspace.world_ab_contact_discrimination import run
from systems.workspace.world_ab_active_set_trial import run as prior
from network.tests.test_world_ab_contact_discrimination import check
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE="docs/world_ab_contact_discrimination.html"

def replay(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    native=run();check(native)
    parent=prior()
    http=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    t=threading.Thread(target=http.serve_forever,daemon=True);t.start()
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={"width":1250,"height":890})
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto("http://127.0.0.1:"+str(http.server_port)+"/"+PAGE,wait_until="load")
                if page.evaluate("typeof window.worldTrial11")!="object":
                    raise ValueError("Trial11 JS failed: "+repr(errors))
                if page.evaluate("window.worldTrial11.receipt()") is not None:
                    raise ValueError("fake observation preloaded")
                page.wait_for_function("""() => {
                  let a=document.getElementById('original')?.contentWindow;
                  return !!a?.worldTrial10&&!!a.document.getElementById('source')?.contentWindow?.worldTrial09;
                }""")
                page.locator("#run").click()
                received=page.evaluate("window.worldTrial11.receipt()")
                if received is None:
                    raise ValueError("new browser research failed: "+page.locator("#status").inner_text()+" "+repr(errors))
                source=page.evaluate("window.worldTrial11.source()")
                if not source_equivalent(source,parent):
                    raise ValueError("unchanged Trial10 Chromium source disagrees with independent native Trial10")
                if not source_equivalent(received,native):
                    for i,(x,y) in enumerate(zip(received.get("cases",[]),native["cases"])):
                        if not source_equivalent(x,y):
                            details=[(k,x.get(k),y.get(k)) for k in x if not source_equivalent(x.get(k),y.get(k))]
                            raise ValueError("Trial11 case "+str(i)+" differs: "+repr(details)[:2300])
                    raise ValueError("Trial11 global source/claim mismatch: "+repr((received.get("counts"),native["counts"])))
                for i in range(35):
                    page.locator("#case").select_option(str(i))
                    for k in range(9):
                        page.locator("#sensor").select_option(str(k))
                        if page.evaluate("window.worldTrial11.selected()")!={"case":i,"sensor":k}:
                            raise ValueError("UI selected reading without evidence")
                page.locator("#case").select_option("16")
                page.locator("#sensor").select_option("8")
                if "NOT OBSERVED" not in page.locator("#status").inner_text():
                    raise ValueError("synthetic outcome misrepresented as observation")
                page.screenshot(path=str(folder/"world_trial11_chromium.png"),full_page=True)
                (folder/"world_trial11_browser.json").write_text(json.dumps(received,sort_keys=True,indent=2)+"\n")
                page.locator("#reset").click()
                if page.evaluate("window.worldTrial11.receipt()") is not None:
                    raise ValueError("reset retained a fictional measurement")
                if errors:raise ValueError("Chromium page errors "+repr(errors))
            finally:browser.close()
    finally:
        http.shutdown();http.server_close();t.join(timeout=5)
    (folder/"world_trial11_native.json").write_text(json.dumps(native,sort_keys=True,indent=2)+"\n")
    witness={"schema":"world-ab-contact-discrimination-chromium-witness/v1",
      "original_trial10_and_trial09_browser_replayed":True,
      "all_35_case_sensor_grids_agree":True,"counts":native["counts"],
      "real_physical_reading_present":False,"frictional_mu_point_four_solver_proven":False,
      "original_blueprint_generated":False,
      "sha256_native_canonical":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (folder/"world_trial11_verification.json").write_text(json.dumps(witness,indent=2,sort_keys=True)+"\n")
    print(json.dumps(witness,sort_keys=True))
    return witness

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--output-dir",required=True)
    replay(ap.parse_args().output_dir)
