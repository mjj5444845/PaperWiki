# -*- coding: utf-8 -*-
import datetime,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from automation.inbox import Runner,Lock,Busy,sha,stamp,atomic
from automation import content

class InboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.config=json.loads(Path('automation/config.json').read_text());self.r=Runner(self.root,self.config)
    def pdf(self,name,payload=b'fake PDF for hash tests'):
        p=self.r.inbox/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(payload);os.utime(p,(time.time()-1200,)*2);return p
    def published(self,path):
        digest=sha(path);self.r.data['papers'][digest]=dict(sha256=digest,filename=path.name,files=[path.name],title='Title',status='published',attempts=1,commit_sha='a'*40,page_url=self.config['base_url']+'papers/Ptest.html')
        return digest,self.r.data['papers'][digest]
    def test_hash_duplicates_and_partial_files(self):
        a=self.pdf('a.pdf');b=self.pdf('renamed.pdf');self.pdf('different.pdf',b'different');fresh=self.r.inbox/'fresh.pdf';fresh.write_bytes(b'fresh');self.pdf('~$temp.pdf');self.pdf('incomplete.pdf.part')
        found=self.r.scan();self.assertEqual(len(found),2);self.assertEqual(len(found[sha(a)]),2)
        self.r.data['papers'][sha(a)]['status']='cleaned';self.pdf('third-name.pdf');self.r.scan();self.assertEqual(len(self.r.data['papers']),2);self.assertTrue(self.r.summary['duplicates'])
    def test_failure_isolation_and_retry_ceiling(self):
        bad=self.pdf('broken.pdf');good=self.pdf('other.pdf',b'other');found=self.r.scan();digest=sha(bad)
        with patch.object(self.r,'clean_git',side_effect=ValueError('simulated failure')):
            for _ in range(5):self.r.process(digest,found[digest])
        self.assertEqual(self.r.data['papers'][digest]['attempts'],3);self.assertEqual(self.r.data['papers'][sha(good)]['status'],'pending');self.assertTrue(bad.exists())
    def test_cleanup_requires_every_gate(self):
        p=self.pdf('a.pdf');digest,r=self.published(p)
        with patch.object(self.r,'remote_has',return_value=False),patch.object(self.r,'deployed') as deployment:
            self.r.cleanup(0);deployment.assert_not_called();self.assertTrue(p.exists())
        with patch.object(self.r,'remote_has',return_value=True),patch.object(self.r,'deployed',side_effect=ValueError('deployment failed')):
            self.r.cleanup(0);self.assertTrue(p.exists())
        p.write_bytes(b'replaced under same name');os.utime(p,(time.time()-1200,)*2)
        with patch.object(self.r,'remote_has',return_value=True),patch.object(self.r,'deployed',return_value='ok'):
            self.r.cleanup(0);self.assertTrue(p.exists());self.assertEqual(r['status'],'published')
    def test_trash_retention_and_failed_file_preserved(self):
        p=self.pdf('a.pdf');digest,r=self.published(p);bad=self.pdf('bad.pdf',b'corrupt');self.r.scan();self.r.data['papers'][sha(bad)]['status']='failed'
        with patch.object(self.r,'remote_has',return_value=True),patch.object(self.r,'deployed',return_value='ok'):
            self.r.cleanup(0)
        self.assertFalse(p.exists());self.assertEqual(r['status'],'cleaned');trash=self.r.inbox/r['trash'][0]['path'];self.assertTrue(trash.exists());self.assertTrue(bad.exists())
        self.r.cleanup(0);self.assertTrue(trash.exists())
        r['trash'][0]['trashed_at']=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=15)).isoformat();self.r.cleanup(0);self.assertFalse(trash.exists());self.assertTrue(bad.exists())
    def test_lock_and_stale_recovery(self):
        p=self.r.state/'run.lock'
        with Lock(p,21600):
            with self.assertRaises(Busy):
                with Lock(p,21600):pass
        self.assertFalse(p.exists());p.write_text('{}');os.utime(p,(time.time()-22000,)*2)
        with Lock(p,21600) as lock:self.assertTrue(lock.stale)
    def test_reject_symlinks_and_outside_paths(self):
        outside=self.root/'outside.pdf';outside.write_bytes(b'outside');(self.r.inbox/'linked.pdf').symlink_to(outside)
        self.assertEqual(self.r.scan(),{})
        with self.assertRaises(ValueError):self.r.source('../outside.pdf')
    def test_evidence_must_match_physical_page(self):
        with self.assertRaises(ValueError):content.validate_evidence([{'page':2,'quote':'42','section':'Results'}],[{'text':'42'}])
        content.validate_evidence([{'page':1,'quote':'4 2','section':'Results'}],[{'text':'42'}])
    def test_first_link_only(self):
        entities=[dict(id='C1',canonical_name='测试',aliases=['testing'])]
        text=content.relink('测试 testing 测试\n\n## 参见\n\n- [[测试]]',entities,'P1')
        self.assertEqual(text.split('## 参见')[0].count('[['),1)
    def test_pull_conflict_cannot_commit_candidate(self):
        from automation import inbox
        calls=[]
        def fake_git(*args,**kwargs):
            calls.append(args)
            if args[:2]==('rev-parse','HEAD'):return 'baseline'
            if args[:2]==('pull','--rebase'):raise RuntimeError('conflict')
            return ''
        with patch.object(self.r,'clean_git'),patch.object(self.r,'verify_depth'),patch.object(inbox,'git',side_effect=fake_git):
            with self.assertRaises(ValueError):self.r.publish(self.root,{'title':'Paper'},'baseline')
        self.assertFalse(any(c[0]=='commit' for c in calls));self.assertFalse(any(c[0]=='add' for c in calls))
    def test_recover_interrupted_trash_move(self):
        p=self.pdf('a.pdf');digest,r=self.published(p);dest=self.r.inbox/'.trash'/digest/'a.pdf';dest.parent.mkdir(parents=True);p.rename(dest)
        r['trash']=[dict(path=dest.relative_to(self.r.inbox).as_posix(),source='a.pdf',trashed_at=stamp(),purged_at=None)]
        with patch.object(self.r,'remote_has',return_value=True),patch.object(self.r,'deployed',return_value='ok'):self.r.cleanup(0)
        self.assertEqual(r['status'],'cleaned');self.assertTrue(dest.exists())
    def test_failed_file_does_not_stop_next_record(self):
        bad=self.pdf('a.pdf');good=self.pdf('z.pdf',b'valid');seen=[]
        def process(digest,files):
            seen.append(digest)
            if digest==sha(bad):self.r.data['papers'][digest]['status']='failed'
            else:self.r.data['papers'][digest]['status']='published'
        with patch.object(self.r,'process',side_effect=process),patch.object(self.r,'cleanup'):self.r.run()
        self.assertEqual(len(seen),2);self.assertEqual(self.r.data['papers'][sha(good)]['status'],'published')
    def test_remote_tip_and_ancestor_both_required(self):
        from automation import inbox
        def fake_git(*args,**kwargs):
            if args[0]=='ls-remote':return 'a'*40+'\trefs/heads/main'
            if args[0]=='rev-parse':return 'b'*40
            return ''
        with patch.object(inbox,'git',side_effect=fake_git):
            with self.assertRaises(ValueError):self.r.remote_has('c'*40)
    def test_two_paper_stable_concept_promotion(self):
        q={'page':1,'section':'Example','quote':'example'};fact={'text':'示例概念（example）是测试对象。','evidence':[q]};meta={k:{'value':'','evidence':[]} for k in ['title','title_zh','authors','year','venue','doi','arxiv','code']};meta['title']={'value':'New paper','evidence':[q]}
        entities=[dict(id='Pold',type='论文',canonical_name='Old paper',aliases=[],markdown_path='papers/Pold.md',html_path='papers/Pold.html',appears_in_papers=['Pold'],cites_papers=[])]
        for i in range(2):entities.append(dict(id='C'+str(i),type='概念',canonical_name='概念'+str(i),aliases=['term'+str(i)],markdown_path='concepts/C'+str(i)+'.md',html_path='concepts/C'+str(i)+'.html',appears_in_papers=['Pold']))
        wiki=self.root/'wiki';content.dump(wiki/'registry.json',{'entities':entities,'counts':{}});content.dump(wiki/'redirects.json',{})
        for e in entities:content.write(wiki/e['markdown_path'],content.front({'id':e['id'],'title':e['canonical_name']},'定义。\n\n## 在本站论文中的应用\n\n## 参见\n\n## 参考文献'))
        concept=lambda original,name,existing:dict(original_term=original,canonical_name=name,existing_id=existing,aliases=[],stable=True,prerequisite=False,definition=fact,application=fact)
        concepts=[concept('term0','概念0','C0'),concept('term1','概念1','C1'),concept('example','示例概念','')]
        data=dict(metadata=meta,field='测试',lead=[fact],background=[],method=[fact],contributions=[fact]*3,datasets=[],results=[],limitations=[],concepts=concepts,cites_existing=[],introduced_methods=[])
        history=dict(metadata=meta,paper_id='Pold',concepts=[concepts[-1]])
        paper,created,_=content.generate(self.root,data,[{'text':'example'}],'d'*64,[],[history]);self.assertEqual(created,['示例概念'])
        updated=json.loads((wiki/'registry.json').read_text());new=next(e for e in updated['entities'] if e['canonical_name']=='示例概念');self.assertEqual(set(new['appears_in_papers']),{'Pold',paper['id']})
        self.assertIn('[[Old paper]]',(wiki/new['markdown_path']).read_text())

    def test_numeric_substring_is_not_evidence(self):
        q={'page':1,'section':'Example','quote':'42'};fact={'text':'测得 4 个。','evidence':[q]}
        metadata={k:{'value':'','evidence':[]} for k in ['title','title_zh','authors','year','venue','doi','arxiv','code']};metadata['title']={'value':'42','evidence':[q]}
        data=dict(metadata=metadata,field='测试',lead=[fact],background=[],method=[fact],contributions=[fact]*3,datasets=[],results=[],limitations=[],concepts=[],cites_existing=[],introduced_methods=[],review=[],publishable=True,checklist=[dict(item=i,status='pass',reason='synthetic test') for i in range(1,13)])
        with self.assertRaisesRegex(ValueError,'数字未出现'):content.validate(data,[{'text':'42'}])
        fact['text']='测得 42 个。';content.validate(data,[{'text':'42'}])

if __name__=='__main__':unittest.main()
