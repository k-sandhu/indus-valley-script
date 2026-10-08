"""Annotate frozen payloads with P's cell-based correction evidence; never remap."""
from collections import defaultdict


def cell_key(value):
    if isinstance(value, dict):
        return f"p{value['pdf_page']}_c{value['column']}_r{value['row']}"
    if value.startswith('p'):
        return value
    page, column, row = map(int, value.split(':'))
    return f'p{page}_c{column}_r{row}'


class ChartChanges:
    def __init__(self, original, current, comparison, impact):
        self.old = {cell_key(r): r for r in original['rows']}
        self.new = {cell_key(r): r for r in current['rows']}
        self.changes = {r['cell']: r['fields'] for r in comparison['changes']}
        self.impact = impact
        self.code_cells = defaultdict(set)
        for cell, row in self.old.items():
            for code in [row['code']] + row['alternatives']:
                self.code_cells[code].add(cell)

    def reference_flags(self, row, version=None, authoritative=False):
        """One flag per unit, keeping definite cell joins separate from possibilities."""
        group = self.impact['M_references'].get(version) if authoritative else None
        flags = []
        for index, unit in enumerate(row.get('units', [])):
            unit_index = unit.get('unit_index', index)
            cells = set()
            for field in ('chart_locations', 'chart_references', 'shape_only_chart_locations'):
                locs = unit.get(field, []) or []
                values = [x for v in locs.values() for x in (v if isinstance(v, list) else [v])] if isinstance(locs, dict) else locs
                cells.update(cell_key(x) for x in values)
            affected = sorted(cells.intersection(self.changes))
            potential = []
            if group:
                potential = [dict(field=x['field'], old_code=x['old_code'], possible_cell_mappings=x['possible_cell_mappings'])
                             for x in group['potential_mappings'] if x['sample_index'] == row['sample_index'] and x['unit_index'] == unit_index]
                changes = sorted({x['field'] for x in group['unit_changes'] if x['sample_index'] == row['sample_index'] and x['unit_index'] == unit_index})
            else:
                changes = []
                for field in ('strict_candidate_codes', 'shape_only_candidate_codes'):
                    for code in unit.get(field, []):
                        identities = self.code_cells[code]
                        if not identities.intersection(cells) and identities.intersection(self.changes):
                            potential.append(dict(field=field, old_code=code,
                                possible_cell_mappings={c: sorted({self.new[c]['code'], *self.new[c]['alternatives']}) for c in sorted(identities)}))
            conflict = version == 'v3' and any(x['sample_index'] == row['sample_index'] and x['unit_index'] == unit_index
                           for x in self.impact['M_v3_reported_location_conflicts'])
            flags.append(dict(unit_index=unit_index, corrected_cell=bool(affected), cells=affected,
                changed_fields={c: sorted(self.changes[c]) for c in affected}, candidate_fields_would_change=changes,
                candidate_identity_review=bool(potential), potential_mappings=potential, locator_conflict=conflict))
        return flags

    def prediction_flags(self, row):
        flags = []
        for index, unit in enumerate(row['units']):
            alternatives = []
            for rank, alternative in enumerate(unit['alternatives']):
                key = alternative.get('template_key')
                cell = cell_key(key) if key else None
                if cell in self.changes:
                    alternatives.append(dict(alternative_index=rank, cell=cell, changed_fields=sorted(self.changes[cell])))
            flags.append(dict(unit_index=index, corrected_cell=bool(alternatives), alternatives=alternatives))
        return flags
