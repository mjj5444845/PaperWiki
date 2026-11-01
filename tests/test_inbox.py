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
if __name__=='__main__':unittest.main()
