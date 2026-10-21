# Feasibility ledger

This ledger records, for each comparison source, whether its legends link to a physical object and a site, how many legends survive the protocol's rules, and what would close each gap. It was written on 21 October 2026 (UTC), after normalisation and before the discrimination runs. The counts come from [corpus-counts.json](corpus-counts.json) and from the eligibility code of `discriminate.py`, and contain no statistic. Record-level files stay under `data/raw/2026-10-21-head-direction-corpora/`.

## Sources acquired

Each file was downloaded into its own empty directory with [fetch_source.py](fetch_source.py), and every acquisition record is in [acquisition/](acquisition/). The Internet Archive files matched the SHA-1 and size published by the archive's metadata API. The ORACC Old Akkadian archive was first fetched without TLS peer verification after repeated certificate failures; we downloaded it again with verification and obtained the same SHA-256.

| Source id | Edition | File and size | SHA-256 (first 16) | Rights status | Used for |
|---|---|---|---|---|---|
| `asi-ar-1903-04` | Bloch, "Excavations at Basarh", *ASI Annual Report 1903–04* (1906), inscribed clay seals pp. 101–120 | Internet Archive `in.ernet.dli.2015.207529`, PDF 204,293,478 bytes, 476 pages; second scan `in.gov.ignca.21816` | 83ad9f30191c4aa2 | Government publication of 1906, public domain by age (our assessment); archive item states no licence | 140 entries, 120 with legends |
| `asi-ar-1909-10` | Director-General's summary of Marshall's first Bhita season, *ASI Annual Report 1909–10*, pp. 40–42 | `in.ernet.dli.2015.35501`, PDF 15,007,114 bytes | 96392b89b3dc54e8 | As above (1914) | Witness that no seal list was printed |
| `asi-ar-1911-12` | Marshall, "Excavations at Bhita", *ASI Annual Report 1911–12* (1915), seals and sealings pp. 44–61 | `in.ernet.dli.2015.207521`, PDF 33,076,046 bytes; second scan `in.ernet.dli.2015.35495` | 5e0695ea81c24167 | As above (1915) | 120 entries, 101 readings; findspot index of 25 places |
| `asi-ar-1913-14` | Spooner, "Excavations at Basarh", *ASI Annual Report 1913–14* (1917), list of seals from p. 124 and field register | `dli.ministry.09311`, PDF 50,488,078 bytes; second scan `in.ernet.dli.2015.35545` | 25943cb02f068dc9 | As above (1917) | 235 entries and 51 impressions; 233 register rows |
| `mahadevan-2003` | Mahadevan, *Early Tamil Epigraphy*, Harvard Oriental Series 62 (2003), Tables 1.6–1.8 | Third-party upload `iravatham-mahadevan-early-tamil-epigraphy-…`, PDF 233,674,839 bytes, 772 pages | 2cc1fc9eab8fbe76 | Copyright 2003; upload carries no licence; local-only, aggregates tracked | 13 coins, 5 seal-table rows, 14 rings |
| `oracc-oakk` | ORACC `epsd2/admin/oakk` JSON archive | 29,933,476 bytes | 4d4eaf78ba1fa6d9 | CC0, declared in the JSON | Lemmatised Old Akkadian sealings |
| `cdli-data` | CDLI bulk data, GitHub `cdli-gh/data` at commit `d66b12b` | `cdli_cat.csv` 154,768,722 bytes; `cdliatf_unblocked.atf` 86,897,831 bytes | 2e3232f75325b61c; 2896ec253767fa07 | CDLI terms: free re-use under common and fair academic practice with credit; no licence file | Old Akkadian seals and sealings |
| `sumerian-ur3-v1` (held) | ORACC `epsd2/admin/ur3` JSON archive, acquired 12 October | 561,755,376 bytes | b220f3ee0707912d | CC0, declared in the JSON | All Ur III seal legends, not only the 3,000-entry sample |

The four Survey reports and the CDLI data have the status `rights-unverified` in the project's vocabulary, because the vocabulary has no public-domain status; the public-domain assessment for the reports rests on their dates of publication. Our transcriptions of the Survey legends could be tracked after a maintainer's review under [REDISTRIBUTION.md](../../knowledge/provenance/REDISTRIBUTION.md); this package keeps them local.

## Object and site linkage

Every normalised record names its object. The Survey lists name a seal die (Bloch's varieties), a clay lump with its register number (Spooner) or a numbered seal or sealing (Marshall), always at Basarh or Bhita. ORACC and CDLI name the sealed tablet, envelope or bulla, or the seal. Mahadevan's rows name a seal, ring or coin, but six of his coins have no findsite in the passages he prints, only a collection.

| Corpus | Records | Objects | With site | Excluded | Eligible legends, sign level | Eligible legends, word level |
|---|---:|---:|---:|---:|---:|---:|
| `ia-ganges` (Basarh and Bhita) | 556 | 495 | 556 | 0 | 245 | 30 |
| `ta-brahmi` (Mahadevan) | 31 | 31 | 25 | 1 touchstone, before normalisation | 23 (16 seals and rings) | 7 |
| `sux-ur3` (Ur III) | 31,512 | 31,220 | 30,520 | 5 composite editions, 1 cast | 3,044 | 3,026 |
| `akk-sargonic` (Old Akkadian, Akkadian) | 89 | 89 | 68 | 17 composite editions | 11 | 10 |
| `sux-sargonic` (Old Akkadian, Sumerian) | 175 | 175 | 110 | 2 composite editions | 42 | 36 |

A legend is eligible when, after grouping by die, shared alias and identical sign sequence, its chosen record is complete or restored, has an object and a site, and has at least two units at the level. Composite editions are legends CDLI reconstructs from several impressions and catalogues as one object without a physical carrier; under section 4 of the protocol they are edited texts, not objects.

## Why two corpora fall short

The Old Akkadian corpus is small because the record is small. The CDLI catalogue lists 62 Akkadian-language seals and 31 Akkadian-language sealings of the period, and only 210 of its 777 Old Akkadian seal entries of any language name a provenience; most inscribed cylinder seals are museum acquisitions without findspot. Of the 72 Akkadian records left after the exclusions, 27 have lost their first or last signs, 21 have no site, and 16 are complete with a site; grouping leaves 11 distinct legends. A larger Akkadian corpus would need the Old Assyrian seals of Kültepe or the Old Babylonian seals, whose formulae are written largely in Sumerian logograms, or the sealings of Tell Brak (ancient Nagar) and Tell Mozan (ancient Urkesh), which the corpus samples through CDLI, read in full from their excavation reports.

The Tamil-Brahmi corpus is small because few Tamil-Brahmi seals and rings were known in 2003 and most are surface finds from the Amaravati river bed at Karur. Mahadevan's seal and ring tables give 16 legends with a site, and his coins add 7 more with a findsite. Four of the 16 seal and ring legends are in Prakrit or Pali. The revised edition of *Early Tamil Epigraphy* (2014), later Karur and Keeladi finds and the Tamil Nadu graffiti volumes held locally (Rajan and Sivanantham 2026, which record names on potsherds, a different genre) are the routes to a larger corpus.

## Word level

Only 30 Indo-Aryan legends have two or more words, because most Gupta legends are one compound in the genitive (`kumārāmātyādhikaraṇasya`, `kulika-harisya`), which the editors print as one word with hyphenated members. Only 7 Tamil-Brahmi legends do. Word-level statistics therefore cannot enter for the head-final group, and the title-and-name statistic has 9 eligible Indo-Aryan legends and 1 Tamil one. A word-level test would need the compound members as units, which the editors mark inconsistently.

## Line divisions for the matched-segmenter control

Section 11 of the protocol requires re-cutting the comparison legends with the segmenter trained on line divisions. The Ur III and Old Akkadian editions give the ATF lines of every legend (29,674 and 84 records). The Survey editors state a line division for 30 Indo-Aryan records and Mahadevan for 2. The Indo-Aryan legends are short and often in one line, so this control can be run on the cuneiform corpora and hardly on the head-final ones.

## Sources not acquired

| Source | Status | Route |
|---|---|---|
| Avigad and Sass, *Corpus of West Semitic Stamp Seals* (1997) | No lawful digital copy found | Library copy; transcription of the legends with object numbers and proveniences, local-only |
| Ancient South Arabian seals in DASI (Digital Archive for the Study of pre-Islamic Arabian Inscriptions) | An Open EpiHub record gives CC BY 4.0; the site's bot protection refused automated access on 21 October | A maintainer's browser session or a request to the archive |
| Marshall's preliminary Bhita note, *Journal of the Royal Asiatic Society* 1911 | Not acquired; the 1911–12 report supersedes it | JSTOR Early Journal Content |
| SIDDHAM (siddham.network) | Edits two Basarh royal seal legends with object identifiers (IN00016/OB00015, IN00031/OB00028) | Alias source for Bloch's royal seals; licence badge without a stated licence |
| Sastri, *Nālandā and its Epigraphic Material* (1942) | Not acquired | A further Indo-Aryan sealing corpus; Government of India publication |

## Coordinator corrections

Thirteen corrections were made after checking page images or the editor's own statements, in `review/corrections.json` (local): spacing in Bhita 21, 30, 31 and 33, the period of Bhita 28, the reading of Spooner 556 B (the print reads *Mukaśa·ya*; the transcription had *Mukāsa·ya*, and the raised dot marks a lost letter), the language of six Mahadevan rows, and the exclusion of his touchstone. A check of eight Bloch entries (pp. 108 and 117) found no error.

## Unresolved review items

The Codex runs listed items for review that do not change eligibility under the protocol's rules: the findspot conflicts between Marshall's catalogue and his index (entries 33, 36, 41, 45, 58, 73, 86, 110); uncertain characters in Bloch 11, 19, 27, 53, 70, 91, 104, 128–133 and Spooner 64 A, 168, 200, 226, 482, 488, 572, 603, 764, 770 and 821; proposed identities between Spooner's and Bloch's seals (Spooner 64/Bloch 131, 272 A/Bloch 87, and others), which the analysis merges only when the readings agree; the composite and mixed-language cuneiform records; four objects whose ORACC edition is unreadable and whose CDLI edition is readable; and two chronology conflicts. They are listed with locators in [codex/a1-basarh/REVIEW-DECISIONS.md](codex/a1-basarh/REVIEW-DECISIONS.md), the run notes of [codex/a2-bhita-tamil/](codex/a2-bhita-tamil/) and [codex/b-cuneiform/REVIEW-DECISIONS-CODEX.md](codex/b-cuneiform/REVIEW-DECISIONS-CODEX.md).
