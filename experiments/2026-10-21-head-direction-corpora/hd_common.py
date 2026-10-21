"""Shared helpers; import from sibling scripts under python -I (no standalone CLI).

Percentiles use linear interpolation at (N-1)*q/100, NumPy's default method.
The median is the 50th percentile. Empty samples return None.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def read_jsonl(path):
    with open(path, encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected object")
            yield value


def write_jsonl(path, records):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def seeded_random(text):
    return random.Random(int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16))


def percentile(values, q):
    if not 0 <= q <= 100:
        raise ValueError("percentile must lie in [0,100]")
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * q / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def median(values):
    return percentile(values, 50)


class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left == right:
            return
        if self.rank[left] < self.rank[right]:
            left, right = right, left
        self.parent[right] = left
        if self.rank[left] == self.rank[right]:
            self.rank[left] += 1
