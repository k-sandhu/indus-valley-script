"""Write the authorized Helsinki interface specification."""
from common import OWN

TEXT='''# Joining the Helsinki 1979 edition

The revised importer accepts Package M's per-occurrence `segment_id` and letter-suffixed text numbers. A historical concordance must identify the physical object, and a separate review must align each occurrence to a source surface. No real Helsinki layer has been accepted: all 11,369 staged occurrences are quarantined with an empty crosswalk. [Interface checks](verification-2026-10-07-v3/helsinki-interface.json), `real_accepted`, `real_quarantined`; [implementation](import_helsinki1979_v2.py).

## Concordance lead and source schemes

CISI 1 printed 365/PDF 401 explains that column 2 of the basic-data table is the object's Finnish Concordance number in its then-current version. The supplied review reports M-197 = 2371 on printed 367. This is a lead to verify against the 1979 numbering, including duplicated appearances and intervening revisions. Length agreement supplies no identity proof. The column-definition page was opened locally; the M-197 row number is inherited from the review. [CISI 1](https://ignca.gov.in/Asi_data/76884.pdf), Joshi and Parpola (eds.), 1987, *Corpus of Indus Seals and Inscriptions. 1. Collections in India*, Annales Academiae Scientiarum Fennicae B 239; [review](REVIEW.md), Helsinki import section.

Kimmo Koskenniemi and Asko Parpola's *Documentation and Duplicates of the Texts in the Indus Script* (1980, University of Helsinki) provides another concordance route. Package M inspected four Finnish-to-Mahadevan mappings; their physical-object/CISI joins remain unverified. Its licence is unresolved, so copied concordance rows stay local. [Package M retrospective](../2026-10-07-helsinki1979-digitization/RETROSPECTIVE.md), Concordance, rights and integration; [1980 source](https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf).

| Crosswalk target scheme | Resolution rule |
|---|---|
| CISI, CISI1, reported_catalogue_reference | Normalize spacing/hyphen and a catalogue side/photo suffix to the physical-object base, then resolve uniquely across the ledger's two catalogue schemes. H 2218 resolves H-2218. The source-surface check remains separate. |
| excavation_registration, HARP_excavation_registration | Exact attributed registration string. A parsed registration supplies no new cross-object identity assertion. |
| museum_accession: plus institution | Exact accession in the source-qualified institution namespace. |
| Lipi_family@ plus pinned commit | Exact source-qualified export family; this is an export identity, subject to carrier review. |
| registration_variant, reported_export_identifier_string or candidate alias | Cannot establish an accepted target. Raw combined export strings remain attributed observations, outside the join index. |

Other confirmed ledger schemes resolve exactly; unknown schemes and ambiguous targets enter quarantine. A target number alone cannot select an object.

## Occurrence crosswalk and Package M adapter

The input row requires `edition_id=Koskenniemi-Parpola-1979`, a string or integer `text_number`, nonempty `segment_id`, inventory/version, positive source PDF page, glyph and auxiliary arrays, order, boundary status, digitization version, review status and the CC BY rights block. Numbers such as 669S and 2Z remain source strings. The exact occurrence key is `(edition_id, text_number, segment_id)`; repeated appearances remain distinct witnesses. [Machine-checkable interface](verification-2026-10-07-v3/interface-schema-v2.json).

A Package L crosswalk row requires `edition_id`, `text_number`, `segment_id`, `concordance_source`, `concordance_page`, `source_access=opened_primary_concordance`, `target_identifier={scheme,value}`, `relation=same_physical_object`, `status=confirmed`, `review_status=reviewed_object_identity` and `surface_review_status=reviewed_source_surface_alignment`. It supplies either an existing `surface_id` or `create_surface=true` and a reviewed `source_surface_label`. A new surface ID is source-qualified and belongs to the resolved carrier. This lets catalogue-only carriers receive surfaces. Physical face/line boundaries must have been reviewed before creation.

Package M supplies a JSON object with a `rows` array. The adapter converts the following fields:

| Package M | Package L |
|---|---|
| source_edition | edition_id |
| target_scheme and target_identifier | target_identifier.scheme and target_identifier.value |
| review_status=confirmed | status=confirmed and review_status=reviewed_object_identity |
| surface_relation object | relation, surface_id or create_surface/source_surface_label, surface_review_status |
| rights_status | retained as concordance rights status |
| concordance_source, concordance_page, source_access | retained with the opened-source gate |
| segment_id | exact occurrence key |

A text-level row may omit segment_id only at the adapter boundary. It expands to matching Package M occurrences using `occurrence_surfaces`, keyed by each exact segment ID. A single surface can cover multiple appearances only with `surface_scope=all_verified_occurrences` and reviewed alignment evidence. Missing per-occurrence alignment remains quarantined. A plain surface_relation string does not supply that evidence. `to_package_m` reverses the adapter for explicit occurrence rows. [Adapter](import_helsinki1979_v2.py), `expand_crosswalk`, `to_package_m`.

## Import, projection and rights

The source edition is Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979, University of Helsinki, Research Reports 1). Its exact source URL is http://hdl.handle.net/10138/342677 and the licence field is CC-BY-4.0. Attribution and modifications remain mandatory. Inventory codes, auxiliary markers, order and boundaries remain attached to each occurrence. Null/unresolved text numbers, duplicates, target collisions, unreviewed surfaces, missing concordances or invalid rights enter quarantine.

```powershell
python experiments/2026-10-07-object-ledger/import_helsinki1979_v2.py --rows experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl --crosswalk data/raw/2026-10-07-object-ledger/reviewed-crosswalk.json --ledger experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/hash-ordered/ledger-without-transcription-payloads-or-images.json --raw-dir data/raw/2026-10-07-object-ledger/helsinki-import-reviewer-v1 --project
```

`reviewed-crosswalk.json` is a required future input, not a supplied concordance. The command writes accepted payloads, quarantine and optional projection only to a fresh raw directory. `project_layer` repeats identity/surface/rights checks, creates reviewed surfaces, adds transcription metadata and asset rights, and excludes glyph payloads from the metadata projection. Synthetic fixtures are rejected by the archaeological import. A specialist must review any real projected layer before it becomes an accepted endpoint.
'''

if __name__=='__main__':
    (OWN/'HELSINKI-INTERFACE.md').write_text(TEXT,encoding='utf-8')
