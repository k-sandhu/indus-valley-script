# Amendment, 12 October 2026, before computation

Written after the Part 1 joins and Reader 1's image checks and before any Part 3 statistic was computed or any analysis code was written. Reader 2's blinded readings had not been returned. The frozen [protocol](PROTOCOL.md) stays in force; this file adds rules for situations the checks exposed and fixes details the protocol left open.

## Orientation of the Lipi codes

Lipi's visual sign order matches the impression drawings for most round seals. For two West Asian seals it is the mirror image: Failaka 148.1 (Laursen no. 12) and Qala'at al-Bahrain 3863.1 (no. 7). On 148.1 the mirroring also moves the broken edge, so that a right-to-left reading of the impression begins at the break. Janabiyah 5232.1 carries Lipi's direction L/R, yet its visual order equals the impression and Lipi's parse starts at the right end, as Parpola's reading reported by Laursen does. The protocol's rule for the reading-initial sign follows Lipi's direction field, and for these three texts it points to a sign that differs from Lipi's own parse. None of the three begins with two human figures under either definition, so the "twins" count is unaffected; the report gives both ends for each.

A new sensitivity **S1b** applies the checked transcriptions of S1 and, in addition, rewrites 148.1 and 3863.1 in impression order, read right to left with the edge flags of the impression. Indus impressions show the bull facing right with the text read from the right, and both drawings show the bull facing right. S1 itself keeps Lipi's orientation, as the protocol specifies.

## Populations and details left open

- **S3** contains the T1 seals joined to Laursen's Table 1 nos. 1–27 and 56. It drops the Daimabad, Dholavira, M-500 and M-2039 seals, which are absent from Table 1, and the Kalba seal, which Laursen illustrates in Fig. 10 but does not list.
- **S4** adds every single-line cylinder face: the Susa cylinder 3882.1, the South Asian cylinders 1387.1, 1388.1, 1388.2, 1924.1, 3669.1 and 5468.1, and the unprovenanced cylinders 3888.1 and 5557.1.
- **Positive controls** sample only texts whose length has at least 20 complete texts in the matched pool. Subsets are drawn with seed 20261018 and control nulls with seed 20261019.
- **Reader 2** reads the 13 West Asian texts with a known start that have a witness, mixed with the 15 South Asian human-figure-initial texts that have a Lipi photograph, in an order shuffled with seed 20261017. The nine West Asian texts without a local witness are non-round objects, none coded 091, and count as unconfirmed.
- **South Asian reference count.** Three of the five South Asian texts that Lipi codes as 091-initial (two Harappa tablets, H-1862 and H-1863, and a Dholavira seal) have no local image and cannot be identified by Reader 1. The primary count follows the protocol. The sensitivity that admits unconfirmed Lipi readings applies to both sides of the comparison.
- **Museum photographs.** The British Museum collection pages returned HTTP 403. The Louvre record for the Susa cylinder (SB 2425) served two photographs, which are used. No other museum images were sought.
- **Font.** Lipi's WOFF2 font could not be decoded without the Brotli extension, so the TTF decoded from the same file by the 2026-10-08 Bonta-extension package is used for rendering.
