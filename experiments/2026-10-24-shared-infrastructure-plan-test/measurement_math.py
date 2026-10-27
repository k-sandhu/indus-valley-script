"""Independent arithmetic for source-plan reading bounds, not survey confidence."""
from math import hypot, isfinite


def distance(a, b):
    if len(a) != 2 or len(b) != 2 or not all(isfinite(float(v)) for v in (*a, *b)):
        raise ValueError('Two finite image coordinates are required.')
    return hypot(b[0] - a[0], b[1] - a[1])


def metric_length(feature, bar, bar_metres, feature_radius_px, bar_radius_px, bar_metres_error=0):
    """Each clicked endpoint may move inside a disc of the declared radius."""
    d = distance(*feature)
    b = distance(*bar)
    if min(bar_metres, b) <= 0 or min(feature_radius_px, bar_radius_px, bar_metres_error) < 0:
        raise ValueError('Scale must be positive and uncertainty nonnegative.')
    if b <= 2 * bar_radius_px or bar_metres <= bar_metres_error:
        raise ValueError('The scale lower bound must remain positive.')
    d_min, d_max = max(0, d - 2 * feature_radius_px), d + 2 * feature_radius_px
    b_min, b_max = b - 2 * bar_radius_px, b + 2 * bar_radius_px
    return {
        'estimate_m': d * bar_metres / b,
        'reading_lower_m': d_min * (bar_metres - bar_metres_error) / b_max,
        'reading_upper_m': d_max * (bar_metres + bar_metres_error) / b_min,
        'feature_pixels': d, 'scale_bar_pixels': b,
        'bound_type': 'Conservative endpoint and scale reading sensitivity; not survey accuracy or a confidence interval',
    }


def retained_width(before_bounds, after_bounds):
    b_lo, b_hi = before_bounds
    a_lo, a_hi = after_bounds
    if b_lo <= 0 or b_hi < b_lo or a_lo < 0 or a_hi < a_lo:
        raise ValueError('Positive ordered width bounds are required.')
    return {'retained_fraction_lower': a_lo / b_hi,
            'retained_fraction_upper': a_hi / b_lo,
            'loss_fraction_lower': 1 - a_hi / b_lo,
            'loss_fraction_upper': 1 - a_lo / b_hi,
            'connectivity_inferred': False}


def controls():
    from fractions import Fraction
    from math import isclose
    result = metric_length(((0, 0), (300, 400)), ((0, 0), (1000, 0)), 20, 2, 2)
    tests = {
        '3_4_5_length': result['estimate_m'] == 10,
        'integer_lower_bound': isclose(result['reading_lower_m'], float(Fraction(9920, 1004))),
        'integer_upper_bound': isclose(result['reading_upper_m'], float(Fraction(10080, 996))),
        'rotation_keeps_length': distance((0, 0), (-400, 300)) == 500,
        'translation_keeps_length': distance((10, 20), (310, 420)) == 500,
        'width_ratio_does_not_infer_connectivity': not retained_width((4, 6), (2, 3))['connectivity_inferred'],
        'independent_ratio_bounds': retained_width((4, 6), (2, 3))['retained_fraction_upper'] == .75,
    }
    try:
        metric_length(((0, 0), (1, 1)), ((0, 0), (1, 0)), 1, 1, 1)
        tests['degenerate_scale_rejected'] = False
    except ValueError:
        tests['degenerate_scale_rejected'] = True
    return {'synthetic': True, 'checks': tests, 'passed': all(tests.values()), 'archaeological_measurements': 0}


if __name__ == '__main__':
    import argparse, hashlib, json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out
    if out.exists():
        raise FileExistsError(out)
    result = controls()
    result['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
