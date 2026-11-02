# -*- coding: utf-8 -*-
"""Summarize real saved audits and immutable baselines; never infer a pass from length."""
import hashlib,json,re,statistics
from pathlib import Path
from depth_metrics import metrics_md
ROOT=Path(__file__).resolve().parents[1]
def main():
 from validate_depth import main as validate
 validation=validate()
 progress=json.loads((ROOT/'qa/depth-progress.json').read_text()) if (ROOT/'qa/depth-progress.json').exists() else {}
 reg=json.loads((ROOT/'wiki/registry.json').read_text());byid={e['id']:e for e in reg['entities']};before={x['id']:x for x in json.loads((ROOT/'qa/depth-baseline/papers-before.json').read_text())};rows=[]
 nav=json.loads((ROOT/'qa/navigation-normalization.json').read_text()) if (ROOT/'qa/navigation-normalization.json').exists() else []
 def lineage(pid,old,new):
  seen={old}
  for _ in range(len(nav)+1):
   for r in nav:
    if r['id']==pid and r['visible_prose_unchanged'] and r['before_sha256'] in seen:seen.add(r['after_sha256'])
  return new in seen
 for i in range(1,26):
  pid='P%02d'%i;e=byid[pid];p=ROOT/'wiki'/e['markdown_path'];m=metrics_md(p);m['id']=pid;m['title']=e['canonical_name'];m['old_words']=before[pid]['words'];m['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  f=ROOT/'qa/rewrite-audits'/(pid+'.json')
  if f.exists():
   a=json.loads(f.read_text());current=lineage(pid,a['page_sha256'],m['sha256']);m.update(score=a['score'],passed=a['passed'] and current,audit_status='通过' if a['passed'] and current else '修订后待复核' if not current else '待修订',audit_page_sha256=a['page_sha256'])
  else:m.update(score=None,passed=False,audit_status='待复核')
  raw=p.read_text();front,body=raw.split('---',2)[1:];orig=set(re.findall(r'https://doi\.org/([^\s)]+)',front));docs=set()
  for line in body.splitlines():
   if not re.match(r'^\[\^[^]]+\]:',line):continue
   urls=re.findall(r'https?://[^\s)\]>]+',line)
   doi=re.findall(r'https://doi\.org/([^\s)]+)',line)
   if doi and any(d in orig for d in doi):continue
   if urls:docs.add('doi:'+doi[0] if doi else urls[0].rstrip('。，；'))
  m['non_original_documents']=len(docs);m['non_original_document_keys']=sorted(docs);rows.append(m)
 conceptrows=[];origconcept={x['id']:x for x in json.loads((ROOT/'qa/depth-baseline/concepts-before.json').read_text())}
 for e in reg['entities']:
  if e['type']=='概念':
   m=metrics_md(ROOT/'wiki'/e['markdown_path']);m['id']=e['id'];m['title']=e['canonical_name'];m['old_words']=origconcept.get(e['id'],{}).get('words',0);conceptrows.append(m)
 output=ROOT/'qa/depth-baseline';(output/'papers-after.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(output/'concepts-after.json').write_text(json.dumps(conceptrows,ensure_ascii=False,indent=2)+'\n')
 passed=sum(r['passed'] for r in rows);phase='验收完成' if passed==25 and validation['all_passed'] else '验收中'
 text=['# 论文与概念深度重写报告（'+phase+'）','','工作分支：`depth-rewrite-pilot`。用户已确认三篇试点并批准继续全量。本文根据原始基线、实际页面快照与保存的独立审校记录生成；尚未闭环的稿件不记通过。','','## 规模与计数口径','',f'- 原25篇论文全部重写；原87个概念重写，并增建皮尔逊相关系数，共{len(conceptrows)}个概念。另有此前收件箱测试留下的LIME、SHAP两论文页，本次不计入原25篇。',f'- 原25篇正文中位数{statistics.median(r["old_words"] for r in rows):g}单位，新稿{statistics.median(r["words"] for r in rows):g}单位；当前内容验收通过{passed}/25。','- 一个汉字、英文词或数字为一个正文单位，排除YAML、参见和参考文献；不是文件总字符数。篇幅没有硬性及格线。','- “原论文之外文档”按脚注中的独立DOI/网址去重，排除当前原论文；包括本站其他论文，一份文档的多个入口仍可能计为多项，因此同时公开文档键供复查，不冒称纯二手来源数。','','## 25篇论文逐页记录','','| ID | 标题 | 旧单位 | 新单位 | 新汉字 | 表格 | 引用标记 | 非原论文文档 | 盲读 | 状态 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
 for r in rows:text.append('| '+r['id']+' | '+r['title'].replace('|','／')+' | '+' | '.join(str(r[k]) for k in ['old_words','words','han','tables','citations','non_original_documents'])+' | '+str(r['score'] if r['score'] is not None else '—')+'/10 | '+r['audit_status']+' |')
 text+=['','## 独立验收协议与修订记录','','三篇试点保留已交给用户的原始盲读与独立事实核对记录；用户确认后，25篇均追加独立临时进程分工的验收：原文出题者只收到全文，不见草稿；读者只收到新页面与问题；阅卷者对照原文；另一事实角色读取全文、PDF页图及实际打开的外部资料。读者至少8/10，12项风格、7反模式及事实错误全部闭环才通过。','','早期部分精读笔记较压缩，定稿后已把实际独立全文核对的论断、出处与理由补入私有笔记，明确标为事后补充，不冒称初稿前形成。作者题的冻结时点不全部可证明，故保留作者题，重新由未看草稿的原文出题者生成验证题。这些验证题在修订与复测中保持不变；原PDF断词、连字及页码造成的引文索引错误仅修正定位或缩为真实逐字片段，不修改题目及答案要点。原始输出和修复记录保留在忽略上传的state/logs/。不得把这项补救说成所有作者题都在初稿前冻结。','','逐题原始答案、评分理由、逐项事实结论与历史轮次见`qa/rewrite-audits/`；概念审校见`qa/concept-audits/`。作者修订说明见`qa/rewrite-*-author.md`和`qa/concepts-*-author.md`，作者自查不替代独立审校。历史目录也包含后来被原文推翻的审校建议（例如ESP确认阈值），不代表均已接受；以当前快照的最终核对为准。首链规范化和未用脚注删除保留哈希转换链，验证可见正文不变；事实与表述变化重新审校。','','已发现并处理的问题包括：遗漏核心机制及实验条件、把访谈次数当身份分组的风险、把任务刺激声称的80%当实测精度、混淆解释使用和观影决定的分母、公式转义控制字符、图内数字提取缺失、引文物理页/章节定位和评价归属。具体修正以各轮原始报告为准，未将来源访问失败一律算成事实错误。','','## 明确的资料边界','','P15取得并阅读全文19页版本及附录，原13页缓存未被误当完整版本。P16正文引用独立补充材料，但本次未取得该补充文件；正文及可得材料已读，不能宣称补充文件已核实，也不据未取得材料补写细节。多数原论文实验未重新实施，原始参与者记录没有另行取得。','','## 自动收件流程','','入口改为：全文及逐页图像精读与私有笔记→冻结十题→抽取索引与实体增量→含外部来源的深度写作→独立盲读→独立阅卷→独立事实和反模式检查→构建及发布。读者隔离原文、答案、网络和项目文件；事实角色重新查阅外源。评分不足8、未核事实、未完成检查或验收后内容改变均停止发布，进入待复核。','','实际负例集成：一份自动候选仅6/10被拦；加入图像与覆盖要求后的候选为8/10，但仍有未修正论断/归属问题，被事实门槛拦住。二者均未提交或推送。已审定稿的后续验收集成另记录，不将其冒称为自动作者成功生成新稿。','',('构建、链接、浏览器和部署最终结果另见`qa/report.md`、`qa/deployment.md`。新版本已发布；原12小时收件箱任务沿用更新后的门槛，本机载入状态用调度status命令查看。' if progress.get('published') else '构建、链接、浏览器和部署最终结果另见`qa/report.md`、`qa/deployment.md`。在全部内容验收及部署完成之前，旧自动发布任务保持暂停。')]
 text+=['','## 概念逐页篇幅与独立验收','',f'当前概念通过{validation["concept_passes"]}/{len(conceptrows)}。此项由当前文件SHA-256、保留的规范化转换链及最新对应审校记录核对，不按字数判通过。','','| ID | 概念 | 旧单位 | 新单位 | 状态 |','|---|---|---:|---:|---|']
 conceptstatus={x['id']:x for x in validation['concepts']}
 for r in conceptrows:
  a=conceptstatus[r['id']];text.append('| '+r['id']+' | '+r['title']+' | '+str(r['old_words'])+' | '+str(r['words'])+' | '+('通过' if a['passed'] else '待闭环')+' |')
 corrections={
 'P01':'补足Xerox过程理由文档及访谈构成；移除编辑指令。',
 'P02':'补共享反馈机制与观察出处；纠正Discussion页段并核对关联论文DOI。',
 'P03':'区分期刊版案例节名，去除不存在的4.2节号与无依据外推。',
 'P04':'补网络项完整公式，区分线程深度系数与相对效用的显著性。',
 'P05':'补完整分类与复杂度数据；纠正逐手势评分和手数偏好的时间顺序。',
 'P06':'补各实验设置与指标，限定midmean和bootstrap的适用实验。',
 'P07':'展开六种设计质量、STS双向作用与具体性别案例。',
 'P08':'修正研究二统计比较基准，补研究四混合赞扬与批评条件。',
 'P09':'补Allen五人反向证据、其他计分方法、隐藏评分评价及群体变化。',
 'P10':'将6/7明确为访谈执行者分工，避免写成参与者身份分组。',
 'P11':'区分请求公开许可与已获许可，移除无直接支持的身份设计动机。',
 'P12':'以未报告区别于断言未进行，保留资料边界并展开原型案例。',
 'P13':'区分自拟示例与访谈实例，纠正人物亲属关系及API出处。',
 'P14':'补完整伦理框架，区分实践分类与已验证效果。',
 'P15':'阅读全文19页版本及附录，补清晰度图、演变与比较表。',
 'P16':'工具怀疑数改为1/46；补理解分布、能力选项及44分钟排除离群值条件。',
 'P17':'补完整能力框架和九类伦理议题，核对后续报告作者归属。',
 'P18':'区分编码演变的原文结论与无直接支持的过早冻结推论。',
 'P19':'修正词表阈值为100个片段及聚类计数，补完整类型和偏差框架。',
 'P20':'区分作者跨路径归纳与全体受访者表态，去除自行删改标签的拼接行为。',
 'P21':'区分合并SXAI与单个条件、模拟AI刺激和实测表现，核对外部元分析书目。',
 'P22':'区分解释查阅和观影决定计数；去除原例未说的独自观影情节。',
 'P23':'移除无来源的删除功能动机及实验室噪声比较，补分国部署出处。',
 'P24':'补表3个体差异、有效性与误报讨论，明确多人结果来自模拟聚合。',
 'P25':'区分已实现机制与未来建议，避免把作者括号中的时长换算当独立记录。'}
 text+=['','## 逐篇修订要点','']
 for r in rows:text.append('- '+r['id']+'：'+corrections[r['id']]+' 独立成绩'+str(r['score'])+'/10；当前'+r['audit_status']+'。')
 text+=['','## 审校工具修订与测试边界','','发现审校JSON路径约束与其他字符串字段共享对象，导致若干旧输出只剩文件名。已修正为独立路径字段并加入回归测试；此类无具体理由输出不作为通过证据，保留于历史目录。Crossref仅选择原始书目字段，去除庞大的参考文献数组；大组拆分，不允许截断后冒称全文核对。','','全文定位修复只允许选择同页真实片段，不改冻结问题或答案；无法定位仍阻止发布。另有自动P24候选因OCR引文定位或阶段输出失败被拦。当前没有把这些负例描述为成功的自动新论文发布。28项单元测试覆盖门槛、审校后篡改、漏审文件、锁及清理，三个BASE_URL构建均通过。','','P24所提另一篇配套论文附录本次未取得；本页原论文本身已读全，未将该附件内容冒充已核。']
 (ROOT/'qa/rewrite-report.md').write_text('\n'.join(text)+'\n');print(phase,passed,'/25')
if __name__=='__main__':main()
