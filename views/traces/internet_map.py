"""Source-bound geographic Internet observation map.

World outline is real Natural Earth geography. Public RIPE Atlas probes are a
bounded, explicitly nonrepresentative SAMPLE of network measurement sites.
Cloudflare Radar country HTTP request shares are displayed ONLY when a valid
API token and actual source response are present. No simulated packet flows.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import re
import tempfile
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

DIR = Path(__file__).resolve().parent
NE_SHA = "ca96624a56bd078437bca8184e78163e5039ad19"
GEOGRAPHY = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/" + NE_SHA + "/geojson/ne_110m_admin_0_countries.geojson"
RIPE = "https://atlas.ripe.net/api/v2/probes/?status=1&is_public=true&page_size=300&format=json"
CLOUDFLARE = "https://api.cloudflare.com/client/v4/radar/http/top/locations?dateRange=1d&limit=250"
W,H=1200,650


def get_json(url: str, *, token: str | None = None, max_bytes: int = 2_100_000):
    if not url.startswith(("https://atlas.ripe.net/", "https://api.cloudflare.com/", "https://raw.githubusercontent.com/nvkelso/")):
        raise ValueError("unregistered data host")
    headers={"User-Agent":"huntingthereferent-trace-map/1.0 (source-only)","Accept":"application/json"}
    if token:
        headers["Authorization"]="Bearer "+token
    req=Request(url,headers=headers)
    with urlopen(req,timeout=22) as response:
        if response.status != 200:
            raise ValueError("source HTTP status not successful")
        blob=response.read(max_bytes+1)
    if len(blob)>max_bytes:
        raise ValueError("source byte limit exceeded")
    return json.loads(blob)


def read_geojson(raw: dict) -> list[dict]:
    if raw.get("type")!="FeatureCollection" or not isinstance(raw.get("features"),list) or len(raw["features"])<100:
        raise ValueError("invalid real world geometry")
    features=[]
    for feature in raw["features"]:
        geometry=feature.get("geometry") or {}
        if geometry.get("type") not in ("Polygon","MultiPolygon"):
            continue
        code=(feature.get("properties") or {}).get("ISO_A2_EH")
        if not isinstance(code,str) or not re.fullmatch(r"[A-Z]{2}",code):
            code=(feature.get("properties") or {}).get("ISO_A2")
        if not isinstance(code,str) or not re.fullmatch(r"[A-Z]{2}",code):
            code="--"
        pol=geometry["coordinates"] if geometry["type"]=="MultiPolygon" else [geometry["coordinates"]]
        if not isinstance(pol,list) or len(pol)>1000:
            raise ValueError("bad geographic polygons")
        features.append({"iso2":code,"polygons":pol})
    if len(features)<100:
        raise ValueError("not enough valid country shapes")
    return features


def read_probes(source:dict) -> dict:
    if not isinstance(source,dict) or not isinstance(source.get("results"),list):
        raise ValueError("unsupported RIPE Atlas probe response")
    coords=[]
    for item in source["results"]:
        geometry=item.get("geometry") if isinstance(item,dict) else None
        if not item.get("is_public") or (item.get("status") or {}).get("id")!=1:
            continue
        values=(geometry or {}).get("coordinates")
        if (isinstance(values,list) and len(values)==2 and
                all(isinstance(z,(float,int)) and math.isfinite(z) for z in values) and
                -180<=values[0]<=180 and -90<=values[1]<=90):
            coords.append([round(float(values[0]),2),round(float(values[1]),2)])
    if len(coords)>300:
        raise ValueError("probe sample exceeds bound")
    return {"sampled_page_size":300,"points":coords,
            "meaning":"First retrieved page of connected public probes; not a representative sample or measurement of traffic."}


def read_traffic(raw:dict) -> dict:
    if not isinstance(raw,dict) or raw.get("success") is not True:
        raise ValueError("Cloudflare Radar request unsuccessful")
    data=raw.get("result") or {}
    top=data.get("top_0")
    meta=data.get("meta") or {}
    if not isinstance(top,list) or not top:
        raise ValueError("empty Cloudflare traffic coverage")
    if meta.get("normalization")!="PERCENTAGE":
        raise ValueError("this map only accepts percentages, not counts or normalized scores")
    dates=meta.get("dateRange")
    if not isinstance(dates,list) or len(dates)!=1:
        raise ValueError("missing native traffic observation interval")
    begin,end=dates[0].get("startTime"),dates[0].get("endTime")
    if not isinstance(begin,str) or not isinstance(end,str):
        raise ValueError("invalid traffic interval")
    rows=[]
    seen=set()
    for x in top:
        k=x.get("clientCountryAlpha2")
        if not isinstance(k,str) or not re.fullmatch("[A-Z]{2}",k) or k in seen:
            raise ValueError("invalid/duplicated country identity")
        seen.add(k)
        try:v=float(x["value"])
        except (TypeError,ValueError) as exc:raise ValueError("invalid traffic proportion") from exc
        if not math.isfinite(v) or not (0<=v<=100):
            raise ValueError("country percentage out of range")
        rows.append({"country":k,"percent":round(v,4)})
    return {"source":"Cloudflare Radar HTTP share by client country",
            "measurement_kind":"sampled share of Cloudflare HTTP requests, not global packet count",
            "window_start":begin,"window_end":end,
            "provider_last_updated":meta.get("lastUpdated"),"values":rows,
            "coverage_note":"Countries absent from source results remain NO DATA, not zero traffic."}


def validate_snapshot(data):
    if data.get("schema")!="internet-observations-map/v1":
        raise ValueError("unknown snapshot schema")
    traffic=data.get("traffic")
    if traffic is None and data.get("traffic_state")!="TOKEN_NOT_CONFIGURED":
        raise ValueError("missing traffic may never be called measured")
    if traffic is not None and data.get("traffic_state")!="SOURCE_MEASURED":
        raise ValueError("traffic state contradicts source")
    if data.get("probe_state") not in ("PUBLIC_SAMPLE","SOURCE_UNAVAILABLE"):
        raise ValueError("unknown probe status")
    if data.get("probe_state")=="PUBLIC_SAMPLE" and not isinstance(data.get("probes"),dict):
        raise ValueError("probe status inconsistent")
    return data


def sample(s:dict, coordinates:tuple) -> str:
    lon,lat=coordinates
    return f'{(lon+180)*W/360:.2f},{(90-lat)*H/180:.2f}'


def polygon_paths(geo: list[dict], traffic:dict | None):
    levels={a["country"]:a["percent"] for a in traffic["values"]} if traffic else {}
    out=[]
    for f in geo:
        components=[]
        for polygon in f["polygons"]:
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<3:
                    continue
                commands=[]
                for idx,point in enumerate(ring):
                    if not isinstance(point,list) or len(point)<2:
                        raise ValueError("malformed country coordinate")
                    lon,lat=point[:2]
                    if not isinstance(lon,(int,float)) or not isinstance(lat,(int,float)) or not (-180.01<=lon<=180.01 and -90.01<=lat<=90.01):
                        raise ValueError("unbounded geography")
                    commands.append(("M" if idx==0 else "L")+sample({},(lon,lat)).replace(","," "))
                components.append(" ".join(commands)+" Z")
        if not components:
            continue
        value=levels.get(f["iso2"])
        if value is None:
            fill="#142237" # NO DATA, including no-token case
        else:
            # Color intensity reflects observed Cloudflare share, NOT total global traffic.
            fraction=min(1,math.sqrt(value/20))
            r=round(17+(28-17)*fraction)
            g=round(40+(214-40)*fraction)
            b=round(65+(235-65)*fraction)
            fill=f"#{r:02x}{g:02x}{b:02x}"
        out.append(f'<path d="{" ".join(components)}" fill="{fill}" stroke="#385471" stroke-width=".40" stroke-linejoin="round"/>')
    return "".join(out)


def render_map(geo,record):
    validate_snapshot(record)
    traffic=record.get("traffic")
    probes=record.get("probes")
    roads=polygon_paths(geo,traffic)
    marker=""
    if probes:
        for lon,lat in probes["points"]:
            x,y=sample({},(lon,lat)).split(",")
            marker+=f'<circle cx="{x}" cy="{y}" r="2.3" fill="#a3a0ed" fill-opacity=".78"/>'
    count=len(probes["points"]) if probes else 0
    label=(f'Cloudflare sampled HTTP request share · {escape(traffic["window_start"])} to {escape(traffic["window_end"])}'
           if traffic else 'Traffic by country: NO SOURCE DATA (Cloudflare token not configured)')
    update=escape(record["checked_at"][:19].replace("T"," ")+" UTC")
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+100}" viewBox="0 0 {W} {H+100}" role="img" aria-labelledby="title desc">
<title id="title">Geographic Internet observations</title>
<desc id="desc">Country silhouettes are public domain Natural Earth data. Traffic layer {"shows Cloudflare Radar country request share" if traffic else "has no values and does not imply global traffic"}. {count} publicly located RIPE Atlas probes sampled from one retrieved page; dots are probes, not packets or traffic flow. Checked {update}.</desc>
<style>
text{{font-family:ui-monospace,Consolas,monospace}}
.probe{{animation:pulse 3.6s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.45}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect width="{W}" height="{H+100}" fill="#080e19" rx="14"/>
<g transform="translate(0 43)">{roads}<g class="probe">{marker}</g></g>
<text x="25" y="29" font-size="19" font-weight="bold" fill="#e5edf8">INTERNET / OBSERVATIONAL WORLD MAP</text>
<rect x="16" y="{H+34}" width="{W-32}" height="52" rx="9" fill="#101b2a" stroke="#33506c"/>
<text x="30" y="{H+53}" font-size="12" fill="#5fd3e7">{label}</text>
<text x="30" y="{H+70}" font-size="12" fill="#b5c9df">RIPE Atlas: {count} connected public probes from FIRST PAGE ONLY; locations are approximate and not representative. Snapshot {update}.</text>
</svg>'''
    ET.fromstring(svg)
    return svg


def fetch_all(token=None):
    # Source errors are explicit in saved snapshot. No fabricated substitution.
    geo=read_geojson(get_json(GEOGRAPHY))
    raw_probes=get_json(RIPE,max_bytes=750000)
    probes=read_probes(raw_probes)
    traffic=read_traffic(get_json(CLOUDFLARE,token=token)) if token else None
    at=datetime.now(timezone.utc).isoformat()
    snap={"schema":"internet-observations-map/v1","checked_at":at,
          "geography":{"source":GEOGRAPHY,"license":"Natural Earth public domain"},
          "probe_state":"PUBLIC_SAMPLE","probes":probes,"probe_source":RIPE,
          "traffic_state":"SOURCE_MEASURED" if traffic else "TOKEN_NOT_CONFIGURED",
          "traffic_source":CLOUDFLARE,"traffic":traffic,
          "limitations":["The map does not observe all internet packets.",
                         "Probe markers denote geographic measuring points, not network traffic.",
                         "Cloudflare shares are bounded to Cloudflare-served HTTP requests."]}
    return geo,validate_snapshot(snap)


def write(data,svg,out):
    out.mkdir(parents=True,exist_ok=True)
    for name,body in (("internet-map.svg",svg),("internet-map.json",json.dumps(data,indent=2,sort_keys=True)+"\n")):
        tmp=None
        try:
            with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",dir=out,delete=False) as f:
                tmp=f.name
                f.write(body)
            os.replace(tmp,out/name)
        finally:
            if tmp and os.path.exists(tmp):os.unlink(tmp)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh",action="store_true",help="Fetch only allowlisted public sources")
    ap.add_argument("--out-dir",type=Path,default=DIR)
    args=ap.parse_args()
    if not args.refresh:
        raise SystemExit("Explicit --refresh required; do not mistake a stale map for a live sample.")
    geo,data=fetch_all(os.environ.get("CLOUDFLARE_RADAR_TOKEN"))
    write(data,render_map(geo,data),args.out_dir)
    print(f'Observed {len(data["probes"]["points"])} probe locations; traffic state {data["traffic_state"]}.')


if __name__=="__main__":
    main()
