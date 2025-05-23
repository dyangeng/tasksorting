from __future__ import annotations
from typing import Dict, List, Tuple
import itertools, math, random

from models.tasks import Task
from models.map   import Coordinate


# ───────────────────── helpers ──────────────────────
def _dist(a: Coordinate, b: Coordinate) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])        # Manhattan


def _path_cost(seq: List[str], loc: Dict[str, Coordinate]) -> int:
    """Sum of distances along a station-name sequence."""
    return sum(_dist(loc[s1], loc[s2]) for s1, s2 in zip(seq, seq[1:]))


def _best_perm(stations: List[str],
               loc: Dict[str, Coordinate],
               start_pos: Coordinate) -> List[str]:
    """
    Return the cheapest ordering of `stations`, *starting* at `start_pos`.
    (Brute-force because len(stations) ≤ 3.)
    """
    best, best_cost = None, math.inf
    for perm in itertools.permutations(stations):
        cost = _dist(start_pos, loc[perm[0]]) + _path_cost(list(perm), loc)
        if cost < best_cost:
            best, best_cost = perm, cost
    return list(best)


# ───────────────────── main entry --––––─────────────
def sort_tasks(tasks: List[Task],
               station_loc : Dict[str, Coordinate],
               start: Coordinate,
               end  : Coordinate,
               cap: int = 3) -> List[Task]:
    """
    Return a new task list such that:
        • robot starts empty at `start`
        • never carries > `cap` objects
        • ends at `end`
    """

    # ---- 1. split tasks into pick/place pairs keyed by object ---- #
    # works because generate_tasks.py always outputs Pick then Place rows
    pairs: Dict[str, Tuple[Task, Task]] = {}
    for t in tasks:
        key = f"{t.objects[0]}"          # object name is unique per pair
        pairs.setdefault(key, [None, None])
        if "pick" in t.task_name.lower():
            pairs[key][0] = t
        else:
            pairs[key][1] = t
    # sanity
    pairs = {k: tuple(v) for k, v in pairs.items() if None not in v}

    remaining = set(pairs.keys())
    plan: List[Task] = []
    cur_pos = start

    # ---- 2. repeatedly load ≤ cap objects, then deliver them ---- #
    while remaining:
        # ---- pick phase ---------------------------------------- #
        batch = random.sample(remaining, k=min(cap, len(remaining)))
        batch_picks  = [pairs[k][0] for k in batch]

        # best order to *pick* this mini-TSP
        pick_order_names = _best_perm(
            [t.station for t in batch_picks], station_loc, cur_pos)
        for name in pick_order_names:
            task = next(t for t in batch_picks if t.station == name)
            plan.append(task)
            cur_pos = station_loc[name]

        # ---- place phase --------------------------------------- #
        batch_places = [pairs[k][1] for k in batch]
        place_order_names = _best_perm(
            [t.station for t in batch_places], station_loc, cur_pos)
        for name in place_order_names:
            task = next(t for t in batch_places if t.station == name)
            plan.append(task)
            cur_pos = station_loc[name]

        # done with these objects
        remaining -= set(batch)

    # optional: let caller move to END after plan is executed
    return plan
