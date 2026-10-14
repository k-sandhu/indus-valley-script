# Amendment 2: bracketed merge for the CISI 2 blocks left unadjudicated

14 October 2026, written after the CISI 1 adjudication was complete and three CISI 2 blocks (p. 437L, 438L, 439L) had been adjudicated, and before any CISI 2 final table was built or any cross-check or coverage was computed.

The two CISI 2 readings disagree on 3,126 cells, about a third of the total, against 112 for CISI 1. Most of these are cells where one reader bracketed a digit that the other read definitely, on pages that both readers describe as blurred or pixelated. Adjudicating every one of them against the page, as the protocol requires, was stopped at the owner's request because of its cost, after 256 decisions in three blocks.

For the other 21 CISI 2 blocks, the M-595 entry and the CISI 2 corrigenda, each disagreement is settled by rule instead of by a third reading, with [auto_adjudicate.py](auto_adjudicate.py):

- A disagreeing cell becomes a bracketed cell that keeps every candidate either reader allowed: where one reading's candidates include the other's, the wider reading is kept; otherwise the two readings are aligned character by character and each differing stretch is written as `[a/b]`, or `[??]` when the stretches cannot be expressed as alternatives (an inserted or deleted stretch, a wildcard, or more than four candidates). The outcome is recorded as `undecidable` with a note that it was not adjudicated.
- A corrigenda line read differently is merged the same way.
- When one printed entry was given different CISI numbers by the two readers (it appears as an entry present in one pass only on each side, at the same place), the entry is kept once under the first reader's number with its other cells merged as above, and the second reader's number is recorded as `absent`. The entry the second reader read from the cut-off foot of a strip, which the tail reading repeats, is dropped by the assembly rule of Amendment 1.

Cells on which the two readers agree are final as read, and the three adjudicated blocks keep their decisions. The consequence is that the CISI 2 table keeps more uncertain cells than full adjudication would have left, and its error rates cannot be measured for the unadjudicated blocks: the report gives the agreement between readers for all blocks, the adjudicated error rates for CISI 1 and the three CISI 2 blocks, and coverage counted both with and without bracketed cells. The re-reading of cross-check flags against the page is also not done; the flags are counted and listed for later work. Everything else in the protocol is unchanged.
