# -*- coding: utf-8 -*-
"""Comparable descriptive counts; content quality requires manual reading."""
import csv,json,re,statistics
import mwparserfromhell as mw
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prose_md(raw):
    text=raw.split('---',2)[-1] if raw.startswith('---\n') else raw
    text=text.split('## 参考文献')[0].split('## 参见')[0]
    text=re.sub(r'\[\^.*?\]','',text)
    text=re.sub(r'\[\[([^]|]+)\|([^]]+)\]\]',r'\2',text)
    text=re.sub(r'\[\[([^]]+)\]\]',r'\1',text)
    text=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',text)
    return re.sub(r'[#*`|]','',text)
def count(text):return len(re.findall(r'[\u3400-\u9fff]|[A-Za-z]+(?:[-’\'][A-Za-z]+)*|\d+(?:\.\d+)?',text))
def metrics_md(path):
    raw=path.read_text();prose=prose_md(raw)
    urls=set(re.findall(r'https?://[^\s)\]>]+',raw))
    return dict(title=path.stem,words=count(prose),han=len(re.findall('[\u3400-\u9fff]',prose)),sections=len(re.findall(r'^#{2,6} ',raw,re.M)),numbers=len(re.findall(r'(?<![A-Za-z])\d+(?:[.,]\d+)*(?:%|％)?',prose)),tables=len(re.findall(r'^\|(?:\s*:?-+:?\s*\|)+\s*$',raw,re.M)),citations=len(re.findall(r'\[\^[^]\n]+\](?!:)',raw)),references=len(re.findall(r'^\[\^[^]]+\]:',raw,re.M)),external_sources=len(urls),url_list=sorted(urls))
def wiki_corpus():
    texts={};wikis={}
    for p in (ROOT/'raw').glob('text-*.json'):
        for a in json.loads(p.read_text()).get('query',{}).get('pages',[]):texts[a['title']]=a.get('extract','')
    for p in (ROOT/'raw').glob('wikitext-*.json'):
        for a in json.loads(p.read_text()).get('query',{}).get('pages',[]):
            if a.get('revisions'):wikis[a['title']]=a['revisions'][0]['slots']['main']['content']
    return texts,wikis
def metrics_wiki(title,text,wt):
    # TextExtracts may omit tables and formulas; count them from wikitext separately.
    body=re.split(r'^==\s*(?:參考|参考|参见|參見|参阅|參閱|注释|註釋|脚注|腳註|外部連結|外部链接|延伸閱讀|延伸阅读)',wt,flags=re.M)[0]
    code=mw.parse(body)
    for tag in list(code.filter_tags()):
        if str(tag.tag).lower() in ['ref','math','chem','score','gallery','timeline']:
            try:code.remove(tag)
            except ValueError:pass
    for link in list(code.filter_wikilinks()):
        if re.match(r'(?:File|Image|文件|檔案|图像|圖像):',str(link.title),re.I):
            try:code.remove(link)
            except ValueError:pass
    prose=code.strip_code()
    sources=json.loads((ROOT/'notes/benchmark-sources.json').read_text()).get(title,[])
    source_count=len(sources)
    return dict(title=title,words=count(prose),han=len(re.findall('[\u3400-\u9fff]',prose)),sections=len(re.findall(r'^={2,6}[^=].*?={2,6}\s*$',wt,re.M)),numbers=len(re.findall(r'(?<![A-Za-z])\d+(?:[.,]\d+)*(?:%|％)?',prose)),tables=len(re.findall(r'^\s*\{\|',wt,re.M)),citations=len(re.findall(r'<ref\b',wt,re.I))+len(re.findall(r'\{\{(?:sfn|sfnp|harvnb)\b',wt,re.I)),references=len(re.findall(r'<ref\b[^>]*>.*?</ref>',wt,re.I|re.S))+len(re.findall(r'\{\{(?:sfn|sfnp)\b',wt,re.I)),external_sources=source_count,external_urls=len(set(re.findall(r'https?://[^\s|<>}\]]+',wt))),formulas=len(re.findall(r'<math\b',wt)))
SELECTED=['馬克士威方程組','量子场论','旋度','三角函数','DNA纳米技术','電機工程學','PowerBook 100','百萬美元首頁','2channel','坎尔井地下水利工程','阿波罗17号','菱形十二面體']
def main():
    dest=ROOT/'qa/depth-baseline';dest.mkdir(exist_ok=True)
    papers=[metrics_md(p) for p in sorted((ROOT/'wiki/papers').glob('*.md'))]
    reg=json.loads((ROOT/'wiki/registry.json').read_text());names={e['id']:e['canonical_name'] for e in reg['entities']}
    for r in papers:r['id']=r['title'];r['title']=names[r['id']]
    texts,wikis=wiki_corpus();samples=[]
    for title in SELECTED:
        if title not in texts or title not in wikis:raise ValueError('Missing corpus entry '+title)
        samples.append(metrics_wiki(title,texts[title],wikis[title]))
    for name,rows in [('papers-before',papers),('benchmarks',samples)]:
        target=dest/(name+'.json')
        if name!='papers-before' or not target.exists():target.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print('paper median',statistics.median(r['words'] for r in papers),'benchmark median',statistics.median(r['words'] for r in samples))
    print('sample count',len(samples),'papers',len(papers))
if __name__=='__main__':main()
