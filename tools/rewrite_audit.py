# -*- coding: utf-8 -*-
"""Run a fresh blind reader, source-based grader, and separate fact checker per paper.
Usage: .venv/bin/python tools/rewrite_audit.py P02 P03
Private raw model logs stay in state/logs; public reports contain answers/reasons.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from automation.inbox import Runner
from automation.depth import Pipeline, ANSWERS, GRADES, CHECK, QUESTION, NeedsReview, evaluate, digest, check_schema, compact_metadata
from automation.schema import obj, array
from automation import content
ROOT=Path(__file__).resolve().parents[1]

def run(pid, reader_only=False):
    r=Runner(ROOT)
    markdown=(ROOT/f'wiki/papers/{pid}.md').read_text()
    questions=(ROOT/f'notes/{pid}-questions.md').read_text()
    source=json.loads((ROOT/f'extract/sources/{pid}.json').read_text())['pages']
    full=ROOT/f'raw/depth-external/{pid}-complete.pdf'
    if full.exists():
        import fitz
        with fitz.open(full) as doc:source=[{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]
    metadata=[]
    for f in [ROOT/f'extract/metadata/{pid}.json']+sorted((ROOT/'raw/depth-external').glob(pid+'*publisher.json'))+sorted((ROOT/'raw/depth-external').glob(pid+'*crossref.json'))+([ROOT/'raw/depth-external/ESP-JainParkes-crossref.json'] if pid=='P25' else []):
        if f.exists():metadata.append(compact_metadata(json.loads(f.read_text())))
    # Cross-referenced corpus papers also need independently fetched bibliographic records.
    for f in sorted((ROOT/'extract/metadata').glob('*.json')):
        record=compact_metadata(json.loads(f.read_text()))
        if record not in metadata:metadata.append(record)
    external_cache=[json.loads(f.read_text()) for f in sorted((ROOT/'raw/depth-external').glob(pid+'*-external-verbatim.json'))]
    # Source-only examiner prevents author-tailored questions. Preserve the author set.
    examiner_job=ROOT/f'state/logs/rewrite-questions/{pid}'/digest(source)[:16]
    examiner=Pipeline(r,examiner_job)
    qfile=examiner_job/'source-examiner/output.json'
    if not qfile.exists():
        qdata=examiner.stage('source-examiner',obj({'questions':array(QUESTION)}),
            '只读原论文，未取得百科草稿。设计10个从基础到细节的读后问题，必须覆盖完整核心框架各组成、方法如何运作、主要设置/结果及局限；不得只问摘要或琐碎元数据。expected写答案要点，evidence给准确物理页和同页逐字短引文。不要假设看过作者已写页面。',
            {'original_paper':source})
        if sorted(q['id'] for q in qdata['questions'])!=list(range(1,11)):raise NeedsReview('独立出题不足10题')
        for q in qdata['questions']:content.validate_evidence(q['evidence'],source)
    else:qdata=json.loads(qfile.read_text())
    if sorted(q['id'] for q in qdata['questions'])!=list(range(1,11)):raise NeedsReview('独立出题不足10题')
    for q in qdata['questions']:content.validate_evidence(q['evidence'],source)
    author_backup=ROOT/f'notes/{pid}-questions-author.md'
    if not author_backup.exists():author_backup.write_text(questions)
    questions='# '+pid+' 独立原文出题（冻结验证版）\n\n'+'\n\n'.join(str(q['id'])+'. '+q['question'] for q in qdata['questions'])+'\n'
    (ROOT/f'notes/{pid}-questions.md').write_text(questions)
    identifier=digest({'page':markdown,'questions':questions,'source':source,'publisher_metadata':metadata,'external_cache':external_cache,'audit_protocol':4})[:16]
    job=ROOT/f'state/logs/rewrite-audit/{pid}/{identifier}'
    pipe=Pipeline(r,job)
    def cached(name,schema,instruction,payload,web=False):
        f=job/name/'output.json'
        # A successful stage is reused only under the identical input snapshot.
        if f.exists() and (job/(name+'.complete')).exists():return json.loads(f.read_text())
        if (job/name).exists():
            import shutil
            shutil.move(str(job/name),str(job/(name+'-failed-'+str(int(__import__('time').time())))))
        result=pipe.stage(name,schema,instruction,payload,web)
        (job/(name+'.complete')).write_text('ok\n')
        return result
    answers=cached('reader',ANSWERS,
        '你没有读过原论文。只阅读给定新百科页回答全部10题，引用页面章节作为根据。找不到或不完整就明确指出，不能从既有知识猜补，不自行评分。',
        {'page':markdown,'questions':questions})
    if reader_only:return
    grades=cached('grader-v3',GRADES,
        '你是独立阅卷者。根据原文、独立出题者的答案要点及冻结题目检查10个读者答案。题目均基于原文，不考外部发展。每题1或0，关键部分缺失或错误记0，不替读者补答案。答案要点只是索引，以所给原文为准，给逐题理由。',
        {'original_paper':source,'page':markdown,'questions':questions,'reader_answers':answers,'source_based_answer_key':qdata['questions']})
    image_dir=job/'source-images'
    if not image_dir.exists():
        sourcefile=full if full.exists() else Path(json.loads((ROOT/f'extract/sources/{pid}.json').read_text())['file'])
        images=r.render_source_pages(sourcefile,job)
        (job/'page-images').rename(image_dir)
    pipe.images=[str(p) for p in sorted(image_dir.glob('*.png'))]
    related_sources={}
    registry=json.loads((ROOT/'wiki/registry.json').read_text())
    for entity in registry['entities']:
        if entity['type']!='论文' or entity['id']==pid:continue
        header=(ROOT/'wiki'/entity['markdown_path']).read_text().split('---',2)[1]
        dois=re.findall(r'https://doi\.org/([^\s)]+)',header)
        if not (any(name in markdown for name in [entity['canonical_name']]+entity['aliases']) or any('https://doi.org/'+d in markdown for d in dois)):continue
        sourcefile=ROOT/'extract/sources'/(entity['id']+'.json')
        if sourcefile.exists():related_sources[entity['id']]=json.loads(sourcefile.read_text())['pages']
    audit=cached('factchecker-visual-v5-related',check_schema(['papers/'+pid+'.md']),
        '你是独立事实审校者，只取得原文、新百科页和写作规范，未见作者笔记/自评/读者答案。'
        '逐项核对核心框架、所有数字与表格、实验条件、结论、局限和引用对应。必须使用web打开并阅读外部引用资料，不能只看搜索摘要。'
        'related_original_papers同样是本站原始论文全文，可核站内比较及指定物理页，不必用失败的网络请求替代已给全文。新外部背景/后续仍须实际打开核。'
        'findings逐个列关键论断和数字，source给原PDF页/节或真实网址，reason具体说明对应。'
        '既有原文已提供，publisher_metadata是实际获取的Crossref原始书目缓存，可据其确认DOI等元数据；不要求经DOI重新获取同一原文。verbatim_external_cache为所标官方URL实际获取的原始全文，可直接独立阅读核对；新增外部来源必须实际核对，无法核对记unverified。'
        'coverage列本页面核过的全部章节及未核细节。12项checklist和7反模式逐项有具体理由。'
        '发现错误或未覆盖必须如实记录，不能因为网页写得详细就放行；不自行修正文稿。本角色只核页面事实、行文及原文覆盖。站内死链由构建器查，冻结题目和盲读记录由独立读者与阅卷角色查，未重跑实验不是本文事实核对缺口；不要把不属于本角色的工作放入coverage.unverified或判风格失败。该列表只记录未核实的页面事实论断。',
        {'original_paper':source,'publisher_metadata':metadata,'verbatim_external_cache':external_cache,'related_original_papers':related_sources,'candidate_pages':{'papers/'+pid+'.md':markdown},'skill':pipe.rules},web=True)
    try:
        score=evaluate(answers,grades,audit,['papers/'+pid+'.md']);passed=True;error=None
    except NeedsReview as e:
        score=sum(g['correct'] for g in grades['grades']);passed=False;error=str(e)
    report={'id':pid,'protocol':'source-only-examiner-with-visual-factcheck-v5','factcheck_role':'factchecker-visual-v5-related','job_id':identifier,'page_sha256':hashlib.sha256(markdown.encode()).hexdigest(),
            'questions_sha256':hashlib.sha256(questions.encode()).hexdigest(),'score':score,
            'passed':passed,'error':error,'reader':answers,'grader':grades,'factcheck':audit}
    dest=ROOT/'qa/rewrite-audits';dest.mkdir(exist_ok=True)
    prior=dest/(pid+'.json')
    if prior.exists():
        old=json.loads(prior.read_text());history=dest/'history';history.mkdir(exist_ok=True)
        stamp=hashlib.sha256(prior.read_bytes()).hexdigest()[:12]
        (history/(pid+'-'+stamp+'.json')).write_text(prior.read_text())
    (dest/(pid+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(pid,'PASS' if passed else 'REVIEW',score,'/10',error or '',flush=True)
    return passed
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('papers',nargs='+');p.add_argument('--reader-only',action='store_true');args=p.parse_args()
    for pid in args.papers:
        if not re.fullmatch(r'P\d{2}',pid):raise SystemExit('Invalid original-paper ID')
        try:run(pid,args.reader_only)
        except Exception as e:print(pid,'STAGE FAILED',str(e),flush=True)
