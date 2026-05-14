# FlyAI / Fliggy Tool

本目录保存飞猪旅行搜索工具，用于查询酒店、机票、火车票、景点等实时结果。

## 本地路径

- Skill 仓库：`06-research/tools/flyai-skill`
- CLI 安装目录：`06-research/tools/flyai-cli`
- CLI 可执行文件：`06-research/tools/flyai-cli/node_modules/.bin/flyai`

## 验证命令

```bash
06-research/tools/flyai-cli/node_modules/.bin/flyai --help
06-research/tools/flyai-cli/node_modules/.bin/flyai search-hotel --help
```

## 酒店查询示例

```bash
06-research/tools/flyai-cli/node_modules/.bin/flyai search-hotel \
  --dest-name "昆明" \
  --key-words "青旅" \
  --check-in-date 2026-06-01 \
  --check-out-date 2026-06-02 \
  --max-price 120 \
  --sort price_asc
```

## API Key

不配置 API Key 也可用体验模式，但结果可能受限。需要完整服务时再配置：

```bash
06-research/tools/flyai-cli/node_modules/.bin/flyai config set FLYAI_API_KEY "your-key"
```

不要把 `FLYAI_API_KEY` 写进项目文档或提交到版本控制。
