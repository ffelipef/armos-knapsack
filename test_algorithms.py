import random
import unittest

from algorithms import dp_exact, greedy_modified, greedy_ratio, scan_arrival


def brute_force(c, p, C):
    best = 0
    for mask in range(1 << len(c)):
        cost = sum(c[i] for i in range(len(c)) if mask >> i & 1)
        if cost <= C:
            best = max(best, sum(p[i] for i in range(len(c)) if mask >> i & 1))
    return best


def random_instance(rng, strong=False):
    n = rng.randint(1, 10)
    c = [rng.randint(1, 30) for _ in range(n)]
    p = [x + 3 for x in c] if strong else [rng.randint(1, 30) for _ in range(n)]
    C = rng.randint(1, max(1, sum(c)))
    return c, p, C


class TestKnapsack(unittest.TestCase):
    def test_counterexample_from_paper(self):
        c, p = [1, 100], [2, 100]
        self.assertEqual(greedy_ratio(c, p, 100), 2)
        self.assertEqual(greedy_modified(c, p, 100), 100)

    def test_dp_matches_brute_force(self):
        rng = random.Random(1)
        for _ in range(500):
            c, p, C = random_instance(rng)
            self.assertEqual(dp_exact(c, p, C), brute_force(c, p, C))

    def test_bounds_and_half_guarantee(self):
        rng = random.Random(2)
        for i in range(2000):
            c, p, C = random_instance(rng, strong=i % 2 == 0)
            opt = dp_exact(c, p, C)
            for fn in (greedy_ratio, greedy_modified, scan_arrival):
                self.assertLessEqual(fn(c, p, C), opt)
            self.assertGreaterEqual(2 * greedy_modified(c, p, C), opt)

    def test_all_items_fit(self):
        c, p = [3, 4, 5], [1, 2, 3]
        self.assertEqual(greedy_ratio(c, p, 100), 6)
        self.assertEqual(dp_exact(c, p, 100), 6)

    def test_items_larger_than_capacity_are_ignored(self):
        self.assertEqual(greedy_modified([50, 2], [999, 3], 10), 3)


if __name__ == "__main__":
    unittest.main()
