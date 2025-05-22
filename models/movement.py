from __future__ import annotations
import heapq
from typing import Dict, List, Set, Tuple

Coordinate = Tuple[int, int]  # (row, col)


def _a_star(start: Coordinate, goal: Coordinate, rows: int, cols: int,
            obstacles: Set[Coordinate]) -> List[Coordinate]:
    """Classic 4‑neighbour A* search on a rectangular grid."""

    def in_bounds(c: Coordinate) -> bool:
        r, c1 = c
        return 0 <= r < rows and 0 <= c1 < cols

    def neighbours(c: Coordinate):
        r, c1 = c
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n = (r + dr, c1 + dc)
            if in_bounds(n) and n not in obstacles:
                yield n

    h = lambda c: abs(c[0] - goal[0]) + abs(c[1] - goal[1])  # Manhattan

    frontier: List[Tuple[int, int, Coordinate]] = [(h(start), 0, start)]
    g_cost: Dict[Coordinate, int] = {start: 0}
    parent: Dict[Coordinate, Coordinate] = {}

    while frontier:
        f, g, cur = heapq.heappop(frontier)
        if cur == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            path.reverse()
            return path
        for nb in neighbours(cur):
            ng = g + 1
            if nb not in g_cost or ng < g_cost[nb]:
                g_cost[nb] = ng
                parent[nb] = cur
                heapq.heappush(frontier, (ng + h(nb), ng, nb))

    raise RuntimeError("No path found – check obstacle layout")


def _elastic_band(path: List[Coordinate], obstacles: Set[Coordinate], *,
                  iterations: int = 200, spring: float = 0.3,
                  repel: float = 2.0, obstacle_radius: float = 1.5
                  ) -> List[Tuple[float, float]]:
    """Simple elastic‑band (TEB‑style) smoothing over an A* seed path."""

    pts = [[float(r), float(c)] for r, c in path]
    r_sq = obstacle_radius ** 2

    for _ in range(iterations):
        for i in range(1, len(pts) - 1):
            prev, cur, nxt = pts[i - 1], pts[i], pts[i + 1]
            # spring force
            cur[0] += spring * ((prev[0] + nxt[0]) / 2 - cur[0])
            cur[1] += spring * ((prev[1] + nxt[1]) / 2 - cur[1])
            # obstacle repulsion
            fx = fy = 0.0
            for ox, oy in obstacles:
                dx, dy = cur[0] - ox, cur[1] - oy
                d2 = dx * dx + dy * dy or 1e-6
                if d2 < r_sq:
                    fac = 1.0 / d2 - 1.0 / r_sq
                    fx += dx * fac
                    fy += dy * fac
            cur[0] += repel * fx
            cur[1] += repel * fy

    return [(p[0], p[1]) for p in pts]


def plan_path(rows: int, cols: int, start: Coordinate, goal: Coordinate,
              obstacles: Set[Coordinate], *, smooth: bool = True
              ) -> List[Tuple[float, float]]:
    """Public API – A* path, optionally smoothed."""
    grid_path = _a_star(start, goal, rows, cols, obstacles)
    if smooth:
        return _elastic_band(grid_path, obstacles)
    return [(float(r), float(c)) for r, c in grid_path]