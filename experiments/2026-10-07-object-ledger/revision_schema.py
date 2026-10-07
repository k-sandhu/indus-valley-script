"""Version 2 schema; the original schema and endpoint remain untouched."""
import copy
from schema import schema, CELL

OBJECT_EXTRA = ['export_excavation_identifier', 'bibliographic_locator']
CONTEXT_EXTRA = ['lot_identifier', 'country', 'periodization_scheme', 'design_classification']

def schema_v2():
    s = copy.deepcopy(schema())
    s['properties']['schema_version'] = {'const': '2.0'}
    for table, extra in [('objects', OBJECT_EXTRA), ('contexts', CONTEXT_EXTRA)]:
        fields = s['$defs'][table]['properties']['fields']
        fields['required'] += extra
        fields['properties'].update({f: copy.deepcopy(CELL) for f in extra})
    s['$defs']['assertions']['properties']['confidence']['enum'].append('derived')
    s['$defs']['measurements']['properties']['dimension']['enum'] += ['diameter', 'mass']
    s['$defs']['sources']['properties']['creator_role'] = {'enum': ['author', 'editor', 'repository contributor']}
    s['$defs']['sources']['required'].append('creator_role')
    return s
