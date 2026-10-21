# Seal findspot maps, 20 October 2026

This package draws where identical seal texts were found, where seals carry texts that differ from them in one sign, and where clay sealings match a seal text. The idea under test is that seal legends name individuals, offices or titles. A personal legend should occur once, or only where its holder lived. A title should recur in several cities. Sealings found far from the matching seal trace where sealed goods ended up. Status: exploratory. The population and grouping come from the [seal-text identity study](../2026-10-12-seal-text-identity/REPORT.md), and the comparisons below were chosen after that study had reported.

## What was built

[build.py](build.py) imports the population rules of the 12 October study rather than copying them, and asserts that they reproduce its counts. The population is 1,430 seals with a complete, legible, single-line text of at least two signs from South Asian sites, one face per object family. Among them, 65 texts recur on 174 seals, and 16 sealings or tags carry a seal text. Site coordinates come from the [8 October site map](../2026-10-08-site-map-and-overview/README.md). Wattoowala, which has one seal, has no coordinate and is left off the map.

The page has three parts. A Leaflet map draws an arc between two sites for every text found on seals at both, with width proportional to the number of such texts. Dashed arcs join a sealing's findspot to the findspot of the matching seal. Clicking a text shows each seal and sealing that carries it, with the photograph crops held locally, the animal, face size, material, findspot, depth and period. It also shows seals of the same length whose text differs in one sign. The site-pair table compares each link with a reference in which site labels are shuffled 5,000 times across all 1,430 seals (seed 20261020). Each site keeps its number of seals, and the grouping of seals into shared texts is held fixed.

The page carries sign sequences, catalogue numbers and findspots taken from the Lipi export. That export has no licence at the pinned commit, so the page and its record table stay local, in `data/raw/2026-10-20-seal-findspot-maps/`. The tracked output, [run-2026-10-20/site-links.json](run-2026-10-20/site-links.json), holds only site counts, site-pair counts with their reference ranges, and sealing links.

To open the page, serve `data/` and visit the page in a browser. The photograph links are relative to `data/`, so a `file://` URL shows the map without images.

```text
python -m http.server 8765 --bind 127.0.0.1 --directory data
http://127.0.0.1:8765/raw/2026-10-20-seal-findspot-maps/seal-findspots.html
```

## What the comparison shows

Across all lengths, Mohenjo-daro and Harappa share 23 texts against 21.6 expected from random placement (95% range 15–29). Mohenjo-daro holds 32 texts with two or more copies in the city, against 36.4 expected (29–43). Both figures match random placement, which repeats the 12 October result: within and between the two largest cities, copies of a text fall where the seals are.

The smaller sites behave differently:
- Banawali has 2 texts repeated within the site, against 0.02 expected.
- Dholavira has 2, against 0.35.
- Banawali and Kalibangan, about 130 km apart on the Ghaggar plain, share 2 texts against 0.08 expected.
- Among texts of four or more signs, Chanhu-daro and Harappa, 666 km apart, share 2 against 0.2.

These links fit families or offices tied to particular places or particular pairs of cities, beside a stock of short texts spread across every city. With dozens of site pairs compared, a few would pass at p < 0.05 by chance, so they are leads for a frozen test, not results.

Of the 16 matching sealings, 11 were found at Lothal: ten carry the text of Mohenjo-daro seal M-895 and one the text of two other Mohenjo-daro seals. Three Mohenjo-daro tags carry texts also found on seals at Mohenjo-daro, Harappa, Lothal and Kalibangan, and one sealing each at Kalibangan and Rupar matches Mohenjo-daro seals.

## Limits

Texts, animals, sizes and findspots come from one transcription and have not all been checked against the photographs. Two-sign texts can coincide with no connection between holders. A seal's findspot is where it was lost or discarded, not necessarily where it was used. The near-copy layer is a display aid: some near copies will be misreadings of the same text.

The boldest reading these maps support is that Indus seal legends come in two kinds: a stock of short titles shared at random across every city, and longer legends held by families or offices tied to particular sites or particular pairs of cities, as at Banawali, Dholavira, Banawali with Kalibangan, and Chanhu-daro with Harappa. A frozen test would settle it. On seals that no analysis has read, such as the CISI 3.1 seals absent from the local corpus, predict that copies of texts of four or more signs fall on fewer site pairs than random placement allows, while copies of two-sign texts follow random placement.
