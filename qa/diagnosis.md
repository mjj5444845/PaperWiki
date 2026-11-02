# 论文页面深度诊断

本报告在修改任何论文页之前生成。基线分支起点为 `a4a74c1`；统计 27 篇现有论文，原始范围为 P01–P25，另两篇为收件箱测试新增论文。后续试点仅改 P01、P09、P24。

## 统计口径

- 正文计数单位：一个汉字算 1 个单位；一个英文词或连续数字算 1 个单位。另保存纯汉字数。它不是英文分词意义的 word count，也不是阅读质量评分。
- 两类文本均排除书目、参见及导航。论文去掉 YAML 与脚注标记；维基从保存的 wikitext 去掉 ref、math、图片及模板后提取正文，避免 TextExtracts 将公式重复展开而虚增长度。原纯文本另用于审读。
- 章节数包含二级以下标题及参见/参考等栏目；具体数字是正文数值出现次数，不等于独立实验结果数。年份、参数、常数也会计入，不以数量替代解释。
- 表格只计显式 Markdown/wikitext 表格，不含模板生成的信息框；脚注为调用次数，不是不同来源数量。
- 论文外部来源数按去重 URL；标杆按去重的具名 cite/citation 书目条目（含无 URL 的书籍）。存在裸 ref 等遗漏，因此是可复现的来源下界，不能把二者当完全等价的书目总数。
- 来源类型人工审读每篇首 6 个不同书目及其引用用途，共 72 条；P=原始记录/原研究/官方自述，S=教材/综述/历史或独立报道，U=材料不足或混合用途。没有把所有期刊都判成一手，或把所有机构页面判成二手；此为样本引用用途分类，没有重新验证这些来源的全部事实。

## 整体对比

| 集合 | 篇数 | 正文单位中位数 | 章节中位数 | 数值中位数 | 表格中位数 | 脚注调用中位数 | 来源下界中位数 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 原始论文 | 25 | 498 | 8 | 16 | 1 | 14 | 1 |
| 现有全部论文 | 27 | 500 | 8 | 16 | 1 | 14 | 1 |
| 科技类标杆 | 12 | 6049.5 | 26.5 | 80.5 | 0.0 | 77.0 | 49.0 |

## 现有论文逐篇统计

| ID | 标题 | 正文单位 | 章节 | 数值 | 表格 | 引用 | 外部来源URL |
|---|---|---:|---:|---:|---:|---:|---:|
| P01 | Research Through Design as a Method for Interaction Design Research in HCI | 445 | 8 | 10 | 1 | 13 | 1 |
| P01c7aa8f7d9e | A Unified Approach to Interpreting Model Predictions | 1434 | 9 | 21 | 1 | 24 | 2 |
| P02 | Awareness and Coordination in Shared Workspaces | 474 | 8 | 7 | 1 | 13 | 1 |
| P03 | Learning from Notes: Organizational Issues in Groupware Implementation | 429 | 8 | 10 | 1 | 11 | 1 |
| P04 | Predicting Tie Strength With Social Media | 498 | 8 | 14 | 1 | 15 | 1 |
| P05 | User-Defined Gestures for Surface Computing | 525 | 8 | 21 | 1 | 15 | 1 |
| P06 | Crowdsourcing Graphical Perception: Using Mechanical Turk to Assess Visualization Design | 617 | 8 | 24 | 1 | 17 | 1 |
| P07 | Feminist HCI: Taking Stock and Outlining an Agenda for Design | 454 | 8 | 4 | 1 | 12 | 1 |
| P08 | Computers are Social Actors | 524 | 8 | 24 | 1 | 13 | 1 |
| P09 | GroupLens: An Open Architecture for Collaborative Filtering of Netnews | 470 | 8 | 11 | 1 | 14 | 1 |
| P10 | Hollaback!: The Role of Collective Storytelling Online in a Social Movement Organization | 470 | 8 | 12 | 1 | 14 | 1 |
| P11 | Turkopticon: Interrupting Worker Invisibility in Amazon Mechanical Turk | 470 | 8 | 9 | 1 | 15 | 1 |
| P12 | Tangible Bits: Towards Seamless Interfaces between People, Bits and Atoms | 431 | 8 | 5 | 1 | 13 | 1 |
| P13 | “I always assumed that I wasn’t really that close to [her]”: Reasoning about Invisible Algorithms in News Feeds | 493 | 8 | 16 | 1 | 14 | 1 |
| P14 | The Dark (Patterns) Side of UX Design | 458 | 8 | 9 | 1 | 12 | 1 |
| P15 | Guidelines for Human-AI Interaction | 500 | 8 | 28 | 1 | 16 | 1 |
| P16 | Interpreting Interpretability: Understanding Data Scientists’ Use of Interpretability Tools for Machine Learning | 578 | 8 | 19 | 1 | 16 | 1 |
| P17 | What is AI Literacy? Competencies and Design Considerations | 432 | 8 | 13 | 1 | 12 | 1 |
| P18 | Reliability and Inter-rater Reliability in Qualitative Research: Norms and Guidelines for CSCW and HCI Practice | 504 | 8 | 29 | 1 | 15 | 1 |
| P19 | Dark Patterns at Scale: Findings from a Crawl of 11K Shopping Websites | 541 | 8 | 26 | 1 | 16 | 2 |
| P20 | “Everyone wants to do the model work, not the data work”: Data Cascades in High-Stakes AI | 554 | 8 | 25 | 1 | 16 | 1 |
| P21 | To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making | 683 | 8 | 16 | 1 | 14 | 1 |
| P22 | Explaining Collaborative Filtering Recommendations | 500 | 8 | 20 | 1 | 16 | 1 |
| P23 | Technology Probes: Inspiring Design for and with Families | 496 | 8 | 8 | 1 | 14 | 1 |
| P24 | Heuristic Evaluation of User Interfaces | 529 | 8 | 19 | 1 | 13 | 1 |
| P25 | Labeling Images with a Computer Game | 567 | 8 | 27 | 1 | 15 | 1 |
| P365079753571 | “Why Should I Trust You?” Explaining the Predictions of Any Classifier | 1722 | 9 | 51 | 1 | 29 | 3 |

## 12 篇科技标杆

这些条目均来自 sampling/sample.csv 的既有抽样，不是另搜更长的页面。样本中缺乏足量算法/学术著作，因此补以工程、硬件和网站机制条目；不能据此规定论文必须达到这些主题的总篇幅。

| 标杆 | 正文单位 | 章节 | 数值 | 表格 | 脚注调用 | 具名来源下界 | 数学标签 | P/S/U（各抽6） |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 馬克士威方程組 | 8247 | 27 | 37 | 4 | 83 | 34 | 213 | 1/5/0 |
| 量子场论 | 13720 | 28 | 72 | 0 | 67 | 58 | 78 | 1/4/1 |
| 旋度 | 2612 | 12 | 9 | 0 | 11 | 9 | 115 | 1/5/0 |
| 三角函数 | 5421 | 29 | 39 | 8 | 41 | 23 | 272 | 0/6/0 |
| DNA纳米技术 | 6450 | 20 | 38 | 0 | 126 | 73 | 0 | 3/3/0 |
| 電機工程學 | 7890 | 18 | 71 | 0 | 55 | 52 | 0 | 2/4/0 |
| PowerBook 100 | 3662 | 11 | 185 | 1 | 85 | 46 | 0 | 0/3/3 |
| 百萬美元首頁 | 2364 | 8 | 89 | 0 | 71 | 38 | 0 | 2/3/1 |
| 2channel | 5649 | 29 | 268 | 0 | 240 | 117 | 0 | 3/2/1 |
| 坎尔井地下水利工程 | 14103 | 45 | 398 | 0 | 201 | 65 | 0 | 5/1/0 |
| 阿波罗17号 | 12128 | 29 | 361 | 0 | 226 | 93 | 0 | 2/4/0 |
| 菱形十二面體 | 3603 | 26 | 156 | 14 | 57 | 31 | 19 | 1/5/0 |

72 条用途抽核：一手 21/72（29.2%），二手 45/72（62.5%），未定 6/72（8.3%）。分母为分层定额抽核的 72 条，不推断全部书目的总体比例。详见 depth-baseline/source-audit.json。

## 标杆如何回答读者问题

| 条目 | 章节回答的具体问题与解释次序 | 背景、评价与来源分工 |
|---|---|---|
| 馬克士威方程組 | 四条定律分别约束什么；积分/微分形式如何对应；变量、物质响应及适用边界是什么。先解释物理现象，再给符号与形式。 | 原始 Maxwell 论文用于历史；Griffiths、Jackson 等教材解释标准理论，不把作者原话当唯一现代解释。 |
| 量子场论 | 为什么经典场不够；怎样从经典场走向量子化；两种表述、费曼图和重整化分别解决什么问题。 | 历史脉络与理论背景分开；教材、学科史与原始文献并用，具体新成果归属给研究者。 |
| 旋度 | 为什么先需要环量；局部旋转如何定义；不同坐标下怎么计算；两个例子如何解释正负与方向。 | 数学教材支撑定义及推导，早期记录支撑术语历史。不是先甩公式再省略解释。 |
| 三角函数 | 三角形、坐标系、单位圆三个定义各扩展了什么；如何计算；恒等式和应用定理怎样连接。 | 教材与数学史承担不同任务；公式、特殊值表、几何例子互补。 |
| DNA纳米技术 | 为什么碱基互补能成为工程材料；目标结构、二级结构与序列设计怎样依次完成；拼接、折叠、动态组合各有何差别。 | 原始实验支持具体结构，综述解释研究方向、应用和局限。并不以“提出某方法”替代步骤。 |
| 電機工程學 | 领域如何形成；子领域研究什么；仪器、教育和职业实践如何相关。 | 历史介绍、工程机构自述与原始会议记录有不同角色，规模数据附时代。 |
| PowerBook 100 | 为何做出这些硬件/外形选择；各部件如何形成便携体验；发布、评价与后续位置是什么。 | 产品事实与媒体评价分列，体验结论注明评测主体，不把规格表当整篇文章。 |
| 百萬美元首頁 | 像素怎样出售；最小购买单元与收入目标如何相关；传播和攻击怎样改变运作。 | 官方/站点统计支持自家事实，独立报道交代外部反响；背景与实际运行相接。 |
| 2channel | 板块、讨论串、推上/压下及匿名性如何运作；制度怎样影响使用与争议。 | 运营方、法院记录与媒体、学术分析分别支撑制度、事件和评价。 |
| 坎尔井地下水利工程 | 水从哪里来；竖井、暗渠、明渠和蓄水池分别做什么；为何适合当地；哪些病害会破坏运作。 | 起源争论按学者归属，工程组成结合自然条件解释；政策原文与研究结论分开。 |
| 阿波罗17号 | 为何选择该着陆点；每件仪器测什么；任务如何分阶段完成；采样和实验怎样连接科研目标。 | NASA 记录用于任务数据，任务史与后续研究交代背景和位置，不用成果数量替代过程。 |
| 菱形十二面體 | 面、边、顶点与对称性意味着什么；怎样构造/堆砌；坐标、面积体积与应用如何联系。 | 数学参考书与原研究分工；正文/导言还可能存在表述差异，样本不是科学事实的免检权威。 |

### 解释方式的比例与边界

- 12/12 条目均有具体对象、案例、构造或运行实例，而不只罗列名称；这是对以上章节的人工编码，不是对每一句的可靠性背书。
- 数学公式的量化以表中 math 标签计数为准；技术机制条目即使没有公式，也可通过组成、步骤、条件和实例讲清楚。各方式可重叠，因此不制造相加等于 100% 的“公式/例子比例”。
- 12/12 均有背景或发展脉络；影响/评价应按主题选择，不能把政治或产品评价的目录机械套给数学定义。

## 根因定位

### 抽取源头已经丢掉了核心信息

- P24 的 core_method 只有 2 条。全文表1列出 9 条启发式原则，JSON 没有逐条记录；4 个系统被压进一个 data_and_participants 字段，未写明视频图文、虚构查询界面、银行语音系统和公交语音系统的区别。
- P01 的结果字段只写“形成4项评价标准”，没有完整解释过程、发明、相关性和可扩展性如何判断；模型中的跨学科输入、设计产物及三个案例的评估逻辑被压缩。
- P09 只写相关系数和加权预测，未保留评分矩阵、均值校正、分布式评分协议、假名机制以及容量估算前提。4.56/3.75 没有流程解释就变成不可理解的数字。

### 作者程序确实把 JSON 逐字段输出，没有在写页面时回到全文

- scripts/author_wiki.py:118–143 的输入是 ds[ID]；导言直接复制 core_method[0]，背景复制 research_question，方法逐条复制 core_method，结果逐条塞表格。程序没有读取 extract/sources/ 全文的路径。
- 这能证明写作程序没有利用全文；不能据此断言此前完全无人读过论文。原全文缓存存在，早期笔记也有页码，但其压缩格式不足以支持深写。
- 概念应用栏复用每篇 core_method[0]，因而解释的是论文总体方法，而非概念在该论文中的具体作用。
- automation/content.py 后来的增量流程同样由字段数组拼章节，虽有引文定位、数字校验和更完整事实，仍缺少独立读者测验与事实复核，也没有外部研究环节。

### skill 没有字数上限，但缺少深度门槛

- 已安装 SKILL.md、通用规则和引用指南没有要求“每句一注”，也没有禁止网络补充来源；原规则明确引文密度不是质量分数，段落可以合并引用。不能把缺陷归咎于不存在的约束。
- G7“枝节克制”、G11“章节为内容服务”在缺少读者问题和核心内容清单时，容易被实现者误用为压缩理由。规范需要补上完整机制、边界、实例和外部发展要求。
- 上一任务的“论文未写不得补充”本来用于防止编造论文事实；实现将它过度扩展成几乎只用原论文。背景、影响与外部批评应分层取材，不能假装原作者能独立证明全部后续影响。

## 改进方案与试点验收

1. 全文（含附录）→逐节精读笔记→核心内容覆盖表→10个读者问题→外部来源研究→连贯写作，原 JSON 只作索引。
2. skill 新增 depth-standard.md、论文/概念模板；简洁指无废话，不是删核心信息。不设字数上限，4000–8000 字仅为论文的参考范围。
3. 启发式评估试点完整解释 1990 年的9条原则，不把1994年修订的10条倒写进原文；列出4个系统、参与者、分母、个人与模拟集合结果、解释和局限。
4. P01、P09 分别验证方法论与系统论文的适配；不是强塞消融实验，缺失栏目及理由记录在 notes/ 中，不把编辑说明塞入百科正文。
5. 独立读者 agent 只读新页面答题；另一事实 agent 对照原文与外部材料，分别留记录。最低8/10；错误未修正不能通过。
6. 试点只在 depth-rewrite-pilot 分支本地预览，用户确认后再做其余22篇、概念全量重写及自动发布门槛升级；本阶段不合并 main。收件箱调度暂停，避免跨分支自动写入。

## 复现

`python tools/depth_metrics.py`（研究依赖 mwparserfromhell 0.7.2）；输入 sampling/sample.csv、raw/ 和 wiki/；首次基线保存在 qa/depth-baseline/*-before.json。原始来源分类候选在 notes/，抽核摘要在 source-audit.json。重写后不覆盖首次基线。
