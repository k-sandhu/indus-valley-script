"""Reconstruct conditional metrological joins using exact decimal arithmetic.

Run from any directory. The evidence inputs contain short factual observations,
not redistributed catalogue pages. See PROTOCOL.md for historical assumptions.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent


def present(value):
    return {'exact_fraction': str(value), 'decimal': float(value)}


def summarize(rows):
    bases = [Fraction(row['mass_g']) / Fraction(row['proposed_coefficient']) for row in rows]
    low, high = min(bases), max(bases)
    symmetric = (high - low) / (high + low)
    loss = 1 - low / high
    grid = []
    for percentage in ['0', '0.5', '1', '2', '3', '5']:
        r = Fraction(percentage) / 100
        lower = max(base / (1 + r) for base in bases)
        upper = min(base / (1 - r) for base in bases)
        loss_lower, loss_upper = high, low / (1 - r)
        grid.append(dict(tolerance_percent=percentage,
                         symmetric_compatible=lower <= upper,
                         symmetric_common_unit_interval_g=[float(lower), float(upper)] if lower <= upper else None,
                         loss_only_compatible=loss_lower <= loss_upper,
                         loss_only_common_unit_interval_g=[float(loss_lower), float(loss_upper)] if loss_lower <= loss_upper else None))
    return dict(objects=[dict(**row, implied_unit_g=present(base)) for row, base in zip(rows, bases)],
                minimum_symmetric_relative_tolerance=present(symmetric),
                minimum_loss_only_relative_tolerance=present(loss), grid=grid)


def main():
    target = RUN / 'numerical-compatibility.json'
    if target.exists():
        raise FileExistsError('Frozen endpoint exists; use a new version for a changed analysis.')
    evidence = RUN / 'evidence-table.json'
    data = json.loads(evidence.read_text(encoding='utf-8'))
    lookup = {row['id']: row for row in data['objects']}
    inputs = [dict(id=key, mass_g=lookup[key]['mass_g'], proposed_coefficient=coefficient)
              for key, coefficient in [('susa-sb13677', '25'), ('susa-sb13323', '1'), ('susa-sb17774', '2')]]
    controls = [dict(id=key, mass_g=lookup[key]['mass_g'], proposed_coefficient=coefficient)
                for key, coefficient in [('girsu-ao247', '10'), ('girsu-ao248', '5')]]
    result = dict(status='exploratory reconstruction of published interpretations',
                  input_path=evidence.name, input_sha256=sha256(evidence.read_bytes()).hexdigest(),
                  susa_quarter_mina_hypothesis=summarize(inputs),
                  girsu_readable_shekel_control=summarize(controls),
                  sb13677_four_additive_units_implied_unit_g=present(Fraction('334.25') / 4),
                  sb13677_quarter_mina_implied_mina_g=present(Fraction('334.25') * 4),
                  sb13677_expected_mass_from_sb17774_g=present(Fraction('27.25') / 2 * 25),
                  sb13677_mass_difference_from_sb17774_g=present(Fraction('27.25') / 2 * 25 - Fraction('334.25')),
                  measurement_uncertainty='unknown; sensitivity grid is not historically calibrated',
                  graphic_interpretation='Source hypothesis retained; no new Indus glyph reading assigned.')
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({name: {metric: result[name][metric]['decimal'] for metric in
                            ['minimum_symmetric_relative_tolerance', 'minimum_loss_only_relative_tolerance']}
                      for name in ['susa_quarter_mina_hypothesis', 'girsu_readable_shekel_control']}, indent=2))


if __name__ == '__main__':
    main()
