"""Preserve narrow locator and rubric clarifications in successor registers."""
from pathlib import Path
from datetime import datetime, timezone
import json

BASE=Path(__file__).resolve().parent
documentary={
 'P01':'Ganweriwala is known archaeology inside the nested P02 region; the remaining remote proposals still need confirmation (R08).',
 'P02':'Ganweriwala surface archaeology and ground survey are documented; buried margins remain unknown (R06–R08).',
 'P03':'The reviewed Tohana–Agroha survey records extant archaeology, including Agroha; this does not establish survival in negative cells (R10).',
 'P06':'Kalibangan is a known archaeological anchor; proposed covered valley-flank surfaces remain undated (R70).',
 'P07':'Rakhigarhi–Masudpur rural archaeology is documented; contemporaneity and peripheral survival require testing (R23,R24,R29).',
 'P08':'Harappa is a known regional archaeological anchor; proposed covered interfluve margins remain unresolved (R11).',
 'P09':'Tulamba and surviving medieval contexts establish regional archaeological survival, without dating the proposed channel-margin occupation (R11).',
 'P10':'Lakhanjo-Daro lower contexts survive locally amid upper destruction; new parcels remain unknown (R21).',
 'P12':'Excavation documents western Kutch habitation and cemetery contexts; catchment margins need separate evidence (R20,R28).',
 'P13':'Kotada/Morodharo features are documented; exterior phase-specific extent is the untested question (R19).',
 'P15':'Kaj and Kanjetar excavation contexts establish local archaeological evidence; covered estuary surfaces remain unresolved (R25).',
 'P16':'Miri Qalat supplies a local sequence including Indus occupation; proposed fan surfaces have no transferred age (R26).',
 'P17':'Mehrgarh and Nausharo document surviving regional contexts of different periods; their ages do not date untested fan margins (R39,R40,R45).',
 'P18':'Ghazi Shah supplies dated cultural attribution in a known settlement context; fan margins and cave attribution remain unresolved (R41,R42).',
 'P19':'Siranda-area middens, lithics and occupation contexts are documented with varied dates; other lagoon margins need local ages (R31).',
 'P20':'Known Lothal archaeology anchors the region; local environmental chronology does not establish offshore occupation (R32,R54,R55).',
 'P21':'Sutkagen-Dor is a contained known-settlement anchor; raised, buried or submerged coastal targets need separate chronology (R48,R66).',
}

def write_new(name,obj):
    path=BASE/name
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    s=json.loads((BASE/'sources-v5.json').read_text(encoding='utf-8'))
    r=next(r for r in s['sources'] if r['id']=='R08')
    old='paragraph beginning “Our data suggest,”'
    assert old in r['observation']
    r['observation']=r['observation'].replace(old,'sentence beginning “Our data suggest,”')
    s.update(version='v6',preceding_version='sources-v5.json',authored_utc=datetime.now(timezone.utc).isoformat(),
             revision_basis='Final source audit: correct sentence locator only; numeric inputs and crosswalk metadata unchanged')
    write_new('sources-v6.json',s)
    c=json.loads((BASE/'candidates-v4.json').read_text(encoding='utf-8'))
    c.update(version='v5',preceding_version='candidates-v4.json',
             preservation_rubric_interpretation='P2 means directly documented archaeological survival somewhere in the editorial region, including other periods or surface contexts. It is common in this register and does not rank target-parcel preservation, Indus affiliation or operational priority.',
             review_basis=c['review_basis']+['Final source-region audit: consistent documentary P2 criterion'])
    for t in c['targets']:
        if t['id'] in documentary:
            t['preservation_evidence_level']='P2'
            t['preservation_evidence_basis']=documentary[t['id']]
        elif t['id'] in ('P04','P05'):
            t['preservation_evidence_basis']='Registered observations support a regional survey/visibility process; a specific surviving context inside this editorial box has not been concorded here.'
        else:
            t['preservation_evidence_basis']='The registered sources have not established local target-age surfaces or a contained known-context anchor for this editorial region.'
    write_new('candidates-v5.json',c)
    write_new('review/final-audit-resolutions.json',dict(
        authored_utc=datetime.now(timezone.utc).isoformat(),prior_audit='review/final-source-region-checks.json',
        decisions=[
          dict(finding='R08_locator',status='resolved',output='sources-v6.json',repair='Sentence beginning, not paragraph beginning; its XML paragraph starts An important result.'),
          dict(finding='P2_consistency',status='resolved',output='candidates-v5.json',repair='Apply literal regional documentary criterion; record each context basis. No new archaeological observation or target-parcel prediction.')],
        known_context_regions=sorted(documentary),source_count=len(s['sources']),local_witness_count=s['local_witness_count'],regions=len(c['targets'])))
    print('Created sources-v6, candidates-v5 and final audit resolutions; prior registers preserved.')

if __name__=='__main__':main()
