# PaperWiki

论文百科是一个个人论文阅读库，包含25篇人机交互与CSCW论文和85个基础概念页。原始论文及本地研究数据不进入本仓库。网站无后端，不使用维基百科名称或标志作为本站品牌。

## 本地构建与预览

需要Python 3.9或更高版本。

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build.py
```

默认输出`site/`，链接前缀为`/PaperWiki/`。GitHub Actions从`GITHUB_REPOSITORY`自动推导仓库名；重命名仓库无需修改构建代码。本地按根路径预览：

```sh
BASE_URL=/ python build.py
python -m http.server -d site
```

打开终端显示的localhost地址。项目路径也可自行配置，例如`BASE_URL=/AnotherWiki/ python build.py`。不要把项目路径版本直接放在根路径服务器上预览，否则浏览器会请求错误前缀。

## 新增论文或概念页

1. 在本地阅读原论文，核实作者、DOI、结果口径及局限。原始PDF保存在被忽略的本地目录；所有事实使用真实来源和PDF页码。
2. 在`wiki/papers/`或`wiki/concepts/`添加一个Markdown文件，使用新的稳定ID，保留已有ID。论文以英文原题为规范标题，中文译名列为别名；Amazon Mechanical Turk和SHAP保留原名。
3. 在`wiki/registry.json`的`entities`添加对应记录：`id`、`canonical_name`、`type`（论文/概念）、`aliases`、`appears_in_papers`、`markdown_path`和`html_path`。更新计数；保持别名唯一。`wiki/redirects.json`是便于审阅的别名映射，构建以registry为准。
4. Frontmatter示例：

```yaml
---
id: P26
title: Original Paper Title
aliases: [论文中文译名]
type: 论文
field: 人机智能交互
created: '2026-11-01'
updated: '2026-11-01'
infobox:
  作者: 已核实的作者
  年份: 2026
  DOI: '[真实DOI](https://doi.org/真实DOI)'
---
```

正文先写定义与研究概述，再组织背景、方法、材料与结果、作者自述局限、与其他工作的关系。质性与理论研究不必伪造实验或基线。数字须保留条件与分母。

内部链接使用`[[规范页面名]]`或`[[页面名|显示文字]]`。可链接别名；只有第一次正文出现加链接，不链接自己；“参见”另列3—6个相关页面。构建器解析显式wikilinks，不会盲目给普通词自动加链接。正文中的未建页链接显示为红链，点击会显示提示页面，不会产生HTTP 404。

脚注使用Markdown格式：

```markdown
可核验的陈述。[^source]

## 参考文献

[^source]: 作者（年份）。[论文原题](https://doi.org/真实DOI)。PDF第3页，Methods。
```

公式使用`\(...\)`或`$$...$$`；KaTeX脚本、样式与字体均随仓库本地托管，其MIT许可见`assets/katex/LICENSE`。不要添加未核实的DOI或参考文献。缺少资料时标记`[来源请求]`。

5. 首页 `wiki/index.md` 的 `latest_batch` 标识最新发布批次，`latest_papers` 列出该批论文的稳定 ID。手动新增时替换为新批次；同批多篇合并列入。首页使用领域列表相同的链接与灰色概览样式，旧批论文继续保留在领域目录。收件箱流程在成功生成并通过审核后自动更新该列表，同一次运行中发布的论文合并为一批；没有新论文时保持原批次。

6. 运行构建和检查，再提交并推送：

```sh
python build.py
python -m unittest discover -s tests
python check.py
# 查看本次变化后，只添加需要公开的文件
git status
```

修改页面、registry并提交到main后，Actions重新构建和部署，无需提交`site/`。本仓库不包含原始材料到页面的全自动总结器；新增论文仍需来源审核。

## GitHub Pages

首次启用时，仓库 **Settings → Pages → Build and deployment → Source → GitHub Actions**。确认Actions可运行，首次部署时如有环境审批则批准`github-pages`环境。部署工作流使用官方`upload-pages-artifact`和`deploy-pages`，只发布`site/`，不会占用账号根站点。

已上线：<https://mjj5444845.github.io/PaperWiki/>。本仓库已将 Pages Source 配置为 GitHub Actions。首次推送文件清单经仓库所有者确认；部署验收见 `qa/deployment.md`。

## 页面解析与检查

`build.py`生成HTML、搜索索引、别名跳转和链接图，并验证站内文件/资源路径。`check.py`额外检查锚点、首次链接、孤立页面、未链接实体和参见数量，写入`qa/report.md`。链接数按有向页面对去重，不包含目录、脚注、自动反向链接与别名跳转；“参见”计入页面间导航。

`qa/fact-check.md`记录五个论文页面对照原文的抽查；`qa/style-check.md`记录风格自检。自动检查不能代替对新增事实与来源的人工审核。

## 增量收件箱

新论文放入 `inbox/`，运行 `./run.sh`；简报在 `reports/`，状态在本地 `state/manifest.json`。安装依赖、12 小时 macOS 调度、暂停/删除任务和保守清理规则见 [收件箱说明](automation/README.md)。定时任务须完成测试并经确认后才启用。

## 深度写作与审核

论文与概念页遵循仓库内 `skills/wiki-style-writer/`。先读全文及附录、按页记录私有 `notes/`、冻结10个读者问题，再组织方法、实验及外部背景/后续资料；不要把 `extract/` 字段直接转成文章。每篇论文以独立盲读至少8/10、独立事实核对和七类反模式检查作为发布条件。私有原文、笔记和日志均不上传。

`qa/diagnosis.md`记录诊断，`qa/rewrite-report.md`记录重写与问题闭环。可选研究工具依赖见 `requirements-research.txt`；`tools/depth_metrics.py`统计篇幅和结构，统计量不能替代内容审阅。`tools/rewrite_audit.py P02`会调用独立Codex角色并保存审校证据，使用已登录账户的用量。

收件箱的新流程见 `automation/README.md`。无法通过独立验收的论文保留为待复核，不发布；审核后任何候选页面变化都必须重新核对。
