# Source-reading convention, 8 October 2026

Two readers independently inspect every one of the 80 selected numbered
occurrences and all 21 count pages. A third reader adjudicates their frozen
source readings. Use a separate scratch directory for each reader and record
the files actually opened, uncertain observations, start/finish times and any
exposure. Readers must not open predictions, the frame, pipeline code, full
proposals, development results, earlier references or another reader's work.
The original PDF image and chart pages are permitted. Read pixels without the
PDF OCR layer.

The locator names the intended numbered row, its number/classification field,
the source context and exact source crops. Judge a crop by whether it contains
all its drawing and uncertainty-underline ink and excludes neighbour and
field ink. Keep `crop_issues` observations for every rejected crop. The
`printed_line_crops` list can contain a numbered line and proposed unnumbered
continuations. Inspect the source to determine the actual continuation
membership; the list is a geometry proposal. Read all lines belonging to the
numbered occurrence, even if the proposed list omits one. Judge `crop_correct`
true only when the proposed list covers the complete intended occurrence and
each separate box is acceptable. Record missing, extra or misattached lines.

Record units within each physical line in visual left-to-right order, then
concatenate lines top-to-bottom for the numbered-occurrence metric. Preserve
the line break explicitly in source notes or `physical_lines`. An unnumbered
line remains a physical line; it does not create another printed number. Do
not infer an ancient side/line boundary from a blank gap. A loss rectangle or
hatched span is one modern editorial unit with unknown ancient extent. Read
letter-suffixed numbers literally and preserve all five classification
positions, including spaces for printed blank positions.

Use the position-chart cards and check disputed geometry against chart pages
20–21. Code 25 is the high pair of ticks and code 2 the centred pair. Codes
597/13 place a narrow hatched patch at its cell's left edge; 598/542 place it
at the right edge. Their tight shapes coincide. Use the neighbouring sign's
cell offset and the roughly two-point inter-cell gap: a patch ending roughly
two points before the next cell can support the right-edge variant; the
left-edge version implies about eight more points of space before that next
cell. Compare source ink to the chart and retain both candidates when the
cell geometry is unresolved. An underline spans the sign cell, so retain its
full width and associate it with that cell. Do not select a code from an
expected sequence. Other chart candidate sets remain sets. Leave an
unresolved strict set empty with an explanation. Preserve coincident cards,
including the documented 144/244 labelling uncertainty, as source observations.

Reference JSON has a `rows` array containing all indices 0–79. Each row needs
`sample_index`, `printed_inscription_id`, `classification_literal`,
`drawn_unit_count`, `crop_correct`, `crop_issues`, `units` and source notes.
Each unit needs `strict_candidate_codes`; also record shape-only candidates,
chart locations, underline presence, unit kind and uncertainty where useful.
Count and list every modern editorial unit. A damaged or wrongly cropped
target remains in the denominator. A locator that identifies no valid
printed target gets `valid_printed_target: false` and a source explanation.

For each count-page image, find the actual columns, including the compact
five-to-eight-column stress pages. Count numbered/classification pairs as
numbered occurrences. Also count every physical glyph line, including
unnumbered continuations and damaged lines. Count JSON has a `pages` array;
each page has `pdf_page` and `columns`. Each column needs `x_extent_pdf`
(including its field), `row_count`, `row_centers_pdf`,
`physical_line_count`, `physical_line_centers_pdf` and `continuation_lines`
with source centers and proposed parent numbers when readable. Coordinates
are PDF points; the supplied page PNG has two pixels per point. Set the
numbered center at the numbered glyph line and the physical centers at each
glyph line's vertical middle. The numbered center list length must equal
`row_count`; the physical list length must equal `physical_line_count`.
Disclose uncertainty instead of imposing two columns or 36 rows. Random
pages and prespecified stress pages are evaluated separately.

Attribution: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus
Script* (1979), University of Helsinki, [handle](http://hdl.handle.net/10138/342677),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Cropping and card
arrangement are modifications by this project.
