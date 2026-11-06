---
id: Cdb409e731fdb
title: 统一机器人描述格式
aliases:
- URDF
type: 概念
field: 人机智能交互
created: '2026-11-06'
updated: '2026-11-06'
---

统一机器人描述格式（Unified Robot Description Format，URDF）是ROS生态中描述机器人运动学的格式，以连接件及关节组织部件关系。关节描述不只是两份网格相接，还包括相对参照系、运动轴和限制等信息。RealTwin把这一格式用于日常对象的机械结构，将重建组件转为可导入仿真环境的运动关系。[^ros][^real]

## 连接件与关节

连接件（link）表示机械结构中的部件，关节（joint）连接两个link。ROS文档区分有角度限制的转动关节、无位置限制的连续转动关节，以及沿轴滑动的移动关节。关节可以被驱动，也可以由外力或其他关节被动带动；描述关节并不意味着它必须装有电机。[^ros]

官方示例中的joint具有parent、child、origin、axis和limit字段。parent和child指定连接的两端，origin描述关节参照位置和方向，axis指定运动轴，limit可写下限、上限、速度和力等约束。示例还用mimic定义一个关节跟随另一个关节的关系。URDF的标准运动学表示存在拓扑限制，不能凭一条耦合说明就认为任意闭环机械都已完整表达。[^ros]

在对象重建中，这些字段分别回答“哪些部件相连”“在哪里连接”“围绕哪根轴或沿哪个方向运动”“允许移动多少”。几何形状再逼真，若铰链轴放错，模拟的盖子仍可能绕错误位置运动；文件可以被解析，也不等于机械参数与实物一致。[^joint]

## RealTwin怎样使用URDF

《[[RealTwin: Concept Graph Representation and Grounding Framework for Reality-Preserving Digital Twin Reconstruction]]》先构建对象概念图，再实现机械连接属性。图中的有向边是组件细分关系，无向边是物理耦合；URDF承担后者的运动描述，因此概念图父子分解不能直接等同于URDF父子link。机械属性包括固定、转动或移动关节、运动链和动态约束，可存入连接属性字典。[^graph]

唱片机图提供了具体区别：唱臂包含臂、唱针和唱臂基座，是对象结构分解；臂与基座的转动、臂与唱针的固定，是机械连接。URDF化时需要为相连部件选择link与joint，补齐位置、轴和运动范围，才能模拟对应运动。[^record][^graph]

第一阶段提示给模型提供节点与边知识表、唱片机示例及JSON范例，并要求机械连接使用URDF关节类型，给出joint、parent和child等信息。模型因此先建立语义结构，后续工具链再补充无法仅靠文字可靠取得的几何参数。[^prompt]

## 从[[图像标注]]估计关节位置

RealTwin在分出组件网格后渲染多个正交视图，让模型以红点标注二维关节位置。设第\(i\)相机为\(C_i\)，二维标注为\(x_i\)，待估三维点为\(p\)，其求解为：

\[
p^*=\operatorname{Proj}\left(\arg\min_p\sum_i\|\operatorname{OrthProj}(C_i,p)-x_i\|^2,M\right).
\]

\(OrthProj\)把三维点投到相机图像，误差项检查该投影与标注是否相符；优化后再投到网格\(M\)上，得到关节位置。作者采用三个均匀分布的正交视图，以降低噪声、遮挡及对称形状带来的不稳定。关节类型和范围依赖模型先验，方向还结合分割平面与关节处切平面估计。[^joint]

这一步把“盖子与主体是转动连接”细化为可模拟参数。它不能从不存在的视觉线索恢复真实隐藏转轴，也没有给出两视图与三视图的定量消融。封闭铰链和厚外壳正是论文报告的困难对象。[^joint][^evaluation]

## 仿真检查与结果解释

RealTwin将URDF导入Isaac Sim，观察组件运动是否与实物相符，分别检查关节类型、位置和范围。30个对象共35个关节，类型接受率97.1%，范围94.2%，位置标注88.7%；其中26个关节三项参数均正确，并成功模拟。97.1%只说明类型判断，不能作为完整机械结构恢复率。[^evaluation]

位置错误常见于对称几何、隐藏连接和多关节紧密耦合。模型可能在盖子的另一侧放置转轴，或把多个自由度缩成一个简化关节。这类错误需要几何一致性、运动观察或物理可行性检查；作者把利用更多运动示例和轻量仿真检验列为未来改进。[^evaluation]

## 表达与实现的边界

URDF在RealTwin中是连接语言推断与仿真的接口，不承担所有对象属性。纹理、材料外观和手部姿态仍在概念图的其他属性中；真实交互还可能涉及变形、液体、电子逻辑和多手操作。论文虽讨论更丰富的物理参数，但并未通过URDF输出证明全部属性已被恢复。[^graph][^limits]

用户可用自然语言修正图中的连接类型，例如把把手与主体改为固定连接。细调复杂关节依赖、间接交互和连续行为仍是发展方向，不能把“可导入仿真”视为对象所有功能已经复制。[^interface][^limits]

## 参见

- [[RealTwin: Concept Graph Representation and Grounding Framework for Reality-Preserving Digital Twin Reconstruction]]
- [[数字孪生]]
- [[多模态大语言模型]]
- [[手部可供性]]

## 参考文献

[^ros]: ros2_control。[Joint Kinematics for ros2_control](https://control.ros.org/humble/doc/ros2_control/hardware_interface/doc/joints_userdoc.html)，Nomenclature、URDF及mimic关节示例。
[^real]: Zisu Li等（2026）。[RealTwin: Concept Graph Representation and Grounding Framework for Reality-Preserving Digital Twin Reconstruction](https://doi.org/10.1145/3772318.3790590)，PDF物理第10—11页，§4.2.2。
[^graph]: RealTwin，物理第5页，§3.2.1—3.2.2。
[^record]: RealTwin，物理第2页，图1。
[^prompt]: RealTwin，物理第6—7页，§3.3.1、图3。
[^joint]: RealTwin，物理第6—8页，§3.3.2 A2、式（2）。
[^evaluation]: RealTwin，物理第11页，§4.2.2。
[^interface]: RealTwin，物理第9页，§3.3.3。
[^limits]: RealTwin，物理第15页，§7。
