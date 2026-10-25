"""Finite cubical 3-torus supporting the existing F_3 World transitions.

The quotient of a 3x3x3 periodic cubical lattice realizes T^3 as a
finite cubical complex. This is a combinatorial model of a 3-manifold,
not a claim that its 27 vertices form a smooth manifold.
"""
from dataclasses import dataclass
from itertools import combinations, product
from work.arc_like_maze.math import World

Vertex = tuple[int, int, int]


@dataclass(frozen=True)
class FiniteTorus3:
    side: int = 3

    def __post_init__(self):
        if self.side < 3:
            raise ValueError("side must be >= 3 for distinct cubical cells")

    def vertices(self) -> tuple[Vertex, ...]:
        return tuple(product(range(self.side), repeat=3))

    def cell(self, base: Vertex, axes: tuple[int, ...]) -> frozenset[Vertex]:
        """Vertices of a periodic cube face, identified by base and active axes."""
        if len(set(axes)) != len(axes) or any(a not in (0, 1, 2) for a in axes):
            raise ValueError("invalid axes")
        return frozenset(
            tuple((base[i] + (int(i in subset))) % self.side for i in range(3))
            for count in range(len(axes) + 1)
            for subset in combinations(axes, count)
        )

    def cells(self, dimension: int) -> frozenset[frozenset[Vertex]]:
        if dimension not in (0, 1, 2, 3):
            raise ValueError("dimension must be 0..3")
        return frozenset(
            self.cell(v, axes)
            for v in self.vertices()
            for axes in combinations(range(3), dimension)
        )

    def f_vector(self) -> tuple[int, int, int, int]:
        return tuple(len(self.cells(k)) for k in range(4))

    def neighbors(self, v: Vertex) -> frozenset[Vertex]:
        if v not in self.vertices():
            raise ValueError("vertex outside world")
        return frozenset(
            tuple((v[j] + (direction if j == axis else 0)) % self.side for j in range(3))
            for axis in range(3) for direction in (-1, 1)
        )

    def transition(self, vertex: Vertex, action: str, phi=(0, 1, 2)) -> Vertex:
        """Use the repository's original World.step, without redefining A/B."""
        if self.side != 3:
            raise ValueError("World uses F_3: side must be 3 for this adapter")
        return World(3, phi).step(vertex, action)

    def verify(self) -> dict:
        counts = self.f_vector()
        return {
            "f_vector": counts,
            "euler_characteristic": counts[0] - counts[1] + counts[2] - counts[3],
            "degree_six": all(len(self.neighbors(v)) == 6 for v in self.vertices()),
            "transition_closed": all(
                self.transition(v, a) in self.vertices()
                for v in self.vertices() for a in "AB"
            ) if self.side == 3 else None,
            "transition_bijective": all(
                len({self.transition(v, a) for v in self.vertices()}) == len(self.vertices())
                for a in "AB"
            ) if self.side == 3 else None,
        }
