"""Infer simple involutive geometric generators from a payload/target relation.

No AR25 tags or predeclared axis type are required by the search layer.
Candidate transforms are inferred from point correspondences and retained only
when they are involutions and preserve the integer lattice.
"""

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

Point=tuple[int,int]

@dataclass(frozen=True)
class AffineMap:
    # integer affine map p -> A p + b
    a11:int; a12:int; a21:int; a22:int
    b1:int; b2:int
    name:str=""

    def __call__(self,p:Point)->Point:
        x,y=p
        return (self.a11*x+self.a12*y+self.b1,
                self.a21*x+self.a22*y+self.b2)

    def compose(self,other:"AffineMap")->"AffineMap":
        return AffineMap(
            self.a11*other.a11+self.a12*other.a21,
            self.a11*other.a12+self.a12*other.a22,
            self.a21*other.a11+self.a22*other.a21,
            self.a21*other.a12+self.a22*other.a22,
            self.a11*other.b1+self.a12*other.b2+self.b1,
            self.a21*other.b1+self.a22*other.b2+self.b2,
            name=f"{self.name}o{other.name}",
        )

    def is_involution(self)->bool:
        c=self.compose(self)
        return (c.a11,c.a12,c.a21,c.a22,c.b1,c.b2)==(1,0,0,1,0,0)

ID=AffineMap(1,0,0,1,0,0,"id")

# Orthogonal lattice involution linear parts. Translation terms are inferred.
LINEAR_INVOLUTIONS=[
    (1,0,0,-1,"reflect_y_const"),
    (-1,0,0,1,"reflect_x_const"),
    (0,1,1,0,"reflect_diag"),
    (0,-1,-1,0,"reflect_anti_diag"),
    (-1,0,0,-1,"half_turn"),
]

def infer_b_for_pair(A:tuple[int,int,int,int,str],p:Point,q:Point)->AffineMap:
    a11,a12,a21,a22,name=A
    x,y=p;u,v=q
    b1=u-(a11*x+a12*y)
    b2=v-(a21*x+a22*y)
    return AffineMap(a11,a12,a21,a22,b1,b2,name)

def candidate_involutions(points:Iterable[Point])->set[AffineMap]:
    pts=list(points)
    out=set()
    for p in pts:
        for q in pts:
            for A in LINEAR_INVOLUTIONS:
                f=infer_b_for_pair(A,p,q)
                if f.is_involution():
                    out.add(f)
    return out

def orbit(seed:Iterable[Point],gens:Iterable[AffineMap],limit:int=256)->set[Point]:
    seen=set(seed)
    frontier=list(seed)
    gs=list(gens)
    while frontier and len(seen)<=limit:
        p=frontier.pop()
        for g in gs:
            q=g(p)
            if q not in seen:
                seen.add(q);frontier.append(q)
    return seen

def clipped(points:Iterable[Point],width:int,height:int)->set[Point]:
    return {(x,y) for x,y in points if 0<=x<width and 0<=y<height}
