# Presentation review

We inspected every version 2 slide individually at its 1600 by 900 PowerPoint render size. We checked source captions and scale bars, annotated feature locations, table wrapping, chart bounds, the distinction between route geometry and open access, and the final test design. The full Figure 11 caption in the Harappa context excerpt remains visible, including its conflicting find-context assignment.

The review led to two further repairs: the unit header on slides 6 and 16 wrapped within the word `Metres`, so version 3 uses `m`. We rendered every version 3 slide again. The PNG hashes show that the other 24 slides are identical to their inspected version 2 images. We inspected final slides 6 and 16 individually and then reviewed the final 26-slide contact sheet. No outstanding layout defect was found.

Microsoft PowerPoint 16.0 opened the final file, rendered 26 slides and left its hash unchanged. In a separate test copy we changed and resized each of the three native charts, saved the file and reopened it. The edit and reopen checks passed. The finalizer reported no package or layout findings and no layout warnings. The independent package verifier matched all 42 numeric chart cache points to the frozen inputs, checked all 19 authored input files and 95 image assets, and found 26 note pages, three native charts, eight native tables and 23 embedded media files.

The notes preserve the exact input identities and locators. This review checks readable presentation and faithful transfer of the frozen evidence. The root source and measurement audits support the archaeological content. A local plan width remains a local geometric reading, and the deck does not turn it into a survival rate or evidence for an institution.

Review artifacts remain on D: under `presentation/build/v3/`. `render-comparison.json` records all final PNG hashes, `powerpoint/native-review.json` records the native application checks, and `powerpoint/contact.png` records the final slide overview. The manifest points to them and records their hashes.
