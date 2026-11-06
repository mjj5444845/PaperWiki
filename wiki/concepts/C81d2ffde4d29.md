---
id: C81d2ffde4d29
title: 社会空间界面
aliases:
- socio-spatial interface
type: 概念
field: 人类与机器人交互
created: '2026-11-05'
updated: '2026-11-05'
---

社会空间界面（socio-spatial interface）是通过感知并调节人际距离、身体朝向、凝视或可见关系，中介共享环境中社会互动的交互系统。界面作用不必集中在屏幕或物体表面，也可表现为声音、投影、家具运动及反射视野变化。MirrorBot论文将机器人视为一个实例：机体有边界，但主要改变的是两名陌生人之间的视觉场。[^definition][^auto1]

## 空间关系进入交互回路

Serena Guo的2025年博士论文摘要将基本关系描述为：计算日常环境中的人际距离、朝向和凝视，并将其转成空间及技术线索。SocialStools与MirrorBot是两项设计实例，分别探索视听反馈和可重定位镜面。共同点是把人与人之间的关系纳入输入输出，而不只把每个人当作独立操作者；机构库摘要并不能替代各系统完整技术评估。[^definition]

MirrorBot的相机及ROS-People模块提供头部坐标，镜面平台和移动底盘改变观看关系。两镜转动后，参与者看见自己、搭档或环境的组合随之变化，谁在何时能看见谁成为设计内容。实验中导航和状态切换由研究员遥控，人的社会判断仍在回路内。[^implementation]

它与[[共享工作空间]]有相邻的协调问题，但没有共同编辑的文档；其资源是可见关系和事件时段。机器人运动先吸引注意，镜面再把搭档带入视野，使装置可能从焦点转为中介。这是作者对系统作用的解释，不是所有机器人角色的普遍分类。[^auto2]

## MirrorBot的三个作用层次

| 层次 | 构件或操作 | 改变的关系 |
|---|---|---|
| 进入与位置 | 全向轮底盘接近，停在双方等距处 | 使干预成为可共同察觉的事件 |
| 反射配置 | 两面各两自由度镜子切换状态 | 改变自己、搭档与环境的可见性 |
| 时段组织 | 呈现、停留、继续调整和退出 | 调节观看机会，并让位于直接互动 |

例如，Dual Self中甲从两镜看自己、乙看环境，再轮换；Dual Other使双方经两镜看对方；Self + Other让甲分别看自己和乙，乙看甲与环境，再交换角色。作用单位是两人、两镜与位置构成的观看关系，不只是一面镜子显示的信息。[^states]

图4机场故事板还把退出纳入设计：双方开始直接交流或都无兴趣时，机器人离开。移动物体的到场和离场可使干预时段清楚，但这不是机场自主部署的实测证据。[^scenario]

## 在本站论文中的应用

《[["When We’re Looking at the Robot, We See Each Other": A Comparison of Robotic, Mirror-Based, and Hybrid Interventions for Stranger Interaction]]》在§6.1.4用这一概念解释系统。实验比较动态镜面机器人、同机体无反射、静态镜面和无干预。MirrorBot组[[共同注意|共同注意]]时间占23.0%，高于其余三组的10.4%、2.1%、2.2%，三个比较均显著；社会临场感问卷与交谈时长未显著。因此，部分共同观看行为的改变不能概括为全面提升社交关系。[^application]

仅机器人组被评为更能表达情绪、更有兴趣与人互动，却没有显示更好的人际结果。作者据访谈认为，没有镜面时机器人可能把注意留在自身，有镜面时参与者能一边看装置一边观察搭档。社会空间界面由此提出不同评价问题：系统是否使人更容易察觉彼此，而不只是物体是否显得有社会性。[^role]

## 变体与适用条件

作者提出倾转墙镜、顶棚镜和响应式表面等分布式形式，以考察同类机制。它们可能改变系统被理解为单个行动者还是环境一部分的程度；论文没有实测这些替代形式，不能认定底盘可被无损替换。[^auto1]

四条件未分离运动与具身：动态镜面只在MirrorBot中，静态镜面只在无机器人条件中，缺少无底盘动态镜面、机器人配静态镜面两种对照。现有结果不能确定反射配置本身解释多少效果。[^limits]

可见性也可能带来暴露感。作者建议略离正面视轴的可选观看位置、短暂缓慢动作、镜面之外的参与焦点，以及容易忽略或暂停的途径。原型在每人距机器人约2.5米内较可靠，远距与拥挤遮挡会削弱面孔辨认；公共场所重复使用和自主社会决策仍待研究。[^boundaries]

## 参见

- [["When We’re Looking at the Robot, We See Each Other": A Comparison of Robotic, Mirror-Based, and Hybrid Interventions for Stranger Interaction]]
- [[礼貌性忽视]]
- [[共同注意]]
- [[共享工作空间]]
- [[机器人自主程度]]

## 参考文献

[^definition]: Serena Guo（2025年8月）。[Designing Socio-Spatial Interfaces for Embodied and Situated Social Interaction](https://ecommons.cornell.edu/entities/publication/d166cc3e-1862-4221-85ce-2531bc5aff30)，Cornell博士论文，机构库摘要，社会参数、反馈和两项实例说明。
[^auto1]: Serena Ge Guo等（2026）。["When We’re Looking at the Robot, We See Each Other": A Comparison of Robotic, Mirror-Based, and Hybrid Interventions for Stranger Interaction](https://doi.org/10.1145/3772318.3791832)，PDF物理第19页§6.1.4。
[^auto2]: 同上，PDF物理第18—19页§6.1.1—6.1.4。
[^implementation]: 同上，PDF物理第6—7页§3.5、图5，第9页§4.3.2、第18页§6.1.2。
[^states]: 同上，PDF物理第4—5页§3.2、图3。
[^scenario]: 同上，PDF物理第5—6页§3.3、图4。
[^application]: 同上，PDF物理第8页§4.2、第12—15页§5.2—5.5、第31—32页表8—9。
[^role]: 同上，PDF物理第15页§5.6、第18—19页§6.1.1—6.1.3。
[^limits]: 同上，PDF物理第21页§7。
[^boundaries]: 同上，PDF物理第7页§3.5、第20—21页§6.2.2—7。
