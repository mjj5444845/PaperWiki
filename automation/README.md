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

模型只做只读、带物理 PDF 页码与逐字短引文的信息提取；Python 校验出处与数值出现位置，再按 skill 生成页面、精确别名归并、更新概念应用和相关论文导航。无法确定的语义同义关系保留到待复核，不强行合并；新概念仅对有明确定义的稳定必需前置知识建页，其余候选报告留待审核。一般性的文本检查不能证明论文的所有解释都正确，精确出处核验亦不能代替语义审稿。

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
