"""Explicit search-tree constructors for the three requested problems."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Iterable, TypeVar

State = TypeVar("State", bound=Hashable)
Action = TypeVar("Action")


@dataclass(frozen=True)
class SearchResult(Generic[State, Action]):
    states: tuple[State, ...]
    actions: tuple[Action, ...]
    expanded: int
    tree: dict[State, tuple[State, ...]]


def breadth_first_tree(
    initial: State,
    goal: Callable[[State], bool],
    successors: Callable[[State], Iterable[tuple[Action, State]]],
    max_nodes: int = 100_000,
) -> SearchResult[State, Action] | None:
    """Construct a BFS tree and return its shortest root-to-goal path."""
    frontier = deque([initial])
    parent: dict[State, tuple[State, Action] | None] = {initial: None}
    tree: dict[State, tuple[State, ...]] = {}
    expanded = 0
    while frontier and len(parent) <= max_nodes:
        state = frontier.popleft()
        expanded += 1
        if goal(state):
            states: list[State] = []
            actions: list[Action] = []
            cursor = state
            while True:
                states.append(cursor)
                edge = parent[cursor]
                if edge is None:
                    break
                cursor, action = edge
                actions.append(action)
            return SearchResult(
                tuple(reversed(states)), tuple(reversed(actions)), expanded, tree
            )
        children = []
        for action, child in successors(state):
            children.append(child)
            if child not in parent:
                parent[child] = (state, action)
                frontier.append(child)
        tree[state] = tuple(children)
    return None


# ------------------------------- 8-Puzzle ----------------------------------
Puzzle = tuple[int, ...]
PUZZLE_GOAL: Puzzle = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def puzzle_successors(state: Puzzle) -> Iterable[tuple[str, Puzzle]]:
    blank = state.index(0)
    row, column = divmod(blank, 3)
    for action, dr, dc in (("up", -1, 0), ("down", 1, 0), ("left", 0, -1), ("right", 0, 1)):
        nr, nc = row + dr, column + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            target = nr * 3 + nc
            child = list(state)
            child[blank], child[target] = child[target], child[blank]
            yield action, tuple(child)


def puzzle_is_solvable(state: Puzzle) -> bool:
    values = [value for value in state if value]
    inversions = sum(values[i] > values[j] for i in range(8) for j in range(i + 1, 8))
    return inversions % 2 == 0


def solve_8_puzzle(initial: Puzzle) -> SearchResult[Puzzle, str] | None:
    if len(initial) != 9 or set(initial) != set(range(9)):
        raise ValueError("8-Puzzle state must be a permutation of 0..8")
    if not puzzle_is_solvable(initial):
        return None
    return breadth_first_tree(initial, lambda state: state == PUZZLE_GOAL, puzzle_successors)


# ---------------------- Missionaries and Cannibals -------------------------
# (missionaries_left, cannibals_left, boat_side), boat_side: 0 left, 1 right
MCState = tuple[int, int, int]


def _mc_safe(missionaries: int, cannibals: int, total: int) -> bool:
    if not (0 <= missionaries <= total and 0 <= cannibals <= total):
        return False
    right_m, right_c = total - missionaries, total - cannibals
    return (missionaries == 0 or missionaries >= cannibals) and (
        right_m == 0 or right_m >= right_c
    )


def mc_successors(state: MCState, total: int = 3) -> Iterable[tuple[str, MCState]]:
    missionaries, cannibals, boat = state
    direction = -1 if boat == 0 else 1
    for moved_m, moved_c in ((1, 0), (2, 0), (0, 1), (0, 2), (1, 1)):
        child = (
            missionaries + direction * moved_m,
            cannibals + direction * moved_c,
            1 - boat,
        )
        if _mc_safe(child[0], child[1], total):
            action = f"move {moved_m}M {moved_c}C {'right' if boat == 0 else 'left'}"
            yield action, child


def solve_missionaries(total: int = 3) -> SearchResult[MCState, str] | None:
    if total < 1:
        raise ValueError("total must be positive")
    return breadth_first_tree(
        (total, total, 0), lambda state: state == (0, 0, 1), lambda s: mc_successors(s, total)
    )


# ---------------------- Rotating Workforce Scheduling ---------------------
# A shift pattern is a binary tuple across the planning days. State is
# (next_pattern_index, remaining_demand_tuple, chosen_worker_counts_tuple).
WorkState = tuple[int, tuple[int, ...], tuple[int, ...]]


def solve_workforce(
    demand: tuple[int, ...],
    patterns: tuple[tuple[int, ...], ...],
    max_workers_per_pattern: int | None = None,
) -> SearchResult[WorkState, str] | None:
    """Build a BFS decision tree for repeating rotation-pattern assignments."""
    if not demand or any(value < 0 for value in demand):
        raise ValueError("demand must contain non-negative values")
    if not patterns or any(len(pattern) != len(demand) for pattern in patterns):
        raise ValueError("every pattern must have one value per day")
    cap = max(demand) if max_workers_per_pattern is None else max_workers_per_pattern
    initial: WorkState = (0, demand, ())

    def goal(state: WorkState) -> bool:
        index, remaining, _ = state
        return index == len(patterns) and all(value == 0 for value in remaining)

    def successors(state: WorkState) -> Iterable[tuple[str, WorkState]]:
        index, remaining, counts = state
        if index >= len(patterns):
            return
        pattern = patterns[index]
        # Larger useful assignments enter first; BFS still minimizes tree depth,
        # while the per-layer choice represents one pattern decision.
        useful_cap = max(
            (remaining[d] + pattern[d] - 1) // pattern[d]
            for d in range(len(demand))
            if pattern[d]
        ) if any(pattern) else 0
        for workers in range(min(cap, useful_cap), -1, -1):
            new_remaining = tuple(
                max(0, remaining[d] - workers * pattern[d]) for d in range(len(demand))
            )
            yield f"pattern {index}: {workers} workers", (index + 1, new_remaining, counts + (workers,))

    return breadth_first_tree(initial, goal, successors)


DEFAULT_ROTATIONS = tuple(
    tuple(1 if offset in (0, 1, 2, 3, 4) else 0 for offset in ((day - start) % 7 for day in range(7)))
    for start in range(7)
)

