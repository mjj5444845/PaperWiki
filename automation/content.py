# -*- coding: utf-8 -*-
"""Evidence validation and deterministic Markdown generation."""
import datetime, hashlib, html, json, re
from pathlib import Path
import yaml
from .schema import SCHEMA

def norm(s):return re.sub(r'\s+', '', s).casefold()
def read(path):return path.read_text(encoding='utf-8')
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def dump(path,data):write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def validate_evidence(items,pages):
    if not items:raise ValueError('事实缺少出处')
    for e in items:
        if e['page']>len(pages) or not e['quote'].strip() or norm(e['quote']) not in norm(pages[e['page']-1]['text']):
            raise ValueError('引文不能在指定 PDF 页定位：第 '+str(e['page'])+' 页')
def validate(data,pages):
    import jsonschema
    jsonschema.validate(data,SCHEMA)
    if not data['publishable']:raise ValueError('提取器判定不宜自动发布：'+'；'.join(data['review']))
    for k,m in data['metadata'].items():
        if m['value']:validate_evidence(m['evidence'],pages)
    if not data['metadata']['title']['value'] or not data['lead'] or not data['method']:raise ValueError('缺少标题、导言或方法')
    if not 3<=len(data['contributions'])<=5:raise ValueError('主要贡献应为 3–5 条')
    for section in ['lead','background','method','contributions','datasets','results','limitations']:
        for f in data[section]:
            validate_evidence(f['evidence'],pages)
            if '[来源请求]' in f['text'] or re.search(r'革命性|突破性|最伟大|卓越',f['text']):raise ValueError('存在待查证或宣传性陈述')
            # Reject introduced numeric values. Do not infer units, percentages or denominators.
            supplied=norm(' '.join(e['quote'] for e in f['evidence']))
            for number in re.findall(r'\d+(?:[.,]\d+)*',f['text']):
                if number.replace(',','') not in supplied.replace(',',''):raise ValueError('数字未出现在就近证据中：'+number)
    if {c['item'] for c in data['checklist']}!=set(range(1,13)):raise ValueError('风格自评未覆盖 12 项')
    if any(c['status']=='review' for c in data['checklist']):raise ValueError('风格自评存在必须修订项')
    for c in data['concepts']:
        validate_evidence(c['application']['evidence'],pages)
        if c['definition']['text']:validate_evidence(c['definition']['evidence'],pages)
    for c in data['cites_existing']:validate_evidence(c['evidence'],pages)

def front(meta,body):return '---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n\n'+body.strip()+'\n'
def split(text):
    _,head,body=text.split('---',2)
    return yaml.safe_load(head),body.strip()
def relink(body,entities,self_id):
    """First occurrence only; protect references, code and existing links."""
    lookup={a.casefold():e for e in entities for a in [e['canonical_name']]+e['aliases']}
    names=sorted((a for a in lookup if len(a)>1),key=len,reverse=True)
    if not names:return body
    pat=re.compile(r'\[\[([^\n]+?)\]\]|\[[^\]\n]*\]\([^\n)]*\)|\[\^[^]]+\]|`[^`]+`|https?://\S+|(?P<term>'+ '|'.join(re.escape(n) for n in names)+')',re.I)
    seen=set();out=[];nav=False
    for segment in re.split(r'(^## .*?$)',body,flags=re.M):
        if segment.startswith('## '):nav=segment.strip() in ['## 参见','## 参考文献'];out.append(segment);continue
        if nav:out.append(segment);continue
        def sub(m):
            if m.group(1):
                name,sep,label=m.group(1).partition('|');e=lookup.get(name.casefold())
                if not e:return m.group()
                if e['id']==self_id or e['id'] in seen:return label if sep else name
                seen.add(e['id']);return m.group()
            term=m.group('term')
            if not term:return m.group()
            # Short generic English words are ambiguous; explicit model links remain allowed.
            if term.casefold() in {'awareness','explanations','precision','replication','acf','nfc','irr','xai','rtd'}:return term
            if term.isascii() and ((m.start() and segment[m.start()-1].isalnum()) or (m.end()<len(segment) and segment[m.end()].isalnum())):return term
            e=lookup[term.casefold()]
            if e['id']==self_id or e['id'] in seen:return term
            seen.add(e['id']);return '[['+e['canonical_name']+'|'+term+']]'
        out.append(pat.sub(sub,segment))
    return ''.join(out)

class References:
    def __init__(self,metadata):self.metadata=metadata;self.lines=[]
    def cite(self,f):
        key='auto'+str(len(self.lines)+1)
        pages='、'.join(str(e['page']) for e in f['evidence'])
        sections=' / '.join(dict.fromkeys(e['section'] for e in f['evidence']))
        m=self.metadata;title=m['title']['value'];authors=m['authors']['value'];year=m['year']['value']
        doi=m['doi']['value'];arxiv=m['arxiv']['value']
        url='https://doi.org/'+doi if doi else 'https://arxiv.org/abs/'+arxiv if arxiv else ''
        link='['+title.replace('[','').replace(']','')+']('+url+')' if url else title
        self.lines.append('[^'+key+']: '+authors+'（'+year+'）。'+link+'。PDF 第'+pages+'页，'+sections+'。')
        return f['text']+'[^'+key+']'

def generate(work,data,pages,digest,review):
    root=Path(work);regpath=root/'wiki/registry.json';reg=json.loads(read(regpath));entities=reg['entities'];byid={e['id']:e for e in entities}
    lookup={norm(a):e for e in entities for a in [e['canonical_name']]+e['aliases']}
    m=data['metadata'];title=m['title']['value'];pid='P'+digest[:12]
    if norm(title) in lookup:raise ValueError('原标题与已有实体相同：需人工确认不同版本，不自动另建页')
    chosen=[];created=[];applications={};today=datetime.date.today().isoformat()
    for c in data['concepts']:
        matches={lookup[norm(n)]['id'] for n in [c['original_term'],c['canonical_name']]+c['aliases'] if norm(n) in lookup}
        if c['existing_id']:
            if c['existing_id'] not in byid:raise ValueError('不存在的概念 ID')
            # A suggested semantic merge is accepted only with an existing exact alias.
            if c['existing_id'] not in matches:
                review.append('未自动合并：'+c['original_term']+' → '+c['existing_id']+'，没有完全一致别名');continue
        if len(matches)>1:review.append('别名有歧义，未合并：'+c['original_term']);continue
        if matches:e=byid[next(iter(matches))]
        elif c['stable'] and c['prerequisite'] and c['definition']['text']:
            name=c['canonical_name']
            if not re.search('[\u4e00-\u9fff]',name) and name not in ['SHAP','Amazon Mechanical Turk']:
                review.append('新概念缺少已确定中文常用名，暂不建页：'+name);continue
            cid='C'+hashlib.sha256(name.encode()).hexdigest()[:12]
            aliases=list(dict.fromkeys(a for a in [c['original_term']]+c['aliases'] if norm(a)!=norm(name)))
            if any(norm(a) in lookup for a in [name]+aliases):review.append('别名冲突：'+name);continue
            e=dict(id=cid,canonical_name=name,type='概念',aliases=aliases,appears_in_papers=[pid],field=data['field'],markdown_path='concepts/'+cid+'.md',html_path='concepts/'+cid+'.html',evidence=c['definition']['evidence'],source_sha256=digest)
            entities.append(e);byid[cid]=e
            for a in [name]+aliases:lookup[norm(a)]=e
            created.append(e)
        else:
            review.append('暂不独立建页（未满足稳定且必需前置知识的保守标准）：'+c['original_term']);continue
        if e['type']!='概念':continue
        if e['id'] not in [x['id'] for x in chosen]:chosen.append(e);applications[e['id']]=c
    if len(chosen)<3:raise ValueError('少于 3 个有证据的相关概念，无法满足站内导航约束，转人工复核')
    aliases=[m['title_zh']['value']] if m['title_zh']['value'] and norm(m['title_zh']['value'])!=norm(title) else []
    if any(norm(a) in lookup for a in aliases):raise ValueError('中文标题别名冲突')
    cites=[]
    for c in data['cites_existing']:
        if c['paper_id'] not in byid or byid[c['paper_id']]['type']!='论文':raise ValueError('无效站内引用')
        cites.append(c['paper_id'])
    paper=dict(id=pid,canonical_name=title,type='论文',aliases=aliases,appears_in_papers=[pid],field=data['field'],markdown_path='papers/'+pid+'.md',html_path='papers/'+pid+'.html',evidence=m['title']['evidence'],cites_papers=cites,source_sha256=digest)
    entities.append(paper);byid[pid]=paper
    for e in chosen:
        if pid not in e['appears_in_papers']:e['appears_in_papers'].append(pid)
    refs=References(m);body='\n\n'.join(refs.cite(f) for f in data['lead'])
    for key,heading in [('background','背景与动机'),('method','方法'),('contributions','主要贡献'),('datasets','研究材料'),('results','实验与结果'),('limitations','局限性')]:
        facts=data[key]
        if not facts:continue
        body+='\n\n## '+heading+'\n\n'
        if key=='results':body+='| 结果及比较条件 | 出处 |\n|---|---|\n'+'\n'.join('| '+refs.cite(f).replace('|','／')+' | PDF 第'+ '、'.join(str(e['page']) for e in f['evidence'])+'页 |' for f in facts)
        else:body+='\n\n'.join(('- ' if key=='contributions' else '')+refs.cite(f) for f in facts)
    body+='\n\n## 与其他工作的关系\n\n'
    if cites:
        for c in data['cites_existing']:
            body+=refs.cite({'text':'论文的参考文献列有[['+byid[c['paper_id']]['canonical_name']+']]。','evidence':c['evidence']})+'\n\n'
    body+='理解本论文涉及'+ '、'.join('[['+e['canonical_name']+']]' for e in chosen)+'。\n\n## 参见\n\n'+'\n'.join('- [['+e['canonical_name']+']]' for e in chosen[:6])+'\n\n## 参考文献\n\n'+'\n\n'.join(refs.lines)
    infobox={'作者':m['authors']['value'],'年份':m['year']['value'],'发表场所':m['venue']['value'],'领域':data['field']}
    for key,label in [('doi','DOI'),('arxiv','arXiv'),('code','代码')]:
        if m[key]['value']:infobox[label]=m[key]['value']
    meta=dict(id=pid,title=title,aliases=aliases,type='论文',field=data['field'],created=today,updated=today,infobox={k:v for k,v in infobox.items() if v})
    write(root/'wiki'/paper['markdown_path'],front(meta,relink(body,entities,pid)))
    changed=[]
    for e in chosen:
        c=applications[e['id']];path=root/'wiki'/e['markdown_path'];cr=References(m)
        app='- [['+title+']]：'+cr.cite(c['application'])
        if e in created:
            definition=cr.cite(c['definition']);eng=c['original_term']
            cm=dict(id=e['id'],title=e['canonical_name'],aliases=e['aliases'],type='概念',field=data['field'],created=today,updated=today)
            cb=definition+'\n\n## 原理与用法\n\n'+definition+'\n\n## 在本站论文中的应用\n\n'+app+'\n\n## 参见\n\n'+'\n'.join('- [['+x['canonical_name']+']]' for x in [paper]+[x for x in chosen if x!=e][:4])+'\n\n## 参考文献\n\n'+'\n\n'.join(cr.lines)
        else:
            cm,cb=split(read(path));prefix='inbox'+digest[:8]
            app=app.replace('[^auto','[^'+prefix)
            reflines='\n\n'.join(cr.lines).replace('[^auto','[^'+prefix)
            if '## 在本站论文中的应用' not in cb:raise ValueError('已有概念页缺少应用栏：'+e['id'])
            cb=cb.replace('## 参见',app+'\n\n## 参见',1)+'\n\n'+reflines
            cm['updated']=today;changed.append(e['markdown_path'])
        write(path,front(cm,relink(cb,entities,e['id'])))
    # Add only navigational reciprocal links for cited papers, never a claim of reciprocal citation.
    for cid in cites:
        e=byid[cid];path=root/'wiki'/e['markdown_path'];cm,cb=split(read(path));section=cb.split('## 参见',1)[1].split('## 参考文献')[0]
        n=len(re.findall(r'^- \[\[',section,re.M))
        if n<6:cb=cb.replace('## 参考文献','- [['+title+']]\n\n## 参考文献',1)
        else:cb=cb.replace('## 参见','本站后续相关论文：[['+title+']]。\n\n## 参见',1)
        cm['updated']=today;write(path,front(cm,relink(cb,entities,cid)));changed.append(e['markdown_path'])
    # Link new stable entities in existing prose only on an exact, unambiguous alias match.
    for e in entities:
        path=root/'wiki'/e['markdown_path'];before=read(path);cm,cb=split(before);after=front(cm,relink(cb,entities,e['id']))
        if after!=before:write(path,after);changed.append(e['markdown_path'])
    reg['counts']['papers']=sum(e['type']=='论文' for e in entities);reg['counts']['concepts']=sum(e['type']=='概念' for e in entities)
    reg['counts']['bibliographic_citation_edges']=sum(len(e.get('cites_papers',[])) for e in entities)
    dump(regpath,reg)
    # build.py derives redirects from aliases; retain the source redirect manifest too.
    red=json.loads(read(root/'wiki/redirects.json'))
    if isinstance(red,dict):
        red['generated_from']='registry.json';red['updated']=today
        dump(root/'wiki/redirects.json',red)
    return paper,[e['canonical_name'] for e in created],sorted(set(changed))
