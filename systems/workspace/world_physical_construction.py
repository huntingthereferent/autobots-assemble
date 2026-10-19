"""WORLD physical construction from the recorded Phase-1-contained Phase-2
blueprint and the exact W13 native room dimensions.

Dimensions are GRID UNITS derived from evidence: six blueprint relationship
lanes * original W13 first-room width (4); two distinct physical build/test
stages * original room height (3). Thus 24x6=144 navigable/blocked cells.
No metric length, building dimensions or real NIH facility is inferred.
"""
from __future__ import annotations
from collections import deque
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

SCHEMA="world-phase1-phase2-physical-construction/v1"
LANES=("source","assertion","valid interval","availability","query","witness")
WIDTH_PER_LANE=4
HEIGHT_PER_STAGE=3
STAGES=("construct","reason")
BLOCKS=(
    {"id":"boundary-wall","kind":"wall","x":12,"y":1,"height":2},
    {"id":"guide","kind":"guide","x":4,"y":1,"height":1},
    {"id":"funnel","kind":"funnel","x":8,"y":1,"height":1},
    {"id":"diverter","kind":"diverter","x":16,"y":4,"height":1},
    {"id":"spiral","kind":"spiral","x":20,"y":4,"height":1},
)
SOURCE={"id":"source-station","x":2,"y":1,"stage":"construct"}
QUERY={"id":"reasoning-station","x":22,"y":4,"stage":"reason"}
GATE={"from":[12,2],"to":[12,3],"requires":"source-constructed"}
ORIGIN=[0,1]
GOAL=[23,4]

def footprint(bp):
    from systems.workspace.world_temporal_blueprint import validate
    validate(bp)
    room1,room2=bp["base_world"]["rooms"]
    w=room1["spec"]["width"]
    h=room2["spec"]["height"]
    if w!=WIDTH_PER_LANE or h!=HEIGHT_PER_STAGE:
        raise ValueError("original physical W13 grid calibration altered")
    return {
        "schema":SCHEMA,"unit":"W13 movement cell (arbitrary virtual unit, NOT meters)",
        "dimensions":{"width":w*len(LANES),"height":h*len(STAGES),
                      "lane_width":w,"stage_height":h,
                      "area_cells":w*h*len(LANES)*len(STAGES)},
        "lanes":[{"id":name,"x_start":i*w,"x_end_exclusive":(i+1)*w}
                 for i,name in enumerate(LANES)],
        "stages":[{"id":name,"y_start":i*h,"y_end_exclusive":(i+1)*h}
                  for i,name in enumerate(STAGES)],
        "source_station":deepcopy(SOURCE),"reasoning_station":deepcopy(QUERY),
        "gate":deepcopy(GATE),"start":list(ORIGIN),"end":list(GOAL),
        "solid_blocks":[deepcopy(block) for block in BLOCKS],
        "blueprint_sha256":sha256(json.dumps(bp,sort_keys=True,separators=(",",":"),
                                       ensure_ascii=False).encode()).hexdigest(),
        "physical_scale_authenticated":False,
        "source_assertions_not_constrained_by_physical_grid_cells":True,
        "original_W13_rooms_preserved":True}

def verify_geometry(data):
    if type(data) is not dict or set(data)!={
        "schema","unit","dimensions","lanes","stages","source_station",
        "reasoning_station","gate","start","end","solid_blocks","blueprint_sha256",
        "physical_scale_authenticated","source_assertions_not_constrained_by_physical_grid_cells",
        "original_W13_rooms_preserved"}:
        raise ValueError("physical construction schema missing or invented")
    d=data["dimensions"]
    if (data["schema"]!=SCHEMA or
        d!={"width":24,"height":6,"lane_width":4,"stage_height":3,"area_cells":144} or
        [r["id"] for r in data["lanes"]]!=list(LANES) or
        [r["id"] for r in data["stages"]]!=list(STAGES) or
        data["start"]!=ORIGIN or data["end"]!=GOAL or
        data["gate"]!=GATE or data["source_station"]!=SOURCE or
        data["reasoning_station"]!=QUERY or
        data["solid_blocks"]!=list(BLOCKS) or
        data["physical_scale_authenticated"] is not False or
        data["source_assertions_not_constrained_by_physical_grid_cells"] is not True or
        data["original_W13_rooms_preserved"] is not True):
        raise ValueError("original blueprint physical dimensions or provenance drifted")
    solids={(b["x"],b["y"]) for b in data["solid_blocks"]}
    if len(solids)!=len(BLOCKS):raise ValueError("overlapping physical solid blocks")
    special=[tuple(data["start"]),tuple(data["end"]),
             (SOURCE["x"],SOURCE["y"]),(QUERY["x"],QUERY["y"]),
             tuple(GATE["from"]),tuple(GATE["to"])]
    if any(v in solids or not (0<=v[0]<24 and 0<=v[1]<6) for v in special):
        raise ValueError("source station, gate or goal obstructed")
    if not all(0<=x<24 and 0<=y<6 for x,y in solids):
        raise ValueError("physical block outside blueprint floor")
    return solids

def neighbors(data,pos,gate_open):
    solids=verify_geometry(data)
    x,y=pos
    for delta in ((1,0),(-1,0),(0,1),(0,-1)):
        at=(x+delta[0],y+delta[1])
        if at in solids or not (0<=at[0]<24 and 0<=at[1]<6):
            continue
        if pos[1]//3!=at[1]//3:
            if not gate_open or (list(pos),list(at)) not in (
                 (GATE["from"],GATE["to"]),(GATE["to"],GATE["from"])):
                continue
        yield at

def route(data,start,end,gate_open=False):
    verify_geometry(data)
    start,end=tuple(start),tuple(end)
    if start==end:return [list(start)]
    pending=deque([start])
    ancestors={start:None}
    while pending:
        node=pending.popleft()
        for after in neighbors(data,node,gate_open):
            if after in ancestors:continue
            ancestors[after]=node
            if after==end:
                result=[]
                while after is not None:
                    result.append(list(after));after=ancestors[after]
                return result[::-1]
            pending.append(after)
    return None

def witness(data):
    solids=verify_geometry(data)
    source=route(data,ORIGIN,[SOURCE["x"],SOURCE["y"]],False)
    door=route(data,[SOURCE["x"],SOURCE["y"]],GATE["from"],False)
    beyond=route(data,GATE["to"],[QUERY["x"],QUERY["y"]],True)
    complete=route(data,[QUERY["x"],QUERY["y"]],GOAL,True)
    blocked=route(data,ORIGIN,[QUERY["x"],QUERY["y"]],False)
    if any(r is None for r in (source,door,beyond,complete)) or blocked is not None:
        raise ValueError("source/gate/query physically unreachable or unauthorized crossing")
    layout={"schema":SCHEMA,"width":24,"height":6,
            "area_cells":144,"solid_cells":len(solids),
            "free_cells":144-len(solids),
            "physical_construction_path_lengths":{
                "start_to_source":len(source)-1,
                "source_to_gate":len(door)-1,
                "gate_to_query":len(beyond)-1,
                "query_to_goal":len(complete)-1},
            "gate_required":True,"solid_collision_rule_verified":True,
            "all_four_constructed_objects_present":True,
            "source_station_and_query_station_reachable":True,
            "relative_not_metric_dimensions":True,
            "independent_2019_publication_transaction_verified":False}
    return layout
