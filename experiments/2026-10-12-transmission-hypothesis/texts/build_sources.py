"""Record inspected scope, chronology axes, acquisitions and dependencies."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/texts'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def base(ident,title,authors,citation,scope,urls,rights,chronology=None):
    return dict(source_id=ident,title=title,authors=authors,citation=citation,reading_scope=scope,
        primary_urls=urls,rights_status=rights,redistribution='local-only',chronology_axes=chronology or {},
        witnesses=[],derivatives=[],access_attempts=[],selected=True)


def main():
    target=HERE/'SOURCES.json'
    if target.exists():raise FileExistsError(target)
    rvdates=dict(narrated_date='No historical date inferred from narrated first speech or invoked gods.',
        composition='Individual hymn/stanza dates are not independently fixed here. BookIX contains varied earlier/younger compositions; BookX is a later major addition in R01’s account.',
        collection_redaction='Distinct from composition; R01 printed14–17 describes family collections and later consolidation.',
        surviving_manuscript='No manuscript newly collated in this branch; modern editions witness the received text.',
        digital_witness='2026-10-12 acquisition; edition/digitization history recorded separately.',
        independent_archaeological_date=None,basis=['review/O-R01-2'])
    sources=[
      base('T-RVSANS','Rgveda, Mandala9; Rgveda, Mandala10',['Th. Aufrecht (edition)','Barend A. Van Nooten and Gary B. Holland (digitization)','Detlef Eichler (revision/conversion)'],
        'GRETIL unaccented text based on Die Hymnen des Rig Veda,2nd edition,Bonn1877, as stated in the witnesses.',
        'Witness metadata and complete hymns9.112,10.71,10.101, with pada labels. Remaining corpus not claimed read.',
        ['https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/1_sam/1_rv/rv_hn09u.htm','https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/1_sam/1_rv/rv_hn10u.htm'],
        'rights-unverified',rvdates),
      base('T-GRIFFITH','The Hymns of the Rigveda, Translated with a Popular Commentary',['Ralph T. H. Griffith'],
        'Nineteenth-century translation; exact underlying print edition not established by these three modern pages. Digital chapter titles retain hymn numbers.',
        'Complete selected translations9.112,10.71,10.101 and page identity. No whole translation or historical print-volume inspection.',
        ['https://sacred-texts.com/hin/rigveda/rv09112.htm','https://sacred-texts.com/hin/rigveda/rv10071.htm','https://sacred-texts.com/hin/rigveda/rv10101.htm'],
        'mixed-assets: historical translation and modern interface; raw local-only',rvdates),
      base('T-YASNA','YASNA (Sacred Liturgy); Yasna9–11 (Hom Yasht)',['Karl F. Geldner (edition)','L. H. Mills (translation)','Joseph H. Peterson (digital edition)'],
        'Source-language page cites Geldner1896; English page cites Sacred Books of the East,American edition1898 and digital copyright1995.',
        'Complete Yasna9.1–8 paired source/translations; metadata and links. Remaining acquired Yasna text not claimed read.',
        ['https://www.avesta.org/yasna/y9to11.htm','https://www.avesta.org/yasna/yasna.htm'],
        'rights-unverified; observed1995 digital all-rights-reserved notice',
        dict(narrated_date='Preparation and mythical rewards; no actual historical date inferred.',composition='Younger Avestan textual/language comparator; absolute composition not established by these editions.',collection_redaction='Received collection history not independently reconstructed here.',surviving_manuscript='No ancient manuscript newly collated.',digital_witness='Observed1995 digital notice; acquired2026-10-12.')),
      base('T-VENDIDAD','AVESTA: Vendidad; Fargard3, the Earth',['Karl F. Geldner (edition attribution through archive)','James Darmesteter (translation)','Joseph H. Peterson (digital edition)'],
        'Paired Avestan archive text and Darmesteter Sacred Books of the East,American edition1898; digital edition prepared1995.',
        'Complete source-language3.23–33 and corresponding English groups;26–27 and28–29 share translation groups. Translator/editor notes are distinct from the primary clauses.',
        ['https://www.avesta.org/vendidad/vd.htm','https://www.avesta.org/vendidad/vd3sbe.htm'],
        'rights-unverified; digital edition prepared1995',
        dict(narrated_date='Dialogue with Ahura Mazda; not a date of cultivation.',composition='Younger Avestan normative/cultivational comparator; absolute date unresolved here.',collection_redaction='Received text and later explanations distinguished; no reconstruction attempted.',surviving_manuscript='No ancient manuscript newly collated.',digital_witness='1995 preparation notice; acquired2026-10-12.')),
      base('T-ODYSSEY','The Odyssey, with an English Translation',['Homer (attributed author)','A. T. Murray (edition/translation)','Perseus Project,Tufts University (digital text)'],
        'Murray1919,bilingual Loeb edition, as stated in both TEI headers; pinned canonical-greekLit commit01b725d835e6e733062ffd79e0efdbae1ba06e5c.',
        'Greek17.382–386 and English book17 translation card380, including surrounding dialogue. TEI source headers inspected; no entire epic or manuscript collation.',
        ['https://github.com/PerseusDL/canonical-greekLit/tree/01b725d835e6e733062ffd79e0efdbae1ba06e5c/data/tlg0012/tlg002'],
        'mixed-assets: ancient text, historical edition and modern TEI; raw local-only',
        dict(narrated_date='Epic setting does not independently date the portrayed roles.',composition='No absolute composition date established by the modern TEI witness.',collection_redaction='Not reconstructed in this branch.',surviving_manuscript='No manuscript collated; print edition1919.',digital_witness='TEI says scanned1989 and records revisions; repository pinned at2026-10-12.')),
      base('T-DN1','Brahmajālasutta, Dīgha Nikāya1',['Received Pali canon','Mahāsaṅgīti/root-ms digital witness','Bhikkhu Sujato (English translation)','SuttaCentral/Bilara'],
        'Pinned published Bilara commit795983655cc7e5c5694184750426b06a6604be21; root Pali and translation use identical segment IDs.',
        'Pali/English DN1:1.21–1.27,31 aligned segments across7 sections; repository README license requirement inspected. Remainder not claimed read.',
        ['https://github.com/suttacentral/bilara-data/tree/795983655cc7e5c5694184750426b06a6604be21'],
        'mixed-assets; README requires CC0 for supported translations; both witnesses and derivatives kept local-only',
        dict(narrated_date='Gotama’s reported conduct and dialogue; no chronology transferred from narrated time.',composition='Later early-Buddhist normative prose relative to the Rigvedic frame; the particular list’s initial composition is not dated here.',collection_redaction='Distinct from individual lists; no recension stemma or initial-redaction date established.',surviving_manuscript='No DN1 manuscript newly collated; prior manuscript examples from other discourses are not date controls for this locus.',digital_witness='Pinned modern Pali/English files acquired2026-10-12.')),
      base('T-WITZEL','Substrate Languages in Old Indo-Aryan (Ṛgvedic, Middle and Late Vedic)',['Michael Witzel'],
        'Electronic Journal of Vedic Studies5(1),1999,bibliographic attribution. Author-hosted PDF is an undated digital version; filename/upload date is not used as publication date.',
        'Selected printed pp2–3,13,25–26,36,54 and relevant author/reference identity. Definitions, competing plow origins, agricultural list and broader substrates inspected; no full-paper agreement asserted.',
        ['https://www.michaelwitzel.org/wp-content/uploads/2014/06/ejvs0501article.pdf','https://hasp.ub.uni-heidelberg.de/journals/ejvs/article/download/828/806/1648'],
        'rights-unverified',dict(publication='1999 work attribution; retrieved digital version undated.',historical_dates='Author’s absolute RV chronology is an attributed1999 argument and is not adopted as an independent date constraint in this study.')),
      base('T-MW1899','A Sanskrit-English Dictionary',['Monier Monier-Williams','Cologne Digital Sanskrit Lexicon (interface)'],
        'Oxford1899; bounded Cologne displays identify printed pages1219(sīra),431(takṣ),757(bhiṣaj),847(yava),732(bīja).',
        'Five complete queried entries and book-page/entry IDs, including the separately marked post-selection bīja query. No whole dictionary or modern etymological consensus survey.',
        ['https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc/getword.php'],
        'mixed-assets: historical dictionary and modern interface; raw local-only',dict(publication='1899 historical dictionary; modern interface date not an ancient attestation.',lexical_dates='A listed text abbreviation or later sense does not itself date a meaning shift.')),
    ]
    ext=json.loads((ROOT/'experiments/2026-10-12-transmission-hypothesis/review/sources-v2.json').read_text('utf8'))
    exmap={x['source_id']:x for x in ext['sources']}
    for alias,key in [('T-JB2014','R01'),('T-OLDAV2006','R02')]:
        x=exmap[key]
        item=base(alias,x['title'],x['authors'],x.get('citation',str(x['publication_year'])),
            'Reused independently reviewed witness. This branch re-read J&B printed14 and Old Avestan printed35,70,123; other declared control conclusions remain reviewer-attributed.',
            [x['primary_url']],x['rights_status'],dict(composition='Absolute ancient date not established by modern edition.',digital_or_print_witness_year=x['publication_year']))
        item['external_source_id']=key;item['external_ledger']='experiments/2026-10-12-transmission-hypothesis/review/sources-v2.json'
        item['external_ledger_sha256']=sha(ROOT/item['external_ledger']);item['witnesses']=x['witnesses'];sources.append(item)
    lookup={x['source_id']:x for x in sources}
    mapping={
      'rv9-sanskrit':'T-RVSANS','rv10-sanskrit':'T-RVSANS',
      'rv9112-griffith':'T-GRIFFITH','rv10071-griffith':'T-GRIFFITH','rv10101-griffith':'T-GRIFFITH',
      'yasna9-avestan':'T-YASNA','yasna9-avestan-corrected':'T-YASNA','yasna-mills':'T-YASNA',
      'vendidad3-avestan':'T-VENDIDAD','vendidad-avestan-corrected':'T-VENDIDAD','vendidad3-darmesteter':'T-VENDIDAD',
      'odyssey-greek':'T-ODYSSEY','odyssey-english':'T-ODYSSEY','odyssey-english-corrected':'T-ODYSSEY','greek-folder':'T-ODYSSEY','greek-repo-commit':'T-ODYSSEY',
      'dn1-pali':'T-DN1','dn1-sujato':'T-DN1','bilara-license':'T-DN1','bilara-readme':'T-DN1','bilara-root-index':'T-DN1','bilara-repo-commit':'T-DN1',
      'witzel-substrates1999-author':'T-WITZEL','witzel-substrates1999-author-barehost':'T-WITZEL',
      **{f'mw1899-{x}':'T-MW1899' for x in ['sira','taksh','bhishaj','yava','bija-postselection']}}
    excluded=[]
    for manifest in sorted(RAW.glob('capture-v*.json')):
        for row in json.loads(manifest.read_text('utf8'))['attempts']:
            key=mapping.get(row['witness_id'])
            enriched=dict(row,acquisition_manifest=manifest.relative_to(ROOT).as_posix(),acquisition_manifest_sha256=sha(manifest))
            if not key:
                excluded.append(enriched);continue
            lookup[key]['access_attempts'].append(enriched)
            if row.get('path'):
                path=ROOT/row['path']
                good=row.get('status_code')==200 and row.get('witness_id')!='bilara-license'
                role='primary_source_witness' if good else 'failed_or_wrong_locator_witness'
                if row['witness_id'] in ['greek-repo-commit','greek-folder','bilara-repo-commit','bilara-root-index','bilara-readme']:role='repository_metadata'
                lookup[key]['witnesses'].append(dict(path=row['path'],sha256=sha(path),bytes=path.stat().st_size,role=role,redistribution='local-only'))
            if row.get('derivative'):lookup[key]['derivatives'].append(row['derivative'])
    notes=dict(selected_source_groups=len(sources),
        unit='Source groups include paired editions and translations; they are not counts of independent ancient witnesses.',
        blocked_harappa_lead='LanguagesHarappa_1998.pdf returned a200 bot challenge; excluded. Its filename does not establish publication year.',
        bibliographic_search_failure='Crossref title query did not retrieve the Witzel work; unrelated results excluded, retained in capture-v4.',
        limited_lubotsky_lead='Primary search-rendered2001 introduction was inspected as a possible method lead; publisher PDF route redirected to homepage. No token-specific result or full-paper reading is claimed or used.',
        rights='All source text/assets/paired derivatives local-only; authored summaries and code are separate.',
        transport='Per-request public TLS exceptions are explicit in acquisition records after normal failures. They are not authenticated HTTPS transport.')
    target.write_text(json.dumps(dict(scope=notes,script_sha256=sha(Path(__file__)),sources=sources,excluded_or_metadata_attempts=excluded),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(source_groups=len(sources),excluded_or_metadata_attempts=len(excluded))))


if __name__=='__main__':main()
