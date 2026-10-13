"""Record the inspected population-control loci; no institution inferred from DNA."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1"


def main():
    targets = [HERE / "sources.json", HERE / "observations.json"]
    if any(path.exists() for path in targets):
        raise SystemExit("Source ledger exists; no overwrite.")
    acquisition = json.loads((RAW / "acquisition.json").read_text('utf-8'))
    derivation = json.loads((RAW / "derivatives-v1.json").read_text('utf-8'))
    successful = next(row for row in acquisition['records'] if row.get('pdf_signature'))
    source = {
        "source_id": "C01", "authors": ["Vagheesh M. Narasimhan et al."], "year": 2019,
        "title": "The formation of human populations in South and Central Asia",
        "citation": "Science 365, eaat7487 (2019). DOI 10.1126/science.aat7487.",
        "primary_url": successful['requested_url'],
        "reading_scope": "PDF pp.1–2 summary/introduction; p.6 Box 2 selected South Asia findings; p.8 selected South Asian modeling discussion; p.9 Fig.3 and caption, text and rendered page; p.12 admixture dating and explicit modern-group comparison limits; p.13 discussion's two Dravidian-route scenarios. No supplement, genome-level reanalysis or whole-article reading claimed.",
        "witnesses": [successful], "derivatives": derivation['derivatives'],
        "failed_or_excluded_routes": [row for row in acquisition['records'] if not row.get('pdf_signature')],
        "rights_status": "rights-unverified", "redistribution": "local-only",
        "rights_observation": "Author-institution access; no blanket redistribution license established from inspected PDF.",
        "dependency_note": "The reviewer independently reads these same captured bytes. Two access routes and two readers are one scientific work."
    }
    observations = [
        {"observation_id": "C-O01", "source_id": "C01", "locus": "PDF p.2, article p.1, introduction and dataset strategy",
         "source_observation": "The northernmost South Asian time transect begins around 1200 BCE; the study models an IVC-related profile using individuals at sites in cultural contact with the IVC.",
         "kind": "published sampling and model scope", "inference_limit": "A modeled ancestral population is not an excavated teaching institution or the language of an inscription."},
        {"observation_id": "C-O02", "source_id": "C01", "locus": "PDF p.9, article p.8, Fig.3B and caption",
         "source_observation": "The caption treats ancestry arrows as plausible directions rather than resolved exact routes; the figure labels the South Asian entry path uncertain.",
         "kind": "published geographic resolution", "inference_limit": "The diagram does not identify the path of a particular technique or text."},
        {"observation_id": "C-O03", "source_id": "C01", "locus": "PDF p.12, article p.11, admixture dating and modern-group comparison",
         "source_observation": "The authors estimate a post-IVC admixture interval and explicitly qualify the contemporary priestly-group comparison for shared ancestry, nonblinded group selection and changing classification.",
         "kind": "published inference and stated limitations", "inference_limit": "Present classifications are not direct Bronze Age office records; this study performs no genetic recalculation."},
        {"observation_id": "C-O04", "source_id": "C01", "locus": "PDF p.13, article p.12, Dravidian discussion",
         "source_observation": "The authors present an IVC-associated and a southern/eastern scenario for proto-Dravidian spread, combining genetic, archaeological and linguistic premises.",
         "kind": "attributed alternative historical scenarios", "inference_limit": "Neither scenario authenticates a Harappan language or specifies which practical knowledge crossed a contact."}
    ]
    for path, value in zip(targets, [{'scope': 'One independently inspected population-history control with shared reviewer bytes.', 'sources': [source]}, {'scope': 'Selected published observations and attributed interpretations, not newly measured genetic data.', 'observations': observations}]):
        with path.open('x',encoding='utf-8') as stream:
            json.dump(value,stream,ensure_ascii=False,indent=2); stream.write('\n')
    print(json.dumps({'sources':1,'observations':len(observations),'source_sha256':hashlib.sha256(targets[0].read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
