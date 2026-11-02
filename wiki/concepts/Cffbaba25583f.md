---
id: Cffbaba25583f
title: 情境意识
aliases:
- situational awareness
type: 概念
field: 人机智能交互
created: '2026-11-01'
updated: '2026-11-01'
---

**情境意识**（situational awareness，SA）是对当前情境中相关要素、它们的意义及可能发展的理解。在《[[A Taxonomy for Characterizing Modes of Interactions in Goal-driven, Human-robot Teams|目标驱动的人机团队交互模式分类体系]]》援引的框架中，它分为感知、理解和预测三个逐渐复杂的层次，用于分析协作者需要掌握什么信息才能判断和行动。它并不等同于接收了多少数据。[^auto1]

## 从观察到预测

感知层关注相关要素的状态和变化；理解层把这些信息放进当前目标与任务中，形成对局势的解释；预测层则涉及接下来可能发生什么。三层区分使“看见信息”与“知道它意味着什么”能够分别讨论。Parashar等人同时介绍了情境意识驱动的代理透明性模型SAT：该模型将任务描述和所需知识结构用于定性组织这些层次。论文并没有因此提出一套新的情境意识测量工具。[^auto1]

例如，搜救成员发现一段通道发生变化、理解这一变化对当前搜索路线的意义，再判断原计划是否仍可执行，分别涉及不同层次。这是依据论文场景整理的说明性例子，不能作为该论文测得的认知过程或实验结果。[^case]

情境意识还涉及对队友的了解。成员可能知道环境里发生什么，却不知道队友的目标、计划或任务进度；也可能知道计划，却无法观察队友所处空间。因而，物理上接近与远程协作所需补充的信息不同。[^auto2]

## 与心智模型和信息需求的关系

[[心智模型]]可以为解释信息提供线索，但在Parashar等人的框架中，角色只是一种推断成员知识和专长的依据，不能替代精确的信息需求描述。作者提出，要在线适配通信内容，需要知道特定角色已经了解什么、缺少什么，以及哪些细节与当前议题有关。[^auto2]

作者区分两类情境信息。物理情境性涉及彼此对环境的感知，认知情境性涉及彼此目标、计划和任务状态。近距离成员可能直接取得部分物理线索；远程成员则需要交换两类信息，不能假定队友已经看到相同环境。[^auto2]

## 在人机团队分类框架中的应用

《A Taxonomy for Characterizing Modes of Interactions in Goal-driven, Human-robot Teams》在“结果效应”的信息抽象模块使用情境意识，分析消息应具体到何种程度。其机制是先考虑接收方的角色和知识，再结合空间关系、目标和任务依赖，判断哪些更新有助于当前决策。依赖较强时，相关更新可以更细；但无关细节仍可能增加信息负担。[^auto2]

城市搜救说明这一模块怎样工作：成员分布在较大范围，对环境和队友都只有有限观察，因此需要交换空间、事件和自身状态。环境地图是否已有、地图包含哪些语义或物理知识，也会改变需要补充的内容。这里情境意识不是给界面增加一个状态面板，而是用于分析各成员之间具体缺失的知识。[^case]

## 远程操作中的发展与边界

2021年的远程自动驾驶研究讨论了一个更具体的难题：操作者可能临时接入陌生车辆的情境，没有此前持续积累的现场理解。研究由此讨论脱离控制回路、通信延迟、具身线索和工作负荷对情境意识的挑战。增加信息也会增加处理负担，因此不能用消息数量代替对理解的支持。该研究提供相关问题的发展实例，不构成对Parashar分类体系的验证。[^remote]

Parashar等人认为，还需要把情境意识评估扩展到任务、团队和环境三个组成部分，并为角色变化建立更明确的知识要求。其论文没有给出完整量表、测量程序或“足够情境意识”的数值阈值；不能把分类框架直接当作评估工具。[^future]

## 参见

- [[A Taxonomy for Characterizing Modes of Interactions in Goal-driven, Human-robot Teams]]
- [[机器人自主程度]]
- [[心智模型]]

## 参考文献

[^auto1]: Priyam Parashar、Lindsay M. Sanneman、Julie A. Shah、Henrik I. Christensen。[A Taxonomy for Characterizing Modes of Interactions in Goal-driven, Human-robot Teams](https://doi.org/10.1109/IROS40897.2019.8967974)。PDF物理第4页，第II-B1节。
[^auto2]: 同上，PDF物理第7页，第V-C2节。
[^case]: 同上，PDF物理第4页第III-A节及物理第8页第VI节。
[^future]: 同上，PDF物理第8—9页，第VI节。
[^remote]: [Updating our understanding of situation awareness in relation to remote operators of autonomous vehicles](https://link.springer.com/article/10.1186/s41235-021-00271-8)，2021，远程操作者讨论、“SA demons for ROs”及“Workload issues for ROs”。
