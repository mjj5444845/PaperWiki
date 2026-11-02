# -*- coding: utf-8 -*-
"""Independent source-based concept audit, grouped to keep source packets bounded."""
import json,sys,hashlib,time,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from automation.inbox import Runner
from automation.depth import Pipeline,CHECK,digest,check_schema,compact_metadata
ROOT=Path(__file__).resolve().parents[1]

def audit(ids):
    reg=json.loads((ROOT/'wiki/registry.json').read_text());byid={e['id']:e for e in reg['entities']}
    candidates={byid[c]['markdown_path']:(ROOT/'wiki'/byid[c]['markdown_path']).read_text() for c in ids}
    papers=set(pid for c in ids for pid in byid[c]['appears_in_papers'])
    lookup={name.casefold():e for e in reg['entities'] for name in [e['canonical_name']]+e['aliases']}
    for text in candidates.values():
        for name in re.findall(r'\[\[([^\n]+?)\]\]',text):
            e=lookup.get(name.split('|')[0].casefold())
            if e and e['type']=='论文':papers.add(e['id'])
    # A citation to a corpus DOI is also an exact paper reference, even without a wikilink.
    for e in reg['entities']:
        if e['type']!='论文':continue
        header=(ROOT/'wiki'/e['markdown_path']).read_text().split('---',2)[1]
        dois=re.findall(r'https://doi\.org/([^\s)]+)',header)
        if any('https://doi.org/'+doi in text for doi in dois for text in candidates.values()):papers.add(e['id'])
    sources={}
    for pid in papers:
        p=ROOT/f'extract/sources/{pid}.json'
        if p.exists():sources[pid]=json.loads(p.read_text())['pages']
        full=ROOT/f'raw/depth-external/{pid}-complete.pdf'
        if full.exists():
            import fitz
            with fitz.open(full) as doc:sources[pid]=[{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]
        if not p.exists():
            e=byid[pid];d=e.get('source_sha256','')
            found=list((ROOT/'state/logs').glob('*/'+d+'/source.json'))
            if found:sources[pid]=json.loads(found[0].read_text())
    # Large methods papers are given in full; audit groups should contain few concepts.
    external=[]
    if 'C004' in ids:
        for name,url in [('thematic-phases.txt','https://www.thematicanalysis.net/doing-reflexive-ta/'),('thematic-faq.txt','https://www.thematicanalysis.net/faqs/')]:
            f=ROOT/'raw/depth-external'/name
            if f.exists():external.append({'url':url,'verbatim_text':f.read_text(),'retrieval':'Python urllib, original author website'})
    if any(c in ids for c in ['C037','C041','C046']):
        f=ROOT/'raw/depth-external/ChunTie2019-fulltext.txt'
        if f.exists():external.append({'url':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6318722/fullTextXML','verbatim_text':f.read_text(),'retrieval':'EuropePMC full JATS XML, complete original JATS text, without paraphrase'})
    if 'C014' in ids:
        f=ROOT/'raw/external/munzner-2021-vad-pp10-15.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C083' in ids:
        f=ROOT/'raw/depth-external/C083-Fogg-ch42-web-result.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C085' in ids:
        f=ROOT/'raw/depth-external/P01-Gaver2012.txt'
        if f.exists():external.append({'url':'https://research.gold.ac.uk/14818/7/WHAT%20SHOULD%20WE%20EXPECT%20AAM.pdf','verbatim_text':f.read_text(),'retrieval':'complete original author accepted PDF text, physical pages marked'})
    if 'C024' in ids:
        f=ROOT/'raw/external/ids-what-are-participatory-methods.txt'
        if f.exists():external.append({'url':'https://www.participatorymethods.org/what-are-participatory-methods/','verbatim_text':f.read_text(),'retrieval':'official IDS HTML, mechanical plain text extraction'})
    if 'C023' in ids:
        f=ROOT/'raw/depth-external/ids-par-source.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C055' in ids:
        f=ROOT/'raw/depth-external/C055-FTC-2022-locations.txt'
        if f.exists():external.append({'url':'https://search.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf','verbatim_text':f.read_text(),'retrieval':'original FTC report PDF, cited sections'})
    if 'C084' in ids:
        for name,url in [('thematic-phases.txt','https://www.thematicanalysis.net/doing-reflexive-ta/'),('thematic-faq.txt','https://www.thematicanalysis.net/faqs/')]:
            f=ROOT/'raw/depth-external'/name
            if f.exists():external.append({'url':url,'verbatim_text':f.read_text(),'retrieval':'original author website HTML, mechanical text extraction'})
    if 'C082' in ids:
        f=ROOT/'raw/depth-external/C082-Hallgren-web-result.json'
        if f.exists():external.append(json.loads(f.read_text()))
    source_caches = {
        'C043': [('C043-Sculley2015-locations.txt','https://proceedings.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf')],
        'C044': [('C044-frames-locations.txt','https://doi.org/10.1145/196734.196745')],
        'C054': [('C054-NBS-history-locations.txt','https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication300v1.pdf')],
        'C059': [('C059-JohnsonHenderson2002-locations.txt','https://doi.org/10.1145/503355.503366')],
        'C060': [('C060-SHAP-intro-markdown.txt','https://github.com/shap/shap/blob/master/notebooks/overviews/An%20introduction%20to%20explainable%20AI%20with%20Shapley%20values.ipynb'),('C060-SHAP-causality-markdown.txt','https://github.com/shap/shap/blob/master/notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.ipynb')],
        'C061': [('C061-Ellis2011-text.txt','https://www.qualitative-research.net/index.php/fqs/article/download/1589/3095?inline=1')]}
    for cid, files in source_caches.items():
        if cid not in ids:continue
        for name,url in files:
            f=ROOT/'raw/depth-external'/name
            if f.exists():external.append({'url':url,'verbatim_text':f.read_text(),'retrieval':'original source text, cited passages mechanically extracted; not author summary'})
    if 'C061' in ids:
        f=ROOT/'raw/depth-external/C061-Millen2000-web-extract.json'
        if f.exists():external.append({'url':'https://course.ccs.neu.edu/is4300sp13/ssl/articles/p280-millen.pdf','original_web_response':json.loads(f.read_text())})
    if 'C040' in ids:
        f=ROOT/'raw/depth-external/C040-agreement-source.txt'
        if f.exists():external.append({'url':'https://faculty.washington.edu/wobbrock/pubs/tochi-22.pdf','verbatim_text':f.read_text(),'retrieval':'original paper PDF pages 33,34,37,50, unmodified extracted text'})
    if 'C077' in ids:
        f=ROOT/'raw/depth-external/C077-Szeliski-history-stitching.txt'
        if f.exists():external.append({'url':'https://szeliski.org/Book/drafts/SzeliskiBook_20100903_draft.pdf','verbatim_text':f.read_text(),'retrieval':'original textbook PDF, history and image stitching pages'})
    if 'C032' in ids:
        f=ROOT/'raw/external/billinghurst-2015-ar-sections.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C057' in ids:
        f=ROOT/'raw/depth-external/C057-history-web-extract.json'
        if f.exists():external.append({'original_web_response':json.loads(f.read_text()),'retrieval':'actual opened official IBM history page response'})
    if 'C040' in ids:
        f=ROOT/'raw/depth-external/C040-statistical-tests-locations.txt'
        if f.exists():external.append({'url':'https://faculty.washington.edu/wobbrock/pubs/tochi-22.pdf','verbatim_text':f.read_text(),'retrieval':'original 2022 paper statistical test discussion, PDF pages 49–59'})
    if 'C043' in ids:
        f=ROOT/'raw/depth-external/C043-Fowler-technicaldebt-web.json'
        if f.exists():external.append({'url':'https://martinfowler.com/bliki/TechnicalDebt.html','original_web_response':json.loads(f.read_text())})
    if 'C029' in ids:
        f=ROOT/'raw/depth-external/C029-TensorFlow-source.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C003' in ids:
        f=ROOT/'raw/depth-external/triangulation-source.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C069' in ids:
        f=ROOT/'raw/depth-external/harvard-sts-source.json'
        if f.exists():external.append(json.loads(f.read_text()))
    if 'C077' in ids:
        f=ROOT/'raw/depth-external/Szeliski2010-used-pages.txt'
        if f.exists():external.append({'url':'https://szeliski.org/Book/drafts/SzeliskiBook_20100903_draft.pdf','verbatim_text':f.read_text(),'retrieval':'original textbook PDF, selected cited pages'})
    if 'C073' in ids:
        f=ROOT/'raw/depth-external/groupware-grudin-source.json'
        if f.exists():external.append(json.loads(f.read_text()))
    publisher_metadata=[]
    for cid in ids:
        f=ROOT/'raw/depth-external'/(cid+'-publisher.json')
        if f.exists():publisher_metadata.append(compact_metadata(json.loads(f.read_text())))
    for pid in papers:
        f=ROOT/'extract/metadata'/(pid+'.json')
        if f.exists():publisher_metadata.append(compact_metadata(json.loads(f.read_text())))
    visual_map={'C021':{'P09':[6,7]},'C036':{'P16':[8]},'C040':{'P05':[4,5]},'C054':{'P04':[4,5,6]},'C066':{'P04':[5,6]},'C075':{'P21':[10,11,12,13]},'C079':{'P21':[10,11,12,13]},'C081':{'P21':[10,11,12,13]},'C082':{'P19':[11]}}
    visual_pages={}
    for cid in ids:
        for pid,ns in visual_map.get(cid,{}).items():visual_pages[pid]=sorted(set(visual_pages.get(pid,[])+ns))
    extra_images=[ROOT/'raw/depth-external'/('C030-Cleveland1984-%d.png'%n) for n in [2,3]] if 'C030' in ids else []
    identifier=digest({'supplementary_images':[hashlib.sha256(p.read_bytes()).hexdigest() for p in extra_images if p.exists()],'candidates':candidates,'sources':sources,'external':external,'publisher_metadata':publisher_metadata,'visual_pages':visual_pages,'schema_protocol':2})[:16]
    job=ROOT/'state/logs/concept-audit'/identifier;r=Runner(ROOT);pipe=Pipeline(r,job)
    if visual_pages:
        import fitz
        directory=job/'source-images';directory.mkdir(exist_ok=True)
        for pid,ns in sorted(visual_pages.items()):
            sourcefile=Path(json.loads((ROOT/f'extract/sources/{pid}.json').read_text())['file'])
            with fitz.open(sourcefile) as doc:
                for n in ns:
                    target=directory/(pid+'-%03d.png'%n)
                    if not target.exists():
                        p=doc[n-1];p.get_pixmap(matrix=fitz.Matrix(1400/p.rect.width,1400/p.rect.width)).save(str(target))
                    pipe.images.append(str(target))
    pipe.images.extend(str(p.resolve()) for p in extra_images if p.exists())
    out=job/'independent-check/output.json'
    complete=job/'independent-check.complete'
    if out.exists() and complete.exists():result=json.loads(out.read_text())
    else:
        if (job/'independent-check').exists():
            import shutil
            shutil.move(str(job/'independent-check'),str(job/('independent-check-failed-'+str(time.time_ns()))))
        result=pipe.stage('independent-check',check_schema(candidates),
        '独立审校这些概念页。原论文按ID提供全文，页面源引用使用物理PDF页码。核定义、机制、公式/例子、变体、边界与每篇本站应用是否真的讲了概念如何使用。'
        '外部来源优先实际打开查证定义和背景；提供的verbatim_external_cache是从所标官方URL实际抓取的原始全文，可以独立阅读核对，不是作者概括。不能以搜索摘要替代原文。findings逐项记关键具体论断，不能只给总通过；不复制长引文，source标页或URL。'
        'coverage列每页全部实质章节及真正未核实的页面论断。未重跑原实验、未收到盲读题、不访问本站目标文件等不属本角色，不列为事实缺口。'
        'publisher_metadata是实际获取的Crossref原始书目缓存，可作为已读书目证据。区分真正采用概念、提出方法建议、作为设计参照与仅仅相关：这些关系须准确标明，不强行把未命名的统计量或未实施的建议写成已经采用的技术。'
        '12项风格与7反模式有具体理由。不要假定任何作者已经自评通过，发现错误或不完整记录error/unverified，不改正文。',
        {'skill':pipe.rules,'candidate_pages':candidates,'original_papers':sources,'verbatim_external_cache':external,'publisher_metadata':publisher_metadata,'supplementary_visual_sources':([{'source':'Cleveland and McGill 1984','url':'https://faculty.washington.edu/aragon/classes/hcde511/s12/readings/cleveland84.pdf','physical_pages':[2,3],'order':'attached after original corpus images'}] if extra_images else []),'attached_visual_pages_in_order':[(pid,n) for pid,ns in sorted(visual_pages.items()) for n in ns]},web=True)
    complete.write_text('ok\n')
    result={'schema_protocol':2,'ids':ids,'page_hashes':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in candidates.items()},'audit':result}
    dest=ROOT/'qa/concept-audits';dest.mkdir(exist_ok=True)
    prior=dest/('-'.join(ids)+'.json')
    if prior.exists():
        history=dest/'history';history.mkdir(exist_ok=True)
        (history/(prior.stem+'-'+hashlib.sha256(prior.read_bytes()).hexdigest()[:12]+'.json')).write_text(prior.read_text())
    (dest/('-'.join(ids)+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('DONE',ids,[(x['verdict'],x['claim'][:50]) for x in result['audit']['findings'] if x['verdict']!='supported'],'failed checks',[(k,x['item'],x['reason']) for k in ['style','antipatterns'] for x in result['audit'][k] if not x['pass']],flush=True)
if __name__=='__main__':audit(sys.argv[1:])
