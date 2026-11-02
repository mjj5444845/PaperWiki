import importlib.util,json,os,pathlib,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class BuildTests(unittest.TestCase):
    def test_footnote_reuse_is_valid_but_conflicting_definitions_fail(self):
        builder.validate_footnotes('A[^source] B[^source]\n\n[^source]: A source')
        with self.assertRaisesRegex(ValueError, 'Duplicate footnote'):
            builder.validate_footnotes('A[^source]\n\n[^source]: First\n[^source]: Other')

    def test_inline_math_preserves_prices_and_code(self):
        import build
        self.assertEqual(build.inline_math('$R^2$ and $p<0.01$'),r'\(R^2\) and \(p<0.01\)')
        self.assertEqual(build.inline_math('$N(i)$ $0.01$ $κ$'),r'\(N(i)\) \(0.01\) \(κ\)')
        self.assertEqual(build.inline_math('费用$15 and $30，代码`$x$`'),'费用$15 and $30，代码`$x$`')
    def test_project_and_local_paths(self):
        for base in ['/','/PaperWiki/','/renamed-repo/']:
            with self.subTest(base=base),tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'BASE_URL':base}),patch.object(builder,'OUT',pathlib.Path(tmp)/'site'):
                pages=builder.build();report=json.loads((builder.OUT/'link-report.json').read_text())
                self.assertEqual(report['errors'],[])
                p16=(builder.OUT/'papers/P16.html').read_text()
                self.assertIn('id="fnref:',p16)
                self.assertIn('class="footnote-backref"',p16)
                self.assertIn('data-page="C080"',p16)
                cf=(builder.OUT/'concepts/C021.html').read_text()
                self.assertIn('katex',cf)
                self.assertEqual(len(pages),len(json.loads((ROOT/'wiki/registry.json').read_text())['entities']))
                self.assertTrue(all(p['backlinks'] for p in pages.values()))
                self.assertIn(base+'assets/style.css',(builder.OUT/'index.html').read_text())
                home=(builder.OUT/'index.html').read_text()
                self.assertNotIn('最近新增',home)
                self.assertNotIn('[[',home)
                self.assertIn('这里收录人机交互及相关领域的论文介绍',home)
                featured=home.split('<h2>本批新增论文</h2>',1)[1].split('</ul>',1)[0]
                latest=builder.read_page(ROOT/'wiki/index.md')[0]['latest_papers']
                self.assertIn('class="page-list"',featured)
                for pid in latest:
                    self.assertIn('href="'+base+pages[pid]['path']+'"',featured)
                    self.assertIn('<p>',featured)
                    self.assertEqual(pages[pid]['field'],'设计研究与方法' if pid=='Pab7b29056453' else '人类与机器人交互')
                redirects=json.loads((builder.OUT/'redirects.json').read_text());self.assertEqual(redirects['MTurk']['target'],'C001')
    def test_home_batch_rotates_only_on_new_publication(self):
        from automation.content import update_home_batch, split
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            (root/'wiki').mkdir()
            path=root/'wiki/index.md'
            path.write_text("---\nlatest_batch: old\nlatest_papers: [P01]\n---\n首页介绍\n")
            update_home_batch(root,'P02','run-a')
            update_home_batch(root,'P03','run-a')
            update_home_batch(root,'P02','run-a')
            self.assertEqual(split(path.read_text())[0]['latest_papers'],['P02','P03'])
            update_home_batch(root,'P04','run-b')
            meta,body=split(path.read_text())
            self.assertEqual(meta['latest_papers'],['P04'])
            self.assertEqual(body.strip(),'首页介绍')

    def test_repo_inference(self):
        with patch.dict(os.environ,{'GITHUB_REPOSITORY':'someone/AnotherWiki'},clear=True):self.assertEqual(builder.base_url(),'/AnotherWiki/')
    def test_linker_does_not_corrupt_code_or_anchors(self):
        p={'id':'A','title':'Alpha','path':'papers/A.html','outlinks':set(),'redlinks':set()};q={'id':'B','title':'测试','path':'concepts/B.html'}
        linker=builder.Linker({'A':p,'B':q},{'测试':'B','alpha':'A'},'/Repo/')
        result=linker.render('<code>[[测试]]</code><a href="x">[[测试]]</a> [[测试|显示]] [[未建页]] [[Alpha]]',p)
        self.assertIn('<code>[[测试]]</code>',result);self.assertIn('<a href="x">[[测试]]</a>',result)
        self.assertIn('/Repo/concepts/B.html',result);self.assertIn('页面尚未创建',result);self.assertEqual(p['outlinks'],{'B'})
    def test_base_path_rejects_protocol_relative(self):
        with patch.dict(os.environ,{'BASE_URL':'//other.example/'}):
            with self.assertRaises(ValueError):builder.base_url()
if __name__=='__main__':unittest.main()
