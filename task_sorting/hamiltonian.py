"""task_sorting_optimized.py

A faster, memory‑lean pipeline for RoboCup@Work pick‑and‑place.

Highlights
----------
* **Hybrid TSP** – exact bit‑mask DP for ≤ 12 stations; NN + 2‑opt afterwards.
* **Distance caching** – `math.hypot` + `@lru_cache` slashes duplicate work.
* **Greedy batching** – `heapq.nsmallest` chooses the cheapest ≤ *cap* objects.
* **3‑object load limit** baked in (override with `cap`).
* Drop‑in compatible: public signature is still `sort_tasks(tasks, station_loc, start, end=None, cap=3)`.

"""

from __future__ import annotations

import functools
import heapq
import itertools
import math
from typing import Dict, List, Sequence, Tuple

# Project models – adjust import paths if required
from models.tasks import Task
from models.map import Coordinate  # Coordinate = tuple[float, float]

__all__ = [
    "sort_tasks",
]

# ---------------------------------------------------------------------------
#  Distance helpers
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def _euclidean(a: Coordinate, b: Coordinate) -> float:  # noqa: D401
    """Fast Euclidean distance via `math.hypot`, memoised."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------------------------------------------------------------------
#  Quick heuristics (when exact DP is too slow)
# ---------------------------------------------------------------------------

def _nearest_neighbour(stations: Sequence[str], coords: Dict[str, Coordinate], start: Coordinate) -> List[str]:
    unvisited = set(stations)
    current = min(unvisited, key=lambda s: _euclidean(start, coords[s]))
    route = [current]
    unvisited.remove(current)
    while unvisited:
        nxt = min(unvisited, key=lambda s: _euclidean(coords[current], coords[s]))
        route.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    return route


def _tour_length(tour: List[str], coords: Dict[str, Coordinate], start: Coordinate) -> float:
    if not tour:
        return 0.0
    dist = _euclidean(start, coords[tour[0]])
    for a, b in zip(tour, tour[1:]):
        dist += _euclidean(coords[a], coords[b])
    return dist


def _two_opt(tour: List[str], coords: Dict[str, Coordinate], start: Coordinate, rounds: int = 2) -> List[str]:
    best = tour
    best_len = _tour_length(best, coords, start)
    n = len(tour)
    for _ in range(rounds):
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue  # adjacent – skip
                new = best[:i] + best[i:j][::-1] + best[j:]
                new_len = _tour_length(new, coords, start)
                if new_len < best_len - 1e-6:
                    best, best_len = new, new_len
                    improved = True
        if not improved:
            break
    return best


# ---------------------------------------------------------------------------
#  Exact / hybrid TSP solver (Hamiltonian path from *start*)
# ---------------------------------------------------------------------------

def _tsp_order(stations: Sequence[str], coords: Dict[str, Coordinate], start: Coordinate) -> List[str]:
    """Return stations in near‑optimal visiting order.

    * n ≤ 12 → exact O(2ⁿ n²) DP (still fast for cap ≤ 3).
    * n > 12 → NN heuristic + light 2‑opt.
    """
    n = len(stations)
    if n <= 1:
        return list(stations)
    if n <= 3:  # brute force tiny cases
        best, best_cost = list(stations), math.inf
        for perm in itertools.permutations(stations):
            cost = _euclidean(start, coords[perm[0]]) + sum(
                _euclidean(coords[perm[i]], coords[perm[i + 1]]) for i in range(n - 1)
            )
            if cost < best_cost:
                best_cost, best = cost, list(perm)
        return best

    if n > 12:
        return _two_opt(_nearest_neighbour(stations, coords, start), coords, start)

    # --- exact DP for n ≤ 12 ------------------------------------------------
    # Cache pairwise distances to avoid repeated look‑ups
    dist = [[_euclidean(coords[a], coords[b]) for b in stations] for a in stations]
    start_d = [_euclidean(start, coords[s]) for s in stations]

    @functools.lru_cache(maxsize=None)
    def dp(mask: int, last: int) -> float:
        if mask == 0:
            return start_d[last]
        best = math.inf
        m = mask
        while m:
            j = (m & -m).bit_length() - 1  # next set‑bit index
            m ^= 1 << j
            cand = dp(mask ^ (1 << j), j) + dist[j][last]
            if cand < best:
                best = cand
        return best

    full = (1 << n) - 1
    last = min(range(n), key=lambda j: dp(full ^ (1 << j), j) + start_d[j])
    order_idx = [last]
    mask = full ^ (1 << last)

    while mask:
        nxt = min(
            (j for j in range(n) if mask & (1 << j)),
            key=lambda j: dp(mask ^ (1 << j), j) + dist[j][last],
        )
        order_idx.append(nxt)
        mask ^= 1 << nxt
        last = nxt

    return [stations[i] for i in reversed(order_idx)]


# ---------------------------------------------------------------------------
#  Greedy batching under load constraint
# ---------------------------------------------------------------------------

def _select_batch(objs: List[str], pick: Dict[str, str], place: Dict[str, str], loc: Dict[str, Coordinate], cur: Coordinate, cap: int) -> List[str]:
    if len(objs) <= cap:
        return list(objs)
    # (estimated_cost, obj) pairs – cheapest *cap* chosen
    costs = (
        (_euclidean(cur, loc[pick[o]]) + _euclidean(loc[pick[o]], loc[place[o]]), o)
        for o in objs
    )
    return [o for _, o in heapq.nsmallest(cap, costs)]


# ---------------------------------------------------------------------------
#  Public planner
# ---------------------------------------------------------------------------

def sort_tasks(
    tasks: List[Task],
    station_loc: Dict[str, Coordinate],
    start: Coordinate,
    end: Coordinate | None = None,
    cap: int = 3,
) -> List[Task]:
    """Return tasks ordered for efficient execution while holding ≤ *cap* items."""
    # Build object → (pickTask, placeTask)
    pairs: Dict[str, Tuple[Task | None, Task | None]] = {}
    for t in tasks:
        if not t.objects:
            continue
        obj_key = t.objects[0]
        if obj_key not in pairs:
            pairs[obj_key] = [None, None]  # type: ignore[list-item]
        if "pick" in t.task_name.lower():
            pairs[obj_key][0] = t  # type: ignore[index]
        elif "place" in t.task_name.lower():
            pairs[obj_key][1] = t  # type: ignore[index]

    complete_pairs: Dict[str, Tuple[Task, Task]] = {
        k: (p, q)  # type: ignore[assignment]
        for k, (p, q) in pairs.items()
        if p is not None and q is not None
    }
    if not complete_pairs:
        return []

    pick_map = {k: pick.station for k, (pick, _) in complete_pairs.items()}
    place_map = {k: place.station for k, (_, place) in complete_pairs.items()}

    remaining = list(complete_pairs.keys())
    current = start
    plan: List[Task] = []

    while remaining:
        batch = _select_batch(remaining, pick_map, place_map, station_loc, current, cap)

        # -- Pick sequence ---------------------------------------------------
        pick_stations = [pick_map[o] for o in batch]
        for s in _tsp_order(pick_stations, station_loc, current):
            obj = next(o for o in batch if pick_map[o] == s)
            plan.append(complete_pairs[obj][0])
            current = station_loc[s]

        # -- Place sequence --------------------------------------------------
        place_stations = [place_map[o] for o in batch]
        for s in _tsp_order(place_stations, station_loc, current):
            obj = next(o for o in batch if place_map[o] == s)
            plan.append(complete_pairs[obj][1])
            current = station_loc[s]

        for o in batch:
            remaining.remove(o)

    # Optionally finish at *end* (movement task not modelled here)
    return plan
