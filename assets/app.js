'use strict';
const base = document.documentElement.dataset.base;
let entries;
const getIndex = () => entries ||= fetch(base+'search-index.json').then(r=>{if(!r.ok)throw Error('索引加载失败');return r.json()});
const params = new URLSearchParams(location.search);
const from = params.get('from');
if(from){const n=document.querySelector('#redirect-notice');n.textContent='（重定向自 '+from+'）';n.hidden=false;}
if(location.pathname.endsWith('/missing.html')) document.querySelector('#missing-title').textContent='“'+(params.get('title')||'该主题')+'”页面尚未创建。';
if(location.pathname.endsWith('/resolve.html')) getIndex().then(list=>{const q=(params.get('title')||'').toLocaleLowerCase();const p=list.find(e=>[e.title,...e.aliases].some(a=>a.toLocaleLowerCase()===q));if(p)location.replace(p.url+'?from='+encodeURIComponent(params.get('title')));else document.querySelector('#resolve-status').textContent='没有找到这个页面名或别名，请使用搜索。'}).catch(()=>document.querySelector('#resolve-status').textContent='页面索引加载失败，请返回首页。');
const search=document.querySelector('#search-input'),results=document.querySelector('#search-results');
let sequence=0;
async function runSearch(){const seq=++sequence,q=search.value.trim().toLocaleLowerCase().normalize('NFKC');if(!q){results.hidden=true;return;}try{const list=await getIndex();if(seq!==sequence)return;const scored=list.map(e=>{const title=e.title.toLocaleLowerCase().normalize('NFKC'),aliases=e.aliases.map(a=>a.toLocaleLowerCase().normalize('NFKC'));return {e,score:title===q?100:aliases.includes(q)?95:title.includes(q)?80:aliases.some(a=>a.includes(q))?70:e.intro.toLocaleLowerCase().includes(q)?20:0}}).filter(x=>x.score).sort((a,b)=>b.score-a.score).slice(0,14);results.replaceChildren();for(const {e} of scored){const a=document.createElement('a');a.href=e.url;const title=document.createElement('strong');title.textContent=e.title;const detail=document.createElement('small');detail.textContent=e.kind+' · '+e.intro.slice(0,90);a.append(title,detail);results.append(a);}if(!scored.length){const p=document.createElement('p');p.textContent='没有匹配的页面。试试中文术语、英文题名或别名。';results.append(p);}results.hidden=false;}catch(e){results.textContent='搜索索引加载失败，请刷新后重试。';results.hidden=false;}}
search.addEventListener('input',runSearch);
document.querySelector('#search-form').addEventListener('submit',e=>{e.preventDefault();runSearch()});
search.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();results.querySelector('a')?.focus()}if(e.key==='Escape')results.hidden=true});
results.addEventListener('keydown',e=>{const links=[...results.querySelectorAll('a')],i=links.indexOf(document.activeElement);if(e.key==='ArrowDown'){e.preventDefault();links[(i+1)%links.length]?.focus()}if(e.key==='ArrowUp'){e.preventDefault();if(i<=0)search.focus();else links[i-1].focus()}if(e.key==='Escape'){results.hidden=true;search.focus()}});
document.addEventListener('click',e=>{if(!e.target.closest('.search'))results.hidden=true});
document.querySelector('#menu-toggle').addEventListener('click',e=>{const open=document.querySelector('#sidebar').classList.toggle('open');e.currentTarget.setAttribute('aria-expanded',String(open))});
document.querySelector('#theme-toggle').addEventListener('click',()=>{const root=document.documentElement;const dark=root.dataset.theme==='dark'||(root.dataset.theme!=='light'&&matchMedia('(prefers-color-scheme:dark)').matches);root.dataset.theme=dark?'light':'dark';try{localStorage.setItem('paperwiki-theme',root.dataset.theme)}catch(e){}});
document.querySelector('#random-page').addEventListener('click',()=>getIndex().then(list=>location.assign(list[Math.floor(Math.random()*list.length)].url)));
const preview=document.querySelector('#page-preview');let timer,active=null;
function hidePreview(){clearTimeout(timer);active=null;preview.hidden=true;}
document.querySelectorAll('a.internal[data-page]').forEach(link=>{
 const show=()=>{clearTimeout(timer);active=link;timer=setTimeout(async()=>{try{const p=(await getIndex()).find(x=>x.id===link.dataset.page);if(!p||active!==link)return;const t=document.createElement('strong');t.textContent=p.title;const body=document.createElement('p');body.textContent=p.intro.slice(0,260);preview.replaceChildren(t,body);preview.hidden=false;const r=link.getBoundingClientRect();preview.style.left=Math.max(12,Math.min(innerWidth-preview.offsetWidth-12,r.left))+'px';preview.style.top=Math.max(12,Math.min(innerHeight-preview.offsetHeight-12,r.bottom+8))+'px';}catch(e){}},300)};
 link.addEventListener('mouseenter',show);link.addEventListener('focus',show);link.addEventListener('mouseleave',hidePreview);link.addEventListener('blur',hidePreview);
});
addEventListener('scroll',()=>{if(active!==document.activeElement)hidePreview()},{passive:true});
if(window.renderMathInElement)document.querySelectorAll('.prose').forEach(element=>renderMathInElement(element,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false}],throwOnError:false}));
