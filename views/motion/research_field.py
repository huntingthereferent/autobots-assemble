"""A source-bound public movement field, not another opportunities dashboard.

This is a presentation of source-linked evidence from the original
workstation research observer. Parallel rails are NOT claimed to share a
mathematical referent. The only joined endpoints are independently checked
finite action words from the native F3 world.

GitHub-compatible CSS motion is visual pacing, not a live process monitor.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

from systems.workspace.research_observatory import ROOT, research_snapshot
from views.motion.atlas_dashboard import native_paths

OUT=ROOT/"views/motion"/"research-movement-field.svg"
WITNESS="systems/workspace/WITNESS_W13_INDEPENDENT_VERDICT.md"
LANGUAGE="language/SEPARATIONS.md"
COLORS=("#51E5F3","#A99CFF","#6DE2B8","#F2BC8F")


def _plain(value, n=110):
    if not isinstance(value,str):
        raise ValueError("unrecognized original text")
    return escape(value[:n],quote=True)


def snapshot():
    research=research_snapshot()
    records=research["source_records"]
    all_paths={p for section in research["sections"] for p in section["paths"]}
    dive=next((x for x in records if x["path"]=="research/dives/ARC3-TRACE-001/dive.json"),None)
    if not dive or dive["state"]!="MOVE_WITH_WALL" or not dive["walls"]:
        raise ValueError("no original ARC move-with-wall observation")
    experiments=sorted(
        (x for x in records if x["kind"]=="EXPERIMENT" and
         x["path"].startswith("research/dives/ARC3-TRACE-001/experiments/")),
        key=lambda x:x["path"])
    if not experiments or any(not x["state"] or x["state"]=="UNCLASSIFIED" for x in experiments):
        raise ValueError("no original experiment outcomes")
    cp=sorted(
        (x for x in records if x["kind"]=="CHECKPOINT" and x["path"].endswith(".json")),
        key=lambda x:x["path"])
    if len(cp)<2 or not all(x["state"]=="witnessed" for x in cp):
        raise ValueError("checkpoint receipts are not witnessed")
    for p in (WITNESS,LANGUAGE):
        if p not in all_paths:
            raise ValueError("source not indexed by workstation: "+p)
    w13=(ROOT/WITNESS).read_text(encoding="utf-8")
    finding=re.search(r"^\*\*Verdict:\*\*\s+\*\*(.+?)\*\*",w13,re.M)
    if not finding or "W13 PASS" not in finding.group(1):
        raise ValueError("W13 local witness document does not establish stated outcome")
    finite=native_paths()
    if len(finite["routes"])!=2 or finite["routes"][0]["states"][-1]!=finite["target"] or finite["routes"][1]["states"][-1]!=finite["target"]:
        raise ValueError("native finite paths have not met")
    return {"native":finite,"arc":dive,"experiments":experiments,
            "cp":cp,"w13":{"path":WITNESS,"verdict":finding.group(1)},
            "language":{"path":LANGUAGE,"scope":"Original correction record"},
            "research_schema":research["schema"]}


def text(x,y,label,size=14,color="#B5C8DD",bold=False,anchor="start",ls=0):
    return (f'<text x="{x}" y="{y}" font-family="ui-monospace,Consolas,monospace" '
            f'font-weight="{"700" if bold else "400"}" font-size="{size}" '
            f'letter-spacing="{ls}" text-anchor="{anchor}" fill="{color}">'
            +_plain(str(label),140)+"</text>")


def lane_line(x1,x2,y,color,cls="flow"):
    return (f'<path d="M{x1} {y}H{x2}" stroke="{color}" stroke-width="1.5" opacity=".37"/>'
            f'<path class="{cls}" d="M{x1} {y}H{x2}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')

def group_label(x,y,label,color,subtitle):
    return text(x,y,label,15,color,True,ls=1.3)+text(x,y+25,subtitle,11,"#7897B2")


def render(data):
    if data.get("research_schema")!="workstation-research-continuity/v1":
        raise ValueError("not the original workstation source")
    routes=data["native"]["routes"]
    if any(len(row["states"])!=len(row["actions"])+1 for row in routes):
        raise ValueError("step receipts invalid")
    cp=data["cp"]
    ex=data["experiments"]
    # Nonempty documented evidence; no invented activity counter.
    title="THE WORK IS MOVING"
    css="""text{font-family:ui-monospace,Consolas,monospace}
    .flow{stroke-dasharray:7 17;animation:drift 3.6s linear infinite}
    .slow{stroke-dasharray:7 17;animation:drift 5.8s linear infinite}
    .pulse{animation:pulse 3.6s ease-in-out infinite}
    .appear{animation:appear 1.3s ease-out both}
    .lag{animation-delay:.5s}
    .spark{animation:flicker 5s ease-in-out infinite}
    @keyframes drift{to{stroke-dashoffset:-144}}
    @keyframes pulse{50%{opacity:.34}}
    @keyframes appear{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
    @keyframes flicker{0%,100%{opacity:.35}50%{opacity:1}}
    @media(prefers-reduced-motion:reduce){*{animation:none!important}}
    """
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="920" viewBox="0 0 1280 920" role="img" aria-labelledby="title description">',
       '<title id="title">Hunting the Referent — observable research movements</title>',
       '<desc id="description">A research field showing an independently replayed finite A/B meeting, the original ARC-AGI-3 move-with-wall result and experiments, witnessed CP checkpoint records, and bounded W13 local verdict. Each rail preserves its own source boundaries; this is not live telemetry or a claim that independent sources converge.</desc>',
       '<defs><linearGradient id="sky" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#060B16"/><stop offset=".55" stop-color="#11213A"/><stop offset="1" stop-color="#070E1D"/></linearGradient>',
       '<linearGradient id="beam"><stop stop-color="#51E5F3" stop-opacity=".03"/><stop offset=".5" stop-color="#51E5F3" stop-opacity=".24"/><stop offset="1" stop-color="#A99CFF" stop-opacity=".02"/></linearGradient>',
       '<radialGradient id="aura"><stop stop-color="#67DFF5" stop-opacity=".29"/><stop offset="1" stop-color="#67DFF5" stop-opacity="0"/></radialGradient>',
       '<pattern id="mesh" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#6D8BA9" stroke-opacity=".12"/></pattern></defs>',
       '<style>'+css+'</style>',
       '<rect width="1280" height="920" rx="14" fill="url(#sky)"/>',
       '<rect width="1280" height="920" rx="14" fill="url(#mesh)"/>',
       '<path d="M22 22H1258V898H22Z" stroke="#4D6883" stroke-opacity=".53" fill="none"/>',
       '<path d="M44 69H1235" stroke="#4C7793" stroke-opacity=".75"/>',
       '<circle class="pulse" cx="1220" cy="45" r="5" fill="#62E0C9"/>',
       text(46,47,"HUNTING THE REFERENT   /   ORIGINAL SOURCE EVIDENCE",13,"#74E8F3",True,ls=1.3),
       '<g class="appear">',
       text(45,153,title,69,"#F0F8FF",True,ls=-2.8),
       text(48,193,"Move. Witness. Hit a wall. Keep the trace.",21,"#A6C7DA"),
       text(49,226,"Four source-grounded views of the same ongoing investigation — without invented joins.",12,"#8DADC6"),
       '</g>',
       '<path d="M44 261H1234" stroke="#3A6580"/>',
       text(46,290,"01   FINITE MATHEMATICS",15,COLORS[0],True,ls=1),
       text(1230,289,"NATIVE REPLAY + INDEPENDENT CHECK",12,"#94BFD8",anchor="end"),
       '<rect x="45" y="307" width="1189" height="175" rx="9" fill="#0B1729" stroke="#30526B"/>',
       '<circle cx="115" cy="395" r="80" fill="url(#aura)"/>',
       '<circle cx="115" cy="395" r="6" fill="#D9F8FF"/>',
       text(116,345,"ORIGIN",11,"#8FA7C4",anchor="middle"),
       text(116,454,"(0,0,0)",12,"#B7D7E9",anchor="middle"),
       '<circle class="pulse" cx="1045" cy="395" r="44" fill="url(#aura)"/>',
       '<circle cx="1045" cy="395" r="13" fill="#5ED4ED" fill-opacity=".23" stroke="#A0F5FF" stroke-width="2"/>',
       '<circle cx="1045" cy="395" r="5" fill="#E6FAFF"/>',
       text(1045,347,"SAME VERIFIED STATE",11,"#8FD9E6",anchor="middle"),
       text(1045,447,"("+",".join(map(str,data["native"]["target"]))+")",20,"#E8F8FF",True,anchor="middle"),
    ]
    # These are TWO original action sequences, not arbitrary invented destinations.
    for i,route in enumerate(routes):
        y=360 if i==0 else 430
        color=COLORS[i]
        segments=len(route["actions"])
        pts=[(160+(790*j/segments),y-22 if i==0 else y+22) for j in range(segments+1)]
        path=f'M115 395 Q148 {y} 160 {pts[0][1]} '+ " ".join(
            f'L{px:.1f} {py:.1f}' for px,py in pts[1:])
        path+=f' Q1000 {y} 1045 395'
        p.append(f'<path d="{path}" stroke="{color}" stroke-opacity=".18" stroke-width="10" fill="none"/>')
        p.append(f'<path class="{"flow" if i==0 else "slow"}" d="{path}" stroke="{color}" stroke-width="2.6" fill="none"/>')
        for j,(px,py) in enumerate(pts[1:-1],1):
            p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.8" stroke="{color}" fill="#071528"/>')
            p.append(text(f"{px:.1f}",f"{py-15 if i==0 else py+22:.1f}",
                          route["actions"][j-1],11,color,True,anchor="middle"))
        p.append(text(325,331 if i==0 else 471,
                      route["actions"]+" / "+str(len(route["actions"]))+" native steps",13,color,True))
    p.extend([
       text(1169,458,"ONE FINITE EXAMPLE",10,"#839EB6",anchor="end"),
       text(46,520,"02   ARC / CAUSAL REASONING",15,COLORS[1],True,ls=1),
       text(1230,520,_plain(data["arc"]["state"]),12,"#D0B7FF",anchor="end"),
       '<path d="M46 544H1233" stroke="#3C5978"/>',
       text(48,581,"OBSERVED SOURCE",12,"#809CB6",True),
       text(48,611,data["arc"]["title"],23,"#E9F2FF",True),
       text(48,637,str(len(data["arc"]["walls"]))+" original unresolved walls preserved",15,"#BE9FEA"),
       text(48,668,"EXPONENT? No: each result comes from a separate original experiment.",11,"#7F9FB6"),
       text(48,700,"SOURCE CONTRACT",11,"#728DA9"),
       text(48,725,"research/dives/ARC3-TRACE-001/dive.json",12,"#B0C9DF"),
       '<path d="M596 563V746" stroke="#31516D"/>',
       text(628,568,"EXPERIMENTS / ORIGINAL OUTCOMES",12,"#A6BBD0",True,ls=.4)
    ])
    ys=[603+i*27 for i in range(min(len(ex),6))]
    for i,(record,y) in enumerate(zip(ex[:6],ys)):
        color=COLORS[1] if "PARTIAL" in record["state"] else COLORS[0]
        p.append(f'<rect x="628" y="{y-13}" width="589" height="23" rx="5" fill="#122641" opacity=".55"/>')
        p.append(f'<circle cx="645" cy="{y-1}" r="3.5" fill="{color}"/>')
        p.append(text(659,y+4,re.search(r"FM-\d+",record["path"]).group(0),11,color,True))
        p.append(text(722,y+4,record["title"][:43],11,"#CDDDED"))
        p.append(text(1201,y+4,"PARTIAL" if "PARTIAL" in record["state"] else "RECORD",10,color,True,anchor="end"))
    p.extend([
       '<path d="M44 768H1234" stroke="#3A6580"/>',
       text(46,800,"03   CHECKPOINT CONTINUATION",14,COLORS[2],True,ls=.5),
       text(651,800,"04   GAME WORLD / W13",14,COLORS[3],True,ls=.5),
       '<path d="M626 791V886" stroke="#34526F"/>',
    ])
    cp_small=cp[-4:]
    for i,record in enumerate(cp_small):
        x=61+i*137
        p.append(f'<rect x="{x}" y="818" width="125" height="51" rx="8" fill="#112C36" stroke="#338A7E" stroke-opacity=".7"/>')
        p.append(text(x+11,841,"CP-"+re.search(r"CP-(\d+)",record["path"]).group(1),13,COLORS[2],True))
        p.append(text(x+11,857,record["state"].upper(),10,"#9DCEC3"))
        if i<3:
            p.append(lane_line(x+125,x+135,843,COLORS[2],"slow"))
    p.extend([
       text(655,828,"W13 BOUNDED LOCAL PASS",21,"#F2D0B2",True),
       text(655,851,"Independent witness report; not deployed or origin-authenticated.",12,"#A6BED4"),
       text(655,876,"language/SEPARATIONS.md  /  corrections preserved as source",11,"#8BA5BF"),
       text(49,901,"SOURCE-BOUNDED RESEARCH FIELD · GitHub SVG animation is NOT a live worker feed",10,"#6D9BB9"),
       "</svg>"
    ])
    svg="".join(p)
    ET.fromstring(svg)
    return svg


def generate(out:Path=OUT):
    view=render(snapshot())
    if "<script" in view or "<image" in view or "href=" in view:
        raise ValueError("image must be static standalone SVG with CSS animation")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(view+"\n",encoding="utf-8")
    return view


if __name__=="__main__":
    generate()
    print("Rendered original research movement field.")
