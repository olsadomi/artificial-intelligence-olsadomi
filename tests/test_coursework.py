import unittest

from ai_coursework import latin_square, social_golfers, sudoku
from ai_coursework.search_trees import (
    DEFAULT_ROTATIONS, PUZZLE_GOAL, solve_8_puzzle, solve_missionaries, solve_workforce,
)


class CourseworkTests(unittest.TestCase):
    def test_social_golfers_reaches_ten_week_upper_bound(self):
        schedule = social_golfers.solve()
        self.assertIsNotNone(schedule)
        self.assertEqual(len(schedule), social_golfers.pair_upper_bound(32, 4))
        self.assertEqual(len(schedule), 10)
        self.assertTrue(social_golfers.is_valid(schedule, 32, 4))
        self.assertEqual(social_golfers.objective(schedule), 0)

    def test_social_golfers_impossible_above_upper_bound(self):
        self.assertIsNone(social_golfers.solve(weeks=11))

    def test_all_sudoku_difficulties(self):
        for level, puzzle in sudoku.PUZZLES.items():
            with self.subTest(level=level):
                result = sudoku.solve(sudoku.parse(puzzle))
                self.assertIsNotNone(result)
                self.assertEqual(sudoku.objective(result.board), 0)
                self.assertNotIn(0, result.board)

    def test_invalid_sudoku_is_rejected(self):
        self.assertIsNone(sudoku.solve(sudoku.parse("11" + "0" * 79)))

    def test_latin_squares(self):
        for n in range(1, 7):
            with self.subTest(n=n):
                result = latin_square.solve(n)
                self.assertIsNotNone(result)
                self.assertTrue(latin_square.is_valid(result.square))
                self.assertEqual(latin_square.objective(result.square), 0)

    def test_8_puzzle(self):
        result = solve_8_puzzle((1, 2, 3, 4, 5, 6, 0, 7, 8))
        self.assertIsNotNone(result)
        self.assertEqual(result.states[-1], PUZZLE_GOAL)
        self.assertEqual(len(result.actions), 2)
        self.assertIsNone(solve_8_puzzle((1, 2, 3, 4, 5, 6, 8, 7, 0)))

    def test_missionaries_and_cannibals(self):
        result = solve_missionaries()
        self.assertIsNotNone(result)
        self.assertEqual(result.states[-1], (0, 0, 1))
        self.assertEqual(len(result.actions), 11)

    def test_rotating_workforce_covers_demand(self):
        demand = (3, 3, 3, 3, 3, 2, 2)
        result = solve_workforce(demand, DEFAULT_ROTATIONS)
        self.assertIsNotNone(result)
        counts = result.states[-1][2]
        coverage = tuple(
            sum(counts[p] * DEFAULT_ROTATIONS[p][day] for p in range(7))
            for day in range(7)
        )
        self.assertTrue(all(coverage[day] >= demand[day] for day in range(7)))


if __name__ == "__main__":
    unittest.main()
