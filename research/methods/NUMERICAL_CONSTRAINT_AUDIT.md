# Conditional numerical equalities: exact algebra and its limits

The [author-posted 2023 reprint of Fuls's 2020 proceedings chapter](https://www.researchgate.net/profile/Andreas-Fuls/publication/373522958_Ancient_Writing_and_Modern_Technologies_-_Structural_Analysis_of_Numerical_Indus_Inscriptions/links/64f04b160f7ab20a8667db0b/Ancient-Writing-and-Modern-Technologies-Structural-Analysis-of-Numerical-Indus-Inscriptions.pdf), reprint printed pages 29–32, proposes numerical relationships for M1383, ICIT3786 and M331. The original chapter is bibliographically pages 57–90; all detailed coordinates here refer to the linked reprint, which prints pages 15–48. This audit checks the exact arithmetic conditional on those relationships; it does not validate the referents or positional readings.

Let `L` and `S` be the hypothesized integer multipliers for the selected long- and short-stroke positions, and `v` the proposed unit value of W900. Assume

`v = 2S-L` and `vL+1 = 7S+5`.

Eliminating `v` gives

`(2L-7)S = L²+4`.

Set `d=2L-7`. Then

`4(L²+4) = d(2L+7)+65`.

For integer `L,S`, `d` must divide 65. For positive `S`, `d` is positive because `L²+4` is positive. The complete unbounded positive solution set therefore comes from `d=1,5,13,65`:

| L | S | v | Assumed M1383 expression 7+L |
|---:|---:|---:|---:|
| 4 | 20 | 36 | 11 |
| 6 | 8 | 10 | 13 |
| 10 | 8 | 6 | 17 |
| 36 | 20 | 4 | 43 |

Both assumed ranges `8≤L≤13` and `8≤L≤18` select only `(L,S,v)=(10,8,6)`. The same holds through upper bound 35; admitting 36 adds `(36,20,4)`. If one assumes only a positional digit maximum requiring `L≥10`, two solutions remain, with bases 10 and 36. Every positive solution already has `S≥8`, positive `v`, and composite `L`, so neither an even-base nor prime-base exclusion is needed for this conjunction.

The chapter's printed-page-30 footnote incorrectly infers that integer `S=(v+L)/2` makes `S` even. It only makes `v` and `L` have the same parity: `(L,S,v)=(10,9,8)` satisfies that first equation with odd `S`. Even `S` emerges from the full joint solution set here, rather than from that inference.

The numerical uniqueness is conditional on identifying equal quantities on different faces, assigning the selected positional multipliers, adding specified text parts, and identifying a bangle expression with a reconstructed total. Images can corroborate carving and physical grouping; they do not establish those semantic operations. The source also describes three long strokes on ICIT3786 while naming W032, which requires independent graphic adjudication. Source assumptions and page locations are recorded in the machine-readable audit.

“ICIT3786” is the paper's historical identifier. Its physical/CISI identity is unresolved here, and it is not joined to a current Lipi row by that number. The corpus versions are known to renumber records; the current numeric match is a different inscription. The author figure or an older source register is required for a physical identification.

A structural search by the root agent found a candidate current object 1786 / CISI H904 with reading-order sequences `002-840-032-740` and `817-368-645-900-033-700`. This is a candidate based on matching sign clusters, not an established historical identifier correspondence. It needs the author's Fig. 16 or a historical register for that correspondence. Any numerical interpretation would also require an explicit treatment of the additional signs omitted from the abstract equality. Subset matching alone cannot prove equal quantities, a common commodity, or permission to ignore the extra signs.

The literature agent subsequently acquired the original Vats (1940) Plate XCVI photograph 477, corresponding to candidate H904. An independent AI visual check of that retained crop confirms three long strokes beside the crescent/U face and two beside the overlapping-circle face; the finer short-stroke marks are less clear. This supports the prose coefficient 3 for the candidate, rather than an observed two-stroke correction. It does not yet establish the historical ICIT3786 correspondence or validate the equality. Retained crop: `../literature/metrology/primary_numeric/vats_h904/477_crop12x.png`.

The primary Vats text table, printed p. 349 / PDF p. 378, joins photograph 477 to find J213 in Mound D and dimensions 0.65 by 0.28 inches, matching H904's supplied J213(D)477 and 16.5 by 7.1 mm. This supports the H904/Vats physical-object join, while the author's historical ICIT3786 join remains provisional. Primary sources: [Vats plates](https://ignca.gov.in/Asi_data/9842.pdf) and [excavation table](https://ignca.gov.in/Asi_data/18220.pdf); the complete audit is in `../literature/metrology/numerical_source_premises.json`.

The externally selected bangle range also remains ungrounded in this investigation. The literature agent inspected Vidale's original 1987 chapter, *More Evidence on a Protohistoric Ceramic Puzzle*, printed pp. 105–111 / PDF pp. 108–114 of the [government-hosted Interim Reports Vol. 2](https://ignca.gov.in/Asi_data/77275.pdf). It describes a fused DK-B,C kiln-slag block whose identity with M1383 has not been established, with a conjectural five-bowls/two-bangles-each total and an apparent seven-bowl anomaly. The inspected chapter does not provide an M1383 inscription/object join, 82 fragments or a 15–20 total. This does not prove the proposed M1383 count false; it means that this primary source does not establish the inscription-specific bound. The remaining historical reconstruction is cited through Wells (2015) and has not been independently verified here.

The inspected author reprint's Fig. 15 caption explicitly names M-1383. A current record with that CISI identifier contains the expected `017-031` cluster but is labelled ClayTAG:R/MN82a, raising an unresolved object-type/context join. Neither the matching cluster nor this metadata conflict establishes the bangle total, and the conflict is not treated as proof of distinct physical objects.

An independent AI visual check of the original CISI1 M331 plate, printed page 84/PDF page 120, corroborates the coarse five-stacked, four-stroke, crescent-plus-one, and three-stroke groups on the same physical object. The retained plate is `../literature/metrology/primary_numeric/M331_pdf120.png`. This is graphic corroboration, with no specialist certification of height categories; it neither establishes numerical ranks nor makes the faces an arithmetic total/parts record.

The count discrepancy directly affects the equation. Holding the other proposed readings fixed, an actual two-long-stroke first side would give `v=2S`. Together with the M331 relation its sole positive integer solution is `(L,S,v)=(4,4,8)`, so none remains with `S≥8` or either bangle range. A hypothetical four-stroke first side instead yields the selected-range solution `(13,18,10)`. These are input-premise sensitivities, not verified source readings. `numerical_count_delta.py` proves the corresponding divisor bounds and records them in `results/numerical_equalities/numerical_count_delta_sensitivity.json`.

These proposed equations and selected values are published prior. The useful result is a precise, falsifiable constraint: freeze the graphic coefficients, units and equal-quantity rule, then predict a separately acquired total/parts or externally counted object. Without those anchors, this arithmetic is neither a new numeral decipherment nor a sound/meaning assignment.

`src/methods/audit_numerical_equalities.py` uses exact fractions, enumerates every signed divisor, checks both equations, and independently brute-forces `1≤L≤1000, 8≤S≤1000`. Results: `results/numerical_equalities/numerical_equalities_audit.json`.
