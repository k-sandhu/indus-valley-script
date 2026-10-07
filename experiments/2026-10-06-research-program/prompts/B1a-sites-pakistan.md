# Site census batch A: Pakistan and Afghanistan

Owned directory: `experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/`. Local raw directory: `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/`. Use live web search.

Sites in this batch: Harappa, Mohenjo-daro, Chanhu-daro, Nausharo, Mehrgarh, Kot Diji, Amri, Lakhan-jo-daro, Allahdino, Balakot, Rehman Dheri, Ganweriwala, Pirak, Jhukar, Judeirjo-daro, Sutkagen-dor, Sotka Koh, Nindowari, Lohumjo-daro, Gumla, Sarai Khola, Shortughai, Mundigak, and the sites recorded in the local corpus for these countries (see local-site-coverage.json, regions Lower Indus, Upper Indus and Inter-Riverine where located in Pakistan).

Add any site in the same region that has yielded inscribed Indus objects and is missing from this list, and say how you found it.


This package is one regional batch of a site census. An earlier broad pass (`experiments/2026-10-06-evidence-census/sites-and-publications/`) registered 89 site labels but left almost every metadata field "not assessed" and found object counts for only four sites. Read it, keep what is correct, and complete the work for the sites in your batch. Other batches cover other regions; do not work on sites outside your list except to note cross-references.

The coordinator computed local starting figures in `experiments/2026-10-06-research-program/local-site-coverage.json`: for each site in the local Lipi export, the number of faces, object families, distinct CISI identifiers, the CISI prefixes and the highest CISI number recorded per prefix, object classes, and how many faces carry period, room or grid, dimension and excavation-number fields. The highest CISI number against the count of distinct identifiers is a first indicator of how much of a site's CISI material the local corpus contains, on the assumption that CISI numbers per site are close to contiguous; check that assumption against the CISI volumes where you can.

## For every site in your batch

Fill every field below with a sourced value. Where a value cannot be found, record the searches you ran (query, place searched, date) and what they returned, instead of writing "not assessed". Run at least three distinct searches per site and open at least one primary or substantial secondary source per site.

1. Canonical name, alternative spellings, country and province, coordinates with their source.
2. Excavation campaigns: years, directors and institutions.
3. Primary excavation reports and final publications (exact titles, authors, years), and the CISI volume and page range for the site where it exists (CISI 1, India, 1987; CISI 2, Pakistan, 1991; CISI 3.1, 2010; CISI 3.2, 2019), plus any site count published from ICIT or Mahadevan 1977.
4. Reported counts of inscribed objects by class (seals, sealings, tablets, inscribed pottery and graffiti, metal and other inscribed objects), each with source page, count basis (objects, faces, texts, impressions) and the date of the count. Record disagreements between sources side by side.
5. Local corpus figures from `local-site-coverage.json`, and your judgment of local coverage against the published counts.
6. Metadata available in the main publications: findspot, stratum or phase, absolute dates, dimensions, material, photographs, drawings and registration numbers. Mark each yes, partial or no, with the source location.
7. Inscribed finds reported after the CISI coverage for the site (later seasons, *Indian Archaeology – A Review* summaries, *Pakistan Archaeology*, conference papers, excavation blogs, news reports), with sources and how firmly each is documented.
8. Where the objects are held now, if published.
9. Digital availability of the publications and images, and stated reuse terms.
10. Open problems: unpublished seasons, missing final reports, unresolved counts.

## Outputs

`site-rows.json` and `site-rows.csv` with one row per site and the fields above, `sources.json` with every source opened or seen in a snippet, `searches.json` with every search run, and a short `REPORT.md` giving totals for the batch (sites, sites with a final report, sites with post-CISI finds, published object counts against local counts) and the largest gaps. Do not stop early: finish every site in the list.
