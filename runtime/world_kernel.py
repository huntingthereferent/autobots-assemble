"""Finite moving-torus world experiment. Not a claim about universal topology."""
from dataclasses import dataclass, replace
from typing import Tuple
import hashlib
import json

@dataclass(frozen=True)
class Body:
    identity: str
    x: int
    y: int

@dataclass(frozen=True)
class World:
    identity: str
    size: int
    bodies: Tuple[Body, ...]
    revision: int = 0
    parent: str = ""
    def __post_init__(self):
        if self.size < 2:
            raise ValueError("size must be >= 2")
        if len({b.identity for b in self.bodies}) != len(self.bodies):
            raise ValueError("duplicate body")
        if any(not (0 <= b.x < self.size and 0 <= b.y < self.size) for b in self.bodies):
            raise ValueError("coordinates must be in world")
    def fingerprint(self):
        data=(self.identity,self.size,[(b.identity,b.x,b.y) for b in self.bodies],self.revision,self.parent)
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()

@dataclass(frozen=True)
class Witness:
    before: str
    after: str
    body: str
    displacement: Tuple[int,int]
    old_position: Tuple[int,int]
    new_position: Tuple[int,int]
    result: str

def move(world: World, identity: str, dx: int, dy: int):
    """One witnessed periodic movement; output World is valid input to move."""
    body=next((b for b in world.bodies if b.identity==identity),None)
    if body is None:
        return world,Witness(world.fingerprint(),world.fingerprint(),identity,(dx,dy),(-1,-1),(-1,-1),"WALL")
    target=((body.x+dx)%world.size,(body.y+dy)%world.size)
    next_bodies=tuple(replace(b,x=target[0],y=target[1]) if b.identity==identity else b for b in world.bodies)
    result=replace(world,bodies=next_bodies,revision=world.revision+1)
    return result,Witness(world.fingerprint(),result.fingerprint(),identity,(dx,dy),(body.x,body.y),target,"MOVE")

def branch(world: World, new_identity: str):
    """Branch retains parent witness and independent state identity."""
    if not new_identity or new_identity==world.identity:
        raise ValueError("branch needs a distinct identity")
    return replace(world,identity=new_identity,parent=world.fingerprint(),revision=0)

def relations(world: World):
    """Shortest periodic signed offsets between bodies, preserving their identities."""
    output=[]
    for i,a in enumerate(world.bodies):
        for b in world.bodies[i+1:]:
            def wrap(d):
                return min((d,d-world.size,d+world.size),key=lambda v:(abs(v),v))
            output.append((a.identity,b.identity,wrap(b.x-a.x),wrap(b.y-a.y)))
    return tuple(output)
