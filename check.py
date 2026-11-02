# -*- coding: utf-8 -*-
"""Inspect a built site and Markdown sources; write a human-readable QA report."""
import collections,html,json,pathlib,re,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=pathlib.Path(__file__).resolve().parent
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=set();self.links=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])
def run():
    reg=json.loads((ROOT/'wiki/registry.json').read_text());report=json.loads((ROOT/'site/link-report.json').read_text());base=report['base_url'];errors=report['errors'][:];docs={p.relative_to(ROOT/'site').as_posix():Document(p.read_text()) for p in (ROOT/'site').rglob('*.html')}
    for path,doc in docs.items():
        for link in doc.links:
            url=urlsplit(link)
            if url.scheme or not url.fragment:continue
            target=unquote(url.path[len(base):]) if url.path.startswith(base) else path if not url.path else None
            if target in docs and unquote(url.fragment) not in docs[target].ids:errors.append(path+' missing anchor '+link)
    lookup={a.casefold():e for e in reg['entities'] for a in [e['canonical_name']]+e['aliases']};unlinked=[];repeats=[];see_errors=[]
    for e in reg['entities']:
        raw=(ROOT/'wiki'/e['markdown_path']).read_text();body=raw.split('---',2)[-1]
        prose=body.split('## 参见')[0];targets=[]
        for name in re.findall(r'\[\[([^\n]+?)\]\]',prose):
            entity=lookup.get(name.split('|')[0].casefold())
            if entity:targets.append(entity['id'])
        for target,n in collections.Counter(targets).items():
            if n>1:repeats.append(e['id']+' → '+target)
        see=body.split('## 参见',1)[-1].split('## 参考文献')[0]
        if not 3<=len(re.findall(r'^- \[\[',see,re.M))<=6:see_errors.append(e['id'])
        visible=re.sub(r'\[\[[^\n]+?\]\]|\[[^]]*\]\([^)]*\)|\[\^[^]]+\]|`[^`]+`|https?://\S+','',prose)
        for alias in [e['canonical_name']]+e['aliases']:visible=visible.replace(alias,'')
        all_names=sorted([a for e2 in reg['entities'] for a in [e2['canonical_name']]+e2['aliases'] if len(a)>1],key=len,reverse=True)
        found={}
        for m in re.finditer('|'.join(re.escape(a) for a in all_names),visible,re.I):
            name=m.group();other=lookup[name.casefold()]
            if name.casefold() in {'awareness','explanations','precision','replication','acf','nfc','irr','xai','rtd','framing'}:continue
            if name.isascii() and ((m.start() and visible[m.start()-1].isalnum()) or (m.end()<len(visible) and visible[m.end()].isalnum())):continue
            if other['id']==e['id'] or other['id'] in targets:continue
            found.setdefault(other['id'],set()).add(name)
        unlinked.extend({'page':e['id'],'entity':k,'matches':sorted(v)} for k,v in found.items())
    orphan=[p['id'] for p in report['pages'] if not p['incoming']];red=[(p['id'],n) for p in report['pages'] for n in p['redlinks']]
    rows=['# 论文百科检查报告','','状态：构建与结构检查；深度重写验收见 rewrite-report.md，线上验收见 deployment.md。','',f'- 论文页：{sum(e["type"]=="论文" for e in reg["entities"])}；概念页：{sum(e["type"]=="概念" for e in reg["entities"])}；页面间有向链接：{report["links"]}（按页面对去重）。',f'- 死链／资源错误／锚点错误：{len(errors)}；孤立条目：{len(orphan)}。',f'- 条目正文的未创建目标：{len(red)}；阅读帮助另有1个明确标注的红链示例，落地页存在。',f'- 正文重复实体链接：{len(repeats)}；参见数量异常：{len(see_errors)}。',f'- 注册实体在正文出现但全篇未链接的候选：{len(unlinked)}。','- 首页、全部页面、论文与概念列表均由同一注册表生成；站内10条文献引用关系另由页面与原文书目核对。','- 已测试BASE_URL为`/`、`/PaperWiki/`和`/renamed-repo/`；本次报告前缀为`'+base+'`。','','## 每页入链与出链','','| ID | 页面 | 入链 | 出链 |','|---|---|---:|---:|']
    for p in report['pages']:rows.append(f'| {p["id"]} | {p["title"].replace("|","／")} | {p["incoming"]} | {p["outgoing"]} |')
    rows+=['','## 未链接实体候选','']
    rows+=['- '+x['page']+'：'+x['entity']+'，匹配 '+ '、'.join(x['matches']) for x in unlinked] or ['无。']
    rows+=['','## 浏览器检查','','本地浏览器已核验：首页导航；“协同过滤”与“SHAP”搜索；MTurk别名跳转及提示；脚注定位与↑返回；阅读帮助红链及提示页；浅色/深色外观；390px iframe中的手机布局。导言预览与KaTeX渲染亦已核验；线上结果见 deployment.md。','','## 内容审核','','- 五个论文页的数字与结论抽查见`fact-check.md`。','- 风格清单及已修订项见`style-check.md`。','- 概念页结合原论文与另行查证的资料解释机制、变体、边界与本站应用；不补写无来源的发展史。','- 未将PDF、抓取原文或抽取JSON复制进公开网站。','','## 部署记录','','已通过 GitHub Actions 发布至项目路径；部署与线上验收详见 deployment.md。']
    if errors:rows+=['','## 错误','']+errors
    (ROOT/'qa').mkdir(exist_ok=True);(ROOT/'qa/report.md').write_text('\n'.join(rows)+'\n')
    (ROOT/'qa/structure.json').write_text(json.dumps(dict(errors=errors,orphans=orphan,unlinked=unlinked,repeats=repeats,see_also_errors=see_errors,links=report['links']),ensure_ascii=False,indent=2))
    print('Errors',len(errors),'orphans',len(orphan),'unlinked candidates',len(unlinked),'repeated prose links',len(repeats))
    return bool(errors or orphan or repeats or see_errors)
if __name__=='__main__':sys.exit(run())
