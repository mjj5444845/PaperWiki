# 首次推送前的文件检查

2026-11-01。已检查实际暂存区，首次推送尚未执行。

- 计划提交196个文件；完整清单见`commit-manifest.txt`。
- 已扫描132个文本文件的暂存版本，未检出GitHub/OpenAI/AWS凭据、私钥或疑似密钥赋值。字体与截图仅作文件类型检查。
- 暂存区没有PDF、原始论文目录、raw、extract、.env、密钥、虚拟环境或site构建产物。
- `git check-ignore -v`已确认实际论文PDF及papers/raw/extract/.env/secrets/site示例路径均受忽略规则覆盖。
- 工作流的`id-token: write`是GitHub Pages OIDC权限声明，不是实际凭据；本站没有配置API key。
- 远端已有main初始化提交与README，本地基于该提交，保留已有README标题并扩展说明。没有force push。

## 分类统计

- .github：1个文件
- .gitignore：1个文件
- README.md：1个文件
- assets：66个文件
- build.py：1个文件
- check.py：1个文件
- qa：8个文件
- requirements.txt：1个文件
- templates：2个文件
- tests：1个文件
- wiki：113个文件
