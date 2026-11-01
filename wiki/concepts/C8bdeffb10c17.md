---
id: C8bdeffb10c17
title: 局部忠实性
aliases:
- local fidelity
type: 概念
field: 人机智能交互
created: '2026-11-01'
updated: '2026-11-01'
---

局部忠实性（local fidelity）指解释与模型在待解释实例附近的实际行为相符。[^auto2]

## 在本站论文中的应用

- [[“Why Should I Trust You?” Explaining the Predictions of Any Classifier]]：LIME 用按接近程度加权的扰动样本拟合局部模型，优先近似待解释实例附近的黑箱行为。[^auto1]

## 参见

- [[“Why Should I Trust You?” Explaining the Predictions of Any Classifier]]
- [[模型可解释性]]
- [[Amazon Mechanical Turk]]

## 参考文献

[^auto2]: Marco Tulio Ribeiro、Sameer Singh、Carlos Guestrin（2016）。[“Why Should I Trust You?” Explaining the Predictions of Any Classifier](https://doi.org/10.1145/2939672.2939778)。PDF 第3页，Desired Characteristics for Explainers。

[^auto1]: Marco Tulio Ribeiro、Sameer Singh、Carlos Guestrin（2016）。[“Why Should I Trust You?” Explaining the Predictions of Any Classifier](https://doi.org/10.1145/2939672.2939778)。PDF 第3页，3.3 Sampling for Local Exploration。
