"""Summarize a measure_lines output file."""
import json, sys
r = json.load(open(sys.argv[1], encoding='utf-8'))
a = r.get('arrow')
if a:
    print('arrow', [[round(v, 1) for v in p] for p in a['refined_endpoints_px']], 'dir', round(a['direction_px_deg'], 3), 'sig', round(a['sigma_deg'], 3), 'inl', a['inlier_count'], '/', a['profile_count'])
    print('m/px', r['metres_per_render_pixel'])
for l in r['lines']:
    b = l.get('bearing_raw_deg', l['bearing_deg'])
    print(l['id'], [[round(v, 1) for v in p] for p in l['refined_endpoints_px']], 'raw', round(b, 2), 'brg', round(l['bearing_deg'], 2), 'th', round(l['theta_deg'], 2), 'sig', round(l['sigma_deg'], 3), 'inl', l['inlier_count'], '/', l['profile_count'], 'rms', None if l['residual_rms_px'] is None else round(l['residual_rms_px'], 2), 'L', round(l['length_m'], 1), l.get('warnings'))
