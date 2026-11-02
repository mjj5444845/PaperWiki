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
    def test_existing_redlinks_are_page_scoped_and_ignore_code(self):
        (self.root/'wiki').mkdir()
        entities=[dict(id='P1',canonical_name='First',aliases=[],markdown_path='first.md',html_path='first.html')]
        content.dump(self.root/'wiki/registry.json',{'entities':entities})
        content.write(self.root/'wiki/first.md','[[Missing]] `[[CodeExample]]`')
        self.assertEqual(self.r.existing_redlinks(),{('P1','Missing')})
        # Adding an entity turns the same name into a real link without a whitelist.
        entities.append(dict(id='P2',canonical_name='Missing',aliases=[],markdown_path='second.md',html_path='second.html'))
        content.dump(self.root/'wiki/registry.json',{'entities':entities})
        content.write(self.root/'wiki/second.md','Second')
        self.assertEqual(self.r.existing_redlinks(),set())

    def test_baseline_redlink_cannot_leak_to_new_page(self):
        work=self.root/'candidate';(work/'site').mkdir(parents=True);(work/'qa').mkdir()
        content.dump(work/'qa/structure.json',{k:[] for k in ['errors','orphans','unlinked','repeats','see_also_errors']})
        content.dump(work/'site/link-report.json',{'pages':[{'id':'P1','redlinks':['Missing']}]})
        with patch('automation.inbox.command'),patch.object(self.r,'existing_redlinks',return_value={('P1','Missing')}):
            self.r.check(work)
            content.dump(work/'site/link-report.json',{'pages':[{'id':'P1','redlinks':['Missing']},{'id':'P2','redlinks':['Missing']}]})
            with self.assertRaisesRegex(ValueError,'新的未创建'):self.r.check(work)

    def test_numeric_evidence_accepts_equivalent_not_invented_values(self):
        def check(text,quote):
            e={'page':1,'section':'Results','quote':quote};fact={'text':text,'evidence':[e]}
            data={'metadata':{k:{'value':'','evidence':[]} for k in ['title','title_zh','authors','year','venue','doi','arxiv','code']},
                  'field':'Test','introduced_methods':[],'lead':[fact],'background':[],'method':[fact],
                  'contributions':[fact,fact,fact],'datasets':[],'results':[],'limitations':[],
                  'concepts':[],'cites_existing':[],'review':[],
                  'checklist':[{'item':i,'status':'pass','reason':'index evidence only'} for i in range(1,13)],'publishable':True}
            data['metadata']['title']={'value':'Title','evidence':[dict(e,quote='Title')]}
            content.validate(data,[{'page':1,'text':'Title\n'+quote}])
        for text,quote in [('纳入3项研究','Three studies were included.'),('日期2025年7月29日','July 29, 2025'),('P<.01','P<.01'),('P=0.84','P=.84'),('P=.84','P=0.84'),('21项','twenty-one studies')]:
            with self.subTest(text=text):check(text,quote)
        for text,quote in [('2项','Three studies were included.'),('3项','thirty studies'),('5项','This may improve results.'),('1项','one hundred studies'),('20项','twenty-one studies')]:
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError,'数字未出现'):check(text,quote)

    def test_duplicate_article_title_removed_before_independent_review(self):
        meta={'title':'Original Title','aliases':['中文译名']}
        self.assertEqual(content.remove_duplicate_title(meta,'# 中文译名\n\n导言'),'导言')
        self.assertEqual(content.remove_duplicate_title(meta,'## 背景\n正文'),'## 背景\n正文')
        with self.assertRaisesRegex(ValueError,'不匹配'):content.remove_duplicate_title(meta,'# Other topic\n正文')

    def test_bitmap_ocr_keeps_original_text_and_labels_machine_output(self):
        from automation.ocr import supplement_pdf
        import fitz,base64
        from types import SimpleNamespace
        source=self.root/'figure.pdf'
        with fitz.open() as doc:
            page=doc.new_page()
            page.insert_image(fitz.Rect(20,20,80,80),stream=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
            doc.save(str(source))
        pages=[{'page':1,'text':'PDF body without bitmap labels'}]
        quote={'page':1,'quote':'Articles included N=19','section':'Figure 1'}
        with self.assertRaises(ValueError):content.validate_evidence([quote],pages)
        def machine(args,**kwargs):
            return SimpleNamespace(returncode=0,stdout=json.dumps({args[-1]:[{'text':'Articles included N=19','confidence':0.99}]}))
        with patch('automation.ocr.platform.system',return_value='Darwin'),patch('automation.ocr.shutil.which',return_value='/usr/bin/swift'),patch('automation.ocr.subprocess.run',side_effect=machine):
            result=supplement_pdf(source,pages,self.root)
        self.assertEqual(result[0]['pdf_text'],'PDF body without bitmap labels')
        self.assertIn('Machine OCR',result[0]['text'])
        content.validate_evidence([quote],result)

    def test_original_text_survives_pdf_cleanup_for_later_review(self):
        p=self.pdf('source.pdf');digest=sha(p)
        self.r.archive_source(digest,{'id':'Pnew'},[{'page':1,'text':'Original evidence 42'}],p)
        p.rename(self.r.inbox/'.trash/source.pdf')
        cached=json.loads(content.read(self.root/'extract/sources/Pnew.json'))
        self.assertEqual(cached['sha256'],digest)
        content.validate_evidence([{'page':1,'quote':'Original evidence 42','section':'Results'}],cached['pages'])
        with self.assertRaisesRegex(ValueError,'哈希冲突'):
            self.r.archive_source('different',{'id':'Pnew'},[{'page':1,'text':'Other'}],p)

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
