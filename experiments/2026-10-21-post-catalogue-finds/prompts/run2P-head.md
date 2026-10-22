# Codex run 2P: extract post-catalogue inscribed objects for Pakistan

## Your part

Part letter `P`. Owned paths: `experiments/2026-10-21-post-catalogue-finds/extraction/P/` and `data/raw/2026-10-21-post-catalogue-finds/run2P/`. Output files are named with `P` in place of `<part>`.

Sites (code, project label, aliases, baseline):

| Code | Site | Aliases | Baseline |
|---|---|---|---|
| NHT | Nuhato | Gharo Bhiro, Garho Bhiro | CISI 2, 1991 |
| TJB | Taloor Ji Bhit | | CISI 2, 1991 |
| LKD | Lakhanjo-daro | Lakhan-jo-daro, Lakhueen-jo-daro, Lakheen-jo-daro | CISI 2, 1991 |
| GNW | Ganweriwala | | CISI 2, 1991 |
| CHN | Chanhu-daro | Chanhujo-daro | CISI 3.2, 2019 |
| WTW | Wattoowala | | CISI 2, 1991 |
| CHL | Cholistan sites | Derawar Ther, Rappwala Ther, Guddal A, Bakkar Buthi | CISI 2, 1991 |
| RJP | Rajanpur | Chak 585, Tibba Rajanpur | CISI 2, 1991 |
| HRP | Harappa | | CISI 3.1, 2010 |
| MHJ | Mohenjo-daro | | CISI 3.1, 2010 |
| new | any other Pakistani site with an inscribed find reported after 1991 | | CISI 2, 1991 |

Sources. Held: `nuhato-2018-held` and `chanhu-surface2017-held`, with page text under `data/raw/2026-10-21-post-catalogue-finds/run1a/text/`. Run 1B downloaded these into `data/raw/2026-10-21-post-catalogue-finds/run1b/sources/<id>/`, without page text: `chn-desset-2022` (seals and inscriptions from the renewed Chanhu-daro excavations, published after CISI 3.2, so its objects found from 2015 on are post-catalogue), `chn-didier-2017`, `gnw-parpola-2016`, `hrp-parpola-2019`, `lkd-biagi-2022`, `lkd-doam-notice`, `nht-journal-2019` and `rjp-doam-notice`. Extract their page text into `data/raw/2026-10-21-post-catalogue-finds/run2P/text/<id>/p<NNNN>.txt`. Bibliographic records and the leads that could not be downloaded (Dawn reports for Wattoowala and Lakhan-jo-daro, Mughal 1997 *Ancient Cholistan*, the 2021 Chanhu-daro preliminary report) are in `acquisition-web/source-candidates-1b.csv`; record them in your site notes as unread sources.

The *Puratattva* and *Man and Environment* pages marked for Harappa and Mohenjo-daro in `acquisition/candidate-pages-1a.csv` all predate CISI 3.1 (2010). Under Amendment 1 they give count statements only, and you may stop reading a page once you have established that it reports no object found after 2009.

For Harappa and Mohenjo-daro, an object in a publication after 2010 that carries a CISI number is a catalogued object: record it with `catalogue_status = in-baseline-catalogue` and the CISI number in `other_numbers`, and do not count it as post-catalogue.
