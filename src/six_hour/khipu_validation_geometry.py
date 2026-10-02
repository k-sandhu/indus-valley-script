"""Exact three-value affine intersections with strict positivity."""
from fractions import Fraction as F


def dot(a, b):
    return sum(F(x) * F(y) for x, y in zip(a, b))


def affine(equations):
    matrix = [[F(x) for x in row] for row in equations]
    pivots = []
    for col in range(3):
        i = next((i for i in range(len(pivots), len(matrix)) if matrix[i][col]), None)
        if i is None:
            continue
        j = len(pivots)
        matrix[i], matrix[j] = matrix[j], matrix[i]
        divisor = matrix[j][col]
        matrix[j] = [x / divisor for x in matrix[j]]
        for k in range(len(matrix)):
            if k != j:
                multiplier = matrix[k][col]
                matrix[k] = [x - multiplier * y for x, y in zip(matrix[k], matrix[j])]
        pivots.append(col)
    if any(not any(row[:3]) and row[3] for row in matrix):
        return None
    free = [c for c in range(3) if c not in pivots]
    base = [F(0)] * 3
    slopes = [[F(int(c == j)) for c in range(3)] for j in free]
    for i, c in enumerate(pivots):
        base[c] = matrix[i][3]
        for k, j in enumerate(free):
            slopes[k][c] = -matrix[i][j]
    return base, slopes


def feasible(inequalities, dimension):
    """Return parameters satisfying a*p >= b; each row records strictness."""
    if dimension == 0:
        return [] if all(F(0) > b if strict else F(0) >= b for _, b, strict in inequalities) else None
    positive = [row for row in inequalities if row[0][-1] > 0]
    negative = [row for row in inequalities if row[0][-1] < 0]
    projected = [(a[:-1], b, strict) for a, b, strict in inequalities if not a[-1]]
    for a, b, strict in positive:
        for c, d, other_strict in negative:
            projected.append(([-c[-1] * x + a[-1] * y for x, y in zip(a[:-1], c[:-1])],
                              -c[-1] * b + a[-1] * d, strict or other_strict))
    previous = feasible(projected, dimension - 1)
    if previous is None:
        return None
    lower = [((b - dot(a[:-1], previous)) / a[-1], strict) for a, b, strict in positive]
    upper = [((b - dot(a[:-1], previous)) / a[-1], strict) for a, b, strict in negative]
    if lower and upper:
        lo = max(x for x, _ in lower); hi = min(x for x, _ in upper)
        if lo > hi or (lo == hi and (any(s for x, s in lower if x == lo) or any(s for x, s in upper if x == hi))):
            return None
        value = (lo + hi) / 2
    elif lower:
        value = max(x for x, _ in lower) + 1
    elif upper:
        value = min(x for x, _ in upper) - 1
    else:
        value = F(0)
    answer = previous + [value]
    assert all(dot(a, answer) > b if strict else dot(a, answer) >= b for a, b, strict in inequalities)
    return answer


def intersect(equations, halfspace=None):
    space = affine(equations)
    if space is None:
        return {"status": "empty", "reason": "inconsistent_equalities"}
    base, slopes = space
    inequalities = [([s[c] for s in slopes], -base[c], True) for c in range(3)]
    if halfspace is not None:
        inequalities.append(([dot(halfspace, s) for s in slopes], -dot(halfspace, base), False))
    parameters = feasible(inequalities, len(slopes))
    if parameters is None:
        return {"status": "empty", "reason": "positive_domain_excluded"}
    witness = [base[c] + sum(s[c] * value for s, value in zip(slopes, parameters)) for c in range(3)]
    assert all(x > 0 for x in witness)
    assert all(dot(row[:3], witness) == F(row[3]) for row in equations)
    assert halfspace is None or dot(halfspace, witness) >= 0
    return {"status": "point" if not slopes else "family", "dimension": len(slopes),
            "base": [str(x) for x in base], "slopes": [[str(x) for x in s] for s in slopes],
            "witness": [str(x) for x in witness]}


def validated_set(fitted, model, aggregate, kind, selected_equations, unit_count):
    restrictions = list(selected_equations)
    if unit_count is not None:
        restrictions.append([1, 0, 0, unit_count])
    halfspace = None
    if model == "collective":
        if kind == "equality":
            restrictions.append(list(aggregate) + [0])
        else:
            halfspace = aggregate
    parts = []
    for point in fitted["optimal_points"]:
        _, t, h = map(F, point["values"])
        equations = restrictions + [[-t, 1, 0, 0], [-h, 0, 1, 0]]
        parts.append(intersect(equations, halfspace))
    for family in fitted["optimal_families"]:
        equations = restrictions + ([list(family["line"]) + [0]] if "line" in family else [])
        parts.append(intersect(equations, halfspace))
    survivors = [part for part in parts if part["status"] != "empty"]
    points = sorted({tuple(part["witness"]) for part in survivors if part["status"] == "point"})
    families = [part for part in survivors if part["status"] == "family"]
    status = "empty" if not survivors else "one_absolute_point" if len(points) == 1 and not families else "ambiguous"
    return {"status": status, "points": [list(p) for p in points], "families": families,
            "surviving_dimension": max((part["dimension"] for part in survivors), default=None),
            "parts": parts}
