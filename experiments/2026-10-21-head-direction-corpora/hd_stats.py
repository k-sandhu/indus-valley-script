"""Pure section 7 statistics; import from sibling scripts (no standalone CLI).

Legends contain hashable units; words may be tuples of signs. Tagged legends
contain (member, tag) pairs, flattened across word boundaries. S6 takes legends
of words, each word a sequence of signs. Empty populations return None.
"""
import math
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hd_common import median, percentile, seeded_random


def normalized_entropy(counter, inventory_size):
    if inventory_size <= 1:
        return 0.0
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total)
                for count in counter.values() if count > 0) / math.log2(inventory_size)


def S1(legends):
    if not legends:
        return None
    inventory = {unit for legend in legends for unit in legend}
    return (normalized_entropy(Counter(legend[0] for legend in legends), len(inventory))
            - normalized_entropy(Counter(legend[-1] for legend in legends), len(inventory)))


def closing_stock(legends, size):
    counts = Counter(legend[-1] for legend in legends)
    return sorted(counts, key=lambda unit: (-counts[unit], str(unit)))[:size]


def closing_share(legends, size):
    if not legends:
        return None
    stock = set(closing_stock(legends, size))
    return sum(legend[-1] in stock for legend in legends) / len(legends)


def S2(legends):
    return closing_share(legends, 3)


def shuffled(legends, rng):
    result = []
    for legend in legends:
        copy = list(legend)
        rng.shuffle(copy)
        result.append(copy)
    return result


def S3(legends, seed):
    if not legends:
        return None
    size = math.ceil(len(legends) / 10)
    rng = seeded_random(seed + ":within:S3")
    reference = [closing_share(shuffled(legends, rng), size) for _ in range(200)]
    return closing_share(legends, size) - sum(reference) / len(reference)


def pair_counts(tagged_legends, statistic):
    forward = backward = 0
    for legend in tagged_legends:
        for (_, left), (_, right) in zip(legend, legend[1:]):
            if statistic == "S4":
                forward += left == "TITLE" and right == "NAME"
                backward += left == "NAME" and right == "TITLE"
            elif statistic == "S5":
                forward += left == "NUMBER" and right not in {"NUMBER", "GRAM"}
                backward += right == "NUMBER" and left not in {"NUMBER", "GRAM"}
            else:
                raise ValueError(statistic)
    return forward, backward


def pair_statistic(legends, statistic):
    forward, backward = pair_counts(legends, statistic)
    return (forward - backward) / (forward + backward) if forward + backward else None


def S4(legends):
    return pair_statistic(legends, "S4")


def S5(legends):
    return pair_statistic(legends, "S5")


def S6(legends):
    words = [word for legend in legends for word in legend if len(word) >= 2]
    return S1(words) if len(words) >= 20 else None


def shuffle_reference(legends, seed, shuffles=1000):
    if shuffles < 1:
        raise ValueError("shuffles must be positive")
    if not legends:
        return {"observed": None, "shuffle_mean": None, "p2_5": None,
                "p97_5": None, "shuffles": shuffles}
    rng = seeded_random(seed + ":within:S1")
    values = [S1(shuffled(legends, rng)) for _ in range(shuffles)]
    return {"observed": S1(legends), "shuffle_mean": sum(values) / shuffles,
            "p2_5": percentile(values, 2.5), "p97_5": percentile(values, 97.5),
            "shuffles": shuffles}
