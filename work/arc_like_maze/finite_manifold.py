"""Finite cubical 3-torus supporting the existing F_3 World transitions.

The quotient of a 3x3x3 periodic cubical lattice realizes T^3 as a
finite cubical complex. This is a combinatorial model of a 3-manifold,
not a claim that its 27 vertices form a smooth manifold.
"""
from collections import Counter, deque
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

    def action_closure(self, phi=(0, 1, 2)) -> dict:
        """Exhaustive permutation group generated by A and B on 27 states.

        This is finite closure under composition, not a claim about all
        possible worlds or smooth geometric invariants.
        """
        if self.side != 3:
            raise ValueError("closure requires the F_3 adapter")
        vertices = self.vertices()
        positions = {vertex: index for index, vertex in enumerate(vertices)}
        generators = {
            action: tuple(positions[self.transition(v, action, phi)] for v in vertices)
            for action in "AB"
        }
        identity = tuple(range(len(vertices)))
        seen = {identity: ""}
        pending = deque([identity])
        while pending:
            permutation = pending.popleft()
            for action, generator in generators.items():
                successor = tuple(generator[i] for i in permutation)
                if successor not in seen:
                    seen[successor] = seen[permutation] + action
                    pending.append(successor)
        edges = frozenset(
            frozenset(positions[v] for v in edge) for edge in self.edges()
        )
        geometries = {
            frozenset(frozenset(permutation[i] for i in edge) for edge in edges)
            for permutation in seen
        }
        overlap_counts = Counter(len(graph & edges) for graph in geometries)
        stabilizer_size = sum(
            frozenset(frozenset(permutation[i] for i in edge) for edge in edges) == edges
            for permutation in seen
        )
        length_distribution = Counter(map(len, seen.values()))
        return {
            "shortest_word_distribution": dict(sorted(length_distribution.items())),
            "permutations": len(seen),
            "distinct_edge_geometries": len(geometries),
            "reference_graph_stabilizer": stabilizer_size,
            "overlap_distribution": dict(sorted(overlap_counts.items())),
            "max_shortest_word_length": max(map(len, seen.values())),
        }

    def subgroup_structure(self, phi=(0, 1, 2)) -> dict:
        """Classify the reference-graph stabilizer within the generated group.

        The default phi=(0,1,2) yields the full translation group F_3^3.
        For other phi, report measured properties without asserting that form.
        """
        if self.side != 3:
            raise ValueError("subgroup requires the F_3 adapter")
        vertices = self.vertices()
        index = {v: i for i, v in enumerate(vertices)}
        generators = {
            action: tuple(index[self.transition(v, action, phi)] for v in vertices)
            for action in "AB"
        }
        identity = tuple(range(len(vertices)))
        seen = {identity}
        pending = deque([identity])
        while pending:
            permutation = pending.popleft()
            for generator in generators.values():
                successor = tuple(generator[i] for i in permutation)
                if successor not in seen:
                    seen.add(successor)
                    pending.append(successor)
        reference = frozenset(
            frozenset(index[v] for v in edge) for edge in self.edges()
        )
        stabilizer = {
            permutation for permutation in seen
            if frozenset(
                frozenset(permutation[i] for i in edge) for edge in reference
            ) == reference
        }
        translations = {
            tuple(index[tuple((v[k] + delta[k]) % 3 for k in range(3))]
                  for v in vertices)
            for delta in vertices
        }
        def compose(left, right):
            return tuple(left[i] for i in right)
        return {
            "full_group_order": len(seen),
            "stabilizer_order": len(stabilizer),
            "translation_order": len(translations),
            "stabilizer_equals_translations": stabilizer == translations,
            "stabilizer_abelian": all(
                compose(a, b) == compose(b, a)
                for a in stabilizer for b in stabilizer
            ),
            "stabilizer_normal": all(
                # Conjugation is tested without needing explicit inverses:
                # gH = Hg as sets for every g.
                {compose(g, h) for h in stabilizer}
                == {compose(h, g) for h in stabilizer}
                for g in seen
            ),
            "index": len(seen) // len(stabilizer),
        }

    def semidirect_product_structure(self) -> dict:
        """Verify G = F_3^3 ⋊ C_3 for the default World transitions.

        Composition convention: (f * g)(v) = f(g(v)).
        Conjugation by B on translation vectors is the linear shear
        (x,y,z) -> (x, y+x, z+y), all coordinates modulo 3.
        """
        if self.side != 3:
            raise ValueError("semidirect-product analysis requires side=3")
        vertices = self.vertices()
        index = {v: i for i, v in enumerate(vertices)}
        identity = tuple(range(27))
        def compose(left, right):
            return tuple(left[i] for i in right)
        def translation(delta):
            return tuple(index[tuple((v[k] + delta[k]) % 3 for k in range(3))]
                         for v in vertices)
        translations = {delta: translation(delta) for delta in vertices}
        b = tuple(index[self.transition(v, "B")] for v in vertices)
        b2 = compose(b, b)
        powers = (identity, b, b2)
        def shear(delta):
            x, y, z = delta
            return (x, (y + x) % 3, (z + y) % 3)
        # B inverse is B squared only if B has order exactly three.
        order_three = compose(b2, b) == identity and b != identity
        conjugation = all(
            compose(compose(b, t), b2) == translations[shear(delta)]
            for delta, t in translations.items()
        )
        normal_form = {
            compose(t, power)
            for t in translations.values() for power in powers
        }
        return {
            "translation_order": len(translations),
            "complement_order_three": order_three,
            "conjugation_matches_shear": conjugation,
            "shear_matrix_mod_3": ((1, 0, 0), (1, 1, 0), (0, 1, 1)),
            "normal_form_count": len(normal_form),
            "unique_translation_times_b_power": len(normal_form) == 81,
            "b_powers_intersect_translations_trivially": (
                all(power not in set(translations.values()) for power in powers[1:])
            ),
            "a_is_translation": tuple(
                index[self.transition(v, "A")] for v in vertices
            ) == translations[(1, 0, 0)],
        }

    def lower_central_structure(self) -> dict:
        """Exhaustively determine center, commutators and lower central series.

        Permutations act on the left: (f*g)(v) = f(g(v)).
        No group classification is assumed in the enumeration.
        """
        if self.side != 3:
            raise ValueError("group analysis requires side=3")
        vertices = self.vertices()
        index = {v: i for i, v in enumerate(vertices)}
        identity = tuple(range(len(vertices)))
        generators = [
            tuple(index[self.transition(v, a)] for v in vertices)
            for a in "AB"
        ]
        def mul(a, b):
            return tuple(a[i] for i in b)
        def inverse(p):
            out = [0] * len(p)
            for i, j in enumerate(p):
                out[j] = i
            return tuple(out)
        def closure(gens):
            seen = {identity}
            pending = deque([identity])
            while pending:
                g = pending.popleft()
                for h in gens:
                    gh = mul(g, h)
                    if gh not in seen:
                        seen.add(gh)
                        pending.append(gh)
            return seen
        group = closure(generators)
        inverses = {g: inverse(g) for g in group}
        def commutator(a, b):
            return mul(mul(mul(a, b), inverses[a]), inverses[b])
        center = {
            g for g in group
            if all(mul(g, h) == mul(h, g) for h in generators)
        }
        derived = closure({
            commutator(a, b) for a in group for b in group
        })
        lower = [group]
        while lower[-1] != {identity}:
            nxt = closure({
                commutator(a, b)
                for a in lower[-1] for b in generators
            })
            if nxt == lower[-1]:
                break
            lower.append(nxt)
        return {
            "group_order": len(group),
            "center_order": len(center),
            "commutator_subgroup_order": len(derived),
            "lower_central_orders": [len(level) for level in lower],
            "nilpotency_class": (
                len(lower) - 1 if lower[-1] == {identity} else None
            ),
            "derived_is_abelian": all(
                mul(a, b) == mul(b, a)
                for a in derived for b in derived
            ),
            "center_elements_are_translations": all(
                all(
                    vertices[g[index[v]]] ==
                    tuple((v[k] + vertices[g[index[(0, 0, 0)]]][k]) % 3
                          for k in range(3))
                    for v in vertices
                )
                for g in center
            ),
        }

    def element_order_structure(self) -> dict:
        """Enumerate element orders and exponent in the finite A/B group."""
        if self.side != 3:
            raise ValueError("element-order analysis requires side=3")
        vertices = self.vertices()
        positions = {v: i for i, v in enumerate(vertices)}
        identity = tuple(range(len(vertices)))
        generators = [
            tuple(positions[self.transition(v, a)] for v in vertices)
            for a in "AB"
        ]
        def compose(left, right):
            return tuple(left[i] for i in right)
        seen = {identity}
        pending = deque([identity])
        while pending:
            current = pending.popleft()
            for generator in generators:
                next_perm = compose(generator, current)
                if next_perm not in seen:
                    seen.add(next_perm)
                    pending.append(next_perm)
        orders = Counter()
        for element in seen:
            power = identity
            for n in range(1, len(seen) + 1):
                power = compose(element, power)
                if power == identity:
                    orders[n] += 1
                    break
            else:
                raise AssertionError("element order exceeds group order")
        from math import lcm
        exponent = lcm(*orders.keys())
        return {
            "group_order": len(seen),
            "order_distribution": dict(sorted(orders.items())),
            "exponent": exponent,
            "has_element_order_9": orders[9] > 0,
            "has_element_order_27": orders[27] > 0,
            "all_orders_divide_exponent": all(exponent % k == 0 for k in orders),
        }

    def group_presentation_verification(self) -> dict:
        """Check a finite presentation via the faithful 27-point action.

        Generators x,y,z are unit translations and b is the World B map.
        Relations: x^3=y^3=z^3=b^3=1; [x,y]=[x,z]=[y,z]=1;
        b*x*b^-1=x*y, b*y*b^-1=y*z, b*z*b^-1=z.
        Every word reduces to x^i*y^j*z^k*b^l (i,j,k,l in F_3).
        """
        if self.side != 3:
            raise ValueError("presentation verification requires side=3")
        vertices = self.vertices()
        index = {v: i for i, v in enumerate(vertices)}
        identity = tuple(range(len(vertices)))
        def compose(a, b):
            return tuple(a[i] for i in b)
        def power(g, n):
            out = identity
            for _ in range(n):
                out = compose(out, g)
            return out
        def translation(delta):
            return tuple(
                index[tuple((v[k] + delta[k]) % 3 for k in range(3))]
                for v in vertices
            )
        x = translation((1, 0, 0))
        y = translation((0, 1, 0))
        z = translation((0, 0, 1))
        b = tuple(index[self.transition(v, "B")] for v in vertices)
        bi = power(b, 2)
        gens = (x, y, z, b)
        order_three = all(power(g, 3) == identity for g in gens)
        translations_commute = all(
            compose(a, c) == compose(c, a)
            for a in (x, y, z) for c in (x, y, z)
        )
        conjugation = (
            compose(compose(b, x), bi) == compose(x, y)
            and compose(compose(b, y), bi) == compose(y, z)
            and compose(compose(b, z), bi) == z
        )
        normal_forms = {
            compose(
                compose(compose(power(x, i), power(y, j)), power(z, k)),
                power(b, ell),
            )
            for i, j, k, ell in product(range(3), repeat=4)
        }
        generated = {identity}
        queue = deque([identity])
        while queue:
            g = queue.popleft()
            for h in (x, b):
                gh = compose(g, h)
                if gh not in generated:
                    generated.add(gh)
                    queue.append(gh)
        return {
            "generators_order_three": order_three,
            "translations_commute": translations_commute,
            "conjugation_relations": conjugation,
            "normal_form_count": len(normal_forms),
            "generated_by_a_b_count": len(generated),
            "normal_forms_equal_generated_group": normal_forms == generated,
            "a_equals_x": tuple(index[self.transition(v, "A")] for v in vertices) == x,
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
