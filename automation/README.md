# 论文收件箱

将完整 PDF 放到项目根目录 `inbox/`，文件修改后满 10 分钟才处理；无需改文件名。扫描件先 OCR。保持电脑登录、有网络，Git SSH 和 `gh` 已认证，Codex CLI 保持 ChatGPT 登录；处理会使用当前账户的 Codex 用量。原文只在本机解析和传给已登录的 Codex 服务，不上传 GitHub。

## 安装和手动运行

```bash
.venv/bin/pip install -r requirements-inbox.txt
./run.sh
```

默认每篇最多 3 次尝试。`state/manifest.json` 是本地唯一状态依据，按内容 SHA-256 去重；请备份，不要删除。初始化时可导入已有论文的已核验哈希，避免再次投递首批材料时重建页面。`state/logs/` 保存日志、原文提取及失败候选，`reports/` 保存每次简报。上述目录默认不提交；如确需分享 manifest，先人工检查文件名与元数据再导出，不要强行提交整个 state。失败时修复问题后可以显式重置：

```bash
./run.sh --reset-failed <完整SHA256>
```

新流程先逐页精读全文（含本版本附录），保存本机 `notes/inbox-<sha>/` 笔记及冻结的10题；JSON抽取只用于元数据、注册表和导航，不再直接成为最终正文。深度作者在只读沙箱中检索、打开外部可靠来源，完整解释方法、实验和后续。每个角色使用新的临时进程；盲读者只收到新页面和题目，不收到原文、内部答案、其他QA或项目文件路径。独立评分者对照冻结要点评分，另一事实审校者回原文并重新打开外部来源，逐项检查事实、12项风格与7类反模式。角色均不得运行命令、修改项目或执行发布；只有Python脚本执行Git和清理。

少于8/10、事实有错误/未核、未覆盖的修改页或不完整检查均阻止发布。台账记 `status=failed, needs_review=true`，报告列入待复核并暂停本篇自动重试，人工处理后使用上述reset命令恢复；原始答案、评分、核对及来源记录在 `state/logs/<run>/<sha>/depth/`。修正后须重新运行独立验收，不能把作者自评替代审校。所有通过页面记录内容SHA-256，提交前重新比对，审核后改变内容会再次阻止提交。网络来源读不到或图表不能可靠核验时保守转待复核，不用关键词计分声称质量通过。

精确别名归并、概念建页标准和引用关系仍由带出处抽取约束；新概念及已有页应用由深度作者改写并一起进入事实核对，不能发布旧字段生成器的草架。`notes/`、原文和角色日志不上传。盲读/核对是独立模型审阅，不等同于人工认证，也没有重跑论文实验。

发布前在隔离副本构建并检查，主工作区有手动改动时拒绝提交。使用 `git pull --rebase` 同步，冲突立即停止、撤销本次 rebase；远端变化则下次基于新注册表重做。仅暂存本次 `wiki/*.md/json` 内容，不暂存 PDF、原文、日志或密钥。按篇提交、正常推送；提交后中断可从台账 `commit_sha` 继续，不重复生成。`published` 表示提交已在远端，部署等待或失败会进入报告；清理仍必须再次通过全部发布验证。

每 72 小时检查一次清理；`git ls-remote` 获取远端 main，fetch 后核对 tip，再验证台账提交是其祖先。最近一次部署工作流及 deploy 作业必须成功且包含该提交，线上页面必须返回 200 并包含论文标题，源文件哈希与稳定时间再次符合要求，才由脚本移动到 `inbox/.trash/`。记录保留 14 天后仅删除台账记载且哈希未变的隔离文件，保留哈希台账。损坏、失败、未发布或被同名替换的文件不删除。

## macOS 定时任务

```bash
# 只安装停用的 plist，不运行；测试确认后才执行 enable
.venv/bin/python -m automation.schedule prepare
.venv/bin/python -m automation.schedule enable
# 查看 / 暂停 / 删除任务（均不删除台账或论文）
.venv/bin/python -m automation.schedule status
.venv/bin/python -m automation.schedule pause
.venv/bin/python -m automation.schedule remove
```

任务名 `com.paperwiki.inbox`，登录时运行一次、此后每 43200 秒触发。电脑休眠或关机时不能处理；下次登录/运行会重新判断清理时间。暂停不会中断已经开始的一次运行；需要中止时按日志 PID 先终止进程，切勿在处理期间手动改台账。超过 6 小时且没有活动系统锁的残留运行锁可接管；单次调度有时间预算。源码和本机路径移动后需删除并重新安装 plist。

## 验证与维护

```bash
.venv/bin/python -m unittest discover -s tests
python build.py
python check.py
# 仅本次把清理间隔设为 0，不修改默认 72 小时
./run.sh --cleanup-only --cleanup-hours 0
```

12 小时处理和 72 小时清理的默认配置位于 `automation/config.json`。`run.sh` 不自动安装依赖或保存任何密钥。不需另建清理定时任务。原始抽取和候选可在本地查看；若账户登录失效、权限不足或网络不可用，报告会保留失败原因，达到 3 次后停止自动重试。

实现依据：[Codex 非交互模式](https://developers.openai.com/codex/noninteractive)；本地 `codex exec --help`。使用 `read-only` 沙箱、禁止审批等待和结构化输出，不使用跳过沙箱参数。


深度流程实现：`automation/depth.py`。CLI结构化输出和网络配置依据[官方非交互文档](https://learn.chatgpt.com/docs/non-interactive-mode)及[官方Web search文档](https://learn.chatgpt.com/docs/web-search)。每篇会使用多次独立调用，耗时和账户用量高于旧字段转写流程。

图表检查：本地用 PyMuPDF 渲染完整 PDF，逐页图片仅附给精读、写作和事实核对角色；独立读者仍只收到页面正文和题目。图片保存在忽略上传的 state/logs/ 中。

引文定位失败时，仅允许从同页原文候选中选择片段，不改冻结问题与答案；仍不能定位则转待复核。构建也会拒绝重复脚注定义，防止引用到错误文献。
