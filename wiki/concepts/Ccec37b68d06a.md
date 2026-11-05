---
id: Ccec37b68d06a
title: 认知反馈
aliases:
- cognitive feedback
type: 概念
field: 人类与机器人交互
created: '2026-11-05'
updated: '2026-11-05'
---

认知反馈（cognitive feedback）是在任务执行或失败后提供澄清、程序提示、解释和纠正建议，以帮助接收者更新任务理解并决定下一步行动的反馈。在人类与机器人协作中，它可以说明正在发生什么、哪些操作需要调整及怎样继续；其效果须结合信息准确性、交付方式和接受者需要考察。[^auto1]

## 从状态说明到行动调整

认知反馈把任务状态与下一步操作连接起来：先提供对失败或当前状况的说明，再帮助人调整对目标、顺序或策略的理解，最后给出可执行的纠正方向。它针对信息与程序问题；[[情感反馈]]则主要回应挫败、自责和关系需要。两种作用可以出现在同一段话中，区分的是支持的功能，而非是否使用自然语言。[^auto1]

“说明原因”与“给出下一步”也并不相同。前者帮助理解为何出现偏差，后者帮助选择行动。Kim等人的认知反馈条件将分析与具体纠正策略合在一起，没有分别比较只给状态、只给操作提示或说明理由的效果，因此结果支持的是整个处理方案，不能确定哪类信息是必要成分。[^auto2][^limits]

Honig与Oron-Gilad的RF-HIP模型把失败沟通、感知与理解、解决划分为不同环节。这为认知反馈提供了背景：信息被给出，并不保证人已经发现问题或能完成修复。该框架不是Kim实验中实际运行的反馈生成算法。[^failure]

## 内容与表达方式

任务建议还有社会表达后果。Torrey等人的人类与机器人视频实验发现，加入缓和语或话语标记可改善建议者的体贴、好感及控制性评价。因此，检查反馈不能只看它是否有步骤；措辞也会影响人如何接收指导。这项结果并未证明委婉建议一定提高操作准确率。[^advice]

Kim等人的访谈同样出现分歧：有参与者认为详细分析能帮助形成策略，也有人把仅有分析与建议体验为冷淡。作者据此建议将认知指导配合关系支持，但没有直接检验反馈是否通过减轻防御或提高理解而产生量表变化。[^interview][^limits]

## 在本站论文中的应用

《[[Affective and Cognitive Feedback from a Robot for Human-attributed Failure Handling]]》的FCF条件在预设倒塌后提供原因分析和具体纠正策略，同时用目光和注意性手势维持参与。参与者先学习目标、记忆颜色和顺序，由协作者取块递送，再自行搭建。因此反馈作用于参与者的搭建理解和策略，机器人没有替参与者自动重搭整座塔。[^auto2][^implementation]

NAO按标准脚本回应，人类研究者复制脚本、时机与行为。倒塌由隐藏机构在任务约完成90%时诱发；“失败分析”属于预设实验处理，不是机器人从传感器自动推断出真实原因的结果。该实验比较了反馈及协作者类型，没有验证自动诊断准确性。[^implementation]

P10自述分析与建议使自己改变后来放置积木的方法，P27认为指导帮助形成自己的策略。这是信息被用于调整行动的具体叙述，但没有相应的准确率或恢复速度测量。机器人组与人类组各有15/30人，即50%，将认知反馈选为最有用；对协作者观感最正面的反馈则更多选择情感反馈。[^interview]

量表比较须分清基线。FCF的[[团队合作质量]]高于失败后无反馈，p=.030；共在感和[[亲密感|亲密感]]亦较高，分别p=.003及p<.001。不过FAF在三项量表上都高于FCF。摘要关于认知反馈更强地增强团队合作质量的说法，与结果节FAF高于FCF、p=.002不一致；访谈有用性不能替换量表直接比较。[^results]

## 使用边界

这个实验的认知反馈是包含言语和非言语注意线索的组合，未隔离原因说明、具体建议、目光或手势的独立作用。实际系统要给出可靠原因解释，还需要能判断任务状态与失败原因；此项能力不能从预设倒塌实验推得。[^implementation][^limits]

作者提出的后续方向包括认知指导子类型、不同模态、时机及个性化，以及与情感反馈组合。其研究限于年轻非专业参与者、NAO和低风险轮替式任务；客观完成效率、恢复时间、再次出错和长期适应均未报告。[^limits]

## 参见

- [[情感反馈]]
- [[心智模型]]
- [[团队合作质量]]
- [[感知对方共在感]]
- [[Affective and Cognitive Feedback from a Robot for Human-attributed Failure Handling]]

## 参考文献

[^auto1]: Jihwan Kim等（2026）。[Affective and Cognitive Feedback from a Robot for Human-attributed Failure Handling](https://doi.org/10.1145/3772318.3791738)。PDF物理第3页§2.2。
[^auto2]: 同上，物理第5页§3.4。
[^implementation]: 同上，物理第4–6页§3.2–3.4。
[^interview]: 同上，物理第9–11页§4.4及图7–8。
[^results]: 同上，物理第1页摘要、第7页§4.1–4.3。
[^limits]: 同上，物理第12–13页§5.2、§5.4–5.5。
[^advice]: Cristen Torrey等（2013）。[How a Robot Should Give Advice](https://www.cs.cmu.edu/~kiesler/publications/2013/2013_how-robot-give-advice.pdf)。PDF物理第1–2页摘要与背景。
[^failure]: Shanee Honig、Tal Oron-Gilad（2018）。[Understanding and Resolving Failures in Human-Robot Interaction: Literature Review and Model Development](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.00861/full)。Abstract及RF-HIP模型说明。
