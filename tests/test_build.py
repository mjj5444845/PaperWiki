import importlib.util,json,os,pathlib,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class BuildTests(unittest.TestCase):
    def test_project_and_local_paths(self):
        for base in ['/','/PaperWiki/','/renamed-repo/']:
            with self.subTest(base=base),tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'BASE_URL':base}),patch.object(builder,'OUT',pathlib.Path(tmp)/'site'):
                pages=builder.build();report=json.loads((builder.OUT/'link-report.json').read_text())
                self.assertEqual(report['errors'],[])
                p16=(builder.OUT/'papers/P16.html').read_text()
                self.assertIn('id="fnref:s14"',p16)
                self.assertIn('data-page="C080"',p16)
                cf=(builder.OUT/'concepts/C021.html').read_text()
                self.assertIn(r'\(p_{a,i}',cf)
                self.assertEqual(len(pages),len(json.loads((ROOT/'wiki/registry.json').read_text())['entities']))
                self.assertTrue(all(p['backlinks'] for p in pages.values()))
                self.assertIn(base+'assets/style.css',(builder.OUT/'index.html').read_text())
                redirects=json.loads((builder.OUT/'redirects.json').read_text());self.assertEqual(redirects['MTurk']['target'],'C001')
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
