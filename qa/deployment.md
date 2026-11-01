# 部署与线上验收

日期：2026-11-01。

- 网站：https://mjj5444845.github.io/PaperWiki/
- 仓库：https://github.com/mjj5444845/PaperWiki
- 首次部署提交：`3e1c104`；保留远端原有 main 历史，使用普通推送。
- 成功工作流：https://github.com/mjj5444845/PaperWiki/actions/runs/41348642790
- Pages Source 已通过 GitHub API 设置为 GitHub Actions，无需用户再次设置。
- 所有 348 个生成的 HTML、JSON、CSS、JS 和字体地址在线返回 HTTP 200（见 online-http.json）。构建检查验证 `/PaperWiki/` 前缀及全部内部目标；另有 `/` 和改名路径测试。
- 在线浏览器实测：中文“协同过滤”、英文“SHAP”搜索；MTurk 跳转至 Amazon Mechanical Turk 并显示别名提示；脚注与返回箭头；红链提示及落地页；内部链接导言预览（键盘聚焦触发，与鼠标共用显示逻辑）；协同过滤页 4 个 KaTeX 渲染节点。
- 将线上 P23 页面放入 390px iframe，核验窄屏信息框及折叠菜单，展开后导航可见；见 preview-live-mobile.png。首页截图见 preview-live.png。
- 公开提交树未包含论文 PDF、raw/、extract/、site/ 或本地配置；首次推送已通过清单确认和密钥扫描。

未发现阻碍阅读或部署的问题。线上检查不包括逐一核验外部 DOI 网站的可用性；论文事实抽查覆盖 5 篇，详见 fact-check.md。
