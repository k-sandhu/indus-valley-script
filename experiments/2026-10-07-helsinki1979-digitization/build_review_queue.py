"""Prioritize provisional rows and summarize repeated printed-number witnesses."""
import argparse
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=HERE/'runs/2026-10-07-full-v1/occurrences.jsonl')
    ap.add_argument('--out',type=Path,default=HERE/'review/2026-10-07-v1');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Choose a new owned output directory')
    queue=[];groups=defaultdict(list);counts=Counter();order_groups=defaultdict(list);field_checks=Counter()
    with args.input.open(encoding='utf-8') as stream:
        for line in stream:
            row=json.loads(line);confidence=[u.get('confidence') for u in row['units'] if u.get('confidence') is not None]
            minimum=min(confidence,default=0);mean=sum(confidence)/len(confidence) if confidence else None
            number_missing=row['inscription_number'] is None
            unmatched=sum(not u['alternatives'] for u in row['units'])
            tier=0 if number_missing or unmatched else (1 if minimum<.75 else 2)
            reason=['unresolved_number_or_unmatched_ink'] if tier==0 else (['drawing_unit_confidence_below_0.75'] if tier==1 else ['classification_and_boundaries_require_review'])
            queue.append(dict(occurrence_key=row['occurrence_key'],inscription_number=row['inscription_number'],
               pdf_page=row['pdf_page'],priority=tier,minimum_calibrated_confidence=minimum,mean_calibrated_confidence=mean,
               drawn_units=len(row['units']),reasons=reason,flags=row['flags'],review_crop_local=row['review_crop_local']))
            counts[f'priority_{tier}']+=1
            if row.get('margin_ocr'):
                upper=row['margin_ocr'][0]['text']
                field_checks['digit_vs_tesseract_fields']+=1
                field_checks['digit_vs_tesseract_exact_agreement']+=row['inscription_number']==upper
            if row.get('ocr_number_witnesses'):
                field_checks['original_pdf_ocr_nonempty_fields']+=1
                field_checks['original_pdf_ocr_contains_number_literal']+=row['inscription_number'] in row['ocr_number_witnesses']
            if 22<=row['pdf_page']<=78 and row['inscription_number']:
                import re
                literal=row['inscription_number'];m=re.fullmatch(r'(\d+)([A-Z]?)',literal)
                if m:order_groups[row['pdf_page'],row['pdf_column']].append((row['row_index'],(int(m[1]),m[2]),row['occurrence_key']))
            if row['inscription_number'] is not None:
                sequence=tuple(tuple(u['alternatives'][0]['codes']) if u['alternatives'] else () for u in row['units'])
                groups[row['inscription_number']].append((row['occurrence_key'],sequence))
    repeated=[v for v in groups.values() if len(v)>1]
    order_violations=[]
    for (page,col),items in order_groups.items():
        items.sort()
        for previous,following in zip(items,items[1:]):
            if following[1]<=previous[1]:
                order_violations.append(dict(pdf_page=page,column=col,previous=previous[2],following=following[2],
                                              previous_number=list(previous[1]),following_number=list(following[1])))
    repeated_summary=dict(printed_number_groups=len(groups),multiple_occurrence_number_groups=len(repeated),
       multiple_occurrence_groups_with_exact_top1_candidate_sets=sum(len({s for _,s in v})==1 for v in repeated),
       multiple_occurrence_groups_with_differing_top1_candidate_sets=sum(len({s for _,s in v})>1 for v in repeated),
       limitation='Grouped by unverified printed-number recognition. Same-edition repeat consistency; no verified object deduplication or external accuracy.')
    queue.sort(key=lambda r:(r['priority'],r['minimum_calibrated_confidence'],r['pdf_page'],r['occurrence_key']))
    out.mkdir(parents=True)
    with (out/'priority-queue.jsonl').open('w',encoding='utf-8') as stream:
        for row in queue:stream.write(json.dumps(row)+'\n')
    summary=dict(status='Verified computation',counts=dict(counts),rows=len(queue),repeated_witnesses=repeated_summary,
                 number_field_comparisons=dict(field_checks),number_order_nonincreasing_pairs=len(order_violations),
                 input_sha256=sha(args.input),queue_sha256=sha(out/'priority-queue.jsonl'),source_sha256=sha(__file__))
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
    (out/'number-order-check.json').write_text(json.dumps(dict(status='Exploratory',scope='Within-column monotonic check in numbered section PDF22–78; no forced correction',
                violations=order_violations),indent=2),encoding='utf-8')


if __name__=='__main__':main()
