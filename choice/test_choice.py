from collections import Counter
import math
import random

import pytest

from choice import Choice


NUM_TRIALS = 10000
PRECISION = 3 * 1/math.sqrt(NUM_TRIALS)
SEED = 1


#
# Helpers
#


def outcomes(rng, n, ch):
    counted = Counter(ch.evaluate(rng) for _ in range(n))
    return {k: float(v)/float(n) for (k, v) in counted.items()}


def deviation(dic1, dic2):
    return sum(
        abs(dic2.get(k, 0) - dic1.get(k, 0))
        for k in dic1
    )


#
# Fixtures
#

@pytest.fixture
def rng():
    yield random.Random(SEED)


#
# Tests
#


def test_solo(rng):
    ch = Choice.solo("a")
    expectations = {"a": 1}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_of(rng):
    ch = Choice.of(Choice.solo("a"), Choice.solo("b"))
    expectations = {"a": 1/2, "b": 1/2}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_flat(rng):
    ch = Choice.flat(Choice.solo(x) for x in ["a", "b", "c"])
    expectations = {"a": 1/3, "b": 1/3, "c": 1/3}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_weighted(rng):
    ch = Choice.weighted(1, "a") | Choice.weighted(2, "b") | Choice.weighted(3, "c")
    expectations = {"a": 1/6, "b": 2/6, "c": 3/6}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_otherwise(rng):
    ch = Choice.weighted(20, "a") | Choice.otherwise("b", 100)
    expectations = {"a": 0.2, "b": 0.8}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_percentage(rng):
    ch = Choice.percentage(20, "a") | Choice.otherwise("b")
    expectations = {"a": 0.2, "b": 0.8}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_either(rng):
    ch1 = Choice.weighted(1, "a")
    ch2 = Choice.weighted(3, "b")
    ch = Choice.either(ch1, ch2)
    expectations = {"a": 1/4, "b": 3/4}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_delayed(rng):

    def add(x, y):
        return x + y

    d_add = Choice.delayed(add)
    ch = d_add(Choice.solo(1), Choice.percentage(30, 5) | Choice.otherwise(10))
    expectations = {6: 0.3, 11: 0.7}
    found = outcomes(rng, NUM_TRIALS, ch)
    assert deviation(found, expectations) <= PRECISION


def test_evaluate_nested(rng):
    ch = Choice.solo({"foo": {"bar": [1, 3, [{"q": Choice.solo(5)}]]}})
    assert ch.evaluate(rng) == {"foo": {"bar": [1, 3, [{"q": 5}]]}}
