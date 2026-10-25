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

    def edges(self) -> frozenset[frozenset[Vertex]]:
        """Undirected one-step edges of the reference cubical 1-skeleton."""
        return frozenset(
            frozenset((v, neighbor))
            for v in self.vertices()
            for neighbor in self.neighbors(v)
        )

    def transported_edges(self, action: str, phi=(0, 1, 2)) -> frozenset[frozenset[Vertex]]:
        """Push forward the original edge relation along a state permutation.

        A transported edge may not be an edge in the original cubical lattice.
        This records a transformed relation, not a new smooth manifold.
        """
        return frozenset(
            frozenset(self.transition(v, action, phi) for v in edge)
            for edge in self.edges()
        )

    def geometry_comparison(self, action: str, phi=(0, 1, 2)) -> dict:
        """Compare fixed adjacency with the action-transported adjacency."""
        original = self.edges()
        transported = self.transported_edges(action, phi)
        return {
            "action": action,
            "original_edges": len(original),
            "transported_edges": len(transported),
            "preserved_edges": len(original & transported),
            "lost_edges": len(original - transported),
            "introduced_edges": len(transported - original),
            "is_graph_automorphism": original == transported,
        }

    def apply_word(self, vertex: Vertex, actions: str, phi=(0, 1, 2)) -> Vertex:
        """Apply an ordered action word using the original finite World."""
        if any(action not in "AB" for action in actions):
            raise ValueError("only A and B are admitted")
        current = vertex
        for action in actions:
            current = self.transition(current, action, phi)
        return current

    def transported_edges_word(self, actions: str, phi=(0, 1, 2)) -> frozenset[frozenset[Vertex]]:
        """Transport every original edge through the full action word."""
        return frozenset(
            frozenset(self.apply_word(v, actions, phi) for v in edge)
            for edge in self.edges()
        )

    def trace_geometry(self, actions: str, phi=(0, 1, 2)) -> tuple[dict, ...]:
        """Track reference-edge overlap and relative transported-edge changes.

        Transported geometry is always graph-isomorphic to the starting graph
        when each action is bijective; overlap with the fixed graph may vary.
        """
        original = self.edges()
        previous = original
        records = []
        for index in range(len(actions) + 1):
            word = actions[:index]
            current = self.transported_edges_word(word, phi)
            records.append({
                "step": index,
                "word": word,
                "edges": len(current),
                "fixed_overlap": len(original & current),
                "fixed_lost": len(original - current),
                "previous_overlap": len(previous & current),
                "is_fixed_automorphism": original == current,
            })
            previous = current
        return tuple(records)

    def permutation_signature(self, actions: str, phi=(0, 1, 2)) -> tuple[Vertex, ...]:
        """Canonical finite signature of the full state permutation."""
        return tuple(self.apply_word(v, actions, phi) for v in self.vertices())

    def geometry_return_analysis(self, actions: str, phi=(0, 1, 2)) -> dict:
        """Find first repeated transported graph and first repeated permutation.

        These are distinct return criteria: graph recurrence does not imply
        the state permutation itself has returned.
        """
        initial = self.edges()
        seen_graph = {initial: 0}
        initial_perm = self.permutation_signature("", phi)
        seen_perm = {initial_perm: 0}
        first_graph_repeat = None
        first_permutation_repeat = None
        first_graph_return = None
        first_permutation_return = None
        for index in range(1, len(actions) + 1):
            prefix = actions[:index]
            graph = self.transported_edges_word(prefix, phi)
            perm = self.permutation_signature(prefix, phi)
            if graph in seen_graph and first_graph_repeat is None:
                first_graph_repeat = (seen_graph[graph], index)
            else:
                seen_graph.setdefault(graph, index)
            if perm in seen_perm and first_permutation_repeat is None:
                first_permutation_repeat = (seen_perm[perm], index)
            else:
                seen_perm.setdefault(perm, index)
            if graph == initial and first_graph_return is None:
                first_graph_return = index
            if perm == initial_perm and first_permutation_return is None:
                first_permutation_return = index
        return {
            "word": actions,
            "first_graph_repeat": first_graph_repeat,
            "first_permutation_repeat": first_permutation_repeat,
            "first_graph_return": first_graph_return,
            "first_permutation_return": first_permutation_return,
            "distinct_graphs": len(seen_graph),
            "distinct_permutations": len(seen_perm),
        }

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
