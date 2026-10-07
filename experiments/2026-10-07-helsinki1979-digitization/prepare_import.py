"""Stage source-qualified occurrences for Package L without merging objects."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,default=HERE/'runs/2026-10-07-full-v1/occurrences.jsonl')
    ap.add_argument('--crosswalk',type=Path)
    ap.add_argument('--out',type=Path,default=HERE/'integration/2026-10-07-v1')
    args=ap.parse_args();destination=args.out.resolve()
    if not destination.is_relative_to(HERE) or destination.exists():raise ValueError('Output must be new and inside this package')
    crosswalk=[] if args.crosswalk is None else json.loads(args.crosswalk.read_text(encoding='utf-8'))['rows']
    lookup={}
    for row in crosswalk:
        required=('source_edition','text_number','target_scheme','target_identifier','concordance_source',
                  'concordance_page','surface_relation','rights_status','review_status')
        if any(row.get(k) is None for k in required):raise ValueError('Crosswalk source evidence is incomplete')
        lookup.setdefault((row['source_edition'],str(row['text_number'])),[]).append(row)
    freeze=json.loads((HERE/'freeze-manifest.json').read_text())
    counts=Counter();destination.mkdir(parents=True)
    with args.input.open(encoding='utf-8') as source,(destination/'ledger-import.jsonl').open('w',encoding='utf-8') as sink:
        for line in source:
            row=json.loads(line);key=(row['edition'],row['inscription_number']);joins=lookup.get(key,[])
            reasons=[]
            if row['inscription_number'] is None:reasons.append('printed_number_unresolved')
            if not joins:reasons.append('no_source_qualified_object_crosswalk')
            if len(joins)>1:reasons.append('multiple_object_crosswalk_assertions')
            if joins and any(j['review_status']!='confirmed' for j in joins):reasons.append('crosswalk_not_confirmed')
            # Current extraction remains provisional even if an object relation becomes confirmed.
            if row['flags']:reasons.append('occurrence_requires_source_review')
            disposition='quarantine' if reasons else 'ready_for_ledger_review'
            counts[disposition]+=1
            for reason in reasons:counts[reason]+=1
            result=dict(schema_version='helsinki1979-occurrence-1',source_edition=row['edition'],text_number=row['inscription_number'],
                edition_id=row['edition'],segment_id=row['occurrence_key'],
                occurrence_key=row['occurrence_key'],source_locator=dict(pdf_page=row['pdf_page'],column=row['pdf_column'],
                    row_index=row['row_index'],glyph_pdf_box=row['glyph_pdf_box'],rotation=row['page_rotation']),
                inventory='Finnish-1979-lower-code',rank_system='1979-upper-rank',order=row['serialization'],
                physical_boundaries=row['physical_line_side_boundaries'],
                classification=row['classification_code'],source_sha256=row['source_sha256'],
                source_page=row['pdf_page'],inventory_version='1979-chart-'+freeze['chart_sha256'],
                glyph_tokens=row['units'],auxiliary_markers=row['auxiliaries'],boundary_status=row['physical_line_side_boundaries'],
                digitization_version=freeze['code_sha256'],review_status='automatic_provisional_requires_review',
                rights=dict(status='explicit-license',licence='CC BY 4.0',license='CC-BY-4.0',authors=['Kimmo Koskenniemi','Asko Parpola'],
                     title='Corpus of Texts in the Indus Script',year=1979,publisher='University of Helsinki',
                     source_url='http://hdl.handle.net/10138/342677',license_url='https://creativecommons.org/licenses/by/4.0/',
                     attribution='Kimmo Koskenniemi and Asko Parpola (1979), Corpus of Texts in the Indus Script, University of Helsinki',
                     modifications='raster cropping, image recognition, provisional numerical transcription'),
                object_crosswalk_assertions=joins,disposition=disposition,reasons=reasons)
            sink.write(json.dumps(result,ensure_ascii=False)+'\n')
    summary=dict(status='Verified computation',archaeological_join_status='unverified',counts=dict(counts),
        input_sha256=sha(args.input),crosswalk_sha256=sha(args.crosswalk) if args.crosswalk else None,
        output_sha256=sha(destination/'ledger-import.jsonl'),script_sha256=sha(__file__))
    (destination/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
