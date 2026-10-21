# Plate audit of catalogued line divisions (Q-0027)

Working directory: `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. You are checking how the catalogue divides Indus inscriptions into lines against photographs cut from the printed plates of the *Corpus of Indus Seals and Inscriptions* (CISI). The result is a training and test set for a segmenter, so we need to know, face by face, whether each recorded division is real, where it falls, and which written line comes first on the object.

## What the worklist gives you

Your worklist is `data/raw/2026-10-20-seal-legend-units/plate-audit/worklist-<GROUP>.tsv` (tab-separated). Each row is one inscribed face. `code_visual_ltr` is the transcription in Wells sign numbers as the signs appear on the impression (the positive image a seal leaves in clay), written left to right; `/` marks the catalogue's line division, `000` an unreadable sign and `[` or `]` a damaged edge. `segments` is the number of parts the `/` marks create and `signs_per_segment` their sign counts in code order. The code lists the parts in a fixed order, but nobody has checked whether the first part is the upper row, the lower row, or a group elsewhere on the face. `files` lists the image files with their kind: `object` is a photograph of the seal itself, which shows the signs mirror-reversed; `impression` is a photograph of a modern impression, which shows them the right way round. The files are in `data/lipi/public/seal_images/`. Open them with the Read tool, which displays images; prefer an impression where one exists and use the object photograph to resolve doubts. Rows above and below on a seal stay above and below in both kinds of image, since the mirror reversal is left to right only.

Most faces are square stamp seals: a row of signs runs along the top edge above an animal, and a second, shorter group of signs sits below the first row, beside the animal's head or back, or in a corner. Some objects are tablets, pottery or other items where the rows may be stacked differently.

## What to record for each face

For every row of your worklist, look at its images and write one line of a tab-separated file `data/raw/2026-10-20-seal-legend-units/plate-audit/verdicts-<GROUP>.tsv` with these columns, in this order, and a header line:

1. `record_id` as given.
2. `cisi` as given.
3. `legible`: `yes` if you can count the signs in each group, `partly` if you can count some groups, `no` if the image does not let you count signs (too small, damaged, or the wrong face).
4. `groups_seen`: the number of separate rows or clusters of signs on the face.
5. `counts_seen`: the number of signs you count in each group, listed from the top group downwards, joined by `+` (for example `5+2`). For two groups side by side at the same height, list the right-hand group first on the impression and say so in the note. Count a set of vertical strokes standing together as one sign, and a pair of tall parallel strokes as one sign, since the Wells list numbers a stroke group as one sign. Write `?` where you cannot count.
6. `division_confirmed`: `yes` if the face shows the signs split into the groups the code records (same number of groups, and counts that match the code's counts in some order allowing for one sign of counting doubt), `no` if it does not (for example one continuous row, or a different split), `unclear` otherwise.
7. `first_segment_is`: where the code's first segment sits: `top`, `bottom`, `left`, `right`, `field` (a group placed elsewhere in the picture field), or `undetermined`. Decide this from the sign counts when the two segments differ in length, and from sign shapes when they do not: the code numbers give the shapes (740 is a jar with handles, 002 a pair of tall strokes, 031 to 035 groups of short strokes, 861 and 817 lines with a bend or a bracket shape, 220 a fish-like sign, 400 a comb-like sign).
8. `layout`: `wrapped` when the second group continues the same band of writing on the next row, close to the first row and in the same orientation; `separate` when one group is set apart, such as below the animal, in a corner, or in a different orientation; `numeral` when the separate group is a set of strokes alone; `other` for anything else.
9. `confidence`: `high`, `medium` or `low` for your decisions in columns 6 to 8.
10. `note`: one short sentence where something needs explaining, such as a damaged corner or a crop showing the wrong side.

Record what you see without trying to reconcile it with the code. If a crop shows a different object or side, say so in the note and mark `legible` as `no`. Do not modify any other file, and do not open experiment code or results in the repository: the audit has to be independent of the analysis it feeds.

When you finish, reply with a short account in connected prose: how many faces you could check, how many divisions you confirmed, the pattern you saw in where the code's first segment sits, and anything that should change how these divisions are used. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.
