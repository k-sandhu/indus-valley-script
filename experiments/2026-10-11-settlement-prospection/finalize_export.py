"""Record completed visual inspection and preserve the selected final PDF bytes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import fitz

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent

def record(path):
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    src=ROOT/'tmp/pdfs/indus-settlement-v3.pdf'
    target=ROOT/'output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf'
    if target.exists():raise FileExistsError(target)
    sources=json.loads((BASE/'sources-v6.json').read_text(encoding='utf-8'))
    manuscript=(ROOT/'papers/005-settlement-survey-gaps/manuscript.md').read_text(encoding='utf-8')
    import re
    cited=set(re.findall(r'\bR\d{2}\b',manuscript))
    doc=fitz.open(src)
    actual={link['uri'] for page in doc for link in page.get_links() if 'uri' in link}
    expected={r['url'] for r in sources['sources'] if r['id'] in cited}
    missing=sorted(expected-actual)
    unexpected=sorted(actual-expected)
    if missing or unexpected:raise ValueError(dict(missing=missing,unexpected=unexpected))
    layout=json.loads(src.with_suffix('.layout.json').read_text(encoding='utf-8'))
    assert not layout['out_of_margin_text']
    machine=json.loads((ROOT/'tmp/pdfs/indus-settlement-qa-v3/machine-inspection.json').read_text(encoding='utf-8'))
    assert machine['pages']==33 and machine['page_renders']==33
    assert all(machine[k]==0 for k in ('unicode_replacement_count','black_square_count','unresolved_placeholder_count'))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(src.read_bytes())
    assert target.read_bytes()==src.read_bytes()
    # The staged exports and page rasters remain local. Preserve their hashes
    # and diagnostics as authored review records; the final PDF is reusable.
    report=dict(completed_utc=datetime.now(timezone.utc).isoformat(),status='passed after visual corrections',
      inspection_role='Codex root: AI visual inspection through image tools, not a human typesetter or archaeological reviewer',
      final_pdf=record(target),manuscript=record(ROOT/'papers/005-settlement-survey-gaps/manuscript.md'),
      pages=33,initial_contact_sheets_seen=9,initial_pages_seen=list(range(1,34)),
      full_size_page_checks=[14,17,33],
      changes=[
        dict(export='v1 to v2',issue='Markdown PDF-link parser stopped at a DOI parenthesis, displaying its suffix as text.',repair='Balanced-parenthesis target parsing.',changed_page=33,remaining_32_pages='Exact PNG-byte match, inheriting completed inspection.'),
        dict(export='v2 to v3',issue='Final rounded border in the observation-chain figure slightly crossed the axes edge.',repair='Layout-only figure spacing repair from frozen synthetic inputs.',changed_page=17,remaining_32_pages='Exact PNG-byte match, inheriting completed inspection.')],
      latest_page_hashes=json.loads((ROOT/'tmp/pdfs/page-render-comparison-v3.json').read_text(encoding='utf-8')),
      margin_issues=0,remaining_observed_visual_issues=[],
      visual_checks=['Section transitions, headings, page numbers and footers','Table legibility, repeated continuation header and within-margin cells','Four figures, all 21 region labels and separate P11/P18 labels','Readable references and corrected complete DOI link'],
      external_link_check=dict(cited_records=len(cited),distinct_expected_urls=len(expected),distinct_pdf_urls=len(actual),missing=missing,unexpected=unexpected),
      extraction=dict(unicode_replacements=0,black_squares=0,unresolved_placeholders=0),
      local_export_records=[record(ROOT/f'tmp/pdfs/indus-settlement-v{i}.pdf') for i in (1,2,3)],
      rendering='Poppler pdftoppm at110dpi, all33pages; ReportLab Georgia fonts embedded',
      scope='Visual/export verification and source-link completeness. No scientific validation beyond separately recorded reviews.')
    for name,obj in [('review/pdf-inspection.json',report),('review/pdf-layout.json',layout),('review/pdf-machine-inspection.json',machine)]:
        path=BASE/name
        if path.exists():raise FileExistsError(path)
        path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(pages=len(doc),reference_urls_verified=len(expected),final_pdf=str(target))))

if __name__=='__main__':main()
