"""Render current ledger annotations without revising frozen audits or source records."""
import json
from pdf_followup import OWN


def main():
    rows = [json.loads(line) for line in (OWN / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    lines = ['# Claim ledger', '',
             'Source claims retain their IDs and witnesses. Sounds, meanings and readings are Bonta’s proposals. PDF-review corrections separate lexical construction, source extraction and object identity; earlier ledger states remain in history/.', '']
    for row in rows:
        lines += [f'## {row["id"]}', '', f'**{row["type"]}**. Source: {row["source_id"]}, {row["source_location"]}.', '',
                  row['paraphrase'], '', f'Evidence: {row["offered_evidence"]}', '',
                  f'Tests: {", ".join(row["test_ids"])}. Status: {row["assessment_status"]}.', '']
        if row.get('quotation'):
            lines += [f'Source wording: “{row["quotation"]}”', '']
        if row.get('value_derivation_evidence'):
            detail = row['value_derivation_evidence']
            lines += [f'Derivation: {detail["basis"]} Manuscript pages {", ".join(map(str, detail["source_pages"]))}.', '']
        if row.get('probable_misjoin_source_flag'):
            lines += ['Object join: probable mistyped-CISI alias; retain the original match and exclude it in the conservative join count.', '']
    (OWN / 'claims.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Rendered', len(rows), 'ledger records.')


if __name__ == '__main__':
    main()
