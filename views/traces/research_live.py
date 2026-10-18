"""Project workstation originals to a compact public browser source.

This is not an execution log or fabricated timeline. An index of original
source states, independent native outcomes, and explicit documented walls.
The browser follows GitHub source relationships separately, with no implied
scientific relationship between this record index and Git ancestry.
"""
from __future__ import annotations
import json
from pathlib import Path
from systems.workspace.research_observatory import ROOT, research_snapshot

SCHEMA="workstation-live-projection/v1"
DEST=ROOT/"views/traces/research-live.json"


def projection(research):
    if research.get("schema")!="workstation-research-continuity/v1":
        raise ValueError("not the original workstation")
    records=[]
    seen=set()
    for r in research.get("source_records",[]):
        path=r["path"]
        if path in seen:
            raise ValueError("duplicate original record identity")
        seen.add(path)
        if not (r["kind"] in ("CHECKPOINT","RESEARCH_DIVE","EXPERIMENT","PIN")):
            continue
        records.append({"path":path,"label":r["title"],"state":r["state"],
                        "source_type":r["kind"],"scope":r["scope"],
                        "next":r.get("next",""),"boundary":r.get("boundary","")})
    walls=[]
    for r in research.get("source_records",[]):
        for i,w in enumerate(r["walls"]):
            walls.append({"path":r["path"],"text":w,"kind":"source-recorded-wall","index":i})
    for m in research.get("documented_marks",[]):
        if m["kind"]=="DOCUMENTED_WALL":
            walls.append({"path":m["path"],"text":m["heading"],
                          "kind":"documented-heading-only","line":m["line"]})
    movements=[]
    for r in research.get("source_records",[]):
        if r["state"] not in ("MOVE","MOVE_WITH_WALL"):
            continue
        movements.append({
            "id":"structured:"+r["path"],"path":r["path"],"line":None,
            "title":r["title"],"state":r["state"],"evidence":"structured-source-state",
            "boundary":r.get("boundary",""),"next":r.get("next","")
        })
    for m in research.get("documented_marks",[]):
        if m["kind"]!="DOCUMENTED_MOVEMENT":
            continue
        movements.append({
            "id":"heading:"+m["path"]+"#L"+str(m["line"]),
            "path":m["path"],"line":m["line"],"title":m["heading"],
            "state":"DOCUMENTED_MOVEMENT","evidence":"documented-heading-only",
            "boundary":"This is a recorded heading, not a native verified execution.",
            "next":""
        })
    movements.sort(key=lambda x:(x["path"],x["line"] or 0))
    if not records:
        raise ValueError("original records missing; refuse empty fabricated display")
    # A compact, deterministic projection. Checksums and generation dates are
    # intentionally not evidence of when the historical observation happened.
    priority={"RESEARCH_DIVE":0,"CHECKPOINT":1,"EXPERIMENT":2,"PIN":3}
    records.sort(key=lambda r:(priority[r["source_type"]],r["path"]))
    walls.sort(key=lambda w:(w["path"],w.get("line",0),w.get("index",0)))
    return {"schema":SCHEMA,
            "generated_from":"systems/workspace/research_observatory.py",
            "records":records[:160],
            "walls":walls[:160],
            "movements":movements[:500],
            "source_totals":{
                "source_files":research["totals"]["source_files"],
                "structured_records":research["totals"]["structured_records"],
                "original_wall_entries":research["totals"]["explicit_wall_entries"],
                "documented_wall_headings":research["totals"]["documented_wall_headings"],
                "documented_movement_headings":research["totals"]["documented_movement_headings"]},
            "boundary":"Research entries are source-owned states; the browser's event roots and ancestry must come from GitHub directly. Presence in one display does not establish a causal relationship."}


def generate(out:Path=DEST):
    document=projection(research_snapshot())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(document,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return document


if __name__=="__main__":
    r=generate()
    print("Published original workstation research projection: "
          +str(len(r["records"]))+" records; "+str(len(r["movements"]))+" source movements; "+str(len(r["walls"]))+" walls.")
