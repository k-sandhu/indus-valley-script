"""Freeze the all-mapped-code image check without changing candidate roles."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    frozen = json.loads((HERE / 'families.json').read_text(encoding='utf-8'))
    sources = json.loads((HERE / 'crosswalk-sheet-manifest-initial.json').read_text(encoding='utf-8'))
    conflict_observations = {
        '167': ('A curved outer form with two returned lower ends.',
                'P344 has an upper peaked support and two hanging closed loads.'),
        '168': ('An arched closed form surrounds a central Y-like division.',
                'P345 has an upper support, central stem and two hanging round loads.'),
        '309': ('A rounded upper loop joins spreading lower strokes and small side hooks.',
                'P206 has mostly parallel bent strips with a rounded side attachment.'),
        '354': ('Several separate uprights cross a rail; two central lower ends remain separate.',
                'P091 joins the lower center into a U-shaped return.'),
        '374': ('A vertical stem passes through a horizontal loop and a small upper upright loop.',
                'P103 is a curved plant-like stem with lateral pointed leaves.'),
        '375': ('The loop-on-stem form occurs between two long outer uprights.',
                'P104 places a curved, laterally leaved stem between outer uprights.'),
        '796': ('An oval lies under an outer angular cap with short upper marks.',
                'P180 is a half-round D-shaped boundary under a cap and short upper marks.'),
        '817': ('An oval contains a V-shaped upper division.',
                'P385 is a diamond with an upper V-shaped division.'),
        '850': ('A plain closed diamond has four corners.',
                'P355 is a plain closed oval without diamond corners.'),
        '860': ('A diamond has a small projecting right-side fork.',
                'P356 is a circular outline with a projecting right-side fork.'),
        '930': ('A peaked covering encloses a divided arch and short lower marks.',
                'P339 is a radially divided oval on short lower strokes.'),
    }
    notes = {
        '353': 'The closer paired view resolves the initial misreading: the font has a small U-shaped lower return, agreeing with the common P091 prong/rail/loop component.',
        '700': 'The closer paired view shows one U-shaped font outline, agreeing with P310. The initial repetition note was a contact-sheet column misreading.',
        '940': 'Both witnesses contain a fish-like figure and a more segmented arthropod-like figure within side curves. The initial two-fish reading was too narrow.',
        '942': 'Both witnesses contain a segmented or arthropod-like body beside a fish-like body within side curves.',
        '943': 'Both witnesses contain a segmented or arthropod-like body beside a fish-like body within side curves.',
        '272': 'P070 has a segmented body with appendages and an upward curved tail-like feature. Insect/scorpion remains a direct rival to bird wording.',
        '264': 'Bird, insect, humanoid and segmented-creature readings remain open; P066 does not identify a bird species.',
        '265': 'The flanked segmented form is not uniquely avian; P067 keeps creature rivals open.',
        '266': 'The angled head and hatched body are not a secure species diagnostic; P066 retains segmented-creature alternatives.',
        '267': 'The flanked segmented form is not uniquely avian; P067 keeps creature rivals open.',
        '268': 'P066 retains segmented-creature alternatives to the bird-like exact-font outline.',
        '269': 'P067 retains segmented-creature alternatives to the bird-like exact-font outline.',
        '270': 'P067 retains segmented-creature alternatives; the exact-font silhouette does not establish a bird species.',
        '271': 'P067 retains segmented-creature alternatives; the exact-font silhouette does not establish a bird species.',
        '776': 'The class drawing can be read as three headed people above a curved base; the font has three looped stems. Person, plant and support comparisons remain open.',
        '777': 'The class drawing has headed stems with arm-like strokes; the font has umbrella-like heads. Shared enclosure/terminal structure does not identify a plant.',
        '778': 'The class drawing has headed stems with arm-like strokes; the font has umbrella-like heads. Shared enclosure/terminal structure does not identify a plant.',
        '782': 'Headed-person and branching-stem comparisons both remain available for the terminal qualifications.',
        '783': 'The class drawing has three headed-person-like stems; the font has looped heads and crossbars. Do not replace the exact qualifier with a species claim.',
        '784': 'Headed-person and branching-stem comparisons both remain available; exact inner and terminal strokes differ.',
        '785': 'Headed-person and branching-stem comparisons both remain available; exact inner and terminal strokes differ.',
        '786': 'The class drawing has rounded headed stems; the font has vertically repeated pointed terminal marks. Exact qualification is not depicted by the shared class.',
    }
    rows = []
    for sheet in sources['rows']:
        if sha(ROOT / sheet['path']) != sheet['sha256']:
            raise ValueError(sheet['path'])
        sheet['seen'] = True
        sheet['seen_by'] = 'Codex paired visual-language image inspection, 2026-10-12'
        for witness in sheet['witnesses']:
            code = witness['code']
            row = dict(witness, sheet=sheet['path'], seen=True,
                       exact_identity_confirmed=False,
                       public_chart_status='class-only',
                       suppress_public_glyph=code in conflict_observations,
                       observation=notes.get(code, 'Reviewed as a class comparison. Shared components, orientation, repetition and qualifier differences do not establish exact-code identity.'))
            if code in conflict_observations:
                row.update(font_observation=conflict_observations[code][0],
                           mapped_class_observation=conflict_observations[code][1],
                           public_chart_status='conflicting-class; suppress as code glyph')
            rows.append(row)
    suppressed = sorted(conflict_observations, key=int)
    amendment = dict(date='2026-10-12', basis='Closer paired image inspection after visual family freeze; no new context outputs read by this reviewer.',
      family_map_sha256=sha(HERE / 'families.json'), membership_and_roles_unchanged=True,
      chart_conflict_removals=['353', '940'], source_ambiguity_removals=['700'],
      family_picture_replacements=[
        dict(family_id='rail_tally',
             picture_observation='Several upright rods cross a horizontal rail. W353 has a small U-shaped lower return; W354 has separate lower stems.',
             working_meaning='Joined row or bundled units.', Sanskrit_comparison_words=['śreṇi', 'stamba']),
        dict(family_id='enclosed_fish_group',
             picture_observation='A fish-like oval-and-tail body stands beside a segmented or arthropod-like form within curved side boundaries.',
             working_meaning='Bounded mixed-creature or animal-product group.',
             Sanskrit_comparison_words=['matsya', 'vṛścika', 'paśu', 'varga']),
      ],
      family_rival_additions=[dict(family_id='bird_shapes', codes=['264', '265', '266', '267', '268', '269', '270', '271'],
            graphic_rivals=['Segmented-creature, insect/scorpion and humanoid alternatives remain open alongside bird for these codes.'],
            Sanskrit_comparison_words=['vṛścika', 'paśu'])],
      explanation='The first broad sheets hid a small lower join in W353 and led to a column misreading of W700. Paired font/class comparison also exposed the mixed-creature outline in W940–943. These corrections alter observations and competing meaning vocabulary; no family codes or positional tests were selected from outcomes.')
    write(HERE / 'image-corrections-v1.json', amendment)
    audit = dict(date='2026-10-12', scope='All 498 mapped codes compared side by side with their first licensed chart pointer; 215 codes have no chart pointer in the starting inventory.',
                 rows=rows, counts=dict(seen_codes=len(rows), suppress_as_public_code_glyph=len(suppressed)),
                 suppressed_codes=suppressed, authoritative_for_public_glyph_disposition=True,
                 overrides='Supersedes the suppression/source-ambiguity fields of the frozen family map only where explicitly specified by image-corrections-v1.json.',
                 rights='Exact-font paired contact sheets remain local-only. Public output contains authored observations and hashes, not font images or complete inscriptions.')
    write(HERE / 'chart-crosswalk-audit.json', audit)
    write(HERE / 'crosswalk-image-review-manifest.json', sources)
    write(HERE / 'crosswalk-freeze-manifest.json', dict(date='2026-10-12',
      frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      original_family_map_sha256=sha(HERE / 'families.json'),
      no_new_context_outputs_read=True,
      outputs=[dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path)) for path in
               [HERE / 'image-corrections-v1.json', HERE / 'chart-crosswalk-audit.json', HERE / 'crosswalk-image-review-manifest.json']]))
    print(json.dumps({'mapped_codes_seen': len(rows), 'suppressed_codes': suppressed}))


if __name__ == '__main__':
    main()
