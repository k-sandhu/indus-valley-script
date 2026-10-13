"""Complete the working review response from observed final-export records."""
from pathlib import Path
import json

BASE=Path(__file__).resolve().parent

def main():
    path=BASE/'review/response-to-reviewers.md'
    text=path.read_text(encoding='utf-8')
    text=text.replace('`sources-v5.json`','`sources-v6.json`').replace('`candidates-v4.json`','`candidates-v5.json`')
    text=text.replace('paragraph beginning “Our data suggest.”','sentence beginning “Our data suggest.”')
    text=text.replace('Section 4.3 says “recorded additions and unconfirmed candidates.”','Section 4.3 separates field-checked additions, unconfirmed remote candidates and changed physical units.')
    text=text.replace('The final package will contain review provenance, reproduction commands, a README, manuscript and rendered PDF, with verification recorded after assembly.',
                      'The final package contains review provenance, reproduction commands, a README, manuscript and rendered PDF, with export checks recorded after assembly.')
    text=text.replace('The response no longer claims final rendered-PDF checks have passed. Completed source and numerical checks are recorded separately; final artifact status is given below.',
                      'Final export checks are recorded only after rendering and inspection. Source, numerical and export checks have distinct records; actual artifact status is given below.')
    before='The final-register comparison reports 12 passing checks and no material mismatch. The separate inline-arithmetic output reports 17 passing checks. These are implementation records; their counts do not measure archaeological support. Inspection of the final rendered PDF and the final package manifest remain pending and must be recorded from actual results.'
    assert before in text
    after='The final-register comparison reports 12 passing checks and no material mismatch; final package verification extends the 32-field metadata comparison through sources-v6. The separate inline-arithmetic output reports 17 passing checks. These are implementation records; their counts do not measure archaeological support. The source/region audit preserves its original 127 passes and two clarifications. Successor registers correct the R08 sentence locator and apply the documentary P2 criterion consistently, with a basis for every region. P2 is common because many regions contain known archaeology, including other periods; it does not rank target-parcel survival or Indus affiliation. See `final-source-region-audit.md` and `final-audit-resolutions.json`.'
    text=text.replace(before,after)
    qa=json.loads((BASE/'review/pdf-inspection.json').read_text(encoding='utf-8'))
    assert qa['status']=='passed after visual corrections'
    insert='\nThe final PDF has 33 pages, 69 verified reference URLs, zero out-of-margin text spans and no remaining observed visual defect. All pages were inspected through contact sheets, with full-size checks of the coordinate diagram, observation diagram and corrected references. DOI-parenthesis parsing and a diagram border were repaired in separate print versions. The last changes affect only pages 33 and 17; other rendered pages have identical PNG bytes and inherit their completed inspection. The frozen final text is revised-v5, whose change from revised-v4 is the diagram path. No numerical result changed. `pdf-inspection.json`, `pdf-layout.json` and the final manifest retain the actual hashes and checks.\n'
    position='\nCurrent primary site inventories and row-level supplements remain incomplete.'
    assert position in text
    text=text.replace(position,insert+position)
    path.write_text(text,encoding='utf-8')
    print('Completed response from actual source-audit and final PDF records.')

if __name__=='__main__':main()
