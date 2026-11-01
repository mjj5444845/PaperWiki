---
id: P01c7aa8f7d9e
title: A Unified Approach to Interpreting Model Predictions
aliases:
- 解释模型预测的统一方法
- Kernel SHAP
- Max SHAP
- Deep SHAP
type: 论文
field: 人机智能交互
created: '2026-11-01'
updated: '2026-11-01'
infobox:
  作者: Scott M. Lundberg、Su-In Lee
  年份: '2017'
  发表场所: 31st Conference on Neural Information Processing Systems (NIPS 2017)
  领域: 人机智能交互
  arXiv: 1705.07874v2
  代码: https://github.com/slundberg/shap
---

《解释模型预测的统一方法》是2017年发表于31st Conference on Neural Information Processing Systems (NIPS 2017)的研究论文。[^identity]

本文提出解释模型预测的统一框架 [[SHAP|SHAP]]，通过为单次预测中的各个特征分配重要性值，梳理复杂模型解释方法之间的关系。[^auto1]

论文将六种已有方法纳入加性特征归因类别，并说明在给定简化输入映射时，满足局部准确性、缺失性和一致性的归因解具有唯一性；随后提出近似估计方法，并通过计算实验、用户研究和图像分类案例进行评估。[^auto2]

## 背景与动机

复杂模型可能具有较高预测准确率，却难以解释；论文将这一矛盾作为研究动机。[^auto3]

已有预测解释方法之间的联系以及各自适用条件尚不清晰，因此需要统一的比较框架。[^auto4]

论文聚焦解释单个输入对应预测的局部方法，以可解释的近似模型替代难以直接理解的原模型。[^auto5]

## 方法

首先把解释本身视为模型：使用二元简化输入表示特征状态，并以基准项与各特征归因项的线性相加构成解释模型。论文据此统一讨论 [[“Why Should I Trust You?” Explaining the Predictions of Any Classifier|LIME]]、DeepLIFT、逐层相关性传播，以及三种经典 [[夏普利值|Shapley 值]]估计方法。[^auto6]

其次以三项性质约束归因：局部准确性要求解释模型在当前输入处匹配原模型输出；缺失性要求原输入中缺失的特征不产生归因影响；一致性要求某特征在所有其他输入组合下的边际贡献均不下降时，其归因值也不下降。对给定简化输入映射，论文借助合作博弈论结果确定唯一的加性归因解。[^auto7]

SHAP 将原模型条件期望函数的 Shapley 值作为特征重要性：从不知道任何特征时的预测期望出发，考察逐个加入特征条件后的变化，再对全部加入顺序取平均。特征独立性和模型线性可作为简化期望计算的可选假设。[^auto8]

Kernel SHAP 使用由 Shapley 性质确定的加权线性回归联合估计各特征归因，并通过解析约束处理空特征集和完整特征集处的无限权重。它提供不依赖特定模型类型的 SHAP 近似估计。[^auto9]

论文还讨论针对模型类型的近似：Linear SHAP 在输入特征独立假设下使用线性模型权重；Low-Order SHAP 面向较少特征；Max SHAP 利用排序计算最大值函数的 Shapley 值；Deep SHAP 将网络简单组件的 SHAP 值结合起来，通过反向传递乘子近似整个网络的归因。[^auto10]

## 主要贡献

- 提出加性特征归因这一解释模型类别，统一六种已有预测解释方法。[^auto11]

- 将合作博弈论中的唯一性结果推广到该类别，并以条件期望函数的 Shapley 值定义统一的 SHAP 重要性度量。[^auto12]

- 提出 Kernel SHAP、Max SHAP 和 Deep SHAP，并建立 Shapley 值与加权线性回归、网络组件归因组合之间的联系。[^auto13]

## 研究材料

计算效率实验使用两种决策树设置：一种使用全部 10 个输入特征，另一种仅使用 100 个输入特征中的 3 个；两者均解释单个输入。[^auto14]

用户研究通过 [[Amazon Mechanical Turk|Amazon Mechanical Turk]] 收集简单模型的人工解释，任务分别为症状对应的疾病评分归因和最大得分对应的收益分配；图中采用的最常见解释分别来自 30 名和 52 名随机个体。[^auto15]

图像实验使用 MNIST 数字数据集上的预训练卷积网络，输入归一化到 0 与 1 之间；网络由两个卷积层、两个全连接层和一个十分类 softmax 输出层组成。[^auto16]

## 实验与结果

| 结果及比较条件 | 出处 |
|---|---|
| 在稠密和稀疏决策树的比较中，作者报告 Kernel SHAP 比此前基于采样的估计以更少原模型求值获得更准确的归因估计，加入正则化时尤其如此。图中每个样本量使用 200 次重复估计，并展示第 10 和第 90 百分位数。[^auto17] | PDF 第8页 |
| 在疾病评分和最大收益分配两个任务中，作者报告 SHAP 与人工解释的一致程度高于所比较的其他方法；正文未给出这一差异的数值效应量或显著性检验。[^auto18] | PDF 第8页 |
| MNIST 类别区分实验中，SHAP 和 LIME 均使用 50k 个样本，按照各方法的归因遮蔽 20% 像素，以尝试将预测类别从 8 切换到 3。作者以 20 张随机图像遮蔽后的对数几率变化，支持采用更接近 SHAP 值的估计。[^auto19] | PDF 第9页 |

## 局限性

精确计算 SHAP 值具有困难，因此论文采用近似计算，并将特征独立性和模型线性作为简化期望计算的可选假设。[^auto20]

用户研究以理解模型的人所给出的解释应与良好模型解释一致为前提。[^auto21]

作者将减少假设的更快速模型专用估计、交互效应估计以及新的解释模型类别列为后续研究方向。[^auto22]

## 与其他工作的关系

论文的参考文献列有“Why Should I Trust You?” Explaining the Predictions of Any Classifier。[^auto23]

理解本论文涉及SHAP、夏普利值、Amazon Mechanical Turk。

## 参见

- [[SHAP]]
- [[夏普利值]]
- [[Amazon Mechanical Turk]]

## 参考文献

[^auto1]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第1页，Abstract。

[^auto2]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第1、4、8页，Abstract / 3 Simple Properties Uniquely Determine Additive Feature Attributions / 5 Computational and User Study Experiments。

[^auto3]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第1页，Abstract。

[^auto4]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第1页，1 Introduction。

[^auto5]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第2页，2 Additive Feature Attribution Methods。

[^auto6]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第2、3、5页，2 Additive Feature Attribution Methods / 2.4 Classic Shapley Value Estimation / 4 SHAP (SHapley Additive exPlanation) Values。

[^auto7]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第4页，3 Simple Properties Uniquely Determine Additive Feature Attributions。

[^auto8]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第4、5页，4 SHAP (SHapley Additive exPlanation) Values / Figure 1。

[^auto9]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第6页，4.1 Model-Agnostic Approximations。

[^auto10]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第6、7页，4.2 Model-Specific Approximations—Linear SHAP / 4.2 Model-Specific Approximations—Low-Order SHAP / Max SHAP / Deep SHAP (DeepLIFT + Shapley values)。

[^auto11]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第1页，1 Introduction。

[^auto12]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第2、4页，1 Introduction（续） / 4 SHAP (SHapley Additive exPlanation) Values。

[^auto13]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第5、6、7页，4 SHAP (SHapley Additive exPlanation) Values / 4.1 Model-Agnostic Approximations / Deep SHAP (DeepLIFT + Shapley values)。

[^auto14]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第8页，Figure 3。

[^auto15]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第8、9页，5.2 Consistency with Human Intuition / Figure 4。

[^auto16]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第9页，Figure 5 / 5.3 Explaining Class Differences。

[^auto17]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第8页，5.1 Computational Efficiency / Figure 3。

[^auto18]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第8页，5.2 Consistency with Human Intuition。

[^auto19]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第9页，5.3 Explaining Class Differences / Figure 5。

[^auto20]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第5页，4 SHAP (SHapley Additive exPlanation) Values。

[^auto21]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第8页，5.2 Consistency with Human Intuition。

[^auto22]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第9页，6 Conclusion。

[^auto23]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第10页，References。

[^identity]: Scott M. Lundberg、Su-In Lee（2017）。[A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874v2)。PDF 第1页，标题 / 会议标识。
