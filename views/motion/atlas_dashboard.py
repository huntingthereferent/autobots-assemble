"""Render the living-profile atlas from existing owner-sourced observations.

Self-contained SVG animation. Nothing inside the SVG contacts network sources.
Domain marks represent CATALOGED feeds, not joined systems. Only native
finite A/B convergence is drawn as verified meeting. All source timestamps
and 'no data' boundaries remain intact. No new collection or worker action.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape
import json
from math import cos, sin, pi
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
MOTION = Path(__file__).resolve().parent
COLORS = ["#48D8ED", "#7CBAFF", "#A994EE", "#73D7C4",
          "#DAAAE6", "#90B1EA", "#D5ACDB", "#64BFDE", "#B5B9F6", "#ACDCD3"]


def _load(rel: str) -> dict:
    path = ROOT / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("source object required: " + rel)
    return data


def snapshot() -> dict:
    registry = _load("views/traces/registry.json")
    internet = _load("views/traces/internet-map.json")
    work = _load("views/work_state.json")
    finite = _load("views/motion/convergence-receipt.json")
    world = _load("views/world-continuity/latest.json")
    entries = registry.get("entries")
    if registry.get("schema") != "public-trace-source-registry/v1" or not isinstance(entries, list) or not entries:
        raise ValueError("missing original trace registry")
    if any(not isinstance(e,dict) or not isinstance(e.get("category"),str)
           or not isinstance(e.get("id"),str) or not isinstance(e.get("source_url"),str)
           for e in entries):
        raise ValueError("incomplete registry entry")
    if len({e["id"] for e in entries}) != len(entries):
        raise ValueError("duplicate trace identity")
    cat = Counter(e["category"] for e in entries)
    if len(cat) > 14:
        raise ValueError("too many domains for bounded atlas")
    original = sum(e.get("integration")=="existing_partial_source" for e in entries)
    if internet.get("schema") != "internet-observations-map/v1":
        raise ValueError("internet source not identified")
    probes = internet.get("probes")
    if internet.get("probe_state") != "PUBLIC_SAMPLE" or not isinstance(probes,dict) or not isinstance(probes.get("points"),list):
        raise ValueError("no actual RIPE probe sample")
    if internet.get("traffic_state") not in ("TOKEN_NOT_CONFIGURED", "SOURCE_MEASURED"):
        raise ValueError("traffic source status inconsistent")
    if (internet["traffic_state"]=="SOURCE_MEASURED") != (internet.get("traffic") is not None):
        raise ValueError("measured/no-source contradiction")
    counts=work.get("protocol_results")
    if (not isinstance(counts,dict) or set(counts)!={"MOVE","WALL","UNKNOWN","PARTIAL"}
            or type(work.get("jobs")) is not int
            or any(type(x) is not int or x<0 for x in counts.values())
            or sum(counts.values())!=work["jobs"]):
        raise ValueError("native workstation counts invalid")
    if (finite.get("schema")!="finite-ab-convergence/v1" or
        not isinstance(finite.get("left_word"),str) or
        not isinstance(finite.get("right_word"),str) or
        not isinstance(finite.get("target"),list) or len(finite["target"])!=3 or
        finite["left_word"]==finite["right_word"] or
        not all(isinstance(v,int) for v in finite["target"])):
        raise ValueError("no verified finite convergence receipt")
    # A rendering receipt is not the verifier: independently compute the
    # endpoints using the ORIGINAL finite source and the existing witness.
    from work.arc_like_maze.math import World
    from systems.workspace.ab_relational_cluster import _independent_step
    world_math=World(3,(0,1,2))
    for word in [finite["left_word"],finite["right_word"]]:
        if not word or any(a not in "AB" for a in word) or len(word)>32:
            raise ValueError("invalid native A/B word")
        s=world_math.origin
        for a in word:
            native=world_math.step(s,a)
            if native!=_independent_step(s,a):
                raise ValueError("independent finite verifier rejected move")
            s=native
        if list(s)!=finite["target"]:
            raise ValueError("finite receipt disagrees with actual source")
    if world.get("schema")!="public-world-continuity/v1":
        raise ValueError("unknown world observation source")
    for timestamp in [internet.get("checked_at"),world.get("checked_at")]:
        if not isinstance(timestamp,str):
            raise ValueError("missing source timestamp")
        at=datetime.fromisoformat(timestamp.replace("Z","+00:00"))
        if at.tzinfo is None:
            raise ValueError("timestamp missing timezone")
    return {
        "source_count": len(entries),
        "category_counts": list(sorted(cat.items())),
        "integrated_count": original,
        "sampled_probes": len(probes["points"]),
        "traffic_state": internet["traffic_state"],
        "internet_timestamp":internet["checked_at"],
        "work":work,
        "finite":finite,
        "world_match":world.get("relationship",{}).get("matched_by_declared_url_rule") is True,
        "world_timestamp":world["checked_at"],
    }


def _text(x,y,value,size=14,color="#DDEAFF",weight=None,spacing=None,anchor=None) -> str:
    attrib=""
    if weight: attrib+=f' font-weight="{weight}"'
    if spacing is not None: attrib+=f' letter-spacing="{spacing}"'
    if anchor: attrib+=f' text-anchor="{anchor}"'
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"{attrib}>'
            +escape(str(value))+"</text>")


def dashboard(data:dict) -> str:
    categories=data["category_counts"]
    total=data["source_count"]
    work=data["work"]
    finite=data["finite"]
    css="""text{font-family:ui-monospace,'SFMono-Regular',Consolas,monospace}
    .orbit{transform-origin:861px 316px;animation:spin 36s linear infinite}
    .orbit2{transform-origin:861px 316px;animation:spin 55s linear infinite reverse}
    .radar{transform-origin:861px 316px;animation:spin 9s linear infinite}
    .pulse{animation:blink 4s ease-in-out infinite}
    .light{animation:blink 2.7s ease-in-out infinite}
    .beam{stroke-dasharray:5 15;animation:flow 5s linear infinite}
    .trail{stroke-dasharray:130;animation:draw 8s ease-in-out infinite}
    .trace{stroke-dasharray:12 22;animation:flow 3.5s linear infinite}
    .boot{animation:enter 1.4s ease-out both}
    .delayed{animation-delay:.35s}
    .slow{animation-delay:.8s}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes blink{50%{opacity:.3}}
    @keyframes flow{to{stroke-dashoffset:-156}}
    @keyframes draw{0%,10%{stroke-dashoffset:130}70%,100%{stroke-dashoffset:0}}
    @keyframes enter{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
    @media(prefers-reduced-motion:reduce){*{animation:none!important;transform:none!important}}
    """
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820" role="img" aria-labelledby="title desc">',
       '<title id="title">James Muneoka — a living atlas of observations</title>',
       '<desc id="desc">Animated research profile. Ten cataloged domains, '+str(total)+' candidate sources, '+str(data["sampled_probes"])+' public network probes, '+str(work["jobs"])+' recorded workstation jobs. Actual finite paths '+escape(finite["left_word"])+' and '+escape(finite["right_word"])+' meet at '+escape(str(finite["target"]))+'. Catalog domains are not connected scientific evidence. No live traffic values are invented.</desc>',
       '<defs><radialGradient id="deep"><stop stop-color="#182D46"/><stop offset=".6" stop-color="#0D182C"/><stop offset="1" stop-color="#070D19"/></radialGradient>',
       '<linearGradient id="left"><stop stop-color="#071523"/><stop offset="1" stop-color="#0B0F20"/></linearGradient>',
       '<linearGradient id="cyan"><stop stop-color="#42D9EC"/><stop offset="1" stop-color="#9DA2F8"/></linearGradient>',
       '<radialGradient id="flare"><stop stop-color="#46DCED" stop-opacity=".26"/><stop offset="1" stop-color="#46DCED" stop-opacity="0"/></radialGradient>',
       '<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#39536F" stroke-opacity=".19"/></pattern>',
       '</defs>',
       '<style>'+css+'</style>',
       '<rect width="1200" height="820" rx="16" fill="url(#deep)"/>',
       '<rect width="1200" height="820" rx="16" fill="url(#grid)"/>',
       '<rect x="10" y="10" width="1180" height="800" rx="12" stroke="#415672" fill="none" stroke-opacity=".65"/>',
       '<rect x="11" y="11" width="7" height="798" rx="3" fill="url(#cyan)"/>',
       '<path d="M34 59H1165" stroke="#3C526F" stroke-opacity=".7"/>']
    # top title and status
    p.extend([
      _text(39,37,"HUNTING THE REFERENT / RESEARCH IN MOTION",13,"#62DAEA",weight="bold",spacing=1.65),
      '<circle class="light" cx="1071" cy="34" r="5" fill="#61E0C8"/>',
      _text(1090,39,"SOURCE-BOUND",11,"#B5D7D9"),
      '<g class="boot">',
      _text(43,141,"JAMES",67,"#F1F6FF",weight="bold",spacing=-2),
      _text(42,211,"MUNEOKA",67,"#D3ECF8",weight="bold",spacing=-2),
      _text(45,250,"Watching what continues.",20,"#AFC6E3"),
      _text(45,283,"Language   /   Finite mathematics   /   Software",15,"#92B4CE"),
      '<path d="M45 316H450" stroke="url(#cyan)" stroke-width="2.5"/>',
      _text(45,352,"OBSERVE     TRACE     CHECK     CONTINUE",12,"#70D8E6",weight="bold",spacing=.8),
      '</g>'])
    # Main central orbital schematic - taxonomy rings, no lines between observations.
    p.extend([
      '<circle cx="861" cy="316" r="230" fill="url(#flare)"/>',
      '<circle cx="861" cy="316" r="178" fill="#0E1D30" fill-opacity=".45" stroke="#43617D" stroke-width="1.3"/>',
      '<circle cx="861" cy="316" r="138" fill="none" stroke="#33536F" stroke-dasharray="4 12"/>',
      '<circle cx="861" cy="316" r="94" fill="none" stroke="#52809D" stroke-dasharray="3 10" stroke-opacity=".5"/>',
      '<g class="orbit"><circle cx="861" cy="316" r="178" fill="none" stroke="#60CFE7" stroke-opacity=".38" stroke-width="1.4" stroke-dasharray="33 88"/><circle cx="1039" cy="316" r="6" fill="#61DAF0"/></g>',
      '<g class="orbit2"><circle cx="861" cy="316" r="143" fill="none" stroke="#AF9DF0" stroke-width="2" stroke-dasharray="8 45" stroke-opacity=".68"/><circle cx="718" cy="316" r="5" fill="#BAA7F3"/></g>',
      '<g class="radar"><path d="M861 316L861 142A174 174 0 0 1 1035 316Z" fill="#49D0E9" fill-opacity=".065" stroke="#49D0E9" stroke-opacity=".2"/></g>',
      '<circle cx="861" cy="316" r="77" fill="#0A192A" stroke="#41758F" stroke-width="1.5"/>',
      _text(861,305,"10 DOMAINS",21,"#E3F5FF",weight="bold",anchor="middle"),
      _text(861,328,"NOT JOINED",12,"#79D5E1",anchor="middle"),
      _text(861,348,"SOURCE INDEX",10,"#A7BBD5",anchor="middle"),
      _text(861,104,"CATALOGED / NOT MEASURED LIVE",11,"#A3BDD9",anchor="middle",spacing=1.1),
    ])
    # Display 10 source categories as real source records around orbit; dots are grouped taxonomy, not edges
    shortened={
      "Solar and space weather":"SUN / SPACE WEATHER","Solar system and sky":"ORBITS / OBJECTS",
      "Geology and hazards":"EARTH / HAZARDS","Fire and biosphere":"FIRE / BIOSPHERE",
      "Atmosphere and weather":"ATMOSPHERE","Water and ocean":"OCEAN / WATER",
      "Human mobility":"MOVEMENT","Infrastructure and energy":"POWER / INFRA",
      "Internet and network":"INTERNET / BGP","Digital activity":"DIGITAL EVENTS"
    }
    for i,(category,count) in enumerate(categories):
        theta=2*pi*i/len(categories)-pi/2
        x=861+218*cos(theta);y=316+207*sin(theta)
        color=COLORS[i%len(COLORS)]
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}" fill-opacity=".23" stroke="{color}" stroke-width="1.6"/>')
        p.append(f'<circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}" style="animation-delay:{(i*.28):.2f}s"/>')
        # Codes on orbit avoid pretending coordinates are geospatial
        p.append(_text(f"{x:.1f}",f"{y-13:.1f}",f"{count:02d}",11,color,anchor="middle"))
    # Left readout with visibly separated source semantics
    p.extend(['<rect x="39" y="390" width="490" height="147" rx="12" fill="#0D1A2B" stroke="#35516A"/>',
      _text(59,423,"NATIVE FINITE TRACE",12,"#73DAE9",weight="bold",spacing=1.2),
      _text(59,461,finite["left_word"],26,"#48D8ED",weight="bold"),
      _text(170,462,"+",23,"#9FB3D0"),
      _text(207,461,finite["right_word"],26,"#A994EE",weight="bold"),
      '<path class="trace" d="M60 482H331" fill="none" stroke="#8DB3EE" stroke-width="3"/>',
      _text(342,496,"→",23,"#8DE0EB"),
      _text(379,497,"("+",".join(map(str,finite["target"]))+")",24,"#EDF5FF",weight="bold"),
      _text(59,521,"TWO ORIGINAL PATHS / INDEPENDENT CHECK",11,"#9EB7D0"),
      ])
    # source-backed metrics row
    cells=[
      ("CANDIDATE FEEDS",total,"REGISTERED / NOT ALL ACTIVE","#48D8ED"),
      ("NETWORK PROBES",data["sampled_probes"],"RIPE SAMPLE / NOT PACKETS","#7CBAFF"),
      ("WORKSTATION",work["jobs"],str(work["workstation"] if "workstation" in work else work["protocol_results"]["MOVE"])+" MOVE / "+str(work["protocol_results"]["WALL"])+" WALL","#A994EE")
    ]
    for i,(lab,val,sub,color) in enumerate(cells):
        x=40+i*375
        p.append(f'<rect x="{x}" y="553" width="358" height="133" rx="12" fill="#101C2D" stroke="{color}" stroke-opacity=".55"/>')
        p.append(_text(x+18,581,lab,12,color,weight="bold",spacing=1))
        p.append(_text(x+18,633,str(val),45,"#F1F6FF",weight="bold"))
        p.append(_text(x+18,662,sub,11,"#A6BBD3"))
    # bottom system status
    cloud=data["traffic_state"]
    status="NOT CONFIGURED" if cloud=="TOKEN_NOT_CONFIGURED" else "SOURCE MEASURED"
    match="URL RULE MATCH" if data["world_match"] else "NO SOURCE MATCH"
    p.extend([
      '<rect x="40" y="704" width="1110" height="82" rx="12" fill="#0D1627" stroke="#39516C"/>',
      _text(59,728,"EXTERNAL OBSERVATIONS",12,"#7FDCEB",weight="bold",spacing=1.1),
      _text(59,754,"INTERNET TRAFFIC: "+status,12,"#B6C7D7"),
      _text(478,754,"GITHUB / PYPI: "+match,12,"#B6C7D7"),
      _text(917,754,"USGS: UNJOINED",12,"#B6C7D7"),
      _text(58,772,"NO SHARED CENTER CLAIMED FOR UNRELATED SOURCES  ·  DATA AND RUN DATES ARE SOURCE-OWNED",10,"#839CB8"),
      '</svg>'
    ])
    svg="".join(p)
    ET.fromstring(svg)
    return svg


def generate(out:Path = MOTION) -> str:
    body=dashboard(snapshot())
    if "<script" in body or "<image" in body or "href=" in body:
        raise ValueError("external SVG code forbidden")
    out.mkdir(parents=True,exist_ok=True)
    (out/"atlas-dashboard.svg").write_text(body+"\n",encoding="utf-8")
    return body


if __name__ == "__main__":
    generate()
    print("Atlas dashboard generated from original source records; no systems joined.")
