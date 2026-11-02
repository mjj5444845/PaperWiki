# -*- coding: utf-8 -*-
"""Validate saved independent evidence against current page snapshots, not article length."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 reg=json.loads((ROOT/'wiki/registry.json').read_text())['entities']
 nav=json.loads((ROOT/'qa/navigation-normalization.json').read_text())
 def current(pid,old,new):
  seen={old}
  for _ in range(len(nav)+1):
   for row in nav:
    if row['id']==pid and row['visible_prose_unchanged'] and row['before_sha256'] in seen:seen.add(row['after_sha256'])
  return new in seen
 def complete(audit,paths):
  return (set(x['item'] for x in audit['style'])==set(range(1,13)) and all(x['pass'] for x in audit['style'])
   and set(x['item'] for x in audit['antipatterns'])==set(range(1,8)) and all(x['pass'] for x in audit['antipatterns'])
   and set(x['path'] for x in audit['coverage'])==set(paths)
   and all(x['sections'] and not x['unverified'] for x in audit['coverage'])
   and set(x['path'] for x in audit['findings'])==set(paths)
   and all(x['verdict']=='supported' and x['reason'].strip() and x['source'].strip() and x['reason']!=x['path'] for x in audit['findings']))
 papers=[];concepts=[]
 for e in reg:
  pid=e['id'];page=ROOT/'wiki'/e['markdown_path'];hashed=sha(page)
  if e['type']=='论文':
   if pid not in ['P%02d'%i for i in range(1,26)]:continue
   f=ROOT/'qa/rewrite-audits'/(pid+'.json');d=json.loads(f.read_text()) if f.exists() else {}
   passed=bool(d.get('passed') and d.get('score',0)>=8 and current(pid,d.get('page_sha256',''),hashed) and complete(d['factcheck'],[e['markdown_path']]))
   papers.append({'id':pid,'title':e['canonical_name'],'sha256':hashed,'passed':passed,'score':d.get('score'),'report':str(f.relative_to(ROOT))})
  else:
   matches=[]
   for f in (ROOT/'qa/concept-audits').glob('*.json'):
    d=json.loads(f.read_text())
    if pid in d['ids'] and current(pid,d['page_hashes'].get(e['markdown_path'],''),hashed):matches.append((f.stat().st_mtime,f,d))
   if matches:
    _,f,d=max(matches,key=lambda x:x[0]);passed=complete(d['audit'],list(d['page_hashes']));report=str(f.relative_to(ROOT))
   else:passed=False;report=None
   concepts.append({'id':pid,'title':e['canonical_name'],'sha256':hashed,'passed':passed,'report':report})
 result={'papers':papers,'concepts':concepts,'paper_passes':sum(x['passed'] for x in papers),'concept_passes':sum(x['passed'] for x in concepts),'all_passed':all(x['passed'] for x in papers+concepts)}
 (ROOT/'qa/final-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Papers',result['paper_passes'],'/',len(papers),'Concepts',result['concept_passes'],'/',len(concepts))
 print('Pending:',', '.join(x['id'] for x in papers+concepts if not x['passed']))
 return result
if __name__=='__main__':main()
