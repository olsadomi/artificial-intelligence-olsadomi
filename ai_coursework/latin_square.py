"""Latin-square generation using IDDFS and backtracking."""

from __future__ import annotations

from dataclasses import dataclass

Square = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class LatinResult:
    square: Square
    expanded: int
    depth_iterations: int


def objective(square: Square) -> int:
    """Count row and column repetitions/missing symbols (zero is optimal)."""
    n = len(square)
    target = set(range(1, n + 1))
    return sum(n - len(set(row) & target) for row in square) + sum(
        n - len({square[r][c] for r in range(n)} & target) for c in range(n)
    )


def is_valid(square: Square) -> bool:
    n = len(square)
    target = set(range(1, n + 1))
    return all(set(row) == target for row in square) and all(
        {square[row][column] for row in range(n)} == target for column in range(n)
    )


def solve(n: int) -> LatinResult | None:
    """Generate a reduced Latin square with IDDFS.

    Fixing the first row and column removes symbol/row symmetries without losing
    existence. Each depth-limited iteration uses DFS and restores state on return.
    """
    if n < 1:
        raise ValueError("n must be positive")
    board = [[0] * n for _ in range(n)]
    for i in range(n):
        board[0][i] = i + 1
        board[i][0] = i + 1
    fixed = 1 if n == 1 else 2 * n - 1
    cells = [(r, c) for r in range(1, n) for c in range(1, n)]
    expanded = 0

    def dls(position: int, remaining: int) -> bool:
        nonlocal expanded
        expanded += 1
        if position == len(cells):
            return True
        if remaining == 0:
            return False
        row, column = cells[position]
        forbidden = set(board[row]) | {board[r][column] for r in range(n)}
        for value in range(1, n + 1):
            if value not in forbidden:
                board[row][column] = value
                if dls(position + 1, remaining - 1):
                    return True
                board[row][column] = 0  # backtrack
        return False

    iterations = 0
    for limit in range(len(cells) + 1):
        iterations += 1
        if dls(0, limit):
            square = tuple(tuple(row) for row in board)
            assert is_valid(square)
            return LatinResult(square, expanded, iterations)
    return None


def landscape_size(n: int) -> int:
    """Raw n^(n^2) grid assignments before constraints."""
    if n < 1:
        raise ValueError("n must be positive")
    return n ** (n * n)

