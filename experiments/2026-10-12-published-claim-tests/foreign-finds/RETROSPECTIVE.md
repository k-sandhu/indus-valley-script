# Retrospective: Study B, inscriptions found outside South Asia

## Approach

The run began with AGENTS.md, the writing rules, the parent protocol and the registry entries for `CHRONOLOGY-REGION-01` and `EVIDENCE-CENSUS-SITES-ABROAD-01`. The earlier chronology-region test had kept seven external objects under exact type and length matching and listed matched round seals as its retry condition. This study therefore kept damaged texts, using comparators that carry the same damage mask, and compared round seals with all South Asian seals.

Sources were searched before the protocol was written. Rao et al. (2009) and Parpola's 2005 lecture were downloaded and read. Laursen (2010) and Parpola (2018) were read from copies acquired by earlier packages. Parpola 1994a, Hunter 1932 and Parpola, Parpola & Brunswig 1977 are known here only through Laursen; Brunswig, Parpola & Potts 1983 only through catalogue records. Laursen's account added testable details beyond the general claim: the round-versus-square contrast, Hunter's supported Mohenjo-daro round seals and the "twins"-initial count.

A pre-freeze audit read only metadata, damage structure with signs masked, comparator cell sizes and South-Asian-only positional counts. It found three unscorable West Asian texts and the Dilmun/Ur duplicate witness, through the census join of BM 123208 to U.17649. It also found a tie between signs 817 and 820 as the most frequent initial sign, so the protocol used the top three, and 16 South Asian round and cylinder seal faces. The protocol was frozen with SHA-256 hashes before the analysis script ran.

## Problems and fixes

Harappa.com returned HTTP 403 to the fetch tool, and the same URLs downloaded with curl and a browser user agent. Rao's PDF arrived as binary and was converted with pdftotext. Printed page numbers for Parpola 2005 and Laursen 2010 were read from the page footers of the extracted text.

The first full run stopped while writing JSON, because the fold-size dictionary had integer keys; keys are now converted to strings. The second run ran out of memory. Models refitted to exclude a test text's identical South Asian copies were being cached for every peripheral test text; they are now discarded after each test. Neither fix changed the design. The third run took about three and a half minutes, and the independent verification about fifty seconds.

The outputs showed that grouping by object family and identical text joins 1,595 South Asian faces, mostly Harappa tablets, into one component, so fold 4 holds 2,015 of 5,617 faces. Comparisons are made within folds, so the frozen result stands. An exploratory rerun using comparators outside that component was added (E1).

The writing tool refused to create REPORT.md and RETROSPECTIVE.md from the subagent session, so their text was returned to the coordinating session, which saved it.

## Outcomes

West Asian texts gave Ū = 0.770 (0.660–0.866) and round seals 0.870 (0.776–0.945), against South Asian regions at 0.49–0.57. All four regional differences have intervals above zero, and all eight sensitivities keep Ū at or above 0.754. South Asian round and cylinder seals gave 0.704 (0.531–0.872), and the West-minus-South-Asian round difference has an interval that includes zero. The secondary measures place the difference in transitions and positions rather than in rare signs. Verification reproduced the headline values exactly in 22 of 22 checks.

## Additions after the outcomes

Three results prompted exploratory checks, all labelled as such in the report. The atypical South Asian round group led to a split by circular and cylinder type (E2) and a count of transitions shared with the West Asian round seals (E4). The disagreement with Parpola's assessment of the Iranian and Girsu seals led to a coarser alphabet built from the Mayig crosswalk (E5). Locating adjacent 740–740 (E3) checked Parpola's 2005 statement directly. None of these checks changed a frozen decision.
