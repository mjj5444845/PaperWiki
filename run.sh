#!/bin/bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS:${PATH:-}"
export PYTHONUTF8=1
export PYTHONPYCACHEPREFIX="$PROJECT_DIR/.venv/pycache"
cd "$PROJECT_DIR"
if [[ ! -x .venv/bin/python ]]; then
  echo '请先创建 .venv 并安装 requirements-inbox.txt' >&2
  exit 1
fi
exec .venv/bin/python -m automation.inbox "$@"
