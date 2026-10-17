"""Source-owned bounded BUILD worker. Generates NEW playable room content from WORLD."""
import json
import re
import sys
from collections import deque

CONTRACT = "game-built-room-v1"
ORDER = ("right", "down", "left", "up", "interact")


def validate(world):
    if type(world) is not dict or set(world) != {"contract", "world_id", "spec"}:
        raise ValueError("invalid WORLD build contract")
    if world["contract"] != CONTRACT or type(world["world_id"]) is not str or not re.fullmatch(r"[a-z][a-z0-9-]{0,25}", world["world_id"]):
        raise ValueError("invalid WORLD identity")
    spec = world["spec"]
    if type(spec) is not dict or set(spec) != {"width", "height", "start", "target"}:
        raise ValueError("invalid WORLD geometry")
    w, h = spec["width"], spec["height"]
    if type(w) is not int or type(h) is not int or not (3 <= w <= 9 and 3 <= h <= 9):
        raise ValueError("invalid room dimensions")
    for key in ("start", "target"):
        v = spec[key]
        if type(v) is not list or len(v) != 2 or any(type(x) is not int for x in v) or not (0 <= v[0] < w and 0 <= v[1] < h):
            raise ValueError("invalid room coordinate")
    if spec["start"] == spec["target"]:
        raise ValueError("player overlaps collectible")
    return world


def solve(spec):
    w, h = spec["width"], spec["height"]
    tx, ty = spec["target"]
    start = (*spec["start"], False)
    queue = deque([(start, ())])
    seen = {start}
    while queue:
        (x, y, collected), seq = queue.popleft()
        if collected:
            return list(seq)
        for action in ORDER:
            xx, yy = x, y
            got = collected
            if action == "interact":
                got = collected or abs(tx-x)+abs(ty-y) == 1
            else:
                dx, dy = {"right": (1,0), "down": (0,1), "left": (-1,0), "up": (0,-1)}[action]
                xx, yy = x + dx, y + dy
                if not (0 <= xx < w and 0 <= yy < h):
                    xx, yy = x, y
            next_state = (xx, yy, got)
            if next_state not in seen:
                seen.add(next_state)
                queue.append((next_state, seq + (action,)))
    raise ValueError("no path to collectible")


def render(world):
    # WORLD's fields were bounded before embedding JSON in the page.
    world_json = json.dumps(world, sort_keys=True, separators=(",", ":"))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WORLD ROOM — built by workstation</title>
<style>
:root{color-scheme:dark;font:16px system-ui;background:#101826;color:#e7f4ff}
body{max-width:720px;margin:0 auto;padding:24px}
h1{letter-spacing:-.035em}p{color:#b7cce1}
#grid{display:grid;gap:5px;max-width:520px;margin:20px 0}
.tile{aspect-ratio:1;border-radius:9px;display:grid;place-items:center;
background:#24394d;border:1px solid #456077;font-size:1.45em}
.player{background:#24669c}.treasure{background:#90652e}
button{border:1px solid #729ac2;background:#1e3953;color:#fff;border-radius:8px;
padding:12px;min-width:90px;cursor:pointer;font:inherit}
button:hover{background:#326187}
#status{min-height:2em;font-weight:700;color:#b8f8ce}
.controls{display:flex;flex-wrap:wrap;gap:8px}
</style></head>
<body><h1>WORLD · Built Room</h1><p id="name"></p>
<p>Move with arrow keys or buttons. Interact next to the gold collectible (E).</p>
<div id="grid" aria-label="game board"></div>
<p id="status" role="status"></p><p id="turns"></p>
<div class="controls"><button id="up">↑ Up</button><button id="down">↓ Down</button>
<button id="left">← Left</button><button id="right">→ Right</button>
<button id="interact">Interact (E)</button><button id="reset">Reset (R)</button></div>
<script id="world-config" type="application/json">""" + world_json + """</script>
<script>
(()=>{'use strict';
const world=JSON.parse(document.getElementById('world-config').textContent);
const spec=world.spec;
let x,y,collected,turns;
const grid=document.getElementById('grid');
const status=document.getElementById('status');
function display(){
 grid.style.gridTemplateColumns='repeat('+spec.width+',1fr)';
 grid.replaceChildren();
 for(let yy=0;yy<spec.height;yy++)for(let xx=0;xx<spec.width;xx++){
  const cell=document.createElement('div');cell.className='tile';
  if(xx===x&&yy===y){cell.classList.add('player');cell.textContent='●'}
  else if(!collected&&xx===spec.target[0]&&yy===spec.target[1]){
   cell.classList.add('treasure');cell.textContent='◆'}
  cell.setAttribute('aria-label','cell-'+xx+'-'+yy);grid.append(cell);
 }
 status.textContent=collected?'WORLD COMPLETE — collectible recovered':'Explore and collect ◆';
 document.getElementById('turns').textContent='Turns: '+turns;
 document.body.dataset.solved=String(collected);
 document.body.dataset.position=x+','+y;
}
function reset(){[x,y]=spec.start;collected=false;turns=0;display()}
function step(action){
 if(collected)return;
 if(action==='interact'){
  if(Math.abs(x-spec.target[0])+Math.abs(y-spec.target[1])===1)collected=true;
 }else{
  const dir={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]}[action];
  if(!dir)return;
  const nx=x+dir[0],ny=y+dir[1];
  if(nx>=0&&ny>=0&&nx<spec.width&&ny<spec.height){x=nx;y=ny}
 }
 turns++;display();
}
for(const action of ['up','down','left','right','interact'])
 document.getElementById(action).addEventListener('click',()=>step(action));
document.getElementById('reset').addEventListener('click',reset);
const keys={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right',e:'interact',E:'interact',r:'reset',R:'reset'};
document.addEventListener('keydown',event=>{
 const action=keys[event.key];if(!action)return;event.preventDefault();
 if(action==='reset')reset();else step(action);
});
document.getElementById('name').textContent='Room: '+world.world_id;
reset();
})();
</script></body></html>
"""


def build(world):
    checked = validate(world)
    plan = solve(checked["spec"])
    return {"world": checked, "plan": plan, "html": render(checked),
            "build_contract": CONTRACT, "built_playable": True}


if __name__ == "__main__":
    try:
        source = sys.stdin.read(4097)
        if len(source) > 4096:
            raise ValueError("WORLD request too large")
        print(json.dumps(build(json.loads(source)), sort_keys=True))
    except (ValueError, TypeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
