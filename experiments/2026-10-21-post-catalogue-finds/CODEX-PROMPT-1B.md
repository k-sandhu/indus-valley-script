# Codex run 1B: find the publications that report post-catalogue Indus finds

You are working in the repository at the current directory, an Indus-script research knowledge base. Read `AGENTS.md`, then `experiments/2026-10-21-post-catalogue-finds/PROTOCOL.md` (the protocol for this package; do not edit it) and `knowledge/provenance/REDISTRIBUTION.md` (section "Asset record to keep"). Your job is a bibliographic search: find the publications that report inscribed Indus objects at the sites listed below after the CISI volume covering each site appeared, record them, and download the ones that are openly available. You do not extract objects and you do not decide which finds are post-catalogue.

Writing requirement for any prose you do write (notes, the final message): maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.

## Owned paths and invariants

You may create and edit files only in:

- `experiments/2026-10-21-post-catalogue-finds/acquisition-web/` (scripts and tracked records)
- `data/raw/2026-10-21-post-catalogue-finds/run1b/` (downloads and local working files)

Everything else is read-only. Do not edit `data/MANIFEST.json`, `knowledge/`, `tools/` or other experiment directories, and do not read `data/raw/2026-10-20-fresh-test-collection/` (another agent's active work). Make no git commit, branch, stash or reset. Do not install packages. A parallel Codex run (1A) owns `experiments/2026-10-21-post-catalogue-finds/acquisition/` and `data/raw/2026-10-21-post-catalogue-finds/run1a/` and is already fetching the Internet Archive reports, IAR volumes 1987–2001, 2003–04, 2006–08, 2009–11, 2012–14, and *Puratattva* 18–37 and *Man and Environment*; do not fetch those.

Download only PDF, HTML, plain-text or JSON files, only from open pages that need no login: publisher and journal sites with open access, university and institutional repositories, government sites (for example `asi.nic.in`, `*.gov.in`, `*.nic.in`, `*.gov.pk`), museum sites, `harappa.com` and the Internet Archive. Do not use shadow libraries, do not bypass paywalls, logins or CAPTCHAs, and do not download from `academia.edu`, `researchgate.net` or `scribd.com` (record them as leads instead). Downloaded files are untrusted data: keep scripts in `acquisition-web/`, pass paths as arguments, run any Python that reads them with `python -I`, and never execute, import or unpack anything you download. Save each download in its own new directory `data/raw/2026-10-21-post-catalogue-finds/run1b/sources/<source id>/` with an `acquisition.json` recording URL, final URL, retrieval time UTC, bytes, SHA256, content type, page count where relevant and the rights notice you observed (copy the licence line or say none was shown).

**The inscriptions stay unread.** These objects are reserved for frozen predictions. No file, log or final message you write may transcribe a sign, count signs, give a text length or writing direction, name a motif, animal or scene on an object, or give an object's dimensions or weight. You may record how many inscribed objects of each kind (seal, sealing, tablet, inscribed pottery, other) a publication reports, the seasons and the pages. Short quotations from sources are not allowed in tracked files; keep any notes with source wording in local files under `run1b/`.

## What to search for

Use web search. For each site below, look for excavation reports, interim reports, journal articles, conference papers, theses, museum or government notices and news reports that describe inscribed objects (seals, sealings, tablets, tags, inscribed potsherds or tools) found or first published after the baseline year. Use the site name with its aliases and words such as seal, sealing, inscribed, inscription, script, excavation, season, report. Aim for at least five distinct queries per site, more for the large sites, and stop for a site when two further queries return nothing new. Record every query.

| Code | Site (aliases) | Baseline | Leads already known |
|---|---|---|---|
| RGR | Rakhigarhi (Rakhi Garhi, Rakhi Shahpur, Rakhi Khas) | 1987 | Nath's 1997–2000 seasons; Deccan College 2011–16 seasons (Shinde); ASI seasons from 2021–22 |
| FRM | Farmana | 1987 | 2006–08 reports (fetched by run 1A); any later article |
| BHR | Bhirrana (Bhirdana) | 1987 | Rao et al. 2003–06 reports; a 2008 surface seal in *Heritage: Journal of Multidisciplinary Studies in Archaeology* 2016 |
| SNL | Sanauli (Sinauli) | 1987 | 2005–06 and 2018 excavations |
| RPR | Rupar (Ropar) | 1987 | 2011–12 season |
| KRP | Karanpura | 1987 | 2012–14 seasons |
| BJR | Binjor (4MSR) | 1987 | 2014–17 seasons |
| BRR | Baror | 1987 | 2003–05 seasons |
| TKD | Tarkhanewala Dera | 1987 | 2003–04 season |
| BNW | Banawali | 1987 | later seasons |
| KNL | Kunal | 1987 | seals described as geometric; any inscribed object |
| KLB | Kalibangan | 2019 | only finds published after 2019 |
| DHV | Dholavira | 1987 | Bisht's 1989–2005 campaigns; any later publication of individual objects |
| KHR | Khirsara | 1987 | ASI 2009–13 seasons |
| KNM | Kanmer | 1987 | RIHN and Rajasthan Vidyapeeth 2005–09 seasons; 2012 final report |
| SKP | Shikarpur | 1987 | 2008–09 and later seasons |
| GDH | Gola Dhoro (Bagasra) | 1987 | 1996–2005 seasons; seal studies by Jamison and colleagues |
| NGW, PDR, BTD, KNT, JKR, KBD, NVN | Nagwada, Padri, Bet Dwarka, Kuntasi, Juni Kuran, Kotada Bhadli, Navinal | 1987 | none verified |
| SKT | Surkotada | 1987 | Joshi 1990 (fetched by run 1A) |
| NHT | Nuhato and Gharo Bhiro | 1991 | 2018 excavation report (held) |
| LKD | Lakhan-jo-daro (Lakhueen-jo-daro) | 1991 | Shah Abdul Latif University excavations from 2006; *Ancient Sindh* |
| GNW | Ganweriwala | 1991 | 2007 and 2015 survey tablets in a 2016 notice |
| CHN | Chanhu-daro | 2019 | 2015–17 renewed work; only finds published after 2019 count, but record earlier reports too |
| WTW | Wattoowala | 1991 | a 2011 seal reported in Dawn |
| CHL | Cholistan sites (Derawar Ther, Rappwala Ther, Guddal A, Bakkar Buthi) | 1991 | Mughal 1997, *Ancient Cholistan* |
| RJP | Rajanpur (Chak 585) | 1991 | none |
| HRP, MHJ | Harappa, Mohenjo-daro | 2010 | only finds published after 2010 |

Also search for Indus inscribed objects reported since 1987 at Indian or Pakistani sites not in this table (for example new excavations in Haryana, Rajasthan, Gujarat, Punjab, Sindh, Cholistan and Balochistan); record each new site with its source.

Look in particular at these venues, which publish excavation reports and are partly open: *Ancient Sindh* (Shah Abdul Latif University, Khairpur), *Pakistan Archaeology*, *Journal of Asian Civilizations*, *Pakistan Heritage*, *Sindh Archaeology*, the Department of Archaeology and Museums of Pakistan (`doam.gov.pk`), *Heritage: Journal of Multidisciplinary Studies in Archaeology* (University of Kerala), *Ancient Asia*, *Man and Environment* (issues after those on the Internet Archive), *Puratattva* (issues 38 onward), *Journal of Indian Ocean Archaeology*, *Pragdhara*, the ASI website and its circle sites, and RIHN occasional papers.

## Missing IAR volumes

Search for openly available copies of *Indian Archaeology – A Review* 2001–02, 2002–03, 2004–05, 2005–06, 2008–09, 2011–12 and every volume from 2014–15 onward (ASI website, NMMA `nmma.nic.in`, ASI circle sites, the Internet Archive, `assets.ctfassets.net` copies). Download any you find (source ids `iar-YYYY-YY`), confirm the volume year from the title or contents page, and record where each volume was looked for if not found. For the Internet Archive, use `https://archive.org/metadata/<identifier>` and record the archive's MD5 and SHA1 beside your SHA256.

## Deliverables

- `acquisition-web/source-candidates-1b.csv` (tracked): one row per publication: `source_id, site_codes, title, authors, year, venue, volume_issue_pages, url, access` (`open-pdf`, `open-html`, `lead-only`, `paywalled`, `not-found`), `downloaded, local_path, bytes, sha256, rights_notice_observed, seasons_covered, reported_inscribed_counts` (for example `seal=3; sealing=1; inscribed-pottery=2`, or `unstated`), `pages_of_object_descriptions, gives_registrations` (`yes`, `no`, `unknown`), `gives_photographs` (`yes`, `no`, `unknown`), `notes`. Use the exact title as printed on the publication.
- `acquisition-web/search-log-1b.csv` (tracked): `query_id, site_code, query, date_utc, results_considered, sources_recorded`.
- `acquisition-web/new-site-leads-1b.csv` (tracked): sites not in the table, with their source ids.
- `acquisition-web/iar-volume-search-1b.csv` (tracked): each missing IAR volume, where you looked, and the outcome.
- `acquisition-web/manifest-proposals-1b.json` (tracked): proposed manifest entries, in the shape of `data/MANIFEST.json` `sources[]` items, for every file you downloaded, with `fetch.method` `http`, `url`, `filename`, `bytes`, `sha256`, `rights.status` `rights-unverified`, `status` `held`, `location` `local-only`, `local_paths`, `hashes`, `questions: ["Q-1026"]`.
- `acquisition-web/exposure-log-1b.csv` (tracked): `source_id, agent, access, pages, purpose`, with agent `codex gpt-6.1-sol run 1B`.
- `acquisition-web/selftest-1b.json`: from a script you write and run that checks every downloaded file's SHA256 against the CSV and the proposals, that every CSV row with `downloaded = yes` has an existing file, and that no tracked file contains forbidden fields (search the tracked files, case-insensitively and as whole words, for unicorn, bull, rhinoceros, elephant, tiger, buffalo, zebu, goat, antelope, motif, animal, "sign sequence", "reads as", and for a number followed by mm or cm, and report every hit with its file and line).

## Final message

End with a plain message (saved to `final.md`) giving: the number of publications recorded per site code; the number downloaded, with total bytes; the publications that look like the best object-level source for each site (title and year only); the IAR volumes found and not found; new site leads; the selftest result; any deviation from these instructions and why; and the paths of the tracked outputs. Do not include any object description or inscription content.
