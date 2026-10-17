"""Source-owned bounded BUILD of playable game -> *actual* temporal Python API."""
import json
import os
import sys

CLIENT = r'''
<script id="native-temporal-client">
(()=>{
 const panel=document.createElement("section");
 panel.id="temporal-panel";
 panel.style.cssText="background:#17314a;border:2px solid #3e90a6;border-radius:12px;padding:14px;margin:20px 0";
 panel.innerHTML='<h2>Temporal Witness · game turn</h2><p id="temporal-status">Checking temporal source…</p><p id="temporal-evidence"></p>';
 document.querySelector("#grid").insertAdjacentElement("afterend",panel);
 let sequence=0;
 async function update(){
   const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
   const token=++sequence;
   const res=await fetch("/api/query?turn="+encodeURIComponent(turn),{cache:"no-store"});
   if(!res.ok)throw new Error("temporal source did not return");
   const answer=await res.json();
   if(token!==sequence)return;
   document.querySelector("#temporal-status").textContent="Turn "+turn+" · Known at "+answer.known_at;
   document.querySelector("#temporal-evidence").textContent=
     "Known: "+(answer.temporal_ids.join(", ")||"none")+
     " | Static view: "+(answer.static_snapshot_ids.join(", ")||"none")+
     " | Future leakage: "+(answer.future_leakage_ids.join(", ")||"none");
   panel.dataset.known=answer.known_at;
   panel.dataset.visible=answer.temporal_ids.join(",");
   panel.dataset.leakage=answer.future_leakage_ids.join(",");
   panel.dataset.querySha=answer.prototype_sha256;
   panel.dataset.turn=String(turn);
 }
 for(const action of ["up","down","left","right","interact","reset"])
   document.querySelector("#"+action).addEventListener("click",()=>{update().catch(e=>{panel.dataset.error=e.message;});});
 document.addEventListener("keyup",()=>update().catch(e=>{panel.dataset.error=e.message;}));
 update().catch(e=>{panel.dataset.error=e.message;});
})();
</script>
'''

SERVER = '''"""Generated loopback-only HTTP bridge calls the REAL built temporal Python CLI."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import hashlib, json, subprocess, sys

def serve(root, port):
    root = Path(root).resolve()
    html = (root/"temporal-game.html").read_bytes()
    source = (root/"temporal_query.py")
    dataset = (root/"temporal_dataset.json")
    config = json.loads((root/"game-temporal-config.json").read_text())
    assert source.is_file() and dataset.is_file() and config["synthetic"] is True
    program_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            if url.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
            if url.path != "/api/query":
                self.send_error(404)
                return
            try:
                params = parse_qs(url.query)
                if set(params)!={"turn"} or len(params["turn"])!=1:
                    raise ValueError("one turn required")
                value=params["turn"][0]
                if not value.isdecimal() or len(value)>6 or int(value)>100:
                    raise ValueError("invalid turn")
                turn=int(value)
                knowledge = (config["known_at_after"] if turn>=config["cutover_turn"]
                             else config["known_at_before"])
                req={"known_at":knowledge,"target_at":config["target_at"]}
                ran=subprocess.run([sys.executable,"-I",str(source),str(dataset)],
                      input=json.dumps(req),capture_output=True,text=True,
                      cwd=root,timeout=4,check=False)
                if ran.returncode!=0 or len(ran.stdout)>12000:
                    raise ValueError("actual temporal CLI rejected source query")
                result=json.loads(ran.stdout)
                if result["known_at"] != knowledge:
                    raise ValueError("CLI contradicted source event time")
                result["prototype_sha256"]=program_hash
                body=json.dumps(result,sort_keys=True).encode()
                with (root/"game-temporal-query-events.jsonl").open("a") as fp:
                    fp.write(json.dumps({"turn":turn,"request":req,
                                         "result":result},sort_keys=True)+"\\n")
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Cache-Control","no-store")
                self.send_header("Content-Length",str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (ValueError,KeyError,TypeError,subprocess.TimeoutExpired):
                self.send_error(400)
        def log_message(self,*args):
            pass
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print(server.server_port,flush=True)
    server.serve_forever()

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("expected root and port")
    serve(sys.argv[1],int(sys.argv[2]))
'''

def build(data):
    required={"world","game_html","temporal_source","temporal_dataset",
              "game_html_sha256","prototype_source_sha256","plan","request"}
    if type(data) is not dict or set(data)!=required:
        raise ValueError("game temporal source needs original game and prototype")
    request=data["request"]
    if type(request) is not dict or set(request)!={
        "kind","synthetic","cutover_turn","known_at_before",
        "known_at_after","target_at"}:
        raise ValueError("invalid game temporal WORLD experiment")
    if request["kind"]!="synthetic-live-game-temporal-join/v1" or request["synthetic"] is not True:
        raise ValueError("no clinical or external data supported")
    if type(request["cutover_turn"]) is not int or not 1<=request["cutover_turn"]<=20:
        raise ValueError("invalid source event cutover")
    html=data["game_html"]
    if type(html) is not str or html.count("</body>")!=1 or "id=\"grid\"" not in html:
        raise ValueError("not the built playable game")
    if type(data["temporal_source"]) is not str or type(data["temporal_dataset"]) is not str:
        raise ValueError("temporal executable sources not provided")
    return {
      "kind":"game-temporal-live-bundle/v1",
      "html":html.replace("</body>", CLIENT+"</body>"),
      "server_source":SERVER,
      "temporal_source":data["temporal_source"],
      "temporal_dataset":data["temporal_dataset"],
      "config":{"synthetic":True,"cutover_turn":request["cutover_turn"],
                "known_at_before":request["known_at_before"],
                "known_at_after":request["known_at_after"],
                "target_at":request["target_at"]},
      "source_game_sha256":data["game_html_sha256"],
      "source_temporal_sha256":data["prototype_source_sha256"],
    }

if __name__=="__main__":
    try:
        incoming=sys.stdin.read(140001)
        if len(incoming)>140000: raise ValueError("oversized source input")
        print(json.dumps({"bundle":build(json.loads(incoming)),"pid":os.getpid()},sort_keys=True))
    except (ValueError,KeyError,TypeError) as e:
        print(str(e),file=sys.stderr)
        raise SystemExit(2)
