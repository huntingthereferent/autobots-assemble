"""Opening profile motion from original A/B math and workstation research.

No inventory orbits, unrelated-domain joins, money-job counters, fabricated
live feeds or supposed universal referent. Every state label is computed from
the original finite source and replayed independently.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

from work.arc_like_maze.math import World
from systems.workspace.ab_relational_cluster import _independent_step
from systems.workspace.research_observatory import research_snapshot

ROOT=Path(__file__).resolve().parents[2]
MOTION=Path(__file__).resolve().parent

def native_paths():
    # Use source-built witness, not a user-selected decorative endpoint.
    from views.motion.convergence import discover_convergence
    result=discover_convergence()
    if result.get("status")=="OPEN":
        raise ValueError("original native trace has no convergence witness")
    world=World(3,(0,1,2))
    routes=[]
    for key in ("left_word","right_word"):
        word=result[key]
        state=world.origin
        path=[list(state)]
        for action in word:
            dst=world.step(state,action)
            if dst!=_independent_step(state,action):
                raise ValueError("independent native verification failed")
            state=dst
            path.append(list(state))
        if path[-1]!=result["target"]:
            raise ValueError("trace receipt source mismatch")
        routes.append({"actions":word,"states":path})
    return {"target":result["target"],"routes":routes,
            "explored":result["states_explored"],
            "source":result["source"],"witness":result["witness"]}


def snapshot():
    return {"research":research_snapshot(),
            "native":native_paths()}


def txt(x,y,value,size=13,color="#cfe4f0",weight="",spacing="",anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight or "normal"}" letter-spacing="{spacing or "0"}" '
            f'text-anchor="{anchor}">{escape(str(value))}</text>')


def dashboard(data):
    if set(data)!={"research","native"} or data["research"].get("schema")!="workstation-research-continuity/v1":
        raise ValueError("workstation source projection is required")
    paths=data["native"]["routes"]
    if len(paths)!=2 or any(len(p["states"])!=len(p["actions"])+1 for p in paths):
        raise ValueError("incorrect original paths")
    target=data["native"]["target"]
    if paths[0]["states"][-1]!=target or paths[1]["states"][-1]!=target:
        raise ValueError("animated meeting not present in source")
    totals=data["research"]["totals"]
    css="""text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
    .signal{stroke-dasharray:10 25;animation:flow 5.1s linear infinite}
    .lower{animation-duration:7.3s;animation-delay:-2.2s}
    .endpoint{transform-origin:1010px 351px;animation:pulse 3.4s ease-in-out infinite}
    .horizon{animation:fade 6s ease-in-out infinite}
    .gridline{animation:fade 9s ease-in-out infinite}
    .reveal{animation:enter 1.25s cubic-bezier(.2,.7,.2,1) both}
    .delayed{animation-delay:.5s}
    @keyframes flow{to{stroke-dashoffset:-175}}
    @keyframes pulse{50%{opacity:.5;transform:scale(1.21)}}
    @keyframes fade{50%{opacity:.35}}
    @keyframes enter{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
    @media(prefers-reduced-motion:reduce){*{animation:none!important;transform:none!important}}"""
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="740" viewBox="0 0 1200 740" role="img" aria-labelledby="title desc">',
       '<title id="title">Hunting the Referent — witnessed paths through a mathematical world</title>',
       '<desc id="desc">Finite source-verified paths '+escape(paths[0]["actions"])+' and '+escape(paths[1]["actions"])+' meet at '+escape(str(target))+'. Source-recorded research movements and walls follow the original workstation research observer. This is a finite mathematical observation, not a claim about all external sources.</desc>',
       '<defs><radialGradient id="depth"><stop stop-color="#132A43"/><stop offset=".5" stop-color="#0B172B"/><stop offset="1" stop-color="#050B17"/></radialGradient>',
       '<linearGradient id="trail"><stop stop-color="#3ECDE9" stop-opacity=".15"/><stop offset=".57" stop-color="#53E0F5"/><stop offset="1" stop-color="#A6EFFF"/></linearGradient>',
       '<linearGradient id="violet"><stop stop-color="#7351D9" stop-opacity=".15"/><stop offset="1" stop-color="#B4A3FF"/></linearGradient>',
       '<radialGradient id="glow"><stop stop-color="#5CE4FA" stop-opacity=".30"/><stop offset="1" stop-color="#5CE4FA" stop-opacity="0"/></radialGradient>',
       '<pattern id="mesh" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0V34" stroke="#41607D" stroke-opacity=".14" fill="none"/></pattern></defs>',
       '<style>'+css+'</style>',
       '<rect width="1200" height="740" rx="16" fill="url(#depth)"/>',
       '<rect width="1200" height="740" rx="16" fill="url(#mesh)"/>',
       '<rect x="12" y="12" width="1176" height="716" rx="11" fill="none" stroke="#41627D" stroke-opacity=".7"/>',
       '<path d="M40 58H1160" stroke="#37566D" opacity=".7"/>',
       txt(39,39,"SOURCE  /  RELATION  /  CONTINUATION",13,"#70DFF1","bold",1.4),
       '<circle class="horizon" cx="1127" cy="35" r="6" fill="#61D8E9"/>',
       '<g class="reveal">',
       txt(46,155,"HUNTING",73,"#F3F8FF","bold",-2),
       txt(46,233,"THE REFERENT",71,"#DCF1FF","bold",-2),
       txt(50,281,"Follow the movement.",23,"#96D9E9"),
       txt(50,310,"Keep the difference.",23,"#B9A7F2"),
       txt(50,351,"Language / Mathematics / Witness / Continuity",14,"#B2C5D9"),
       '</g>',
       '<circle cx="1010" cy="351" r="150" fill="url(#glow)"/>',
       '<circle cx="1010" cy="351" r="73" fill="none" stroke="#46677F" stroke-dasharray="4 12"/>',
       '<circle cx="1010" cy="351" r="43" fill="none" stroke="#5BC7EA" stroke-opacity=".43"/>',
       '<circle class="endpoint" cx="1010" cy="351" r="16" fill="#5DD8EC" fill-opacity=".28" stroke="#59DCED"/>',
       '<circle cx="1010" cy="351" r="5" fill="#D3FDFF"/>',
       txt(1010,294,"SAME VERIFIED STATE",12,"#8BDFEE","bold",.4,"middle"),
       txt(1010,414,"("+",".join(map(str,target))+")",24,"#F3F9FF","bold",0,"middle"),
       txt(710,180,"THE PATHS WERE NOT CHOSEN TO MEET",12,"#ABBCD0","",.4,"middle"),
    ]
    # The cinematic routes are illustrations of two independently verified
    # native action sequences. No unverified branch/world source is drawn.
    routes=[("M555 366C670 195 800 205 888 290S966 340 1010 351","#62E4F5",""),
            ("M555 366C675 520 793 514 891 408S973 362 1010 351","#A899FA","lower")]
    for i,((d,col,cls),route) in enumerate(zip(routes,paths)):
        p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="13" stroke-opacity=".09"/>')
        p.append(f'<path class="signal {cls}" d="{d}" fill="none" stroke="{col}" stroke-width="3.4"/>')
        p.append(txt(690,235 if i==0 else 494,
                     route["actions"],22,col,"bold",1))
        p.append(txt(675,255 if i==0 else 516,
                     "verified from native A/B steps",11,"#899FB7"))
    p.extend([
       '<circle cx="555" cy="366" r="7" fill="#DCF0FC"/>',
       txt(548,396,"ORIGIN (0,0,0)",11,"#C9DAE6",anchor="middle"),
       '<path d="M45 559H1155" stroke="#40607A"/>',
       '<g class="reveal delayed">',
       txt(48,589,"ORIGINAL RESEARCH  /  SOURCE-OWNED",13,"#80C7E7","bold",1.2),
       txt(49,621,"Moves, walls, corrections and unfinished relations remain inspectable.",16,"#D3E4EE"),
       txt(49,647,"The workstation indexes the full available repository source, without inventing past events.",12,"#8DA8C4"),
       '</g>',
       '<path d="M45 671H1155" stroke="#29475E"/>',
       txt(49,706,str(totals["structured_records"])+" STRUCTURED RECORDS",13,"#74D9EA","bold",.2),
       txt(419,706,str(totals["explicit_move_states"])+" EXPLICIT MOVES",13,"#A2CFF1","bold",.2),
       txt(734,706,str(totals["explicit_wall_entries"])+" RECORDED WALLS",13,"#C2B7FA","bold",.2),
       txt(1144,706,"SOURCE SUBSET",11,"#789AB4",anchor="end"),
       "</svg>"
    ])
    svg="".join(p)
    ET.fromstring(svg)
    return svg


def generate(out:MOTION.__class__=MOTION):
    svg=dashboard(snapshot())
    if "<script" in svg or "<image" in svg or "href=" in svg:
        raise ValueError("SVG must be stand-alone")
    out.mkdir(parents=True,exist_ok=True)
    (out/"atlas-dashboard.svg").write_text(svg+"\n",encoding="utf-8")
    return svg


if __name__=="__main__":
    generate()
    print("Source-native A/B trace and research continuity generated; no catalog joins.")
