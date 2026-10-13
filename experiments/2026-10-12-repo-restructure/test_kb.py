"""Behavior checks for discovery, preservation and validation in isolated fixtures."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import kb


class FrontmatterTests(unittest.TestCase):
    def test_comments_quotes_and_flow_history(self):
        fields,body=kb.frontmatter('''---
id: C-0001 # comment
title: "A # mark, with a colon: here"
area: seals
authors: ["one, two", 'O''Brien']
sources:
  - file.json#/field
credence_history:
  - {date: 2026-10-12, value: 0.5, reason: "a, b # c"}
other:
  nested: {a: b}
---
# Claim
text
''')
        self.assertEqual(fields['id'],'C-0001')
        self.assertEqual(fields['title'],'A # mark, with a colon: here')
        self.assertEqual(fields['authors'],['one, two',"O'Brien"])
        self.assertEqual(fields['sources'],['file.json#/field'])
        self.assertEqual(fields['credence_history'][0],dict(date='2026-10-12',value=.5,reason='a, b # c'))
        self.assertIsInstance(fields['other'],str)
        self.assertTrue(body.startswith('# Claim'))

    def test_unrecognized_and_malformed_values_remain_raw(self):
        fields,_=kb.frontmatter('---\ntitle: [unfinished\nunknown: |\n  several lines\n---\nbody')
        self.assertEqual(fields['title'],'[unfinished')
        self.assertIn('several lines',fields['unknown'])


class RepositoryFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='indus-kb-')
        self.root=Path(self.temp.name)
        self.real_root=kb.ROOT
        kb.ROOT=self.root
        self.put('knowledge/registry/metadata.json',json.dumps({'schema_version':1,'scope':'synthetic test fixture'}))
        self.put('knowledge/DATA.md','# Fixture data\n')
        for template in ('QUESTION','FINDING'):
            self.put('templates/'+template+'.md',(ROOT/'templates'/f'{template}.md').read_text(encoding='utf-8'))
        self.put('tools/kb.py',(ROOT/'tools/kb.py').read_text(encoding='utf-8'))

    def tearDown(self):
        kb.ROOT=self.real_root
        self.temp.cleanup()

    def put(self,name,text):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

    def attempt(self,identifier,order=None):
        row=dict(id=identifier,theme='fixture',status='old exact status',question='Find the title',outcome='Measured fixture',
                 challenge='fixture',remedy='fixture',evidence=[],retry_when='fixture',status_class='record',area='methods')
        if order is not None:row['registry_order']=order
        self.put('knowledge/registry/attempts/'+identifier+'.json',kb.json_text(row))
        return row

    def command(self,*args):
        return subprocess.run([sys.executable,'-B',str(self.root/'tools/kb.py'),*args],capture_output=True,text=True,encoding='utf-8',cwd=self.root)

    def test_build_order_original_fields_and_idempotence(self):
        one=self.attempt('Z-01',0);two=self.attempt('A-02',1)
        self.attempt('NEW-Z');self.attempt('NEW-A')
        self.assertEqual(kb.build(),['knowledge/experiments/registry.json','knowledge/MAP.md'])
        before={n:(self.root/n).read_bytes() for n in kb.generated()}
        self.assertEqual(kb.build(),[])
        self.assertEqual(before,{n:(self.root/n).read_bytes() for n in kb.generated()})
        entries=json.loads((self.root/'knowledge/experiments/registry.json').read_text())['experiments']
        self.assertEqual([e['id'] for e in entries],['Z-01','A-02','NEW-A','NEW-Z'])
        self.assertEqual(entries[:2],[one,two])

    def test_cli_new_search_show_filters_and_question_range(self):
        self.attempt('ATTEMPT-0001',0)
        self.assertEqual(self.command('new','question','--title','Object alias audit','--area','data').returncode,0)
        self.put('knowledge/questions/Q-1001-other-range.md','---\nid: Q-1001\ntitle: acquisition\n---\n')
        created=self.command('new','question','--title','Second alias audit','--area','data')
        self.assertIn('Q-0002-',created.stdout)
        found=json.loads(self.command('search','Object','alias','--kind','question','--json').stdout)
        self.assertEqual(found[0]['id'],'Q-0001')
        self.assertIn('Object alias audit',self.command('show','Q-0001').stdout)
        listing=json.loads(self.command('list','--kind','question','--area','data','--status','open','--json').stdout)
        self.assertEqual(len(listing),2)
        self.assertIn('Q-0001',self.command('next','--area','data','--difficulty','standard','--kind','analysis').stdout)
        self.assertNotIn('Q-0001',self.command('next','--difficulty','starter').stdout)
        self.assertNotEqual(self.command('show','missing').returncode,0)
        self.assertNotIn('../knowledge/DATA.md',self.command('show','Q-0001').stdout)

    def test_validator_detects_bad_metadata_duplicate_id_and_missing_evidence(self):
        self.attempt('A-01',0)
        self.put('knowledge/findings/F-0001-bad.md','''---
id: F-0001
title: Broken fixture
status_class: invented
area: wrong
date: 2026-10-12
registry_ids: [A-01]
evidence: [missing.json]
population: fixture
---
# Finding
[broken](../missing.md)
''')
        self.put('knowledge/findings/F-0001-other.md','---\nid: F-0001\n---\n')
        kb.build()
        with contextlib.redirect_stdout(io.StringIO()):result=kb.check()
        joined='\n'.join(result['errors'])
        for message in ('invalid status_class','invalid area','duplicate ID','missing path','missing field'):
            self.assertIn(message,joined)

    def test_validator_detects_missing_json_field_and_stale_generated_file(self):
        self.attempt('A-01',0)
        p=self.root/'knowledge/registry/attempts/A-01.json'
        row=json.loads(p.read_text());row['evidence']=['result.json#/not_present'];p.write_text(kb.json_text(row))
        self.put('result.json','{"present":1}')
        kb.build();self.put('knowledge/MAP.md','stale')
        with contextlib.redirect_stdout(io.StringIO()):result=kb.check()
        self.assertTrue(any('missing JSON field' in e for e in result['errors']))
        self.assertTrue(any('fresh build' in e for e in result['errors']))

    def test_valid_cards_and_reviewed_local_only_omission_pass(self):
        row=self.attempt('A-01',0)
        row['evidence']=['local-input.bin']
        self.put('knowledge/registry/attempts/A-01.json',kb.json_text(row))
        self.put('experiments/2026-10-11-public-release/public-omissions.json','{"targets":["local-input.bin"]}')
        for name in ('README.md','AGENTS.md','CONTRIBUTING.md','REPRODUCING.md','knowledge/WORKING-MODEL.md','knowledge/INDEX.md','knowledge/TIMELINE.md'):
            self.put(name,'# Fixture\n')
        self.assertEqual(self.command('new','question','--title','Fixture question','--area','data').returncode,0)
        self.put('result.json','{"value": 1}')
        self.put('knowledge/findings/F-0001-fixture.md','''---
id: F-0001
title: Fixture result
status_class: synthetic
area: methods
date: 2026-10-12
registry_ids: [A-01]
evidence: [result.json#/value]
population: synthetic fixture
---
# Finding
The fixture value is 1.
# Evidence
[result](../../result.json)
# Scope
Synthetic test only.
''')
        kb.build()
        with contextlib.redirect_stdout(io.StringIO()):result=kb.check()
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['reviewed_local_only'],['local-input.bin'])

    def test_registration_is_idempotent_and_rejects_conflicting_entry(self):
        row=self.attempt('A-01',0)
        self.put('tools/register_experiment.py',(ROOT/'tools/register_experiment.py').read_text(encoding='utf-8'))
        supplied={k:v for k,v in row.items() if k not in ('status_class','area','registry_order')}
        self.put('entry.json',json.dumps(supplied))
        cmd=[sys.executable,'-B',str(self.root/'tools/register_experiment.py'),str(self.root/'entry.json')]
        result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',cwd=self.root)
        self.assertEqual(result.returncode,0,result.stderr)
        before=p.read_bytes() if (p:=self.root/'knowledge/registry/attempts/A-01.json').exists() else b''
        supplied['outcome']='different';self.put('entry.json',json.dumps(supplied))
        self.assertNotEqual(subprocess.run(cmd,capture_output=True,cwd=self.root).returncode,0)
        self.assertEqual(p.read_bytes(),before)


if __name__=='__main__':unittest.main(verbosity=2)
