# Independent check of the museum joins

Reviewer: Claude Opus 5.5 (Claude Code), 13 October 2026, local files only. Per-row results are in `independent-check.csv`; crops of the rows and labels read are in `data/raw/2026-10-13-museum-open-access/verification-crops/` (local-only).

For each joined row I re-derived the Lipi family by exact, prefix and substring matching of the CISI and excavation numbers, read the cited row or plate on the page images (pairing drifted Marshall and Mackay rows by counting entries), confirmed the museum identifier in the saved record and compared CISI crops where they exist.

## Results

All 26 joins are supported, none is qualified and none is wrong. Precision (supported plus qualified over checked) is 26/26 = 100%, and strict precision (supported over checked) is also 26/26 = 100%. The one-sided 95% exact binomial lower bound is 89%.

Every printed row reads as stated. Three joins are weaker:

- **BM 1947,0416.1** rests on Dk 7665 and Mackay row 686C. Museum: 3.7 cm, five characters, standing bull; Lipi: 35.1 mm, four signs, zebu.
- **NM 3697-54** rests on the idno prefix DK 3697 plus material, two inscribed faces and size. No printed row links it to M-2053. CISI 1's copper tablets carry NMI 39 to 66 but no NMI 54, which fits a later entry as M-2053.
- **NM 1860/1239**: the CISI row reads 1869, and the join holds through SRG 1239.

Two Lipi faults at Lothal surfaced. Family 2067 (L-122) has the idno 09989, which is CISI 1's number for L-100 (9989, SRG 1331). Its idno-linked fields may belong to L-100; "2845" painted on the object (crop L-122_B) still secures the NM join. Family 2084 (L-142) carries 1831, the number of L-166, where CISI 1 gives 1809.

NM SRG-989/128 describes a mountain goat, but impression L-29 a shows a one-horned bull before a standard, and "SRG.989" is written on the object.

## Non-joins

One non-join resolves: **IM 10377/A7252/C.2803** is family 2194 (M-1809). Marshall p. 403 row 199 reads 0.85 x 0.85 in, 2 ft 6 in, steatite, C 2803. The family's idno is DK-C 2803199, and its unicorn, steatite, 21.6 mm and -2.5 ft agree with the museum's 2.1 cm unicorn seal. The package searched C 2803 as an exact idno; family 2194 was among its 125 descriptive candidates.

The other five find no join:

- **IM 11095/A6721**: neither number appears among CISI 1's Harappa IM entries.
- **NM DK12995**: the only published 12995 is H-13, a Harappa unicorn. The NM-held tiger-grappler M-306 (DK 12596, NMI 145) is only a descriptive candidate.
- **NM dk.7237**: no DK 7237 appears in the Lipi idnos or CISI 1's M rows.
- **NM BNL-1-6230 and NM 3714**: neither number is in Banawali rows B-1 to B-37, and no Banawali crop shows an elephant with signs or a painted number.

## Not checked

- **Museum photographs**: none compared; only Metropolitan and Cleveland images are cached.
- **CISI 3.1**: not held, so M-1662, M-1720, M-1727, M-1809, M-1883, M-1893, M-1906, M-1919 and M-2053 were not read.
- **Mackay 1943 pp. 292-293**: not held. The census text extraction `mackay_1943_chandaro.pdf.txt` is empty, so the Penn pairings rest on Lipi idnos and on plates matching the Penn descriptions.
- **BM 123208**: only its search-listing line is available.

## Reading and test

The package's identifier joins are correct throughout, and its residual error is recall: exact matching misses Lipi idnos that join area prefixes and row or plate numbers to the excavation number. The deciding test is a substring search of normalized idnos against every identifier in the 60 non-joined rows, with each hit read against its printed row.
