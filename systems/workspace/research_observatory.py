"""Read-only research continuity across the EXISTING workstation's source boundaries.

The original runtime journal remains the authority for executed worker jobs.
This indexes public SOURCE records (not jobs), preserving their native status,
unresolved conditions, provenance and distinct domains. Files that are merely
present in the repository are inventory, never counted as witnessed MOVEs.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "workstation-research-continuity/v1"
MAX_FILES = 2500
MAX_BYTES = 500_000
DIRECTORIES = (
    ("Mathematics and checkpoint sources", "work/"),
    ("Research and experiments", "research/"),
    ("Workstation and game development", "systems/workspace/"),
    ("Language and corrections", "language/"),
    ("Independent and native tests", "network/"),
    ("Runtime and trace apparatus", "runtime/"),
    ("Core protocols", "protocols/"),
    ("Public visual evidence", "views/"),
    ("Historical pins", "state/"),
    ("Project and application sources", "companies/"),
    ("Design sources", "design/"),
    ("Other system sources", "systems/"),
    ("Other documents", "docs/"),
    ("Evidence and exports", "evidence/"),
    ("Tools and categories", "tools/"),
    ("Other foundational work", "foundation/"),
    ("Other domain sources", "domains/"),
    ("Other capabilities", "capabilities/"),
    ("Other open sources", "open_source/"),
    ("Other activation and identity", "activations/"),
    ("Other identity", "identity/"),
    ("Other published artifacts", "artifacts/"),
    ("Other jobs", "jobs/"),
    ("Other competition work", "money/"),
)
ALLOWED={".py",".md",".json",".jsonl",".yml",".yaml",".js",".html",".css",".svg",".txt"}
SKIP_DIRS={".git",".venv","node_modules","__pycache__",".pytest_cache","data","build","dist"}
# runtime/data is private; all inventory is read-only and source-only.
REDACT=("runtime/data/","systems/workspace/runtime/","work/private/")


def _load(path:Path)->dict:
    if not path.is_file() or path.is_symlink() or path.stat().st_size>MAX_BYTES:
        raise ValueError("source missing, unsafe or too large")
    value=json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError("source record must be object")
    return value


def _rel(root:Path,path:Path)->str:
    return path.relative_to(root).as_posix()


def _files(root:Path)->list[str]:
    paths=[]
    for label,prefix in DIRECTORIES:
        folder=root / prefix
        if not folder.is_dir() or folder.is_symlink():
            continue
        for path in folder.rglob("*"):
            if path.is_symlink() or not path.is_file() or path.suffix not in ALLOWED:
                continue
            rel=_rel(root,path)
            if any(part in SKIP_DIRS for part in path.relative_to(folder).parts[:-1]):
                continue
            if any(rel.startswith(prefix) for prefix in REDACT):
                continue
            if path.stat().st_size > MAX_BYTES:
                continue
            paths.append(rel)
            if len(paths)>MAX_FILES:
                raise ValueError("source inventory exceeds bounded scope")
    return sorted(set(paths))


def _section(path:str)->str:
    # The longest matching prefix owns the source, not its filename.
    for name,prefix in DIRECTORIES:
        if path.startswith(prefix):
            return name
    return "Other evidence"


def _documented_marks(root:Path, inventory:list[str]) -> list[dict]:
    """Only headings explicitly labeled as a wall or movement.

    They remain DOCUMENTED source sections, not verified native events;
    no interpretation of free prose or broad keyword-based result counting.
    """
    marks=[]
    wall=re.compile(r"^(?:wall|walls|current wall|new wall|remaining walls|open wall)\b",re.I)
    move=re.compile(r"^(?:movement|next movement|next single movement|world w\d+.*movement|build movement|observed movement)\b",re.I)
    for rel in inventory:
        if not rel.endswith(".md"):
            continue
        path=root/rel
        if path.is_symlink() or path.stat().st_size>MAX_BYTES:
            continue
        for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            m=re.match(r"^#{1,5}\s+(.{2,160})\s*$",line)
            if not m:
                continue
            heading=m.group(1).strip()
            kind="DOCUMENTED_WALL" if wall.match(heading) else (
                 "DOCUMENTED_MOVEMENT" if move.match(heading) else None)
            if not kind:
                continue
            marks.append({"path":rel,"section":_section(rel),
                          "line":number,"heading":heading,"kind":kind,
                          "scope":"Document heading only; not a native journal event"})
            if len(marks)>1500:
                raise ValueError("documented movement/wall index exceeds scope")
    return marks


def _record(path:str,kind:str,title:str,state:str,*,wall:tuple[str,...]=(),
            boundary:str="",next_step:str="",scope:str="") -> dict:
    if not path or not title or not state:
        raise ValueError("incomplete original research record")
    return {"path":path,"kind":kind,"title":title,"state":state,
            "walls":list(wall),"boundary":boundary,
            "next":next_step,"scope":scope,
            "source_kind":"committed-record", "section":_section(path)}


def _bounded_text(value, name):
    if value is None:
        return ""
    if type(value) is not str or len(value)>3000:
        raise ValueError("invalid field: "+name)
    return value


def research_snapshot(root:Path=ROOT)->dict:
    """Source projection usable by the existing workstation and public renderer.

    Does not write to WorkspaceStore, RuntimeJournal or private work editions.
    Structured records are source-owned, and plain files are only an inventory.
    """
    root=Path(root)
    inventory=_files(root)
    present=set(inventory)
    groups=Counter(_section(path) for path in inventory)
    records=[]
    walls=0
    exact_moves=0
    # Previously frozen or historical state is NOT a current focus instruction.
    structured=[
        x for x in inventory
        if (x=="state/current.json" or
            (x.startswith("state/pins/") and x.endswith(".json")) or
            (x.startswith("research/dives/") and x.endswith("/dive.json")) or
            (x.startswith("research/dives/") and "/experiments/" in x and x.endswith(".json")) or
            (x.startswith("work/arc_like_maze/chatbot/checkpoints/CP-") and x.endswith(".json")))
    ]
    for rel in structured:
        data=_load(root/rel)
        if data.get("schema_version") not in (None,1):
            raise ValueError("unrecognized structured research schema")
        if rel.endswith("/dive.json"):
            state=_bounded_text(data.get("result_state"),"dive result")
            if not state:
                raise ValueError("dive result missing")
            field=data.get("walls",[])
            if type(field) is not list or any(type(s) is not str or not s for s in field):
                raise ValueError("bad dive walls")
            records.append(_record(rel,"RESEARCH_DIVE",_bounded_text(data.get("title"),"title"),state,
                                   wall=tuple(field),
                                   next_step=_bounded_text(data.get("next_movement"),"next"),
                                   scope="User-directed research record; original result state"))
            walls+=len(field)
            exact_moves+=int(state=="MOVE" or state=="MOVE_WITH_WALL")
        elif "/experiments/" in rel:
            result=_bounded_text(data.get("result"),"experiment result")
            records.append(_record(rel,"EXPERIMENT",_bounded_text(data.get("title"),"experiment title"),
                                   result or "UNCLASSIFIED",
                                   boundary=_bounded_text(data.get("correction_of_prior_result"),"correction"),
                                   next_step=_bounded_text(data.get("next_test"),"next test"),
                                   scope="Recorded experiment result; not automatically a workstation MOVE"))
        elif "/checkpoints/CP-" in rel:
            status=_bounded_text(data.get("status"),"checkpoint status")
            records.append(_record(rel,"CHECKPOINT",
                                   _bounded_text(data.get("title"),"checkpoint title"),
                                   status or "UNCLASSIFIED",
                                   boundary=_bounded_text(data.get("boundary"),"checkpoint boundary"),
                                   next_step=_bounded_text(data.get("next"),"checkpoint next"),
                                   scope="Historical checkpoint summary; external archive may be unavailable"))
        else:
            state=_bounded_text(data.get("result_state"),"state result")
            field=data.get("walls",[])
            if type(field) is not list or any(type(s) is not str or not s for s in field):
                raise ValueError("bad pinned walls")
            historical=(rel=="state/current.json")
            records.append(_record(rel,"HISTORICAL_POINTER" if historical else "PIN",
                                   _bounded_text(data.get("preferred_referent") or data.get("preferred_referent_at_pin") or data.get("pin_id"),"referent"),
                                   state or "UNCLASSIFIED",
                                   wall=tuple(field) if not historical else (),
                                   boundary="Historical non-current pointer; 'walls' are preserved guardrails" if historical
                                   else _bounded_text(data.get("pin_reason") or data.get("credential_boundary") or data.get("note"),"pin boundary"),
                                   next_step=_bounded_text(data.get("resume_from") or data.get("next_movement") or data.get("dependency"),"next"),
                                   scope="Pinned or historical original; not a presently assigned task"))
            if not historical:
                walls+=len(field)
                exact_moves+=int(state=="MOVE" or state=="MOVE_WITH_WALL")
    records.sort(key=lambda x:x["path"])
    marks=_documented_marks(root,inventory)
    # Reversible indices, without silently promoting filenames into results.
    return {
        "schema":SCHEMA,"read_only":True,
        "inventory_scope":"Repository-public source index, not an executed runtime journal",
        "sources_indexed":len(inventory),
        "sections":[{"name":name,"source_count":groups[name],
                     "paths":[p for p in inventory if _section(p)==name]}
                    for name,_ in DIRECTORIES if groups[name]],
        "source_records":records,
        "documented_marks":marks,
        "totals":{
            "structured_records":len(records),
            "explicit_move_states":exact_moves,
            "explicit_wall_entries":walls,
            "source_files":len(inventory),
            "documented_wall_headings":sum(m["kind"]=="DOCUMENTED_WALL" for m in marks),
            "documented_movement_headings":sum(m["kind"]=="DOCUMENTED_MOVEMENT" for m in marks)},
        "caveats":[
            "MOVE count is limited to exact MOVE/MOVE_WITH_WALL source records; not all historic movements are machine-countable.",
            "WALL entries are unresolved requirements in structured records, not automatic failed executions.",
            "Markdown WALL/MOVEMENT heading matches are source locators, not independently witnessed events.",
            "Source files, protocols, native tests, witness documents and checkpoints are indexed separately from runtime jobs.",
            "Local uncommitted or archived conversations and inaccessible external ZIPs are not in this public index.",
            "No synthetic worker admission, evidentiary promotion, cross-source relationship or historical event is created."
        ]}


if __name__=="__main__":
    state=research_snapshot()
    print(json.dumps({k:v for k,v in state.items() if k!="sections" and k!="source_records"},indent=2))
