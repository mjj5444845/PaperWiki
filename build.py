"""Build PaperWiki. BASE_URL=/ for a local root preview; project path by default."""
import collections, hashlib, html, json, os, pathlib, re, shutil, unicodedata
from urllib.parse import quote, urlsplit, unquote
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
R = pathlib.Path(__file__).resolve().parent
OUT = R / 'site'

def base_url():
    repo = os.environ.get('GITHUB_REPOSITORY', 'mjj5444845/PaperWiki').split('/')[-1]
    raw = os.environ.get('BASE_URL', '/' + repo + '/')
    if not raw.startswith('/') or raw.startswith('//') or '?' in raw or '#' in raw or '..' in raw.split('/'):
        raise ValueError('BASE_URL must be a site path, such as /PaperWiki/ or /')
    return raw.rstrip('/') + '/'

def read_page(path):
    text = path.read_text(encoding='utf-8')
    meta = {}
    if text.startswith('---\n'):
        _, head, text = text.split('---', 2)
        meta = yaml.safe_load(head) or {}
    return meta, text.strip()

def plain(text):
    text = re.sub(r'\[\[([^]|]+)\|([^]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\^[^]]+\]', '', text)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>|[*`#]', '', text)).strip()

def inline_math(text):
    """Normalize scientific $...$ while leaving dollar-denominated prices intact."""
    def convert(m):
        value=m.group(1)
        if re.search(r'[\u4e00-\u9fff]',value):return m.group(0)
        if '\\' in value or re.search(r'[_^=<>+{}]',value) or re.fullmatch(r'[A-Za-z\u0370-\u03ff]{1,3}',value.strip()) or re.fullmatch(r'[A-Za-z]+\([^)]*\)',value.strip()) or re.fullmatch(r'[-+]?\d+(?:\.\d+)?%?',value.strip()):
            return r'\('+value+r'\)'
        return m.group(0)
    # Protect fenced and inline code from delimiter conversion.
    parts=re.split(r'(```[\s\S]*?```|`[^`\n]+`)',text)
    for i in range(0,len(parts),2):
        parts[i]=re.sub(r'(?<![\\$])\$(?!\$)([^$\n]{1,250}?)\$(?![$\d])',convert,parts[i])
    return ''.join(parts)

class Linker:
    def __init__(self, pages, lookup, base):
        self.pages, self.lookup, self.base = pages, lookup, base
    def render(self, content, page, record=True):
        # Work on HTML text nodes only: preserve code, pre, existing anchors and attributes.
        parts = re.split(r'(<[^>]+>)', content)
        blocked = []
        for i, part in enumerate(parts):
            if part.startswith('<'):
                close = re.match(r'</(a|code|pre|script|style)\b', part)
                opening = re.match(r'<(a|code|pre|script|style)\b', part)
                if close and blocked: blocked.pop()
                elif opening: blocked.append(opening.group(1))
                continue
            if blocked: continue
            def replace(m):
                target, sep, label = html.unescape(m.group(1)).partition('|')
                name, hashmark, anchor = target.partition('#')
                name = name.strip()
                entity = self.lookup.get(name.casefold())
                label = html.escape(label if sep else name)
                if entity == page['id']: return label
                if entity:
                    if record: page['outlinks'].add(entity)
                    alias = name != self.pages[entity]['title']
                    suffix = ('?from=' + quote(name, safe='')) if alias else ''
                    if hashmark: suffix += '#' + quote(anchor, safe='-')
                    return '<a class="internal" data-page="'+entity+'" href="'+self.base+self.pages[entity]['path']+suffix+'">'+label+'</a>'
                if record: page['redlinks'].add(name)
                return '<a class="redlink" title="页面尚未创建" href="'+self.base+'missing.html?title='+quote(name,safe='')+'">'+label+'</a>'
            parts[i] = re.sub(r'\[\[([^\n]+?)\]\]', replace, part)
        return ''.join(parts)

def validate_footnotes(body):
    definitions = re.findall(r'^\[\^([^]\n]+)\]:', body, flags=re.M)
    repeated = sorted({key for key in definitions if definitions.count(key) > 1})
    if repeated:
        raise ValueError('Duplicate footnote definitions: '+', '.join(repeated))

def build():
    base = base_url()
    registry = json.loads((R/'wiki/registry.json').read_text())
    entities = {e['id']:e for e in registry['entities']}
    pages, lookup = {}, {}
    for e in entities.values():
        src = R/'wiki'/e['markdown_path']
        if not src.exists(): raise ValueError('Registered page is missing: '+str(src))
        meta, body = read_page(src)
        validate_footnotes(body)
        pid = e['id']; title = meta.get('title',e['canonical_name'])
        lead = body.split('\n## ',1)[0]
        pages[pid] = dict(id=pid,title=title,body=body,meta=meta,path=e['html_path'],kind=e['type'],
            aliases=e['aliases'],field=meta.get('field',e.get('field','研究方法与基础概念')),
            intro=plain(lead)[:700],outlinks=set(),redlinks=set(),backlinks=[])
        for name in [title,e['canonical_name']]+e['aliases']:
            key=name.casefold()
            if key in lookup and lookup[key]!=pid: raise ValueError('Ambiguous alias: '+name)
            lookup[key]=pid
    linker=Linker(pages,lookup,base)
    for p in pages.values():
        md=markdown.Markdown(extensions=['tables','fenced_code','footnotes','toc','md_in_html'],extension_configs={'footnotes':{'BACKLINK_TEXT':'↑'},'toc':{'permalink':False}})
        safe_body=re.sub(r'\[\[[^\n]+?\]\]',lambda m:m.group(0).replace('|','&#124;'),p['body'])
        safe_body=inline_math(safe_body)
        maths={}
        def keep_math(m):
            token='PAPERWIKIMATH'+str(len(maths))+'TOKEN';maths[token]=html.escape(m.group(0));return token
        safe_body=re.sub(r'\\\(.+?\\\)|\\\[.+?\\\]|\$\$.+?\$\$',keep_math,safe_body,flags=re.S)
        converted=md.convert(safe_body)
        for token,tex in maths.items():converted=converted.replace(token,tex)
        p['content']=linker.render(converted,p)
        # TOC anchors contain heading text; remove wiki markup without nesting links.
        p['toc']=re.sub(r'\[\[([^]\n]+)\]\]', lambda m:html.escape(html.unescape(m.group(1)).split('|')[-1]), md.toc)
        split=p['content'].find('<h2')
        p['lead_content']=p['content'][:split] if split>=0 else ''
        p['content']=p['content'][split:] if split>=0 else p['content']
        for k,v in p['meta'].get('infobox',{}).items():
            p.setdefault('infobox',[]).append((k,linker.render(markdown.markdown(str(v)),p)))
    for p in pages.values():
        for dest in p['outlinks']:pages[dest]['backlinks'].append(p)
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir();shutil.copytree(R/'assets',OUT/'assets')
    env=Environment(loader=FileSystemLoader(R/'templates'),autoescape=select_autoescape(['html']))
    template=env.get_template('page.html')
    site={'base':base,'name':os.environ.get('SITE_NAME','论文百科'),'repo_url':'https://github.com/'+os.environ.get('GITHUB_REPOSITORY','mjj5444845/PaperWiki'),'papers':sum(p['kind']=='论文' for p in pages.values()),'concepts':sum(p['kind']=='概念' for p in pages.values())}
    def write(path,page):
        dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(template.render(site=site,page=page),encoding='utf-8')
    for p in pages.values():write(p['path'],p)
    def listing(title,items):
        return '<h2>'+html.escape(title)+'</h2><ul class="page-list">'+''.join('<li><a class="internal" data-page="'+p['id']+'" href="'+base+p['path']+'">'+html.escape(p['title'])+'</a><p>'+html.escape(p['intro'][:150])+'</p></li>' for p in items)+'</ul>'
    allpages=list(pages.values()); groups=collections.defaultdict(list)
    for p in allpages:
        if p['kind']=='论文':groups[p['field']].append(p)
    meta,indexbody=read_page(R/'wiki/index.md')
    home=linker.render(markdown.markdown(indexbody,extensions=['tables']),{'id':''},record=False)
    latest=[]
    for pid in meta.get('latest_papers',[]):
        if pid not in pages or pages[pid]['kind']!='论文':
            raise ValueError('Invalid latest paper: '+pid)
        latest.append(pages[pid])
    if latest:home+=listing('本批新增论文',latest)
    home+='<div class="stats"><span><b>'+str(site['papers'])+'</b> 篇论文</span><span><b>'+str(site['concepts'])+'</b> 个基础概念</span><span><b>'+str(len(groups))+'</b> 个领域</span></div>'
    for field,items in groups.items():home+=listing(field,items)
    for path,title,body in [('index.html','论文百科',home),('all.html','全部页面',listing('页面索引',allpages)),('papers.html','论文列表',listing('论文',[p for p in allpages if p['kind']=='论文'])),('concepts.html','概念列表',listing('基础概念',[p for p in allpages if p['kind']=='概念'])),('help.html','阅读帮助','<h2>链接与阅读</h2><p>蓝色链接指向已有条目，红色链接表示尚无独立页面。例如：<a class="redlink" title="页面尚未创建" href="'+base+'missing.html?title='+quote('尚未建立的主题')+'">尚未建立的主题</a>。这个示例用于说明链接状态。</p><p>正文上标编号跳到参考文献，向上箭头返回引用处。将焦点或鼠标停留在条目链接上可查看导言。</p><p>按页面别名查找，例如 <a href="'+base+'resolve.html?title=MTurk">MTurk</a>，会转到规范页面并保留重定向提示。</p>'),('missing.html','页面尚未创建','<p id="missing-title">这个主题暂时没有独立页面。</p><p>可通过顶部搜索查找相关论文与概念。</p>'),('resolve.html','查找页面','<p id="resolve-status">正在根据页面名或别名查找……</p>'),('404.html','未找到页面','<p>这个地址没有对应页面。请使用搜索或首页索引继续阅读。</p>')]:
        write(path,dict(id='',title=title,content=body,kind='导航',meta={'updated':'2026-11-01'},backlinks=[],field='站点导航',toc=''))
    search=[dict(id=p['id'],title=p['title'],aliases=p['aliases'],intro=p['intro'],url=base+p['path'],kind=p['kind'],field=p['field']) for p in allpages]
    (OUT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False))
    redirects={}; aliasdir=OUT/'aliases';aliasdir.mkdir()
    for p in allpages:
        for alias in p['aliases']:
            filename=hashlib.sha256(alias.encode()).hexdigest()[:20]+'.html'
            target=base+p['path']+'?from='+quote(alias,safe='')
            redirects[alias]=dict(target=p['id'],url=base+'aliases/'+filename)
            (aliasdir/filename).write_text(env.get_template('redirect.html').render(target=target,title=alias))
    (OUT/'redirects.json').write_text(json.dumps(redirects,ensure_ascii=False))
    (OUT/'.nojekyll').write_text('')
    check_site(base,pages)
    return pages

def check_site(base,pages):
    from html.parser import HTMLParser
    errors=[]
    class Parser(HTMLParser):
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            for key in ('href','src'):
                value=a.get(key,'')
                if not value or value.startswith(('#','https://','http://','mailto:','data:')):continue
                url=urlsplit(value)
                if not url.path.startswith(base):errors.append('Wrong base path: '+value);continue
                dest=OUT/unquote(url.path[len(base):])
                if dest.is_dir():dest=dest/'index.html'
                if not dest.exists():errors.append('Missing output: '+value)
    for f in OUT.rglob('*.html'):Parser().feed(f.read_text())
    graph=[dict(id=p['id'],title=p['title'],incoming=len(p['backlinks']),outgoing=len(p['outlinks']),redlinks=sorted(p['redlinks'])) for p in pages.values()]
    (OUT/'link-report.json').write_text(json.dumps({'base_url':base,'errors':errors,'pages':graph,'links':sum(x['outgoing'] for x in graph)},ensure_ascii=False,indent=2))
    if errors:raise ValueError('\n'.join(errors[:20]))
    print('Built',len(pages),'pages;',sum(x['outgoing'] for x in graph),'directed links; base',base,'; local links/resources verified.')

if __name__=='__main__':build()
