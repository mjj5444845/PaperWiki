# -*- coding: utf-8 -*-
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from automation.depth import NeedsReview, evaluate, check_schema, CHECK, compact_metadata, Pipeline
from automation.inbox import Runner

class DepthGateTests(unittest.TestCase):
    def test_path_enum_does_not_constrain_claims_or_reasons(self):
        schema = check_schema(['papers/Px.md'])
        props = schema['properties']['findings']['items']['properties']
        self.assertEqual(props['path']['enum'], ['papers/Px.md'])
        for field in ['claim', 'source', 'reason']:
            self.assertNotIn('enum', props[field])
        self.assertNotIn('enum', CHECK['properties']['findings']['items']['properties']['path'])

    def test_metadata_retains_bibliography_without_reference_payload(self):
        original = {'source_url': 'https://api.crossref.org/works/x', 'response':
                    {'message': {'DOI': '10/x', 'title': ['Title'], 'author': [{'family': 'Name'}],
                                 'reference': [{'DOI': '10/y'}]}}}
        selected = compact_metadata(original)
        self.assertEqual(selected['response']['message']['author'], [{'family': 'Name'}])
        self.assertNotIn('reference', selected['response']['message'])
        self.assertIn('reference', original['response']['message'])

    def test_locator_repair_keeps_frozen_question_and_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = object.__new__(Pipeline)
            pipeline.job = Path(tmp)
            pipeline.rules = ''
            question = {'id': 1, 'question': 'Which mechanism?', 'expected': 'fixed answer',
                        'evidence': [{'page': 1, 'section': 'Method', 'quote': 'paraphrase'}]}
            prepared = {'notes': [{'page': 1, 'section': 'Method', 'note': 'note', 'quote': 'literal'}],
                        'questions': [dict(question, id=i) for i in range(1, 11)],
                        'omitted_sections': [], 'review': []}
            # Give each question a separate evidence list, just as decoded JSON does.
            prepared = json.loads(json.dumps(prepared))
            def stage(name, schema, instruction, payload, web=False):
                if name == 'full-reading': return prepared
                self.assertEqual(name, 'evidence-locators')
                return {'anchor_'+str(x['index']): 0 for x in payload['invalid']}
            pipeline.stage = stage
            result = pipeline.prepare([{'page': 1, 'text': 'literal original text'}])
            self.assertEqual(result['questions'][0]['question'], question['question'])
            self.assertEqual(result['questions'][0]['expected'], question['expected'])
            self.assertEqual(result['questions'][0]['evidence'][0]['quote'], 'literal original text')
            self.assertTrue((pipeline.job/'original-invalid-locators.json').exists())

    def test_unresolved_locator_is_held_for_human_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline=object.__new__(Pipeline);pipeline.job=Path(tmp);pipeline.rules=''
            prepared={'notes':[{'page':1,'section':'Method','note':'note','quote':'literal'}],
                      'questions':[{'id':i,'question':'Frozen question','expected':'Frozen answer','evidence':[{'page':1,'section':'Method','quote':'missing words'}]} for i in range(1,11)],
                      'omitted_sections':[],'review':[]}
            def stage(name,schema,instruction,payload,web=False):
                if name=='full-reading':return prepared
                return {'anchor_'+str(x['index']):-1 for x in payload['invalid']}
            pipeline.stage=stage
            with self.assertRaisesRegex(NeedsReview,'人工核对'):pipeline.prepare([{'page':1,'text':'literal original'}])
            self.assertEqual(prepared['questions'][0]['question'],'Frozen question')
            self.assertEqual(prepared['questions'][0]['expected'],'Frozen answer')

    def evidence(self):
        return ({'answers':[{'id':i,'answer':'页面中有依据'} for i in range(1,11)]},
                {'grades':[{'id':i,'correct':i<=8,'reason':'与冻结要点一致'} for i in range(1,11)]},
                {'findings':[{'path':'papers/Px.md','claim':'a fact','source':'PDF p2','verdict':'supported','reason':'matches'}],
                 'coverage':[{'path':'papers/Px.md','sections':['method','results'],'unverified':[]}],
                 'style':[{'item':i,'pass':True,'reason':'verified'} for i in range(1,13)],
                 'antipatterns':[{'item':i,'pass':True,'reason':'verified'} for i in range(1,8)],'review':[]})
    def test_eight_passes_seven_fails(self):
        a,g,c=self.evidence();self.assertEqual(evaluate(a,g,c,['papers/Px.md']),8)
        g['grades'][7]['correct']=False
        with self.assertRaises(NeedsReview):evaluate(a,g,c,['papers/Px.md'])
    def test_duplicate_answers_do_not_count_as_ten(self):
        a,g,c=self.evidence();a['answers'][-1]['id']=1
        with self.assertRaises(NeedsReview):evaluate(a,g,c,['papers/Px.md'])
    def test_unresolved_fact_and_missing_coverage_block(self):
        for mode in ['error','unverified','coverage','style','antipattern']:
            with self.subTest(mode=mode):
                a,g,c=self.evidence()
                if mode in ['error','unverified']:c['findings'][0]['verdict']=mode
                if mode=='coverage':c['coverage'][0]['unverified']=['unread source']
                if mode=='style':c['style'].pop()
                if mode=='antipattern':c['antipatterns'][0]['pass']=False
                with self.assertRaises(NeedsReview):evaluate(a,g,c,['papers/Px.md'])
    def test_unreviewed_changed_page_blocks(self):
        a,g,c=self.evidence()
        with self.assertRaises(NeedsReview):evaluate(a,g,c,['papers/Px.md','concepts/C1.md'])
    def test_publish_requires_packet_and_exact_reviewed_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=json.loads(Path('automation/config.json').read_text());r=Runner(root,config)
            with self.assertRaises(NeedsReview):r.verify_depth(root,{})
            path=root/'wiki/papers/Px.md';path.parent.mkdir(parents=True);path.write_text('reviewed article')
            a,g,c=self.evidence();packet={'score':8,'answers':a,'grades':g,'audit':c,'page_hashes':{'papers/Px.md':hashlib.sha256(path.read_bytes()).hexdigest()}}
            evidence=root/'state/logs/job/depth-qa.json';evidence.parent.mkdir();evidence.write_text(json.dumps(packet))
            record={'depth_qa_path':'state/logs/job/depth-qa.json'};r.verify_depth(root,record)
            with tempfile.TemporaryDirectory() as shadow:
                work=Path(shadow);(work/'wiki/papers').mkdir(parents=True);(work/'wiki/papers/Px.md').write_bytes(path.read_bytes());(work/'wiki/papers/unreviewed.md').write_text('new facts')
                with self.assertRaises(NeedsReview):r.verify_depth(work,record)
            path.write_text('changed after review')
            with self.assertRaises(NeedsReview):r.verify_depth(root,record)
            record['depth_qa_path']='../../outside.json'
            with self.assertRaises(NeedsReview):r.verify_depth(root,record)
if __name__=='__main__':unittest.main()
