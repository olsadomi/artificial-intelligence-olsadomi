"""Sudoku solver using breadth-first search and solution-path reconstruction."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
Board = tuple[int, ...]
ALL = frozenset(range(1, 10))

PUZZLES = {
    "easy": "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
    "medium": "000260701680070090190004500820100040004602900050003028009300074040050036703018000",
    "hard": "100007090030020008009600500005300900010080002600004000300000010040000007007000300",
}


@dataclass(frozen=True)
class SudokuResult:
    board: Board
    path: tuple[Board, ...]
    expanded: int


def parse(text: str) -> Board:
    chars = [char for char in text if char in "0123456789."]
    if len(chars) != 81:
        raise ValueError("a Sudoku must contain exactly 81 cells")
    return tuple(0 if char in "0." else int(char) for char in chars)


def format_board(board: Board) -> str:
    rows = []
    for row in range(9):
        values = board[row * 9 : (row + 1) * 9]
        rows.append(" ".join(str(value) if value else "." for value in values))
    return "\n".join(rows)


def candidates(board: Board, index: int) -> frozenset[int]:
    row, column = divmod(index, 9)
    row_values = set(board[row * 9 : row * 9 + 9])
    column_values = {board[column + 9 * r] for r in range(9)}
    box_row, box_column = 3 * (row // 3), 3 * (column // 3)
    box_values = {
        board[(box_row + dr) * 9 + box_column + dc]
        for dr in range(3)
        for dc in range(3)
    }
    return ALL - row_values - column_values - box_values


def _consistent(board: Board) -> bool:
    units = []
    units.extend(board[r * 9 : r * 9 + 9] for r in range(9))
    units.extend(tuple(board[c + 9 * r] for r in range(9)) for c in range(9))
    units.extend(
        tuple(board[(br + dr) * 9 + bc + dc] for dr in range(3) for dc in range(3))
        for br in (0, 3, 6)
        for bc in (0, 3, 6)
    )
    return all(len([v for v in unit if v]) == len({v for v in unit if v}) for unit in units)


def _propagate(board: Board) -> Board | None:
    current = list(board)
    while True:
        changed = False
        for index, value in enumerate(current):
            if value == 0:
                options = candidates(tuple(current), index)
                if not options:
                    return None
                if len(options) == 1:
                    current[index] = next(iter(options))
                    changed = True
        if not changed:
            return tuple(current)


def objective(board: Board) -> int:
    """Number of empty cells plus duplicate penalties; zero means solved."""
    penalty = board.count(0)
    for r in range(9):
        values = [v for v in board[r * 9 : r * 9 + 9] if v]
        penalty += len(values) - len(set(values))
    for c in range(9):
        values = [board[c + 9 * r] for r in range(9) if board[c + 9 * r]]
        penalty += len(values) - len(set(values))
    return penalty


def solve(board: Board) -> SudokuResult | None:
    """BFS over MRV branches; parent links reconstruct the successful path."""
    if len(board) != 81 or not _consistent(board):
        return None
    initial = _propagate(board)
    if initial is None:
        return None
    frontier = deque([initial])
    parent: dict[Board, Board | None] = {initial: None}
    expanded = 0
    while frontier:
        state = frontier.popleft()
        expanded += 1
        if 0 not in state:
            path: list[Board] = []
            cursor: Board | None = state
            while cursor is not None:
                path.append(cursor)
                cursor = parent[cursor]
            return SudokuResult(state, tuple(reversed(path)), expanded)
        empty = [i for i, value in enumerate(state) if value == 0]
        index = min(empty, key=lambda i: len(candidates(state, i)))
        for value in sorted(candidates(state, index)):
            child = list(state)
            child[index] = value
            propagated = _propagate(tuple(child))
            if propagated is not None and propagated not in parent:
                parent[propagated] = state
                frontier.append(propagated)
    return None


def landscape_upper_bound(board: Board) -> int:
    """Naive assignment landscape before row/column/box constraints."""
    return 9 ** board.count(0)

