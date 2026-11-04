"""Command-line interface for running each coursework problem."""

from __future__ import annotations

import argparse

from . import latin_square, social_golfers, sudoku
from .search_trees import DEFAULT_ROTATIONS, solve_8_puzzle, solve_missionaries, solve_workforce


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI uninformed-search coursework")
    sub = parser.add_subparsers(dest="problem", required=True)
    golfers = sub.add_parser("golfers")
    golfers.add_argument("--weeks", type=int, default=10)
    sdk = sub.add_parser("sudoku")
    sdk.add_argument("--level", choices=sudoku.PUZZLES, default="easy")
    sdk.add_argument("--board", help="81 digits/dots; overrides --level")
    latin = sub.add_parser("latin")
    latin.add_argument("n", type=int)
    puzzle = sub.add_parser("puzzle")
    puzzle.add_argument("state", nargs="?", default="123456078", help="nine digits; 0 is blank")
    missionaries = sub.add_parser("missionaries")
    missionaries.add_argument("--total", type=int, default=3)
    workforce = sub.add_parser("workforce")
    workforce.add_argument("--demand", default="3,3,3,3,3,2,2")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.problem == "golfers":
        schedule = social_golfers.solve(weeks=args.weeks)
        if schedule is None:
            print("No schedule found")
            return
        for week, groups in enumerate(schedule, 1):
            print(f"Week {week}: " + " | ".join(",".join(map(str, group)) for group in groups))
    elif args.problem == "sudoku":
        board = sudoku.parse(args.board or sudoku.PUZZLES[args.level])
        result = sudoku.solve(board)
        print(sudoku.format_board(result.board) if result else "No solution")
        if result:
            print(f"Expanded states: {result.expanded}")
    elif args.problem == "latin":
        result = latin_square.solve(args.n)
        if result:
            print("\n".join(" ".join(map(str, row)) for row in result.square))
            print(f"Expanded states: {result.expanded}; IDDFS iterations: {result.depth_iterations}")
    elif args.problem == "puzzle":
        initial = tuple(map(int, args.state))
        result = solve_8_puzzle(initial)
        print(" -> ".join(result.actions) if result else "No solution")
    elif args.problem == "missionaries":
        result = solve_missionaries(args.total)
        print("\n".join(result.actions) if result else "No solution")
    elif args.problem == "workforce":
        demand = tuple(map(int, args.demand.split(",")))
        result = solve_workforce(demand, DEFAULT_ROTATIONS)
        if result:
            print(f"Workers per starting-day rotation: {result.states[-1][2]}")
        else:
            print("No solution")


if __name__ == "__main__":
    main()

