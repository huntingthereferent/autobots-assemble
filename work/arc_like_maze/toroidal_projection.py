"""Read-only, growing periodic projection of source-owned repository objects.

This does not redefine the A/B World or mutate the source repository.
"""
from dataclasses import dataclass
from math import isqrt


@dataclass(frozen=True)
class ToroidalProjection:
    side: int
    positions: tuple[tuple[str, tuple[int, int]], ...]

    def __post_init__(self):
        if self.side < 1:
            raise ValueError("side must be positive")
        names = [name for name, _ in self.positions]
        if len(names) != len(set(names)):
            raise ValueError("object identities must be unique")
        if any(not (0 <= x < self.side and 0 <= y < self.side)
               for _, (x, y) in self.positions):
            raise ValueError("position outside periodic world")

    @classmethod
    def from_paths(cls, paths, side=48):
        """Deterministic collision-free row-major layout; no semantic claims."""
        names = tuple(sorted(set(paths)))
        if len(names) != len(tuple(paths)):
            raise ValueError("duplicate source paths")
        size = side
        while size * size < len(names):
            size *= 2
        return cls(size, tuple((p, (i % size, i // size))
                               for i, p in enumerate(names)))

    def grow(self, factor=2):
        """Embed W_N in W_(factor*N) by scaling both coordinates."""
        if not isinstance(factor, int) or factor < 2:
            raise ValueError("growth factor must be an integer >= 2")
        return ToroidalProjection(
            self.side * factor,
            tuple((name, (x * factor, y * factor))
                  for name, (x, y) in self.positions),
        )

    def move(self, name, delta):
        """Move one projected object on the periodic world."""
        if len(delta) != 2 or any(not isinstance(v, int) for v in delta):
            raise ValueError("movement must be an integer 2-vector")
        if name not in dict(self.positions):
            raise KeyError(name)
        dx, dy = delta
        return ToroidalProjection(
            self.side,
            tuple((p, ((xy[0] + dx) % self.side,
                       (xy[1] + dy) % self.side)) if p == name else (p, xy)
                  for p, xy in self.positions),
        )

    def displacement(self, name, other):
        """Directed periodic coordinate displacement (not a source relation)."""
        points = dict(self.positions)
        a, b = points[name], points[other]
        return ((b[0] - a[0]) % self.side, (b[1] - a[1]) % self.side)

    def validate_growth(self, grown, factor):
        """Check the old coordinate differences survive under scaling."""
        if grown.side != self.side * factor:
            return False
        before, after = dict(self.positions), dict(grown.positions)
        return set(before) == set(after) and all(
            after[name] == ((xy[0] * factor) % grown.side,
                            (xy[1] * factor) % grown.side)
            for name, xy in before.items()
        )
