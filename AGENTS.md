# AGENTS.md

## 基本约束

- 使用 `uv` 和 `pyenv` 来管理 Python 环境。
- 默认使用简体中文回答，除非用户明确要求使用其他语言。
- 代码、命令、路径、接口字段、报错原文保持原样，不要翻译。
- 执行 shell 命令时默认使用 `rtk` 前缀。

## API Key 约束

- 本项目的本地 API Key 默认从仓库根目录 `.env` 读取。
- 不要把真实 API Key 写入 Markdown、代码、提交信息或可提交配置。
- 需要在 shell 命令里使用 `.env` 时，先显式加载：

```bash
set -a; . ./.env; set +a
```

- MCP 配置如果使用 `${VAR_NAME}`，读取的是启动 Codex/MCP 进程时的环境变量，不会自动读取项目 `.env`。
- 修改 `.env` 后，如需 MCP 生效，需要在启动 Codex 前导出对应环境变量，或重启会话让 MCP 重新读取环境。
